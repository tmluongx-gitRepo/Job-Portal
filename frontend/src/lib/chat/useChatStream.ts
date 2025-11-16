import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  ChatEventTypes,
  type ChatEventType,
  type Match,
  type ChatMessage,
  connectToChat,
  type ChatConnection,
} from "@/lib/chat";

type ConnectionStatus = "idle" | "connecting" | "open" | "closed";

export interface UseChatStreamOptions {
  token?: string;
  autoConnect?: boolean;
}

export interface ChatStreamState {
  status: ConnectionStatus;
  sessionId?: string;
  summary?: string;
  matches: Match[];
  messages: ChatMessage[];
  streamingText: string;
  error?: string;
}

const initialState: ChatStreamState = {
  status: "idle",
  matches: [],
  messages: [],
  streamingText: "",
};

export interface UseChatStreamResult extends ChatStreamState {
  sendMessage(message: string): void;
  connect(): void;
  disconnect(): void;
}

export function useChatStream(
  options: UseChatStreamOptions = {}
): UseChatStreamResult {
  const { token, autoConnect = true } = options;
  const [state, setState] = useState<ChatStreamState>(initialState);
  const connectionRef = useRef<ChatConnection | null>(null);

  const handleEvent = useCallback(
    (eventType: ChatEventType, payload: unknown) => {
      // Type-cast payload to access properties
      const data = payload as Record<string, unknown>;

      setState((prev) => {
        switch (eventType) {
          case ChatEventTypes.INFO:
            return {
              ...prev,
              sessionId: (data.session_id as string) ?? prev.sessionId,
              status: "open",
              error: undefined,
            };
          case ChatEventTypes.HISTORY:
            return {
              ...prev,
              messages: (data.messages as ChatMessage[]) ?? prev.messages,
            };
          case ChatEventTypes.MATCHES:
            return {
              ...prev,
              matches: (data.matches as Match[]) ?? prev.matches,
              summary: (data.summary as string | undefined) ?? prev.summary,
            };
          case ChatEventTypes.SUMMARY:
            return {
              ...prev,
              summary: (data.summary as string) ?? prev.summary,
            };
          case ChatEventTypes.TOKEN:
            return {
              ...prev,
              streamingText: `${prev.streamingText}${(data.text as string) ?? ""}`,
            };
          case ChatEventTypes.COMPLETE:
            return {
              ...prev,
              streamingText: "",
            };
          case ChatEventTypes.ERROR:
            return {
              ...prev,
              error: (data.message as string) ?? "Unexpected chat error",
            };
          default:
            return prev;
        }
      });
    },
    []
  );

  const connect = useCallback(() => {
    connectionRef.current?.close();
    setState((prev) => ({ ...prev, status: "connecting", error: undefined }));

    connectionRef.current = connectToChat({
      token,
      onOpen: () => {
        setState((prev) => ({ ...prev, status: "open" }));
      },
      onClose: () => {
        setState((prev) => ({ ...prev, status: "closed" }));
      },
      onError: (error) => {
        setState((prev) => ({
          ...prev,
          error: error instanceof Error ? error.message : "Unknown error",
        }));
      },
      onEvent: (event) => {
        handleEvent(event.type, event.data);
      },
    });
  }, [handleEvent, token]);

  const disconnect = useCallback(() => {
    connectionRef.current?.close();
    connectionRef.current = null;
    setState((prev) => ({ ...prev, status: "closed" }));
  }, []);

  useEffect(() => {
    if (!autoConnect) {
      return;
    }
    connect();
    return () => {
      connectionRef.current?.close();
      connectionRef.current = null;
    };
  }, [autoConnect, connect]);

  const sendMessage = useCallback((message: string) => {
    if (!connectionRef.current) {
      throw new Error("Chat connection is not established");
    }
    connectionRef.current.sendMessage(message);
  }, []);

  return useMemo(
    () => ({
      ...state,
      sendMessage,
      connect,
      disconnect,
    }),
    [connect, disconnect, sendMessage, state]
  );
}
