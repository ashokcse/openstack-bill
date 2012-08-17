from openstackx.api import base


class EndpointTemplate(base.Resource):
    pass


class EndpointTemplateManager(base.ManagerWithFind):
    resource_class = EndpointTemplate

    def get(self, endpoint_template_id):
        return self._get("/endpointTemplates/%s" % endpoint_template_id, "endpointTemplate")

    def list(self):
        """
        Get a list of endpoint templates.
        :rtype: list of :class:`EndpointTemplate`
        """
        return self._list("/endpointTemplates", "endpointTemplates")
