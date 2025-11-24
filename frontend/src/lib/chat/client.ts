import type { ChatEvent } from "@/lib/chat/types";
import { ChatEventSchema } from "@/lib/chat/schemas";
import { CHAT_WS_PATH } from "@/lib/chat/constants";

type EventCallback = (event: ChatEvent) => void;

type ErrorCallback = (error: unknown) => void;

interface ConnectOptions {
  token?: string;
  onEvent?: EventCallback;
  onError?: ErrorCallback;
  onOpen?: () => void;
  onClose?: (event: CloseEvent) => void;
}

export interface ChatConnection {
  readonly socket: WebSocket;
  sendMessage(message: string): void;
  close(code?: number, reason?: string): void;
}

const defaultApiUrl =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const defaultWsUrl = process.env.NEXT_PUBLIC_WS_URL ?? defaultApiUrl;

function buildWebSocketUrl(path: string, token?: string): string {
  const base = new URL(defaultWsUrl);
  const protocol = base.protocol.startsWith("https") ? "wss:" : "ws:";
  base.protocol = protocol;
  const url = new URL(path, base);
  if (token) {
    url.searchParams.set("access_token", token);
  }
  return url.toString();
}

export function connectToChat(options: ConnectOptions = {}): ChatConnection {
  const { token, onEvent, onError, onOpen, onClose } = options;
  const url = buildWebSocketUrl(CHAT_WS_PATH, token);
  const socket = new WebSocket(url);

  socket.onopen = () => {
    onOpen?.();
  };

  socket.onmessage = (messageEvent: MessageEvent<string>) => {
    try {
      const parsed = JSON.parse(messageEvent.data ?? "{}");
      const validation = ChatEventSchema.safeParse(parsed);
      if (!validation.success) {
        if (process.env.NODE_ENV !== "production") {
          console.warn("chat event validation failed", validation.error);
        }
        return;
      }
      onEvent?.(validation.data);
    } catch (parseError) {
      onError?.(parseError);
      if (process.env.NODE_ENV !== "production") {
        console.error("Failed to parse chat event", parseError);
      }
    }
  };

  socket.onerror = (event) => {
    onError?.(event);
  };

  socket.onclose = (event) => {
    onClose?.(event);
  };

  return {
    socket,
    sendMessage(message: string) {
      if (socket.readyState !== WebSocket.OPEN) {
        throw new Error("Chat connection is not open");
      }
      socket.send(JSON.stringify({ message }));
    },
    close(code?: number, reason?: string) {
      socket.close(code, reason);
    },
  };
}
