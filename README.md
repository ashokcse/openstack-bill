openstack-bill
==============

This is a modified OpenStack (Diablo release) which includes new modules enabling the Billing services (accountability)  

New modules are added to the Diablo release of keystone and horizon (openstack dashboard) to enable these services.

Devstack script is used to establish basic setup of OpenStack. 

Using this setup Administrator can be able to fix the cost per Unit resourses (vcpu,RAM,Vdisk,etc) for each month. 
These values are stored in keystone database. During bill calculations the resourse usage will be retrived from nova 
via nova-api. More details about its working can be found in file named "Detailed_working".


