# 开发时必须保住 `/kubedoor/` 入口

Web 有两个入口，同一份页面：

- `/`：原来的地址，行为保持不变。
- `/kubedoor/`：额外入口，给前置 nginx 只反代这一条路径。页面、`/api`、`/ws`、`/grafana` 都要从这里进去。

当前页面在不在这个前缀下，只看 `location.pathname` 是不是 `/kubedoor` 或以 `/kubedoor/` 开头。从 `/` 打开时不要加前缀。

## 改前端时

- `VITE_PUBLIC_PATH` 保持 `./`。改回 `/` 后，`/kubedoor/` 下会去站点根上找静态资源。
- 路由继续用 hash。站内 `router.push`、相对地址不用加前缀。
- 以 `/` 开头的接口、同源绝对地址、WebSocket，由 `src/kubedoor-web/index.html` 里、模块脚本之前的那段脚本改写。这段必须留在模块之前：xhook 会先拿走原生 `XMLHttpRequest`，之后再改 prototype 已经影响不到真正发出去的请求。
- 浏览器自己发的导航不会经过那段脚本。新增 `window.open`、`location.href`、`<a href>`、iframe 的 `src`，只要地址以 `/` 开头，就用 `withPrefix()`（本目录 `path.ts`）。现有例子：Grafana 看板 iframe、登录后跳回 Grafana、Pod 页新开告警。
- 不要再写一套前缀判断。前缀常量是 `WEB_PREFIX`。

## 改 Web nginx 时

片段在 `deploy/manifests/master/kubedoor-prefix.nginx`，由 `deploy/install.sh` 拆进 `40-web.yaml`。`# ---SERVER---` 上面进 http，下面进 server。

- `/kubedoor/` 用 `rewrite ... last` 剥掉前缀，后面仍走原来的 location。新增的 `/api`、静态路径不用再配一条前缀 location。
- 上游应用自己生成以 `/` 开头的地址时要单独处理，Grafana 就是这样：`root_url` 仍是 `/grafana/`，`/kubedoor/grafana/` 用 `sub_filter` 和 `proxy_redirect` 改写。不要为了前缀去改 Grafana 的 `root_url`。
- `$kd_prefix` 只能来自 `map $request_uri`。不要在 server 里 `set $kd_prefix`，内部跳转会重跑 server 段并清掉它。
- 这个 server 里的 `return` 跳转要加 `absolute_redirect off`。控制端在容器里听 80，绝对跳转会丢掉外面的 NodePort 或前置 nginx 端口。

## 改登录会话时

master 用 `X-Forwarded-Prefix` 决定会话 Cookie 的 `Path`，见 `src/kubedoor-master/auth/prefix.py`。从 `/kubedoor/` 登录是 `Path=/kubedoor`，直接访问是 `Path=/`。写 `kubedoor_session` 走这里，不要写死 `Path=/`。退出时两条 Path 都要清。
