import { z } from "zod";

import { ChatEventTypes } from "@/lib/chat/constants";

const ScoreBreakdownSchema = z.record(z.number());

export const MatchSchema = z.object({
  id: z.string(),
  label: z.string(),
  subtitle: z.string().nullable().optional(),
  match_score: z.number(),
  vector_score: z.number().nullable().optional(),
  score_breakdown: ScoreBreakdownSchema.optional(),
  reasons: z.array(z.string()),
  source: z.string(),
  metadata: z.record(z.unknown()).optional(),
});

const MatchesEventDataSchema = z.object({
  matches: z.array(MatchSchema),
  summary: z.string().optional(),
});

const TokenEventDataSchema = z.object({
  text: z.string(),
});

const SummaryEventDataSchema = z.object({
  summary: z.string(),
});

const InfoEventDataSchema = z.object({
  message: z.string(),
  session_id: z.string(),
});

export const ChatMessageSchema = z.object({
  role: z.string(),
  payload_type: z.string().optional(),
  text: z.string().nullable().optional(),
  structured: z.unknown().optional(),
  tokens_used: z.number().nullable().optional(),
  created_at: z.string().optional(),
});

const HistoryEventDataSchema = z.object({
  messages: z.array(ChatMessageSchema),
});

const ErrorEventDataSchema = z.object({
  message: z.string(),
});

const BaseEventSchema = z.object({
  type: z.enum([
    ChatEventTypes.INFO,
    ChatEventTypes.TOKEN,
    ChatEventTypes.MATCHES,
    ChatEventTypes.HISTORY,
    ChatEventTypes.SUMMARY,
    ChatEventTypes.COMPLETE,
    ChatEventTypes.ERROR,
  ]),
  data: z.unknown(),
});

export const InfoEventSchema = BaseEventSchema.extend({
  type: z.literal(ChatEventTypes.INFO),
  data: InfoEventDataSchema,
});

export const TokenEventSchema = BaseEventSchema.extend({
  type: z.literal(ChatEventTypes.TOKEN),
  data: TokenEventDataSchema,
});

export const MatchesEventSchema = BaseEventSchema.extend({
  type: z.literal(ChatEventTypes.MATCHES),
  data: MatchesEventDataSchema,
});

export const HistoryEventSchema = BaseEventSchema.extend({
  type: z.literal(ChatEventTypes.HISTORY),
  data: HistoryEventDataSchema,
});

export const SummaryEventSchema = BaseEventSchema.extend({
  type: z.literal(ChatEventTypes.SUMMARY),
  data: SummaryEventDataSchema,
});

export const CompleteEventSchema = BaseEventSchema.extend({
  type: z.literal(ChatEventTypes.COMPLETE),
  data: z.object({}).optional().default({}),
});

export const ErrorEventSchema = BaseEventSchema.extend({
  type: z.literal(ChatEventTypes.ERROR),
  data: ErrorEventDataSchema,
});

export const ChatEventSchema = z.discriminatedUnion("type", [
  InfoEventSchema,
  TokenEventSchema,
  MatchesEventSchema,
  HistoryEventSchema,
  SummaryEventSchema,
  CompleteEventSchema,
  ErrorEventSchema,
]);

export const ChatEventStreamSchema = z.array(ChatEventSchema);
