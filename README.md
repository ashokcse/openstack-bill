openstack-bill
==============

This is a modified OpenStack (Diablo release) which includes new modules enabling the Billing services (accountability)  

New modules are added to the Diablo release of keystone and horizon (openstack dashboard) to enable these services.

Devstack script is used to establish basic setup of OpenStack. 



Using this setup Administrator can be able to fix the cost per Unit resources (vcpu, RAM, Vdisk, etc) for each month. 

These values are stored in keystone database. During bill calculations the resources usage will be retrieved from nova 

via nova-api. More details about its working can be found in file named "Detailed_working".


Screen Capture (Screenshots) of the Horizon (openStack Dashboard) are in "Horizon Screenshots" folder.

Billing details can also be downloaded as ".CSV" file from Dashboard as usual. 

-------------------------------------------------------------------------------------------------------------------------

How to Install:
===============

Ubuntu 11.10 (Oneiric Ocelot) server release is used as Base System (for testing) 

Can be downloaded from http://releases.ubuntu.com/11.10/

Step 1: Update apt-get

        sudo apt-get update
        
Step 2: Download these files or git clone 

       git clone git://github.com/ashokcse/openstack-bill.git
       
Step 3: Running initial setup

        sudo python initial_setup.py
        
Step 4: Go to devstach directory (~/devstack)

        cd ~/devstack
        
Step 5: Start the installation (similar to devstack installation process)

        ./stack.sh
        
The remaining steps are same as  normal devstack installation of OpenStack.

------------------------------------------------------------------------------------------------------------------------

Horizon Screenshots
===================

Screenshot 1: System Panel : Billing 

   http://tinyurl.com/cajbhu6

Screenshot 2: System Panel Overview

   http://tinyurl.com/cbovbks
        
Screenshot 3: System Panel : Tenant Bill

   http://tinyurl.com/bu3ckn6
        
Screenshot 4: User Dashboard : MyBill
      
   http://tinyurl.com/cagsfqu

Screenshot 5: System Panel : Unit Bill creation 

   http://tinyurl.com/d4267ub
        
