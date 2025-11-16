export const ChatEventTypes = {
  INFO: "info",
  TOKEN: "token",
  MATCHES: "matches",
  HISTORY: "history",
  SUMMARY: "summary",
  COMPLETE: "complete",
  ERROR: "error",
} as const;

export type ChatEventType =
  (typeof ChatEventTypes)[keyof typeof ChatEventTypes];

export const CHAT_WS_PATH = "/api/chat/ws";
