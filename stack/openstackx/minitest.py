from datetime import datetime
import openstackx.admin
import openstackx.compute
import openstackx.auth
import openstackx.extras
import random
import sys

if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    host = 'localhost'


auth = openstackx.auth.Auth(management_url='http://%s:8080/v2.0/' % host)
token = auth.tokens.create('1234', 'admin', 'secrete')
print token._info

admin_token = auth.tokens.create('1234', 'admin', 'secrete')
accounts = openstackx.extras.Account(auth_token=admin_token.id,
        management_url='http://%s:8081/v2.0' % host)

extras = openstackx.extras.Extras(auth_token=token.id,
                                 auth_url='http://%s:8774/v1.1/' % host,
                                 management_url='http://%s:8774/v1.1/' % host)

admin = openstackx.admin.Admin(auth_token=token.id,
                              auth_url='http://%s:8774/v1.1/' % host,
                              management_url='http://%s:8774/v1.1/' % host)

compute = openstackx.compute.Compute(auth_token=token.id,
                                    auth_url='http://%s:8774/v1.1/' % host,
                                    management_url='http://%s:8774/v1.1/' % host)
#services =  admin.services.list()

print "#####################################################################"
print admin.quota_sets.list(True)
print "#####################################################################"



print "-----"
print "-----"
#print accounts.tenants.get('1234')
#print accounts.tenants.add_tenant_user('1234', 'joeuser')
print accounts.role_refs.get_for_user('joeadmin')
print accounts.role_refs.get_for_user('joeuser')
print "hooray"
print "-----"
print accounts.role_refs.add_for_tenant_user('1234', 'joeuser', 'Admin')

print accounts.role_refs.delete_for_tenant_user('1234', 'joeuser', 'Admin')
print "-----"
#print accounts.tenants.get_tenant_users('1234')
print "-----"
print "-----"
print extras.keypairs.list()
#print extras.keypairs.delete('test')
#print extras.keypairs.create('test')
#print extras.keypairs.create('test2')
print extras.servers.list()[0]._info['attrs']
#print extras.servers.list()[0].update('my server', None, 'description')
print "-----"
#flavors = admin.flavors.list()
#services =  admin.services.list()
#print services
#for s in services:
#    print s._info
#    s.update(False)


print admin.flavors.list()
#admin.flavors.delete(405)
#flavor = admin.flavors.create('', '', '', '', '')
#flavor.delete(True)

if False:
    print accounts.tenants.get('1234')
    print "%d tenants" % len(accounts.tenants.list())
    t = accounts.tenants.create('project:%d' % random.randint(0, 10000))
    t.update("test", False)
    print t.enabled
    print t.description

if False:
    print "%d users" % len(accounts.users.list())
    t = accounts.users.create('jesse', 'anotherjesse@gmail.com', 'asdf', '1234', True)
    print 'created %s' % t
    print "%d users" % len(accounts.users.list())
    t.delete()
    print "after delete: %d users" % len(accounts.users.list())

#console = extras.consoles.create(servers[0].id, 'vnc')
#print console.output

#print compute.servers.list()

if False:
    try:
        project = admin.projects.create('test', 'joeuser', 'desc')
    except:
        admin.projects.delete('test')
        pass

    project.update('joeuser', 'desc2')

    for p in admin.projects.list():
        print p._info
    admin.projects.delete('test')
    #print compute.images.list()
