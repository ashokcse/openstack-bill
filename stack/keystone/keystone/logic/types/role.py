# Copyright (c) 2010-2011 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from lxml import etree

from keystone.logic.types import fault


class Role(object):
    def __init__(self, id, name, description, service_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.service_id = service_id

    @staticmethod
    def from_xml(xml_str):
        try:
            dom = etree.Element("root")
            dom.append(etree.fromstring(xml_str))
            root = dom.find("{http://docs.openstack.org/identity/api/v2.0}" \
                "role")
            if root == None:
                raise fault.BadRequestFault("Expecting Role")
            id = root.get("id")
            name = root.get("name")
            description = root.get("description")
            if name is None:
                raise fault.BadRequestFault("Expecting Role name")
            service_id = root.get("serviceId")
            return Role(id, name, description, service_id)
        except etree.LxmlError as e:
            raise fault.BadRequestFault("Cannot parse Role", str(e))

    @staticmethod
    def from_json(json_str):
        try:
            obj = json.loads(json_str)
            if not "role" in obj:
                raise fault.BadRequestFault("Expecting Role")
            role = obj["role"]

            id = role.get('id')
            name = role.get('name')
            description = role.get('description')
            service_id = role.get('serviceId')

            if name is None:
                raise fault.BadRequestFault("Expecting Role name")

            return Role(id, name, description, service_id)
        except (ValueError, TypeError) as e:
            raise fault.BadRequestFault("Cannot parse Role", str(e))

    def to_dom(self):
        dom = etree.Element("role",
                        xmlns="http://docs.openstack.org/identity/api/v2.0")
        if self.id:
            dom.set("id", unicode(self.id))
        if self.name:
            dom.set("name", unicode(self.name))
        if self.description:
            dom.set("description", unicode(self.description))
        if self.service_id:
            dom.set("serviceId", unicode(self.service_id))
        return dom

    def to_xml(self):
        return etree.tostring(self.to_dom())

    def to_dict(self):
        role = {}
        if self.id:
            role["id"] = unicode(self.id)
        if self.name:
            role["name"] = unicode(self.name)
        if self.description:
            role["description"] = unicode(self.description)
        if self.service_id:
            role["serviceId"] = unicode(self.service_id)
        return {'role': role}

    def to_json(self):
        return json.dumps(self.to_dict())


class Roles(object):
    "A collection of roles."

    def __init__(self, values, links):
        self.values = values
        self.links = links

    def to_xml(self):
        dom = etree.Element("roles")
        dom.set(u"xmlns", "http://docs.openstack.org/identity/api/v2.0")

        for t in self.values:
            dom.append(t.to_dom())

        for t in self.links:
            dom.append(t.to_dom())

        return etree.tostring(dom)

    def to_json(self):
        values = [t.to_dict()["role"] for t in self.values]
        links = [t.to_dict()["links"] for t in self.links]
        return json.dumps({"roles": {"values": values, "links": links}})


class RoleRef(object):
    def __init__(self, role_ref_id, role_id, tenant_id):
        self.role_ref_id = role_ref_id
        self.role_id = role_id
        self.tenant_id = tenant_id

    @staticmethod
    def from_xml(xml_str):
        try:
            dom = etree.Element("root")
            dom.append(etree.fromstring(xml_str))
            root = dom.find("{http://docs.openstack.org/identity/api/v2.0}" \
                            "role")
            if root == None:
                raise fault.BadRequestFault("Expecting Role")
            role_id = root.get("roleId")
            tenant_id = root.get("tenantId")
            if role_id == None:
                raise fault.BadRequestFault("Expecting Role")
            return RoleRef('', role_id, tenant_id)
        except etree.LxmlError as e:
            raise fault.BadRequestFault("Cannot parse Role", str(e))

    @staticmethod
    def from_json(json_str):
        try:
            obj = json.loads(json_str)
            if not "role" in obj:
                raise fault.BadRequestFault("Expecting Role")
            role_ref = obj["role"]

            role_id = role_ref.get('roleId')
            tenant_id = role_ref.get('tenantId')

            if role_id == None:
                raise fault.BadRequestFault("Expecting Role ID")
            if tenant_id == None:
                raise fault.BadRequestFault("Expecting Tenant ID")

            return RoleRef('', role_id, tenant_id)
        except (ValueError, TypeError) as e:
            raise fault.BadRequestFault("Cannot parse Role", str(e))

    def to_dom(self):
        dom = etree.Element("role",
                        xmlns="http://docs.openstack.org/identity/api/v2.0")
        if self.role_ref_id:
            dom.set("id", unicode(self.role_ref_id))
        if self.role_id:
            dom.set("roleId", unicode(self.role_id))
        if self.tenant_id:
            dom.set("tenantId", unicode(self.tenant_id))
        return dom

    def to_xml(self):
        return etree.tostring(self.to_dom())

    def to_dict(self):
        role_ref = {}
        if self.role_ref_id:
            role_ref["id"] = unicode(self.role_ref_id)
        if self.role_id:
            role_ref["roleId"] = unicode(self.role_id)
        if self.tenant_id:
            role_ref["tenantId"] = unicode(self.tenant_id)
        return {'role': role_ref}

    def to_json(self):
        return json.dumps(self.to_dict())


class RoleRefs(object):
    "A collection of role refs."

    def __init__(self, values, links):
        self.values = values
        self.links = links

    def to_xml(self):
        dom = self.to_dom()
        return etree.tostring(dom)

    def to_dom(self):
        dom = etree.Element("roles")
        dom.set(u"xmlns", "http://docs.openstack.org/identity/api/v2.0")

        for t in self.values:
            dom.append(t.to_dom())

        for t in self.links:
            dom.append(t.to_dom())

        return dom

    def to_json(self):
        values = [t.to_dict()["role"] for t in self.values]
        links = [t.to_dict()["links"] for t in self.links]
        return json.dumps({"roles": {"values": values, "links": links}})

    def to_json_values(self):
        values = [t.to_dict()["role"] for t in self.values]
        return values


class UserRole(object):
    """A role granted to a user"""

    def __init__(self, role_id, role_name, tenant_id):
        self.role_id = role_id
        self.role_name = role_name
        self.tenant_id = tenant_id

    @staticmethod
    def from_xml(xml_str):
        try:
            dom = etree.Element("root")
            dom.append(etree.fromstring(xml_str))

            root = dom.find("{http://docs.openstack.org/identity/api/v2.0}" \
                            "role")
            if root == None:
                raise fault.BadRequestFault("Expecting Role")

            role_id = root.get("id")
            role_name = root.get("name")
            tenant_id = root.get("tenantId")

            if role_id is None:
                raise fault.BadRequestFault("Expecting Role ID")

            return UserRole(role_id, role_name, tenant_id)
        except etree.LxmlError as e:
            raise fault.BadRequestFault("Cannot parse Role", str(e))

    @staticmethod
    def from_json(json_str):
        try:
            obj = json.loads(json_str)
            if not "role" in obj:
                raise fault.BadRequestFault("Expecting Role")
            role = obj["role"]

            role_id = role.get('id')
            role_name = role.get('name')
            tenant_id = role.get('tenantId')

            if role_id is None:
                raise fault.BadRequestFault("Expecting Role ID")

            return RoleRef(role_id, role_name, tenant_id)
        except (ValueError, TypeError) as e:
            raise fault.BadRequestFault("Cannot parse Role", str(e))

    def to_dom(self):
        dom = etree.Element("role",
                        xmlns="http://docs.openstack.org/identity/api/v2.0")
        if self.role_id:
            dom.set("id", unicode(self.role_id))
        if self.role_name:
            dom.set("name", unicode(self.role_name))
        if self.tenant_id:
            dom.set("tenantId", unicode(self.tenant_id))
        return dom

    def to_xml(self):
        return etree.tostring(self.to_dom())

    def to_dict(self):
        role = {}
        if self.role_id:
            role["id"] = unicode(self.role_id)
        if self.role_name:
            role["name"] = unicode(self.role_name)
        if self.tenant_id:
            role["tenantId"] = unicode(self.tenant_id)
        return {'role': role}

    def to_json(self):
        return json.dumps(self.to_dict())


class UserRoles(RoleRefs):
    "A collection of roles granted to a user."
