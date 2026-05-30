'use strict';

const path = require('path');

var name = "nuxt-websocket";
var version = "1.0.0";

const CONFIG_KEY = "websocket";
const websocketModule = function(moduleOptions) {
  const options = Object.assign(this.options[CONFIG_KEY] || {}, moduleOptions);

  if(options?.debugSocket === undefined){
    options.debugSocket = false
  }

  const webSocketManagerPath = require.resolve("./templates/WebSocketManager");
  const pluginPath = require.resolve("./templates/plugin");

  this.addTemplate({
    src: webSocketManagerPath,
    fileName: path.join("nuxt-websocket", `WebSocketManager${path.extname(webSocketManagerPath)}`),
    debugSocket : options.debugSocket,
    options,
  });
  this.addPlugin({
    src: pluginPath,
    fileName: path.join("nuxt-websocket", `websocket.client${path.extname(pluginPath)}`),
    options,
  });
};

websocketModule.meta = {name, version};

module.exports = websocketModule;
