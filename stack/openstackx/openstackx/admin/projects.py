from openstackx.api import base


class Project(base.Resource):
    def __repr__(self):
        return "<Project: %s>" % self.name

    def delete(self):
        self.manager.delete(self)

    def update(self, *args, **kwargs):
        self.manager.update(self.name, *args, **kwargs)


class ProjectManager(base.ManagerWithFind):
    resource_class = Project

    def list(self):
        return self._list("/admin/projects", "projects")

    def get(self, project_id):
        return self._get("/admin/projects/%s" % project_id, "project")

    def create(self, name, manager_user, description=None, member_users=None):
        body = {"project": {"name": name, 'manager_user': manager_user}}
        
        return self._create('/admin/projects', body, "project")

    def delete(self, project_id):
        self._delete("/admin/projects/%s" % (project_id))

    def update(self, name, manager_user, description=None):
        body = {"project": {'name': name, 'manager_user': manager_user}}
        if description:
            body["project"]["description"] = description
        self._update("/admin/projects/%s" % name, body)
