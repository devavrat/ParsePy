#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from __init__ import ParseResource, API_ROOT
from __init__ import ResourceRequestLoginRequired, ResourceRequestBadRequest

from query import QueryManager


def login_required(func):
    '''decorator describing User methods that need to be logged in'''
    def ret(obj, *args, **kw):
        if not hasattr(obj, 'sessionToken'):
            message = '%s requires a logged-in session' % func.__name__
            raise ResourceRequestLoginRequired(message)
        func(obj, *args, **kw)
    return ret


class User(ParseResource):
    '''
    A User is like a regular Parse object (can be modified and saved) but
    it requires additional methods and functionality
    '''
    ENDPOINT_ROOT = '/'.join([API_ROOT, 'users'])
    PROTECTED_ATTRIBUTES = ParseResource.PROTECTED_ATTRIBUTES + [
        'username', 'sessionToken']

    def is_authenticated(self):
        return getattr(self, 'sessionToken', None) or False

    @login_required
    def save(self):
        session_header = {'X-Parse-Session-Token': self.sessionToken}
        return self.__class__.PUT(
            self._absolute_url,
            extra_headers=session_header,
            **self._to_native())

    @login_required
    def delete(self):
        session_header = {'X-Parse-Session-Token': self.sessionToken}
        return self.DELETE(self._absolute_url, extra_headers=session_header)

    @staticmethod
    def signup(username, password, **kw):
        return User(**User.POST('', username=username, password=password,
                                **kw))

    @staticmethod
    def login(username, password):
        login_url = '/'.join([API_ROOT, 'login'])
        return User(**User.GET(login_url, username=username,
                                password=password))

    @staticmethod
    def request_password_reset(email):
        '''Trigger Parse's Password Process. Return True/False
        indicate success/failure on the request'''

        url = '/'.join([API_ROOT, 'requestPasswordReset'])
        try:
            User.POST(url, email=email)
            return True
        except Exception, why:
            return False


User.Query = QueryManager(User)
