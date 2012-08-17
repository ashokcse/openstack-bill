from openstackx.api import base


class Snapshot(base.Resource):
    pass


class SnapshotManager(base.ManagerWithFind):
    resource_class = Snapshot

    def create(self, instance_id, name):
        body = {"snapshot": {"instance_id": instance_id, 'name': name}}
        return self._create('/extras/snapshots', body, "snapshot")
