from openstackx.api import base


class Keypair(base.Resource):
    def delete(self):
        self.manager.update(self, self.key_name)


class KeypairManager(base.ManagerWithFind):
    resource_class = Keypair

    def create(self, key_name):
        body = {'keypair': {'key_name': key_name}}
        return self._create('/extras/keypairs', body, 'keypair')

    def delete(self, key_name):
        self._delete('/extras/keypairs/%s' % (key_name))

    def list(self):
        return self._list('/extras/keypairs', 'keypairs')
