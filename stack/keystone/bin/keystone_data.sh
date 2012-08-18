#!/bin/bash
BIN_DIR=${BIN_DIR:-.}
# Tenants
$BIN_DIR/keystone-manage $* tenant add admin
$BIN_DIR/keystone-manage $* tenant add demo
$BIN_DIR/keystone-manage $* tenant add invisible_to_admin

# Users
$BIN_DIR/keystone-manage $* user add admin asd
$BIN_DIR/keystone-manage $* user add demo asd

# Roles
$BIN_DIR/keystone-manage $* role add Admin
$BIN_DIR/keystone-manage $* role add Member
$BIN_DIR/keystone-manage $* role add KeystoneAdmin
$BIN_DIR/keystone-manage $* role add KeystoneServiceAdmin
$BIN_DIR/keystone-manage $* role add sysadmin
$BIN_DIR/keystone-manage $* role add netadmin
$BIN_DIR/keystone-manage $* role grant Admin admin admin
$BIN_DIR/keystone-manage $* role grant Member demo demo
$BIN_DIR/keystone-manage $* role grant sysadmin demo demo
$BIN_DIR/keystone-manage $* role grant netadmin demo demo
$BIN_DIR/keystone-manage $* role grant Member demo invisible_to_admin
$BIN_DIR/keystone-manage $* role grant Admin admin demo
$BIN_DIR/keystone-manage $* role grant Admin admin
$BIN_DIR/keystone-manage $* role grant KeystoneAdmin admin
$BIN_DIR/keystone-manage $* role grant KeystoneServiceAdmin admin

# Services
$BIN_DIR/keystone-manage $* service add nova compute "Nova Compute Service"
$BIN_DIR/keystone-manage $* service add glance image "Glance Image Service"
$BIN_DIR/keystone-manage $* service add keystone identity "Keystone Identity Service"
$BIN_DIR/keystone-manage $* service add swift object-store "Swift Service"

#endpointTemplates
$BIN_DIR/keystone-manage $* endpointTemplates add RegionOne nova http://192.168.179.228:8774/v1.1/%tenant_id% http://192.168.179.228:8774/v1.1/%tenant_id%  http://192.168.179.228:8774/v1.1/%tenant_id% 1 1
$BIN_DIR/keystone-manage $* endpointTemplates add RegionOne glance http://192.168.179.228:9292/v1.1/%tenant_id% http://192.168.179.228:9292/v1.1/%tenant_id% http://192.168.179.228:9292/v1.1/%tenant_id% 1 1
$BIN_DIR/keystone-manage $* endpointTemplates add RegionOne keystone http://192.168.179.228:5000/v2.0 http://192.168.179.228:35357/v2.0 http://192.168.179.228:5000/v2.0 1 1
$BIN_DIR/keystone-manage $* endpointTemplates add RegionOne swift http://192.168.179.228:8080/v1/AUTH_%tenant_id% http://192.168.179.228:8080/ http://192.168.179.228:8080/v1/AUTH_%tenant_id% 1 1

# Tokens
$BIN_DIR/keystone-manage $* token add asd admin admin 2015-02-05T00:00

# EC2 related creds - note we are setting the secret key to ADMIN_PASSWORD
# but keystone doesn't parse them - it is just a blob from keystone's
# point of view
$BIN_DIR/keystone-manage $* credentials add admin EC2 'admin' 'asd' admin || echo "no support for adding credentials"
$BIN_DIR/keystone-manage $* credentials add demo EC2 'demo' 'asd' demo || echo "no support for adding credentials"
