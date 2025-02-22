"""
    Plugin for ResolveUrl
    Copyright (C) 2020 gujal

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

import json
from six.moves import urllib_error, urllib_request
from resolveurl.lib import helpers
from resolveurl import common
from resolveurl.resolver import ResolveUrl, ResolverError


class VeohResolver(ResolveUrl):
    name = "Veoh"
    domains = ["veoh.com"]
    pattern = r'(?://|\.)(veoh\.com)/(?:watch/|.+?permalinkId=)?([0-9a-zA-Z/]+)'

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.CHROME_USER_AGENT, 'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        _data = json.loads(html)
        if 'video' in _data and 'src' in _data.get('video', ''):
            sources = []
            _src = _data['video']['src']
            if 'HQ' in _src:
                sources.append(('HQ', _src['HQ']))
            if 'Regular' in _src:
                sources.append(('RQ', _src['Regular']))

            if len(sources) > 0:
                return self._redirect_test(helpers.pick_source(sources)) + helpers.append_headers(headers)

        raise ResolverError('Unable to locate video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/watch/getVideo/{media_id}')

    def _redirect_test(self, url):
        opener = urllib_request.build_opener()
        opener.addheaders = [('User-agent', common.CHROME_USER_AGENT),
                             ('Referer', 'https://www.veoh.com/')]
        try:
            resp = opener.open(url)
            if url != resp.geturl():
                return resp.geturl()
            else:
                return url
        except urllib_error.HTTPError as e:
            if e.code == 403:
                if url != e.geturl():
                    return e.geturl()
            raise ResolverError('File not found')
