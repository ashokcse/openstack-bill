# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 OpenStack LLC.
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
import logging
from keystone.backends.sqlalchemy import get_session, models
from keystone.backends.api import BaseBillerAPI

LOG = logging.getLogger('keystone.logic.service')

class BillerAPI(BaseBillerAPI):
    def create(self, values):
        bill_ref = models.BillUnit()
        bill_ref.update(values)
        bill_ref.save()
        return bill_ref

    def get(self, biller_date, session=None):
        if not session:
            session = get_session()
        result = session.query(models.BillUnit).filter_by(date=biller_date).first()
        return result

    def get_instance_bill(self, id, session=None):
        if not session:
            session = get_session()
        return session.query(models.InstanceBills).filter_by(id=id).first()

    def create_instance_bill(self, values):
	instance_ref = models.InstanceBills()
        try:
	 instance_ref.update(values)
         instance_ref.save()
        except Exception, e:
         LOG.info('values : %s -----  Exception in backends api sql biller--- : %s' %(values.id, e))
         self.update_instance(values)
        return instance_ref

    def update_instance(self, values, session=None):
        if not session:
            session = get_session()
        with session.begin():
            user_ref = self.get_instance_bill(values.id, session)
            user_ref.update(values)
            user_ref.save(session=session)

    def get_user_bill(self, bill_month, session=None):
        if not session:
            session = get_session()
        return session.query(models.UserBills).filter_by(bill_month=bill_month).first()

    def create_user_bill(self, values):
        instance_ref = models.UserBills()
        try:
         self.update_user_bill(values)
#         instance_ref.update(values)
#         instance_ref.save()
        except Exception, e:
         LOG.info('values : %s -----  Exception in backends api sql biller--- : %s' %(values.id, e))
#         instance_ref = models.UserBills()
         instance_ref.update(values)
         instance_ref.save()  
#         self.update_user_bill(values)
        return instance_ref

    def update_user_bill(self, values, session=None):
        if not session:
            session = get_session()
        with session.begin():
            LOG.info('values : %s -----  update user bill  in backends api sql biller--- ' %(values.tenant_id))
            user_ref = self.get_user_bill_tenant(values.bill_month,values.tenant_id, session)
        if user_ref.enabled:
            user_ref.update(values)
            user_ref.save(session=session)

    def get_user_bill_tenant(self, bill_month, tid, session=None):
        if not session:
            session = get_session()
        return session.query(models.UserBills).filter_by(bill_month=bill_month, tenant_id=tid).first()

        
def get():
    return BillerAPI()
