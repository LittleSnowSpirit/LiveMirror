type MessageHandler = (data: any) => void;

class NotificationWebSocket {
  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private pingTimer: ReturnType<typeof setInterval> | null = null;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private url = '';
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;

  connect(token: string) {
    this.disconnect();
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.url = `${protocol}//${window.location.host}/ws/notifications?token=${encodeURIComponent(token)}`;
    this._connect();
  }

  private _connect() {
    if (!this.url) return;

    try {
      this.ws = new WebSocket(this.url);
    } catch {
      this._scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this.reconnectDelay = 1000;
      this._startPing();
      this._dispatch('_open', {});
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        const type = msg.type || '_unknown';
        this._dispatch(type, msg);
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onclose = (event) => {
      this._stopPing();
      this.ws = null;

      if (event.code !== 4001) {
        this._scheduleReconnect();
      }

      this._dispatch('_close', { code: event.code });
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  private _scheduleReconnect() {
    if (this.reconnectTimer) return;

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this._connect();
    }, this.reconnectDelay);

    this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
  }

  private _startPing() {
    this._stopPing();
    this.pingTimer = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30_000);
  }

  private _stopPing() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  on(type: string, handler: MessageHandler) {
    const list = this.handlers.get(type) || [];
    list.push(handler);
    this.handlers.set(type, list);
  }

  off(type: string, handler: MessageHandler) {
    const list = this.handlers.get(type);
    if (!list) return;
    const idx = list.indexOf(handler);
    if (idx !== -1) list.splice(idx, 1);
  }

  private _dispatch(type: string, msg: unknown) {
    const specific = this.handlers.get(type);
    if (specific) {
      for (const handler of specific) handler(msg);
    }

    const wildcard = this.handlers.get('*');
    if (wildcard) {
      for (const handler of wildcard) handler(msg);
    }
  }

  send(data: unknown) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this._stopPing();

    if (this.ws) {
      this.ws.onclose = null;
      this.ws.onerror = null;
      this.ws.close();
      this.ws = null;
    }

    this.url = '';
    this.reconnectDelay = 1000;
  }
}

export const notificationWs = new NotificationWebSocket();
