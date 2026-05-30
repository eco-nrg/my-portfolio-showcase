const MAX_ATTEMPTS = 10;

export default class WebSocketManager {
  constructor(url, store, debugSocket) {
    this.url = url;
    this.store = store;
    this.debugSocket = debugSocket === 'true';
  }

  open(token) {
    this.socket = new WebSocket(this.url);
    this.socket.onopen = () => {
      this.socket.send(JSON.stringify({
        type: "init",
        data: {
          token,
        },
      }));
    };
    this.socket.onmessage = (message) => this.onmessage(message);
  }

  send(type, data, attempt = 0) {
    if (this.attempt === MAX_ATTEMPTS) {
      return;
    }

    if (this.debugSocket) {
      console.log('%c Send to server MSG:', 'background: #222; color: #bada55', { type, data });
    }

    if (this.isOpen()) {
      this.socket.send(JSON.stringify({
        type,
        data,
      }));
      return;
    }

    setTimeout(() => {
      this.send(type, data, attempt++);
    }, 500);
  }

  isOpen() {
    return this.socket && this.socket.readyState === this.socket.OPEN;
  }

  isClosed() {
    return !this.socket || this.socket.readyState === this.socket.CLOSED || this.socket.readyState === this.socket.CLOSING;
  }

  onmessage(message) {
    if (this.debugSocket) {
      console.log('%c response server MSG:', 'background: #222; color: #bada55', message);
    }
    try {
      const { type, data, code } = JSON.parse(message.data);

      if (code && code === 401) {
        this.store.dispatch('__resetState');
      }

      if (typeof this.store._actions[type] !== 'undefined') {
        this.store.dispatch(type, data);
      } else {
        this.store.dispatch('message', { type, data });
      }
    } catch (err) {
      console.error('error', err);
      this.store.dispatch('message', message);
    }
  }
}
