# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import netaddr
import urllib
import urlparse

from datetime import datetime
from webob import exc


from nova import compute
from nova import crypto
from nova import db
from nova import exception
from nova import flags
from nova import log as logging
from nova import quota
import nova.image
from nova.api.openstack import create_instance_helper
from nova.auth import manager as auth_manager
from nova.db.sqlalchemy.session import get_session
from nova.db.sqlalchemy import models
from nova.db.sqlalchemy import api as sqlalchemy_api


import nova.api.openstack as openstack_api
from nova.api.openstack import extensions
from nova.api.openstack import faults
from nova.api.openstack import views

from nova.compute import instance_types
from nova.scheduler import api as scheduler_api

from sqlalchemy.orm import joinedload

FLAGS = flags.FLAGS
flags.DECLARE('max_gigabytes', 'nova.scheduler.simple')
flags.DECLARE('max_cores', 'nova.scheduler.simple')

LOG = logging.getLogger('nova.api.openstack.admin')


class AdminQuotasController(object):
    def _format_quota_set(self, project_id, quota_set):
        """Convert the quota object to a result dict"""
        if quota_set:
            return {
                'id': project_id,
                'metadata_items': quota_set['metadata_items'],
                'injected_file_content_bytes': quota_set['injected_file_content_bytes'],
                'volumes': quota_set['volumes'],
                'gigabytes': quota_set['gigabytes'],
                'ram': quota_set['ram'],
                'floating_ips': quota_set['floating_ips'],
                'instances': quota_set['instances'],
                'injected_files': quota_set['injected_files'],
                'cores': quota_set['cores'],
            }
        else:
            return {}

    def index(self, req):
        if urlparse.parse_qs(req.environ['QUERY_STRING']).get('defaults', False):
            return {'quota_set_list': [self._format_quota_set('__defaults__',
                quota._get_default_quotas())]}
        else:
            context = req.environ['nova.context']
            user = req.environ.get('user')
            projects = auth_manager.AuthManager().get_projects(user=user)

            quota_set_list = [self._format_quota_set(project.name,
                              quota.get_project_quotas(context, project.name))
                              for project in projects]
            return {'quota_set_list': quota_set_list}

    def show(self, req, id):
        context = req.environ['nova.context']
        project_id = id
        return {'quota_set': self._format_quota_set(id,
                quota.get_project_quotas(context, id))}

    def update(self, req, id, body):
        context = req.environ['nova.context']
        project_id = id
        resources = ['metadata_items', 'injected_file_content_bytes',
                'volumes', 'gigabytes', 'ram', 'floating_ips', 'instances',
                'injected_files', 'cores']

        for key in body['quota_set'].keys():
            if key in resources:
                value = int(body['quota_set'][key])
                try:
                    db.quota_update(context, project_id, key, value)
                except exception.ProjectQuotaNotFound:
                    db.quota_create(context, project_id, key, value)
        return {'quota_set': quota.get_project_quotas(context, project_id)}


class OverrideHelper(create_instance_helper.CreateInstanceHelper):
    """Allows keypair name to be passed in request."""
    def create_instance(self, req, body, create_method):
        if not body:
            raise faults.Fault(exc.HTTPUnprocessableEntity())

        context = req.environ['nova.context']

        password = self.controller._get_server_admin_password(body['server'])

        key_name = body['server'].get('key_name')
        key_data = None

        if key_name:
            try:
                key_pair = db.key_pair_get(context, context.user_id, key_name)
                key_name = key_pair['name']
                key_data = key_pair['public_key']
            except:
                msg = _("Can not load the requested key %s" % key_name)
                return faults.Fault(exc.HTTPBadRequest(msg))
        else:
            key_name = None
            key_data = None
            key_pairs = db.key_pair_get_all_by_user(context, context.user_id)
            if key_pairs:
                key_pair = key_pairs[0]
                key_name = key_pair['name']
                key_data = key_pair['public_key']

        image_href = self.controller._image_ref_from_req_data(body)
        try:
            image_service, image_id = nova.image.get_image_service(image_href)
            kernel_id, ramdisk_id = self._get_kernel_ramdisk_from_image(req,
                                                                        image_service,
                                                                        image_id)
            images = set([str(x['id']) for x in image_service.index(context)])
            assert str(image_id) in images
        except Exception, e:
            msg = _("Cannot find requested image %(image_href)s: %(e)s" %
                                                                    locals())
            raise faults.Fault(exc.HTTPBadRequest(explanation=msg))

        personality = body['server'].get('personality')

        injected_files = []
        if personality:
            injected_files = self._get_injected_files(personality)

        flavor_id = self.controller._flavor_id_from_req_data(body)

        if not 'name' in body['server']:
            msg = _("Server name is not defined")
            raise exc.HTTPBadRequest(explanation=msg)

        zone_blob = body['server'].get('blob')
        name = body['server']['name']
        self._validate_server_name(name)
        name = name.strip()

        reservation_id = body['server'].get('reservation_id')

        security_groups = filter(bool, body['server']
                                       .get('security_groups', '')
                                       .split(',')) + ['default']

        for group_name in security_groups:
            if not db.security_group_exists(context,
                                            context.project_id,
                                            group_name):
                group = {'user_id': context.user_id,
                         'project_id': context.project_id,
                         'name': group_name,
                         'description': ''}
                db.security_group_create(context, group)

        try:
            inst_type = \
                    instance_types.get_instance_type_by_flavor_id(flavor_id)
            extra_values = {
                'instance_type': inst_type,
                'image_ref': image_href,
                'password': password}

            return (extra_values,
                    create_method(context,
                                  inst_type,
                                  image_id,
                                  kernel_id=kernel_id,
                                  ramdisk_id=ramdisk_id,
                                  display_name=name,
                                  display_description=name,
                                  key_name=key_name,
                                  key_data=key_data,
                                  metadata=body['server'].get('metadata', {}),
                                  injected_files=injected_files,
                                  admin_password=password,
                                  zone_blob=zone_blob,
                                  user_data=body['server'].get('user_data', None),
                                  security_group=security_groups,
                                  reservation_id=reservation_id))
        except quota.QuotaError as error:
            self._handle_quota_error(error)
        except exception.ImageNotFound as error:
            msg = _("Can not find requested image")
            raise faults.Fault(exc.HTTPBadRequest(explanation=msg))

        # Let the caller deal with unhandled exceptions.


def user_dict(user, base64_file=None):
    """Convert the user object to a result dict"""
    if user:
        return {
            'username': user.id,
            'accesskey': user.access,
            'secretkey': user.secret,
            'file': base64_file}
    else:
        return {}


def project_dict(project):
    """Convert the project object to a result dict"""
    if project:
        return {
            'id': project.id,
            'name': project.id,
            'projectname': project.id,
            'project_manager_id': project.project_manager_id,
            'description': project.description}
    else:
        return {}

def network_dict(network):
    if network:
        fields = ('created_at', 'updated_at', 'deleted_at','deleted',
                  'id','injected','cidr','netmask','bridge','gateway','broadcast','dns1',
                  'vlan','vpn_public_address','vpn_public_port','vpn_private_address','dhcp_start',
                  'project_id','host','cidr_v6','gateway_v6','label','netmask_v6','bridge_interface','multi_host')
        return dict((field, getattr(network, field)) for field in  fields)
    else:
        return {}


def host_dict(host, compute_service, instances, volume_service, volumes, now):
    """Convert a host model object to a result dict"""
    rv = {'hostname': host, 'instance_count': len(instances),
          'volume_count': len(volumes)}
    if compute_service:
        latest = compute_service['updated_at'] or compute_service['created_at']
        delta = now - latest
        if delta.seconds <= FLAGS.service_down_time:
            rv['compute'] = 'up'
        else:
            rv['compute'] = 'down'
    if volume_service:
        latest = volume_service['updated_at'] or volume_service['created_at']
        delta = now - latest
        if delta.seconds <= FLAGS.service_down_time:
            rv['volume'] = 'up'
        else:
            rv['volume'] = 'down'
    return rv


class PrivilegedServerController(openstack_api.servers.ControllerV11):
    def _build_extended_attributes(self, inst):

        security_groups = [i.name for i in inst.get(
                            'security_groups', [])]
        attrs = {'name': inst['display_name'],
                'memory_mb': inst['memory_mb'],
                'vcpus': inst['vcpus'],
                'disk_gb': inst['local_gb'],
                'image_ref': inst['image_ref'],
                'kernel_id': inst['kernel_id'],
                'ramdisk_id': inst['ramdisk_id'],
                'user_id': inst['user_id'],
                'security_groups': security_groups,
                # TODO remove project_id
                'project_id': inst['project_id'],
                'tenant_id': inst['project_id'],
                'scheduled_at': inst['scheduled_at'],
                'launched_at': inst['launched_at'],
                'terminated_at': inst['terminated_at'],
                'description': inst['display_description'],
                'os_type': inst['os_type'],
                'hostname': inst['hostname'],
                'host': inst['host'],
                'key_name': inst['key_name'],
                'user_data': inst['user_data'],
                #'mac_address': inst['mac_address'],
                'os_type': inst['os_type'],
                }
        return attrs

    def index(self, req):
        # This has been revised so that it is less coupled with
        # the implementation of the Servers API, which is in flux

        # KLUDGE to make this extension working with different nova branches
        # in a soon future there will be only:
        if hasattr(self, '_items'):
            servers = self._items(req, is_detail=True)
        else:
            servers = self._get_servers(req, is_detail=True)

        ids = [server['id'] for server in servers['servers']]

        context = req.environ['nova.context']
        session = get_session()

        instance_map = {}
        for i in session.query(models.Instance).filter(
                               models.Instance.id.in_(ids)).all():
            instance_map[i.id] = i

        for s in servers['servers']:
            s['attrs'] = self._build_extended_attributes(instance_map[s['id']])
        return servers

    @scheduler_api.redirect_handler
    def show(self, req, id):
        """ Returns server details by server id """
        rval = super(PrivilegedServerController, self).show(req, id)
        instance = self.compute_api.routing_get(
            req.environ['nova.context'], id)
        rval['server']['attrs'] = self._build_extended_attributes(instance)
        return rval

    # @scheduler_api.redirect_handler
    def update(self, req, id, body):
        """ Updates the server name or password """
        if len(req.body) == 0:
            raise exc.HTTPUnprocessableEntity()

        if not body:
            return faults.Fault(exc.HTTPUnprocessableEntity())

        ctxt = req.environ['nova.context']
        update_dict = {}

        if 'name' in body['server']:
            name = body['server']['name']
            self.helper._validate_server_name(name)
            update_dict['display_name'] = name.strip()

        if 'description' in body['server']:
            description = body['server']['description']
            update_dict['display_description'] = description.strip()

        self._parse_update(ctxt, id, body, update_dict)

        try:
            self.compute_api.update(ctxt, id, **update_dict)
        except exception.NotFound:
            return faults.Fault(exc.HTTPNotFound())

        return exc.HTTPNoContent()

    def __init__(self):
        super(PrivilegedServerController, self).__init__()
        self.helper = OverrideHelper(self)


def downgrade_context(f):
    def new_f(*args, **kwargs):
        context = kwargs['req'].environ['nova.context']
        context.is_admin = False
        return f(*args, **kwargs)

    return new_f


class ExtrasServerController(PrivilegedServerController):
    # Downgrade context so that admin's don't have to look
    # at the entire cloud's instances from user dash
    @downgrade_context
    def index(self, req):
        return super(ExtrasServerController, self).index(req)

    def __init__(self):
        super(ExtrasServerController, self).__init__()


class ExtrasConsoleController(object):
    def create(self, req, body):
        context = req.environ['nova.context']
        console_type = body['console'].get('type')
        server_id = body['console'].get('server_id')
        compute_api = compute.API()
        if console_type == 'text':
            output = compute_api.get_console_output(
                      context, instance_id=server_id)
        elif console_type == 'vnc':
            output = compute_api.get_vnc_console(
                      context, instance_id=server_id)['url']
        else:
            raise Exception("Not Implemented")
        return {'console':{'id': '', 'type': console_type, 'output': output}}


class ExtrasSnapshotController(object):
    def create(self, req, body):
        context = req.environ['nova.context']
        instance_id = body['snapshot'].get('instance_id')
        name = body['snapshot'].get('name')

        compute_api = compute.API()
        meta = compute_api.snapshot(context, instance_id, name)

        return { 'snapshot': {'id': '',
                              'instance_id': instance_id,
                              'meta': meta,
                              'name': name }}


class ExtrasFlavorController(openstack_api.flavors.ControllerV11):
    def _get_view_builder(self, req):
        class ViewBuilder(views.flavors.ViewBuilderV11):

            def _build_simple(self, flavor_obj):
                simple = {
                    "id": flavor_obj["flavorid"],
                    "name": flavor_obj["name"],
                    #FIXME - why isn't this memory_mb?
                    "ram": flavor_obj["memory_mb"],
                    "disk": flavor_obj["local_gb"],
                    "vcpus": flavor_obj["vcpus"],
                }
                return simple


        base_url = req.application_url
        return ViewBuilder(base_url)


class AdminFlavorController(ExtrasFlavorController):

    def create(self, req, body):
        name = body['flavor'].get('name')
        memory_mb = body['flavor'].get('memory_mb')
        vcpus = body['flavor'].get('vcpus')
        local_gb = body['flavor'].get('local_gb')
        flavorid = body['flavor'].get('flavorid')
        swap = body['flavor'].get('swap')
        rxtx_quota = body['flavor'].get('rxtx_quota')
        rxtx_cap = body['flavor'].get('rxtx_cap')

        context = req.environ['nova.context']
        flavor = instance_types.create(name, memory_mb, vcpus,
                                       local_gb, flavorid,
                                       swap, rxtx_quota, rxtx_cap)
        builder = self._get_view_builder(req)
        values = builder.build(body['flavor'], is_detail=True)
        return dict(flavor=values)

    def delete(self, req, id):
        qs = req.environ.get('QUERY_STRING', '')
        env = urlparse.parse_qs(qs)

        purge = env.get('purge', False)

        flavor = instance_types.get_instance_type_by_flavor_id(id)
        if purge:
            instance_types.purge(flavor['name'])
        else:
            instance_types.destroy(flavor['name'])

        return exc.HTTPAccepted()


class UsageController(object):

    def _hours_for(self, instance, period_start, period_stop):
        # nothing if it stopped before the usage report start
        #terminated_at = instance['terminated_at']
        #launched_at = instance['launched_at']

        launched_at = instance['launched_at']
        terminated_at = instance['terminated_at']
        if terminated_at is not None:
            if not isinstance(terminated_at, datetime):
                terminated_at = datetime.strptime(terminated_at, "%Y-%m-%d %H:%M:%S.%f")

        if launched_at is not None:
            if not isinstance(launched_at, datetime):
                launched_at = datetime.strptime(launched_at, "%Y-%m-%d %H:%M:%S.%f")

        if terminated_at and terminated_at < period_start:
            return 0
        # nothing if it started after the usage report ended
        if launched_at and launched_at > period_stop:
            return 0
        if launched_at:
            # if instance launched after period_started, don't charge for first
            start = max(launched_at, period_start)
            if terminated_at:
                # if instance stopped before period_stop, don't charge after
                stop = min(period_stop, terminated_at)
            else:
                # instance is still running, so charge them up to current time
                stop = period_stop
            dt = stop - start
            seconds = dt.days * 3600 * 24 + dt.seconds\
                      + dt.microseconds / 100000.0

            return seconds/3600.0
        else:
            # instance hasn't launched, so no charge
            return 0

    def _usage_for_period(self, context, period_start, period_stop, tenant_id=None):
        fields = ['id',
                  'image_ref',
                  'project_id',
                  'user_id',
                  'vcpus',
                  'hostname',
                  'display_name',
                  'host',
                  'vm_state',
                  'instance_type_id',
                  'launched_at',
                  'terminated_at']

        tenant_clause = ''
        if tenant_id:
            tenant_clause = " and project_id='%s'" % tenant_id

        connection = get_session().connection()
        rows = connection.execute("select %s from instances where \
                                   (terminated_at is NULL or terminated_at > '%s') \
                                   and (launched_at < '%s') %s" %\
                                   (','.join(fields), period_start.isoformat(' '),\
                                   period_stop.isoformat(' '), tenant_clause
                                   )).fetchall()

        rval = {}
        flavors = {}

        for row in rows:
            o = {}
            for i in range(len(fields)):
                o[fields[i]] = row[i]
            o['hours'] = self._hours_for(o, period_start, period_stop)
            flavor_type = o['instance_type_id']

            try:
                flavors[flavor_type] = \
                    db.instance_type_get_by_id(context, flavor_type)

            except AttributeError:
                # The most recent version of nova renamed this function
                flavors[flavor_type] = \
                    db.instance_type_get(context, flavor_type)
            except exception.InstanceTypeNotFound:
                # can't bill if there is no instance type
                continue

            flavor = flavors[flavor_type]

            o['name'] = o['display_name']
            del(o['display_name'])

            o['ram_size'] = flavor['memory_mb']
            o['disk_size'] = flavor['local_gb']

            o['tenant_id'] = o['project_id']
            del(o['project_id'])

            o['flavor'] = flavor['name']
            del(o['instance_type_id'])

            o['started_at'] = o['launched_at']
            del(o['launched_at'])

            o['ended_at'] = o['terminated_at']
            del(o['terminated_at'])

            if o['ended_at']:
                o['state'] = 'terminated'
            else:
                o['state'] = o['vm_state']

            del(o['vm_state'])

            now = datetime.utcnow()

            if o['state'] == 'terminated':
                delta = self._parse_datetime(o['ended_at'])\
                             - self._parse_datetime(o['started_at'])
            else:
                delta = now - self._parse_datetime(o['started_at'])

            o['uptime'] = delta.days * 24 * 60 + delta.seconds

            if not o['tenant_id'] in rval:
                summary = {}
                summary['tenant_id'] = o['tenant_id']
                summary['instances'] = []
                summary['total_disk_usage'] = 0
                summary['total_cpu_usage'] = 0
                summary['total_ram_usage'] = 0

                summary['total_active_ram_size'] = 0
                summary['total_active_disk_size'] = 0
                summary['total_active_vcpus'] = 0
                summary['total_active_instances'] = 0

                summary['total_hours'] = 0
                summary['begin'] = period_start
                summary['stop'] = period_stop
                rval[o['tenant_id']] = summary

            rval[o['tenant_id']]['total_disk_usage'] += o['disk_size'] * o['hours']
            rval[o['tenant_id']]['total_cpu_usage'] += o['vcpus'] * o['hours']
            rval[o['tenant_id']]['total_ram_usage'] += o['ram_size'] * o['hours']

            if o['state'] is not 'terminated':
                rval[o['tenant_id']]['total_active_ram_size'] += o['ram_size']
                rval[o['tenant_id']]['total_active_vcpus'] += o['vcpus']
                rval[o['tenant_id']]['total_active_disk_size'] += o['disk_size']
                rval[o['tenant_id']]['total_active_instances'] += 1

            rval[o['tenant_id']]['total_hours'] += o['hours']
            rval[o['tenant_id']]['instances'].append(o)

        return rval.values()

    def _parse_datetime(self, dtstr):
        if isinstance(dtstr, datetime):
            return dtstr
        try:
            return datetime.strptime(dtstr, "%Y-%m-%dT%H:%M:%S")
        except:
            try:
                return datetime.strptime(dtstr, "%Y-%m-%dT%H:%M:%S.%f")
            except:
                return datetime.strptime(dtstr, "%Y-%m-%d %H:%M:%S.%f")

    def _get_datetime_range(self, req):
        qs = req.environ.get('QUERY_STRING', '')
        env = urlparse.parse_qs(qs)
        period_start = self._parse_datetime(env.get('start', [datetime.utcnow().isoformat()])[0])
        period_stop = self._parse_datetime(env.get('end', [datetime.utcnow().isoformat()])[0])
        return (period_start, period_stop)

    # TODO(ja): add methods to just get summary
    def index(self, req):
        (period_start, period_stop) = self._get_datetime_range(req)
        context = req.environ['nova.context']
        usage = self._usage_for_period(context, period_start, period_stop)
        return {'usage': {'values': usage}}

    def show(self, req, id):
        (period_start, period_stop) = self._get_datetime_range(req)
        context = req.environ['nova.context']
        usage = self._usage_for_period(context, period_start, period_stop, id)
        if len(usage):
            usage = usage[0]
        else:
            usage = {}
        return {'usage': usage}


class AdminServiceController(object):

    def _format_service(self, service):
        now = datetime.utcnow()
        delta = now - (service['updated_at'] or service['created_at'])
        stats = {}
        if service['binary'] == 'nova-compute':
            # FIXME: the following 2 fields should be reported on a
            #  host-by-host basis
            stats['max_vcpus'] = FLAGS.max_cores
            stats['max_gigabytes'] = FLAGS.max_gigabytes
            if service.compute_node:
                compute_node = service.compute_node[0]
                stats['vcpus'] = compute_node['vcpus']
                stats['vcpus_used'] = compute_node['vcpus_used']
                stats['memory_mb'] = compute_node['memory_mb']
                stats['memory_mb_used'] = compute_node['memory_mb_used']
                stats['local_gb'] = compute_node['local_gb']
                stats['local_gb_used'] = compute_node['local_gb_used']
                stats['hypervisor_type'] = compute_node['hypervisor_type']
                stats['hypervisor_version'] = compute_node['hypervisor_version']
                stats['cpu_info'] = json.loads(compute_node['cpu_info'])
        meta = {
            'id': service['id'],
            'host': service['host'],
            'disabled': service['disabled'],
            'type': service['binary'],
            'zone': service['availability_zone'],
            'last_update': service['updated_at'],
            'up': (delta.seconds <= FLAGS.service_down_time),
            'stats': stats
        }
        return meta

    def index(self, req):
        def service_get_all_compute(context):
            topic = 'compute'
            session = get_session()
            result = session.query(models.Service).\
                          options(joinedload('compute_node')).\
                          filter_by(deleted=False).\
                          filter_by(topic=topic).\
                          all()

            if not result:
                raise exception.ComputeHostNotFound(host=host)

            return result

        context = req.environ['nova.context']
        services = []
        for service in service_get_all_compute(context):
            services.append(self._format_service(service))
        for service in db.service_get_all(context):
            if service.binary == 'nova-compute':
                continue
            services.append(self._format_service(service))
        return {'services': services}

    def show(self, req, id):
        context = req.environ['nova.context']
        service = self._format_service(db.service_get(context, id))
        return {'service': service}

    def update(self, req, id, body):
        context = req.environ['nova.context']
        name = body['service'].get('disabled')
        db.service_update(context, id, body['service'])
        return exc.HTTPAccepted()


class ExtrasKeypairController(object):
    def _gen_key(self, context, user_id, key_name):
        """Generate a key

        This is a module level method because it is slow and we need to defer
        it into a process pool."""
        # NOTE(vish): generating key pair is slow so check for legal
        #             creation before creating key_pair
        try:
            db.key_pair_get(context, user_id, key_name)
            raise exception.KeyPairExists(key_name=key_name)
        except exception.NotFound:
            pass
        private_key, public_key, fingerprint = crypto.generate_key_pair()
        key = {}
        key['user_id'] = user_id
        key['name'] = key_name
        key['public_key'] = public_key
        key['fingerprint'] = fingerprint
        db.key_pair_create(context, key)
        return {'private_key': private_key, 'fingerprint': fingerprint}

    def create(self, req, body):
        context = req.environ['nova.context']
        key_name = body['keypair']['key_name']
        LOG.audit(_("Create key pair %s"), key_name, context=context)
        data = self._gen_key(context, context.user_id, key_name)

        rval = body
        rval['keypair']['fingerprint'] = data['fingerprint']
        rval['keypair']['private_key'] = data['private_key']
        return rval

    def delete(self, req, id):
        context = req.environ['nova.context']
        key_name = id
        LOG.audit(_("Delete key pair %s"), key_name, context=context)
        try:
            db.key_pair_destroy(context, context.user_id, key_name)
        except exception.NotFound:
            # aws returns true even if the key doesn't exist
            pass
        return exc.HTTPAccepted()

    def index(self, req):
        context = req.environ['nova.context']
        key_pairs = db.key_pair_get_all_by_user(context, context.user_id)
        result = []
        for key_pair in key_pairs:
            # filter out the vpn keys
            suffix = FLAGS.vpn_key_suffix
            if context.is_admin or \
               not key_pair['name'].endswith(suffix):
                result.append({
                    'name': key_pair['name'],
                    'key_name': key_pair['name'],
                    'fingerprint': key_pair['fingerprint'],
                })


        return {'keypairs': result}


class AdminProjectController(object):

    def show(self, req, id):
        return project_dict(auth_manager.AuthManager().get_project(id))

    def index(self, req):
        user = req.environ.get('user')
        return {'projects':
            [project_dict(u) for u in
            auth_manager.AuthManager().get_projects(user=user)]}

    def create(self, req, body):
        name = body['project'].get('name')
        manager_user = body['project'].get('manager_user')
        description = body['project'].get('description')
        member_users = body['project'].get('member_users')

        context = req.environ['nova.context']
        msg = _("Create project %(name)s managed by"
                " %(manager_user)s") % locals()
        LOG.audit(msg, context=context)
        project = project_dict(
                     auth_manager.AuthManager().create_project(
                     name,
                     manager_user,
                     description=None,
                     member_users=None))
        return {'project': project}

    def update(self, req, id, body):
        context = req.environ['nova.context']
        name = id
        manager_user = body['project'].get('manager_user')
        description = body['project'].get('description')
        msg = _("Modify project: %(name)s managed by"
                " %(manager_user)s") % locals()
        LOG.audit(msg, context=context)
        auth_manager.AuthManager().modify_project(name,
                                             manager_user=manager_user,
                                             description=description)
        return exc.HTTPAccepted()

    def delete(self, req, id):
        context = req.environ['nova.context']
        LOG.audit(_("Delete project: %s"), id, context=context)
        auth_manager.AuthManager().delete_project(id)
        return exc.HTTPAccepted()


class AdminNetworkController(object):

    def disassociate(self, req, id):
        context = req.environ['nova.context']
        LOG.audit(_("Disassociating network: %s %s"), id, context=context)
        db.network_disassociate(context, id)
        return exc.HTTPAccepted()

    def index(self, req):
        tenant_id = urlparse.parse_qs(req.environ['QUERY_STRING']).get('tenant_id', [None])[0]
        context = req.environ['nova.context']
        LOG.audit(_("Getting networks for project %s"), tenant_id or '<all>')
        if context.is_admin and not tenant_id:
            networks = db.network_get_all(context)
        elif tenant_id:
            networks = db.project_get_networks(context, tenant_id, associate=False)
        else:
            raise exc.HTTPNotFound()
        result = [network_dict(net_ref) for net_ref in networks]
        return  {'networks': result}

    def get(self, req, id):
        context = req.environ['nova.context']
        net = db.network_get(context, id)
        return {'network': network_dict(net)}

    # TODO: implement full CRUD, not done right in nova too


class ExtrasSecurityGroupController(object):
    def __init__(self):
        self.compute_api = compute.API()

    def _format_security_group_rule(self, context, rule):
        r = {}
        r['id'] = rule.id
        r['parent_group_id'] = rule.parent_group_id
        r['group_id'] = rule.group_id
        r['ip_protocol'] = rule.protocol
        r['from_port'] = rule.from_port
        r['to_port'] = rule.to_port
        r['groups'] = []
        r['ip_ranges'] = []
        if rule.group_id:
            source_group = db.security_group_get(context, rule.group_id)
            r['groups'] += [{'name': source_group.name,
                             'tenant_id': source_group.project_id}]
        else:
            r['ip_ranges'] += [{'cidr': rule.cidr}]
        return r

    def _format_security_group(self, context, group):
        g = {}
        g['id'] = group.id
        g['description'] = group.description
        g['name'] = group.name
        g['tenant_id'] = group.project_id
        g['rules'] = []
        for rule in group.rules:
            r = self._format_security_group_rule(context, rule)
            g['rules'] += [r]
        return g

    def index(self, req):
        context = req.environ['nova.context']
        self.compute_api.ensure_default_security_group(context)
        groups = db.security_group_get_by_project(context,
                                                  context.project_id)
        groups = [self._format_security_group(context, g) for g in groups]

        return {'security_groups':
                list(sorted(groups,
                            key=lambda k: (k['tenant_id'], k['name'])))}

    def create(self, req, body):
        context = req.environ['nova.context']
        self.compute_api.ensure_default_security_group(context)
        name = body['security_group'].get('name')
        description = body['security_group'].get('description')
        if db.security_group_exists(context, context.project_id, name):
            raise exception.ApiError(_('group %s already exists') % name)

        group = {'user_id': context.user_id,
                 'project_id': context.project_id,
                 'name': name,
                 'description': description}
        group_ref = db.security_group_create(context, group)

        return {'security_group': self._format_security_group(context,
                                                                 group_ref)}

    def delete(self, req, id):
        context = req.environ['nova.context']
        self.compute_api.ensure_default_security_group(context)

        LOG.audit(_("Delete security group %s"), id, context=context)
        db.security_group_destroy(context, id)

        return exc.HTTPAccepted()

    def show(self, req, id):
        context = req.environ['nova.context']
        security_group = db.security_group_get(context, id)
        return {'security_group': self._format_security_group(context,
                                                              security_group)}


class ExtrasSecurityGroupRuleController(ExtrasSecurityGroupController):
    def __init__(self):
        self.compute_api = compute.API()

    def _revoke_rule_args_to_dict(self, context, to_port=None, from_port=None,
                                  parent_group_id=None, ip_protocol=None,
                                  cidr=None, group_id=None):
        values = {}

        if group_id:
            values['group_id'] = group_id
        elif cidr:
            # If this fails, it throws an exception. This is what we want.
            cidr = urllib.unquote(cidr).decode()
            netaddr.IPNetwork(cidr)
            values['cidr'] = cidr
        else:
            values['cidr'] = '0.0.0.0/0'

        if ip_protocol and from_port and to_port:
            from_port = int(from_port)
            to_port = int(to_port)
            ip_protocol = str(ip_protocol)

            if ip_protocol.upper() not in ['TCP', 'UDP', 'ICMP']:
                raise exception.InvalidIpProtocol(protocol=ip_protocol)
            if ((min(from_port, to_port) < -1) or
                (max(from_port, to_port) > 65535)):
                raise exception.InvalidPortRange(from_port=from_port,
                                                 to_port=to_port)

            values['protocol'] = ip_protocol
            values['from_port'] = from_port
            values['to_port'] = to_port
        else:
            # If cidr based filtering, protocol and ports are mandatory
            if 'cidr' in values:
                return None

        return values

    def _security_group_rule_exists(self, security_group, values):
        """Indicates whether the specified rule values are already
           defined in the given security group.
        """
        for rule in security_group.rules:
            if 'group_id' in values:
                if rule['group_id'] == values['group_id']:
                    return True
            else:
                is_duplicate = True
                for key in ('cidr', 'from_port', 'to_port', 'protocol'):
                    if rule[key] != values[key]:
                        is_duplicate = False
                        break
                if is_duplicate:
                    return True
        return False

    def create(self, req, body):
        context = req.environ['nova.context']
        group_id = body['security_group_rule']['parent_group_id']

        self.compute_api.ensure_default_security_group(context)
        security_group = db.security_group_get(context, group_id)
        if not security_group:
            raise exception.SecurityGroupNotFound(security_group_id=group_id)

        msg = "Authorize security group ingress %s"
        LOG.audit(_(msg), security_group['name'], context=context)
        values = self._revoke_rule_args_to_dict(context,
                                                **body['security_group_rule'])
        if values is None:
            raise exception.ApiError(_("Not enough parameters to build a "
                                       "valid rule."))
        values['parent_group_id'] = security_group.id

        if self._security_group_rule_exists(security_group, values):
            raise exception.ApiError(_('This rule already exists in group %s')
                                     % group_id)

        security_group_rule = db.security_group_rule_create(context, values)

        self.compute_api.trigger_security_group_rules_refresh(context,
                                      security_group_id=security_group['id'])

        return {'security_group_rule': self._format_security_group_rule(
                                                        context,
                                                        security_group_rule)}

    def delete(self, req, id):
        context = req.environ['nova.context']
        rule = sqlalchemy_api.security_group_rule_get(context, id)
        if not rule:
           raise exception.ApiError(_("Rule not found"))
        group_id = rule.parent_group_id

        self.compute_api.ensure_default_security_group(context)

        security_group = db.security_group_get(context, group_id)
        if not security_group:
            raise exception.SecurityGroupNotFound(security_group_id=group_id)

        msg = "Revoke security group ingress %s"
        LOG.audit(_(msg), security_group['name'], context=context)

        db.security_group_rule_destroy(context, rule['id'])
        self.compute_api.trigger_security_group_rules_refresh(context,
                                security_group_id=security_group['id'])
        return exc.HTTPAccepted()


class Admin(object):

    def __init__(self):
        pass

    def get_name(self):
        return "Admin Controller"

    def get_alias(self):
        return "ADMIN"

    def get_description(self):
        return "The Admin API Extension"

    def get_namespace(self):
        return "http:TODO/"

    def get_updated(self):
        return "2011-05-25 16:12:21.656723"

    def get_resources(self):
        resources = []
        resources.append(extensions.ResourceExtension('admin/projects',
                                                 AdminProjectController()))
        resources.append(extensions.ResourceExtension('admin/networks',
                                                 AdminNetworkController(), # TODO(chemikadze): full networking support
                                                 member_actions={'disassociate': 'DELETE'}))
        resources.append(extensions.ResourceExtension('admin/services',
                                                 AdminServiceController()))
        resources.append(extensions.ResourceExtension('admin/quota_sets',
                                                 AdminQuotasController()))
        resources.append(extensions.ResourceExtension('admin/servers',
                                             PrivilegedServerController()))
        resources.append(extensions.ResourceExtension('extras/consoles',
                                             ExtrasConsoleController()))
        resources.append(extensions.ResourceExtension('admin/flavors',
                                             AdminFlavorController()))
        resources.append(extensions.ResourceExtension('extras/usage',
                                             UsageController()))
        resources.append(extensions.ResourceExtension('extras/flavors',
                                             ExtrasFlavorController()))
        resources.append(extensions.ResourceExtension('extras/servers',
                                             ExtrasServerController()))
        resources.append(extensions.ResourceExtension('extras/keypairs',
                                             ExtrasKeypairController()))
        resources.append(extensions.ResourceExtension('extras/snapshots',
                                             ExtrasSnapshotController()))
        resources.append(extensions.ResourceExtension('extras/security_groups',
                                             ExtrasSecurityGroupController()))
        resources.append(extensions.ResourceExtension('extras/security_group_rules',
                                             ExtrasSecurityGroupRuleController()))
        return resources
