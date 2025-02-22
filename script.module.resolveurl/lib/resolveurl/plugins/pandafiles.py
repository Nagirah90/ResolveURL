"""
    Plugin for ResolveURL
    Copyright (C) 2021 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
from resolveurl.lib import helpers, captcha_lib
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class PandaFilesResolver(ResolveUrl):
    name = "PandaFiles"
    domains = ['pandafiles.com']
    pattern = r'(?://|\.)(pandafiles\.com)/([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        rurl = 'https://{0}/'.format(host)
        headers = {'User-Agent': common.FF_USER_AGENT,
                   'Origin': rurl[:-1],
                   'Referer': rurl}
        data = {
            'op': 'download1',
            'usr_login': '',
            'id': media_id,
            'referer': rurl,
            'method_free': 'Free Download'
        }
        html = self.net.http_POST(web_url, form_data=data, headers=headers).content
        payload = helpers.get_hidden(html)
        payload.update(captcha_lib.do_captcha(html))
        html = self.net.http_POST(web_url, form_data=payload, headers=headers).content
        source = re.search(r'id="direct_link".*?href="([^"]+)', html, re.S)
        if source:
            headers.update({'verifypeer': 'false'})
            return source.group(1) + helpers.append_headers(headers)

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/{media_id}')
