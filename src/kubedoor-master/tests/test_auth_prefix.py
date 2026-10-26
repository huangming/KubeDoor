""" /kubedoor/ 入口的会话 Cookie 路径。"""
import pathlib
import sys

from aiohttp import web

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from auth.prefix import SESSION_COOKIE, clear_session_cookie, set_session_cookie  # noqa: E402


def test_cookie_name_matches_store():
    store = pathlib.Path(__file__).resolve().parent.parent.joinpath('auth/store.py').read_text(encoding='utf-8')
    assert f"SESSION_COOKIE = '{SESSION_COOKIE}'" in store


class _Request:
    def __init__(self, headers):
        self.headers = headers


def _paths(response):
    found = []
    for header in response.headers.getall('Set-Cookie', []):
        for part in header.split(';'):
            item = part.strip()
            if item.startswith('Path='):
                found.append(item.split('=', 1)[1])
    return found


def test_direct_login_keeps_cookie_on_root():
    response = web.Response()
    set_session_cookie(response, _Request({}), 'token', None, False)
    assert response.cookies['kubedoor_session']['path'] == '/'
    assert response.cookies['kubedoor_session']['httponly']
    assert response.cookies['kubedoor_session']['samesite'] == 'Strict'


def test_prefixed_login_limits_cookie_to_kubedoor():
    response = web.Response()
    set_session_cookie(response, _Request({'X-Forwarded-Prefix': '/kubedoor/'}), 'token', 60, True)
    cookie = response.cookies['kubedoor_session']
    assert cookie['path'] == '/kubedoor'
    assert cookie['secure']


def test_unknown_prefix_is_ignored():
    response = web.Response()
    set_session_cookie(response, _Request({'X-Forwarded-Prefix': '/other'}), 'token', None, False)
    assert response.cookies['kubedoor_session']['path'] == '/'


def test_logout_clears_both_cookie_paths():
    response = web.Response()
    clear_session_cookie(response, False)
    assert _paths(response) == ['/', '/kubedoor']
