# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

"""
Nova base exception handling, including decorator for re-raising
Nova-type exceptions. SHOULD include dedicated exception logging.
"""

import logging
import sys
import traceback


class ProcessExecutionError(IOError):
    def __init__(self, stdout=None, stderr=None, exit_code=None, cmd=None,
                 description=None):
        if description is None:
            description = "Unexpected error while running command."
        if exit_code is None:
            exit_code = '-'
        message = _("%s\nCommand: %s\nExit code: %s\nStdout: %r\nStderr: %r")\
                    % (description, cmd, exit_code, stdout, stderr)
        IOError.__init__(self, message)


class Error(Exception):
    def __init__(self, message=None):
        super(Error, self).__init__(message)


class ApiError(Error):
    def __init__(self, message='Unknown', code='Unknown'):
        self.message = message
        self.code = code
        super(ApiError, self).__init__('%s: %s' % (code, message))


class NotFound(Error):
    pass


class UnknownScheme(Error):

    msg = _("Unknown scheme '%s' found in URI")

    def __init__(self, scheme):
        msg = self.__class__.msg % scheme
        super(UnknownScheme, self).__init__(msg)


class BadStoreUri(Error):

    msg = _("The Store URI %s was malformed. Reason: %s")

    def __init__(self, uri, reason):
        msg = self.__class__.msg % (uri, reason)
        super(BadStoreUri, self).__init__(msg)


class Duplicate(Error):
    pass


class AuthorizationFailure(Error):
    pass


class NotAuthorized(Error):
    pass


class NotEmpty(Error):
    pass


class Invalid(Error):
    pass


class RedirectException(Error):
    def __init__(self, url):
        self.url = url


class BadInputError(Exception):
    """Error resulting from a client sending bad input to a server"""
    pass


class MissingArgumentError(Error):
    pass


class DatabaseMigrationError(Error):
    pass


class ClientConnectionError(Exception):
    """Error resulting from a client connecting to a server"""
    pass


def wrap_exception(f):
    def _wrap(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception, e:
            if not isinstance(e, Error):
                #exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.exception('Uncaught exception')
                #logging.error(traceback.extract_stack(exc_traceback))
                raise Error("%s" % e)
            raise
    _wrap.func_name = f.func_name
    return _wrap


class GlanceException(Exception):
    """
    Base Glance Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = _("An unknown exception occurred")

    def __init__(self, **kwargs):
        try:
            self._error_string = self.message % kwargs

        except Exception:
            # at least get the core message out if something happened
            self._error_string = self.message

    def __str__(self):
        return self._error_string


class MultipleChoices(GlanceException):
    message = _("The request returned a 302 Multiple Choices. This generally "
                "means that you have not included a version indicator in a "
                "request URI.\n\nThe body of response returned:\n%(body)s")


class InvalidContentType(GlanceException):
    message = _("Invalid content type %(content_type)s")


class BadStoreConfiguration(GlanceException):
    message = _("Store %(store_name)s could not be configured correctly. "
               "Reason: %(reason)s")


class StoreDeleteNotSupported(GlanceException):
    message = _("Deleting images from this store is not supported.")


class StoreAddDisabled(GlanceException):
    message = _("Configuration for store failed. Adding images to this "
               "store is disabled.")


class InvalidNotifierStrategy(GlanceException):
    message = "'%(strategy)s' is not an available notifier strategy."


class NoServiceEndpoint(GlanceException):
    message = _("Response from Keystone does not contain a Glance endpoint.")


class MissingCredentialError(GlanceException):
    message = _("Missing required credential: %(required)s")


class AuthBadRequest(GlanceException):
    message = _("Connect error/bad request to Auth service at URL %(url)s.")


class AuthUrlNotFound(GlanceException):
    message = _("Auth service at URL %(url)s not found.")


class AuthorizationFailure(GlanceException):
    message = _("Authorization failed.")
