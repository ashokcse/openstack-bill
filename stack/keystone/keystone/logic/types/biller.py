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

import logging
import json
from lxml import etree
from datetime import datetime



from keystone.logic.types import fault

LOG = logging.getLogger('keystone.logic.service')
LOG.info('entering Bill_Unit')
class Bill_Unit(object):
    """class for holding bill unit details!"""

    def __init__(self,id=None, vcpu=None, ram=None,
            vdisk=None, date=None, changed_on=None, enabled=None):
        LOG.info('keystone logic biller __init__ id:%s vcpu:%d ram:%d vdisk:%d date:%s changed on : %s enabled:%d'% ( id, vcpu, ram, vdisk, date, changed_on, enabled))
        self.id = id
        self.vcpu = vcpu
        self.ram = ram
        self.vdisk = vdisk
        self.date = date
        self.changed_on = changed_on
        self.enabled = enabled and True or False
       


    @staticmethod
    def from_xml(xml_str):
        try:
            dom = etree.Element("root")
            dom.append(etree.fromstring(xml_str))
            root = dom.find("{http://docs.openstack.org/identity/api/v2.0}" \
                            "biller")
            if root == None:
                raise fault.BadRequestFault("Expecting Bill_Unit")
            vcpu = root.get("vcpu")
            ram = root.get("ram")
            vdisk = root.get("vdisk")
            date = root.get("date")
            enabled = root.get("enabled")
            if not vcpu:
                raise fault.BadRequestFault("Expecting Bill_Unit")
            elif not vdisk:
                raise fault.BadRequestFault("Expecting Bill_Unit vdisk")
            enabled = enabled is None or enabled.lower() in ["true", "yes"]
            LOG.info('keystone logic biller py from_xml dom id:%d vcpu:%d ram:%d vdisk:%d date:%s enabled:%d'% ( id, vcpu, ram, vdisk, date, enabled))
            return Bill_Unit( id, vcpu, ram, vdisk, enabled)
        except etree.LxmlError as e:
            raise fault.BadRequestFault("Cannot parse Bill_Unit", str(e))




    @staticmethod
    def from_json(json_str):
    	LOG.info('keystone logic types biller py from_json before try %s' %json_str)


        try:
            obj = json.loads(json_str)
            if not "biller" in obj:
                raise fault.BadRequestFault("Expecting Bill_Unit")

            LOG.info('keystone logic types biller py from_json object %s' %obj)
            biller = obj["biller"]
            LOG.info('keystone logic types biller py from_json biller %s' %biller)
            vcpu = biller.get('vcpu', None)
            LOG.info('keystone logic types biller py from_json before IF vcpu%s' %vcpu)
            if(vcpu == None or vcpu == 0):
                raise fault.BadRequestFault("Expecting Bill_Unit")
            LOG.info('keystone logic types biller py from_json before ram')
            if "ram" in biller:
                ram = biller["ram"]
            else:
                ram = None
            LOG.info('keystone logic types biller py from_json afterram')
            if "date" in biller:
                date = biller["date"]
                #date =datetime.strptime(biller["date"], "%Y-%m-%d")
            if "changed_on" in biller:
                changed_on = biller["changed_on"]
            LOG.info('keystone logic types biller py from_json after  date : %s created date: %s' %(date, changed_on))
            if "vdisk" not in biller:
                raise fault.BadRequestFault("Expecting Bill_Unit vdisk")
            vdisk = biller["vdisk"]
            LOG.info('keystone logic types biller py from_json vdisk : %s ' %vdisk)
            if "enabled" in biller:
                set_enabled = biller["enabled"]
                if not isinstance(set_enabled, bool):
                    raise fault.BadRequestFault("Bad enabled attribute!")
            else:
                set_enabled = True
            LOG.info('keystone logic types biller py from_json set_enabled : %s ' %set_enabled)
            id = biller.get('id', None)
            LOG.info('before return id :%s vcpu:%d ram:%d vdisk:%d date:%s enabled:%d'% ( id, vcpu, ram, vdisk, date, set_enabled))
            return Bill_Unit(id, vcpu, ram, vdisk, date, changed_on, set_enabled)
        except (ValueError, TypeError) as e:
            raise fault.BadRequestFault("Cannot parse bill Unit", str(e))


    def to_dom(self):
        dom = etree.Element("biller",
                        xmlns="http://docs.openstack.org/identity/api/v2.0")
        if self.vdisk:
            dom.set("vdisk", unicode(self.vdisk))
        if self.ram:
            dom.set("ram", unicode(self.ram))
        if self.id:
            dom.set("id", unicode(self.id))
        if self.vcpu:
            dom.set("vcpu", unicode(self.vcpu))
        if self.date:
            dom.set("date", unicode(self.date))
        if self.changed_on:
            dom.set("created_on", unicode(self.changed_on))
        if self.enabled:
            dom.set("enabled", unicode(self.enabled).lower())
        LOG.info('keystone logic biller py to_ dom id:%d vcpu:%d ram:%d vdisk:%d date:%s changed_on : %s enabled:%d'% ( dom.id, dom.vcpu, dom.ram, dom.vdisk, dom.date, dom.changed_on, dom.enabled))
        return dom

    def to_xml(self):
        return etree.tostring(self.to_dom())

    def to_dict(self):
        biller = {}
        if self.id:
           biller["id"] = unicode(self.id)
        if self.vcpu:
           biller["vcpu"] = unicode(self.vcpu)
        if self.ram:
           biller["ram"] = unicode(self.ram)
        biller["vdisk"] = unicode(self.vdisk)
        biller["date"] = unicode(self.date)
        biller["changed_on"] = unicode(self.changed_on)
        biller["enabled"] = self.enabled
        return {'biller':biller}
  
    def to_json(self):
        return json.dumps(self.to_dict())


class Instance_Bill(object):
    """class for holding instance bill  details!"""

    def __init__(self,id=None, name=None, total_vcpu=None, total_ram=None,
            total_vdisk=None, changed_on=None, total_cost=None, enabled=None):
        LOG.info('keystone logic instance biller __init__ start' )
       # LOG.info('keystone logic instance biller __init__ id: name : %s toatl vcpu:%d ram:%d vdisk:%d total_cost:%s changed on : %s enabled:%d'% ( name,  total_vcpu, total_ram, total_vdisk, total_cost, changed_on, enabled))
        self.id = id
        self.name = name
        self.total_vcpu = total_vcpu
        self.total_ram = total_ram
        self.total_vdisk = total_vdisk
        self.total_cost = total_cost
        self.changed_on = changed_on
        self.enabled = enabled and True or False
        LOG.info('keystone logic instance biller __init__ end' )


    @staticmethod
    def from_xml(xml_str):
        try:
            dom = etree.Element("root")
            dom.append(etree.fromstring(xml_str))
            root = dom.find("{http://docs.openstack.org/identity/api/v2.0}" \
                            "biller")
            if root == None:
                raise fault.BadRequestFault("Expecting Bill_Unit")
            total_vcpu = root.get("total_vcpu")
            total_ram = root.get("total_ram")
            total_vdisk = root.get("total_vdisk")
            name = root.get("name")
            enabled = root.get("enabled")
            if not total_vcpu:
                raise fault.BadRequestFault("Expecting Bill_Unit")
            elif not total_vdisk:
                raise fault.BadRequestFault("Expecting Bill_Unit vdisk")
            enabled = enabled is None or enabled.lower() in ["true", "yes"]
            LOG.info('keystone logic biller py from_xml dom id:%d vcpu:%d ram:%d vdisk:%d date:%s enabled:%d'% ( id, total_vcpu, total_ram, total_vdisk, name, enabled))
            return Bill_Unit( id, name, total_vcpu, total_ram, total_vdisk, enabled)
        except etree.LxmlError as e:
            raise fault.BadRequestFault("Cannot parse Bill_Unit", str(e))



    @staticmethod
    def from_json(json_str):
    	LOG.info('keystone logic types biller py from_json before try %s' %json_str) 
        try:
            obj = json.loads(json_str)
            if not "biller" in obj:
                raise fault.BadRequestFault("Expecting Bill_Unit")

            LOG.info('keystone logic types biller py from_json object %s' %obj)
            biller = obj["biller"]
            LOG.info('keystone logic types biller py from_json biller %s' %biller)
            total_vcpu = biller.get('total_vcpu', None)
            LOG.info('keystone lllogic types biller py from_json before IF vcpu%s' %total_vcpu)
            if(total_vcpu == None or total_vcpu == 0):
                raise fault.BadRequestFault("Expecting Instance_Bill_Unit")
            LOG.info('keystone logic types biller py from_json before ram')
            if "total_ram" in biller:
                total_ram = biller["total_ram"]
            else:
                total_ram = None
            LOG.info('keystone logic types biller py from_json afterram')
            if "name" in biller:
                name = biller["name"]
                #date =datetime.strptime(biller["date"], "%Y-%m-%d")
            if "total_cost" in biller:
                total_cost = biller["total_cost"]

            if "changed_on" in biller:
                changed_on = biller["changed_on"]
            LOG.info('\n keystone logic types biller py from_json after  name : %s created date: %s' %(name, changed_on))
            if "total_vdisk" not in biller:
                raise fault.BadRequestFault("Expecting Bill_Unit vdisk")
            total_vdisk = biller["total_vdisk"]
            LOG.info('keystone logic types biller py from_json vdisk : %s ' %total_vdisk)
            if "enabled" in biller:
                set_enabled = biller["enabled"]
                if not isinstance(set_enabled, bool):
                    raise fault.BadRequestFault("Bad enabled attribute!")
            else:
                set_enabled = True
            LOG.info('keystone logic types biller py from_json set_enabled : %s ' %set_enabled)
            id = biller.get('id', None)
            LOG.info('before instance bill json return id : %s name :%s total_vcpu:%d total_ram:%d total_vdisk:%d total_cost: %s enabled:%d'% (id, name, total_vcpu, total_ram, total_vdisk, total_cost, set_enabled))
            return Instance_Bill(id, name, total_vcpu, total_ram, total_vdisk, changed_on, total_cost, set_enabled)
        except (ValueError, TypeError) as e:
            raise fault.BadRequestFault("Cannot parse Instance bill ", str(e))


    def to_dom(self):
        dom = etree.Element("biller",
                        xmlns="http://docs.openstack.org/identity/api/v2.0")
        if self.vdisk:
            dom.set("total_vdisk", unicode(self.total_vdisk))
        if self.ram:
            dom.set("total_ram", unicode(self.total_ram))
        if self.id:
            dom.set("id", unicode(self.id))
        if self.vcpu:
            dom.set("total_vcpu", unicode(self.total_vcpu))
        if self.date:
            dom.set("name", unicode(self.name))
        if self.total_cost:
            dom.set("total_cost", unicode(self.total_cost))
        if self.changed_on:
            dom.set("created_on", unicode(self.changed_on))
        if self.enabled:
            dom.set("enabled", unicode(self.enabled).lower())
        LOG.info('keystone logic biller py to_ dom id:%d name :- %s  vcpu:%d ram:%d vdisk:%d date:%s changed_on : %s enabled:%d'% ( dom.id, dom.total_vcpu, dom.total_ram, dom.total_vdisk, dom.name, dom.changed_on, dom.enabled))
        return dom

    def to_xml(self):
        return etree.tostring(self.to_dom())

    def to_dict(self):
        biller = {}
        if self.id:
           biller["id"] = unicode(self.id)
        if self.total_vcpu:
           biller["total_vcpu"] = unicode(self.total_vcpu)
        if self.total_ram:
           biller["total_ram"] = unicode(self.total_ram)
        biller["total_vdisk"] = unicode(self.total_vdisk)
        biller["name"] = unicode(self.name)
        biller["total_cost"] = unicode(self.total_cost)
        biller["changed_on"] = unicode(self.changed_on)
        biller["enabled"] = self.enabled
        return {'biller':biller}
  
    def to_json(self):
        return json.dumps(self.to_dict())




#-User Bill----------#
class User_Bill(object):
    """class for holding instance bill  details!"""

    def __init__(self,id=None, user_id=None, tenant_id=None,  total_vcpu=None, total_ram=None,
            total_vdisk=None, bill_month=None, total_cost=None, enabled=None):
        LOG.info('keystone logic User_Billbiller __init__ start' )
       # LOG.info('keystone logic instance biller __init__ id: name : %s toatl vcpu:%d ram:%d vdisk:%d total_cost:%s changed on : %s enabled:%d'% ( name,  total_vcpu, total_ram, total_vdisk, total_cost, changed_on, enabled))
        self.id = id
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.total_vcpu = total_vcpu
        self.total_ram = total_ram
        self.total_vdisk = total_vdisk
        self.total_cost = total_cost
        self.bill_month = bill_month
        self.enabled = enabled and True or False
        LOG.info('keystone logic User_Bill  biller __init__ end' )


    @staticmethod
    def from_xml(xml_str):
        try:
            dom = etree.Element("root")
            dom.append(etree.fromstring(xml_str))
            root = dom.find("{http://docs.openstack.org/identity/api/v2.0}" \
                            "biller")
            if root == None:
                raise fault.BadRequestFault("Expecting Bill_Unit")
            total_vcpu = root.get("total_vcpu")
            total_ram = root.get("total_ram")
            total_vdisk = root.get("total_vdisk")
            name = root.get("name")
            enabled = root.get("enabled")
            if not total_vcpu:
                raise fault.BadRequestFault("Expecting Bill_Unit")
            elif not total_vdisk:
                raise fault.BadRequestFault("Expecting Bill_Unit vdisk")
            enabled = enabled is None or enabled.lower() in ["true", "yes"]
            LOG.info('keystone logic biller py from_xml dom id:%d vcpu:%d ram:%d vdisk:%d date:%s enabled:%d'% ( id, total_vcpu, total_ram, total_vdisk, name, enabled))
            return Bill_Unit( id, name, total_vcpu, total_ram, total_vdisk, enabled)
        except etree.LxmlError as e: 
            raise fault.BadRequestFault("Cannot parse Bill_Unit", str(e))


    @staticmethod
    def from_json(json_str):
        LOG.info('keystone logic types User Bill  biller py from_json before try %s' %json_str)
        try:
            obj = json.loads(json_str)
            if not "biller" in obj:
                raise fault.BadRequestFault("Expecting User_Bill")

            LOG.info('keystone logic types biller py from_json object %s' %obj)
            biller = obj["biller"]
            LOG.info('keystone logic types biller py from_json user_bill %s' %biller)
            total_vcpu = biller.get('total_vcpu', None)
            LOG.info('keystone lllogic types biller py from_json before IF vcpu%s' %total_vcpu)
            if(total_vcpu == None or total_vcpu == 0):
                raise fault.BadRequestFault("Expecting User_Bill")
            LOG.info('keystone logic types biller py from_json before ram')
            if "total_ram" in biller:
                total_ram = biller["total_ram"]
            else:
                total_ram = None
            LOG.info('keystone logic types biller py from_json afterram')
            if "user_id" in biller:
                user_id = biller["user_id"]
                #date =datetime.strptime(biller["date"], "%Y-%m-%d")
            if "tenant_id" in biller:
                tenant_id = biller["tenant_id"]
            if "total_cost" in biller:
                total_cost = biller["total_cost"]

            if "bill_month" in biller:
                bill_month = biller["bill_month"]
            LOG.info('\n keystone logic types biller py from_json after  name : %s created date: %s' %(user_id, bill_month))
            if "total_vdisk" not in biller:
                raise fault.BadRequestFault("Expecting Bill_Unit vdisk")
            total_vdisk = biller["total_vdisk"]
            LOG.info('keystone logic types biller py from_json vdisk : %s ' %total_vdisk)
            if "enabled" in biller:
                set_enabled = biller["enabled"]
                if not isinstance(set_enabled, bool):
                    raise fault.BadRequestFault("Bad enabled attribute!")
            else:
                set_enabled = True
            LOG.info('keystone logic types biller py from_json usr_bill set_enabled : %s ' %set_enabled)
            id = biller.get('id', None)
            LOG.info('before instance bill json return id : %s user_id :%s tenant_id =%s total_vcpu:%d total_ram:%d total_vdisk:%d total_cost: %s billmonth= %s enabled:%d'% (id, user_id, tenant_id,  total_vcpu, total_ram, total_vdisk, total_cost, bill_month, set_enabled))
            return User_Bill(id, user_id, tenant_id, total_vcpu, total_ram, total_vdisk, bill_month, total_cost, set_enabled)
        except (ValueError, TypeError) as e:
            raise fault.BadRequestFault("Cannot parse keystone logic types biller py from_json   User bill ", str(e))


    def to_dom(self):
        dom = etree.Element("biller",
                        xmlns="http://docs.openstack.org/identity/api/v2.0")
        if self.vdisk:
            dom.set("total_vdisk", unicode(self.total_vdisk))
        if self.ram:
            dom.set("total_ram", unicode(self.total_ram))
        if self.id:
            dom.set("id", unicode(self.id))
        if self.vcpu:
            dom.set("total_vcpu", unicode(self.total_vcpu))
        if self.user_id:
            dom.set("user_id", unicode(self.user_id))
        if self.tenant_id:
            dom.set("tenant_id", unicode(self.tenant_id))
        if self.total_cost:
            dom.set("total_cost", unicode(self.total_cost))
        if self.bill_month:
            dom.set("bill_month", unicode(self.bill_month))
        if self.enabled:
            dom.set("enabled", unicode(self.enabled).lower())
        LOG.info('keystone logic biller py to_ dom id:%d user_id :- %s  vcpu:%d ram:%d vdisk:%d date:%s changed_on : %s enabled:%d'% ( dom.id, dom.user_id, dom.total_vcpu, dom.total_ram, dom.total_vdisk, dom.bill_month, dom.enabled))
        return dom

    def to_xml(self):
        return etree.tostring(self.to_dom())

    def to_dict(self):
        biller = {}
        if self.id:
           biller["id"] = unicode(self.id)
        if self.total_vcpu:
           biller["total_vcpu"] = unicode(self.total_vcpu)
        if self.total_ram:
           biller["total_ram"] = unicode(self.total_ram)
        biller["user_id"] = unicode(self.user_id)
        biller["tenant_id"] = unicode(self.tenant_id)
        biller["total_vdisk"] = unicode(self.total_vdisk)
        biller["total_cost"] = unicode(self.total_cost)
        biller["bill_month"] = unicode(self.bill_month)
        biller["enabled"] = self.enabled
        return {'biller':biller}

    def to_json(self):
        return json.dumps(self.to_dict())

