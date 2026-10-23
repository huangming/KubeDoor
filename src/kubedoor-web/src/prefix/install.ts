import { withPrefix } from "./path";

/** 页面在 /kubedoor/ 下时,把绝对路径的接口和 WebSocket 改到同一前缀。相对地址不改。 */
function installPrefix(): void {
  const xhrOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (
    this: XMLHttpRequest,
    method: string,
    url: string | URL,
    async?: boolean,
    username?: string | null,
    password?: string | null
  ) {
    const next = typeof url === "string" ? withPrefix(url) : url;
    return xhrOpen.call(this, method, next, async ?? true, username, password);
  };

  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
    if (typeof input === "string") return nativeFetch(withPrefix(input), init);
    if (input instanceof Request) {
      const next = withPrefix(input.url);
      if (next !== input.url) input = new Request(next, input);
    }
    return nativeFetch(input, init);
  };

  const NativeWebSocket = window.WebSocket;
  const PrefixedWebSocket = function (
    url: string | URL,
    protocols?: string | string[]
  ) {
    const next = typeof url === "string" ? withPrefix(url) : url;
    if (protocols === undefined) return new NativeWebSocket(next);
    return new NativeWebSocket(next, protocols);
  } as unknown as typeof WebSocket;
  PrefixedWebSocket.prototype = NativeWebSocket.prototype;
  Object.setPrototypeOf(PrefixedWebSocket, NativeWebSocket);
  window.WebSocket = PrefixedWebSocket;
}

installPrefix();
