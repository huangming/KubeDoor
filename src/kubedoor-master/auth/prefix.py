"""会话 Cookie 的路径跟着入口走。

/kubedoor/ 是挂到业务域名上的额外入口。Cookie 若仍是 Path=/,会发给这个域名下的其它系统。
直接访问原来的 / 时没有这个头,路径保持 /。
"""

# 与 auth.store.SESSION_COOKIE 相同。不从 store 引入,避免这里牵上数据库。
SESSION_COOKIE = 'kubedoor_session'
WEB_PREFIX = '/kubedoor'


def cookie_path(request):
    raw = (request.headers.get('X-Forwarded-Prefix') or '').strip().rstrip('/')
    if raw == WEB_PREFIX:
        return WEB_PREFIX
    return '/'


def set_session_cookie(response, request, token, max_age, secure):
    response.set_cookie(SESSION_COOKIE, token, max_age=max_age, path=cookie_path(request), httponly=True,
                        samesite='Strict', secure=secure)


def clear_session_cookie(response, secure):
    # 同一个名字、两条 Path,SimpleCookie 只能留一条,所以直接写两个 Set-Cookie。
    extra = '; Secure' if secure else ''
    for path in ('/', WEB_PREFIX):
        response.headers.add(
            'Set-Cookie',
            f'{SESSION_COOKIE}=; Path={path}; Max-Age=0; HttpOnly; SameSite=Strict{extra}',
        )
