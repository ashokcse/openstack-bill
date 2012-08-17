# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2011 Nebula, Inc.
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

from django import template
from django import http
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

import datetime
import logging

from django.contrib import messages

from django_openstack import api
from django_openstack import forms
from django_openstack.dash.views import instances as dash_instances
from django_openstack.decorators import enforce_admin_access

from openstackx.api import exceptions as api_exceptions


TerminateInstance = dash_instances.TerminateInstance
RebootInstance = dash_instances.RebootInstance

LOG = logging.getLogger('django_openstack.syspanel.views.instances')


def _next_month(date_start):
    y = date_start.year + (date_start.month + 1) / 13
    m = ((date_start.month + 1) % 13)
    if m == 0:
        m = 1
    return datetime.date(y, m, 1)


def _current_month():
    today = datetime.date.today()
    return datetime.date(today.year, today.month, 1)


def _get_start_and_end_date(request):
    try:
        date_start = datetime.date(
                int(request.GET['date_year']),
                int(request.GET['date_month']),
                1)
    except:
        today = datetime.date.today()
        date_start = datetime.date(today.year, today.month, 1)

    date_end = _next_month(date_start)
    datetime_start = datetime.datetime.combine(date_start, datetime.time())
    datetime_end = datetime.datetime.combine(date_end, datetime.time())

    if date_end > datetime.date.today():
        datetime_end = datetime.datetime.utcnow()
    return (date_start, date_end, datetime_start, datetime_end)


def _csv_usage_link(date_start):
    return "?date_month=%s&date_year=%s&format=csv" % (date_start.month,
            date_start.year)

def get_unitCost(request, date_start):
    unit_cost = []
    try:
        unit_cost = api.biller_get(request, date_start)
        LOG.info('....unit const.... %s' %unit_cost.__dict__)
        unit_cost.start_date = date_start
        unit_cost.end_date = _next_month(date_start)
        unit_flag = 1
    except api_exceptions.ApiException, e:
        unit_flag = 0
    return (unit_flag, unit_cost)
#
class global_cost_obj:
    def __init__(self, vcpu):
        self.vcpus = vcpu

#


@login_required
@enforce_admin_access
def usage(request):
    (date_start, date_end, datetime_start, datetime_end) = \
            _get_start_and_end_date(request)

    global_summary = api.GlobalSummary(request)
    if date_start > _current_month():
        messages.error(request, 'No data for the selected period')
        date_end = date_start
        datetime_end = datetime_start
    else:
        global_summary.service()
        global_summary.usage(datetime_start, datetime_end)

    dateform = forms.DateForm()
    dateform['date'].field.initial = date_start
    
    global_summary.avail()
    #
    unit_cost = []
    (unit_flag, unit_cost) = get_unitCost(request, date_start)
    LOG.info(' ------System over view  summary-------- %s ' %(global_summary.summary))
    if unit_flag == 0:
       messages.info(request, 'This month unit cost is not set, Pleace set unit cost in Billing tab ')

    global_cost = global_cost_obj(0)
    if (('total_cpu_usage' in global_summary.summary) and (unit_flag == 1)):
        global_cost.vcpus = float(global_summary.summary['total_cpu_usage'])  * float(unit_cost.vcpu)
        global_cost.ram = float(global_summary.summary['total_ram_usage']) * float(unit_cost.ram)
        global_cost.vdisk = float(global_summary.summary['total_disk_usage']) * float(unit_cost.vdisk)
        global_cost.total = global_cost.vcpus + global_cost.ram + global_cost.vdisk
        for usage in global_summary.usage_list:
         LOG.info(' ---$$--usage details-$$$$---- %s -----$-------- ' %(usage.__dict__))
         usage.total_cpu_cost = (float(usage.total_cpu_usage) * float(unit_cost.vcpu))
         usage.total_ram_cost = (float(usage.total_ram_usage) * float(unit_cost.ram))
         usage.total_disk_cost = (float(usage.total_disk_usage) * float(unit_cost.vdisk))
         usage.total_cost = usage.total_cpu_cost + usage.total_ram_cost + usage.total_disk_cost
         for instance in usage.instances:
                LOG.info(' ---$$--instance---- %s --- ' %(instance))
                cost_vcpus = float(instance['vcpus'])  * float(unit_cost.vcpu)
                cost_ram = float(instance['ram_size']) * float(unit_cost.ram)
                cost_vdisk = float(instance['disk_size']) * float(unit_cost.vdisk)
                instance['cost'] = float(cost_vcpus + cost_ram + cost_vdisk) * float(instance['hours'])
                LOG.info(' ---$$--instance cost-$$$$---- %s -----$-------- ' %(instance))

    else:
        global_cost.vcpus = 0.0
        global_cost.ram = 0.0
        global_cost.vdisk = 0.0
        global_cost.total = 0.0

    #
    global_summary.human_readable('disk_size')
    global_summary.human_readable('ram_size')

    if request.GET.get('format', 'html') == 'csv':
        template_name = 'django_openstack/syspanel/instances/usage.csv'
        mimetype = "text/csv"
    else:
        template_name = 'django_openstack/syspanel/instances/usage.html'
        mimetype = "text/html"

    return render_to_response(
    template_name, {
        'dateform': dateform,
        'datetime_start': datetime_start,
        'datetime_end': datetime_end,
        'usage_list': global_summary.usage_list,
        'csv_link': _csv_usage_link(date_start),
        'unit_cost':  unit_cost,
	'global_cost': global_cost,
	'global_summary': global_summary.summary,
        'external_links': settings.EXTERNAL_MONITORING,
    }, context_instance=template.RequestContext(request), mimetype=mimetype)


@login_required
@enforce_admin_access
def tenant_usage(request, tenant_id):
    (date_start, date_end, datetime_start, datetime_end) = \
            _get_start_and_end_date(request)
    if date_start > _current_month():
        messages.error(request, 'No data for the selected period')
        date_end = date_start
        datetime_end = datetime_start

    dateform = forms.DateForm()
    dateform['date'].field.initial = date_start

    usage = {}
    try:
        usage = api.usage_get(request, tenant_id, datetime_start, datetime_end)
    except api_exceptions.ApiException, e:
        LOG.exception('ApiException getting usage info for tenant "%s"'
                  ' on date range "%s to %s"' % (tenant_id,
                                                 datetime_start,
                                                 datetime_end))
        messages.error(request, 'Unable to get usage info: %s' % e.message)
    LOG.info('-------instance usage---%s--+++--  ' %(usage.instances))
    (unit_flag, unit_cost) = get_unitCost(request, date_start)
    running_instances = []
    terminated_instances = []
    if hasattr(usage, 'instances'):
        now = datetime.datetime.now()
	total = 0
        for i in usage.instances:
            # this is just a way to phrase uptime in a way that is compatible
            # with the 'timesince' filter.  Use of local time intentional
            if unit_flag == 1: 
	     cost_vcpus = float(i['vcpus'])  * float(unit_cost.vcpu)
             cost_ram = float(i['ram_size']) * float(unit_cost.ram)
             cost_vdisk = float(i['disk_size']) * float(unit_cost.vdisk)
             i['cost'] = float(cost_vcpus + cost_ram + cost_vdisk) * float(i['hours'])
	     total += i['cost']
            i['uptime_at'] = now - datetime.timedelta(seconds=i['uptime'])
            if i['ended_at']:
                terminated_instances.append(i)
            else:
                running_instances.append(i)
    usage.total_cost = total

    if request.GET.get('format', 'html') == 'csv':
        template_name = 'django_openstack/syspanel/instances/tenant_usage.csv'
        mimetype = "text/csv"
    else:
        template_name = 'django_openstack/syspanel/instances/tenant_usage.html'
        mimetype = "text/html"

    return render_to_response(template_name, {
        'dateform': dateform,
        'datetime_start': datetime_start,
        'datetime_end': datetime_end,
	'unit_cost' : unit_cost,
        'usage': usage,
        'csv_link': _csv_usage_link(date_start),
        'instances': running_instances + terminated_instances,
        'tenant_id': tenant_id,
    }, context_instance=template.RequestContext(request), mimetype=mimetype)


#def get_unitCost(request, date_start):
#    unit_cost = []
#    try:
#        unit_cost = api.biller_get(request, date_start)
#        LOG.info('....unit const.... %s' %unit_cost.__dict__)
#        unit_cost.start_date = date_start
#        unit_cost.end_date = _next_month(date_start)
#        unit_flag = 1
#    except api_exceptions.ApiException, e:
#        unit_flag = 0
#    return (unit_flag, unit_cost)


@login_required
@enforce_admin_access
def index(request):
    for f in (TerminateInstance, RebootInstance):
        _, handled = f.maybe_handle(request)
        if handled:
            return handled
    #added contented starts
    #(date_start, date_end, datetime_start, datetime_end) = \
    #        _get_start_and_end_date(request)

    #(unit_flag, unit_cost) = get_unitCost(request, date_start)
    #instances = []
    #added end
    try:
        instances = api.admin_server_list(request)
#	for instance in instances :  #added
 # 	 LOG.info('-----Instance---%s--++%s-\n' %(instance.attrs.__dict__ , unit_cost.__dict__)) #added
    except Exception as e:
        LOG.exception('Unspecified error in instance index')
        messages.error(request, 'Unable to get instance list: %s' % e.message)
   
    # We don't have any way of showing errors for these, so don't bother
    # trying to reuse the forms from above
    terminate_form = TerminateInstance()
    reboot_form = RebootInstance()

    return render_to_response(
    'django_openstack/syspanel/instances/index.html', {
        'instances': instances,
        'terminate_form': terminate_form,
        'reboot_form': reboot_form,
    }, context_instance=template.RequestContext(request))


@login_required
@enforce_admin_access
def refresh(request):
    for f in (TerminateInstance, RebootInstance):
        _, handled = f.maybe_handle(request)
        if handled:
            return handled

    instances = []
    try:
        instances = api.admin_server_list(request)
    except Exception as e:
        messages.error(request, 'Unable to get instance list: %s' % e.message)

    # We don't have any way of showing errors for these, so don't bother
    # trying to reuse the forms from above
    terminate_form = TerminateInstance()
    reboot_form = RebootInstance()

    return render_to_response(
    'django_openstack/syspanel/instances/_list.html', {
        'instances': instances,
        'terminate_form': terminate_form,
        'reboot_form': reboot_form,
    }, context_instance=template.RequestContext(request))
