import unittest2 as unittest
from keystone.test.functional import common


class TestUrlHandling(common.FunctionalTestCase):
    """Tests API's global URL handling behaviors"""

    def test_optional_trailing_slash(self):
        """Same response returned regardless of a trailing slash in the url."""
        r1 = self.service_request(path='/')
        r2 = self.service_request(path='')
        self.assertEqual(r1.read(), r2.read())


class TestContentTypes(common.FunctionalTestCase):
    """Tests API's Content-Type handling"""

    def test_default_content_type(self):
        """Service returns JSON without being asked to"""
        r = self.service_request()
        self.assertTrue('application/json' in r.getheader('Content-Type'))

    def test_xml_extension(self):
        """Service responds to .xml URL extension"""
        r = self.service_request(path='.xml')
        self.assertTrue('application/xml' in r.getheader('Content-Type'))

    def test_json_extension(self):
        """Service responds to .json URL extension"""
        r = self.service_request(path='.json')
        self.assertTrue('application/json' in r.getheader('Content-Type'))

    def test_xml_accept_header(self):
        """Service responds to xml Accept header"""
        r = self.service_request(headers={'Accept': 'application/xml'})
        self.assertTrue('application/xml' in r.getheader('Content-Type'))

    def test_json_accept_header(self):
        """Service responds to json Accept header"""
        r = self.service_request(headers={'Accept': 'application/json'})
        self.assertTrue('application/json' in r.getheader('Content-Type'))

    def test_versioned_xml_accept_header(self):
        """Service responds to versioned xml Accept header"""
        r = self.service_request(headers={
            'Accept': 'application/vnd.openstack.identity-v2.0+xml'})
        self.assertTrue('application/xml' in r.getheader('Content-Type'))

    def test_versioned_json_accept_header(self):
        """Service responds to versioned json Accept header"""
        r = self.service_request(headers={
            'Accept': 'application/vnd.openstack.identity-v2.0+json'})
        self.assertTrue('application/json' in r.getheader('Content-Type'))

    def test_xml_extension_overrides_conflicting_header(self):
        """Service returns XML when Accept header conflicts with extension"""
        r = self.service_request(path='.xml',
            headers={'Accept': 'application/json'})

        self.assertTrue('application/xml' in r.getheader('Content-Type'))

    def test_json_extension_overrides_conflicting_header(self):
        """Service returns JSON when Accept header conflicts with extension"""
        r = self.service_request(path='.json',
            headers={'Accept': 'application/xml'})

        self.assertTrue('application/json' in r.getheader('Content-Type'))

    def test_xml_content_type_on_404(self):
        """Content-Type should be honored even on 404 errors (Issue #13)"""
        r = self.service_request(path='/completely-invalid-path',
            headers={'Accept': 'application/xml'},
            assert_status=404)

        # Commenting this assertion out, as it currently fails
        self.assertTrue('application/xml' in r.getheader('Content-Type'),
            'application/xml not in %s' % r.getheader('Content-Type'))

    def test_json_content_type_on_404(self):
        """Content-Type should be honored even on 404 errors (Issue #13)"""
        r = self.service_request(path='/completely-invalid-path',
            headers={'Accept': 'application/json'},
            assert_status=404)

        # Commenting this assertion out, as it currently fails
        self.assertTrue('application/json' in r.getheader('Content-Type'),
            'application/json not in %s' % r.getheader('Content-Type'))


if __name__ == '__main__':
    unittest.main()
