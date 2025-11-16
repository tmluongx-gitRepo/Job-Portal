import { z } from "zod";

import {
  ChatEventSchema,
  ChatEventStreamSchema,
  ChatMessageSchema,
  MatchSchema,
} from "@/lib/chat/schemas";

export type Match = z.infer<typeof MatchSchema>;
export type ChatMessage = z.infer<typeof ChatMessageSchema>;
export type ChatEvent = z.infer<typeof ChatEventSchema>;
export type ChatEventStream = z.infer<typeof ChatEventStreamSchema>;
