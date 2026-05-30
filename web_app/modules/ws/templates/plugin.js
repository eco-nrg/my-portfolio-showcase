import WebSocketManager from "./WebSocketManager";

const urlFromOptions = "<%= options.url %>";
const debugSocket = "<%= options.debugSocket %>";

export default ({app}, inject) => {
  const runtimeConfig = app.$config && app.$config.websocket || {};
  const url = runtimeConfig.url || urlFromOptions;

  if (!url) {
    return console.error("WebSocket connection URL is required. Please specify it via options or runtime configuration.");
  }

  const emitter = app.store;
  const manager = new WebSocketManager(url, emitter, debugSocket);

  inject("socket", emitter);
  inject("socketManager", manager);
};