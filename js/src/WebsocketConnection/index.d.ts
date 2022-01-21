
export interface SubscriberId { topic: string }

// Provides a generic RPC stub built on top of websocket.
export interface WebsocketSession {
  // Issue a single-shot RPC.
  call(methodName: string, args: any[]): Promise<any>;
  // Subscribe to one-way messages from the server.
  subscribe(methodName: string, callback: (args: any[]) => Promise<any>): Promise<SubscriberId>;
  // Cancel an existing subscription.
  unsubscribe(id: SubscriberId): Promise<void>;
  close(): void;
}

export interface IWebsocketConnectionInitialValues {
  secret?: string;
  connection?: any;
  session?: any;
  retry?: boolean;
}

// Represents a single established websocket connection.
export interface WebsocketConnection {
  getSession(): WebsocketSession;
  getUrl(): string | null;
  destroy(): void;
}

/**
 * Creates a new SmartConnect object with the given configuration.
 */
export function newInstance(initialValues: IWebsocketConnectionInitialValues): WebsocketConnection;

/**
 * Decorates a given object (publicAPI+model) with WebsocketConnection characteristics.
 */
export function extend(publicAPI: object, model: object, initialValues?: IWebsocketConnectionInitialValues): void;

export declare const WebsocketConnection: {
  newInstance: typeof newInstance;
  extend: typeof extend;
}

export default WebsocketConnection;