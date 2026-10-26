/** 业务 nginx 反代用的额外入口。页面从 / 打开时为空,从 /kubedoor/ 打开时为 /kubedoor。 */
export const WEB_PREFIX = "/kubedoor";

export function webPrefix(pathname = window.location.pathname): string {
  if (pathname === WEB_PREFIX || pathname.startsWith(`${WEB_PREFIX}/`)) {
    return WEB_PREFIX;
  }
  return "";
}

/**
 * 给以 / 开头的地址加上当前入口前缀。
 * 相对地址(./assets、platform-config.json)不动,交给浏览器按当前目录解析。
 */
export function withPrefix(input: string): string {
  const prefix = webPrefix();
  if (!prefix || !input) return input;
  if (input.startsWith("/") && !input.startsWith("//")) {
    const hashAt = input.indexOf("#");
    const before = hashAt >= 0 ? input.slice(0, hashAt) : input;
    const hash = hashAt >= 0 ? input.slice(hashAt) : "";
    const path = before.split("?")[0];
    if (path === prefix || path.startsWith(`${prefix}/`)) return input;
    return prefix + before + hash;
  }
  if (/^(https?|wss?):\/\//i.test(input)) {
    const url = new URL(input);
    if (url.origin !== window.location.origin) return input;
    if (url.pathname === prefix || url.pathname.startsWith(`${prefix}/`)) {
      return input;
    }
    url.pathname = prefix + url.pathname;
    return url.toString();
  }
  return input;
}
