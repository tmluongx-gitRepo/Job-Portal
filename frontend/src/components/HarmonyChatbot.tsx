"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
  type ReactElement,
} from "react";

import clsx from "clsx";
import {
  Bot,
  Briefcase,
  Loader2,
  MapPin,
  MessageCircle,
  Send,
  Sparkles,
  Star,
  UserRound,
  X,
} from "lucide-react";

import { useChatStream } from "@/lib/chat/useChatStream";
import type { ChatMessage, Match } from "@/lib/chat";
import { getAccessToken, getCurrentUser, type AuthUser } from "@/lib/auth";

interface HarmonyChatbotProps {
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
}

type AccountType = "job_seeker" | "employer" | "unknown";

function formatTimestamp(timestamp?: string): string {
  if (!timestamp) return "Just now";
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
  } catch (error) {
    console.warn("Failed to format timestamp", error);
    return "Just now";
  }
}

function renderMatchScore(score: number): string {
  const percentage = Math.round(Math.min(1, Math.max(0, score)) * 100);
  return `${percentage}%`; // percentage string
}

function MatchCard({
  match,
  accountType,
}: {
  match: Match;
  accountType: AccountType;
}): ReactElement {
  const isEmployer = accountType === "employer";
  const icon = isEmployer ? (
    <UserRound className="w-4 h-4 text-green-700" />
  ) : (
    <Briefcase className="w-4 h-4 text-green-700" />
  );
  const location = match.metadata?.location ?? match.subtitle ?? null;
  const company = (match.metadata?.company as string | undefined) ?? undefined;
  const jobType = (match.metadata?.job_type as string | undefined) ?? undefined;
  const experience =
    (match.metadata?.experience_required as string | undefined) ?? undefined;
  const jobId = (match.metadata?.job_id as string | undefined) ?? match.id;
  const skills = Array.isArray(match.metadata?.skills)
    ? (match.metadata?.skills as unknown[])
        .map((skill) => (typeof skill === "string" ? skill : null))
        .filter((skill): skill is string => Boolean(skill))
    : [];

  return (
    <div className="border border-green-200 rounded-lg p-3 bg-green-50/60 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-white border border-green-200">
            {icon}
          </span>
          <div>
            <p className="text-sm font-semibold text-green-900">
              {match.label}
            </p>
            {company && (
              <p className="text-xs text-green-700 font-medium">{company}</p>
            )}
            {match.subtitle && (
              <p className="text-xs text-green-700 mt-0.5">{match.subtitle}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1 bg-white border border-amber-200 text-amber-700 text-xs font-semibold px-2 py-1 rounded-full">
          <Star className="w-3 h-3" />
          {renderMatchScore(match.match_score)}
        </div>
      </div>
      {location && (
        <div className="mt-2 flex items-center gap-1 text-xs text-green-700">
          <MapPin className="w-3 h-3" />
          <span>{location}</span>
        </div>
      )}
      {(jobType || experience) && (
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-green-700">
          {jobType && (
            <span className="inline-flex items-center gap-1">
              <Briefcase className="w-3 h-3" />
              {jobType}
            </span>
          )}
          {experience && (
            <span className="inline-flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-amber-500" />
              {experience}
            </span>
          )}
        </div>
      )}
      {skills.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {skills.slice(0, 6).map((skill) => (
            <span
              key={skill}
              className="text-[11px] font-medium px-2 py-1 rounded-full bg-white border border-green-200 text-green-700"
            >
              {skill}
            </span>
          ))}
        </div>
      )}
      {match.reasons.length > 0 && (
        <ul className="mt-2 space-y-1">
          {match.reasons.slice(0, 3).map((reason: string) => (
            <li
              key={reason}
              className="text-[11px] text-green-700 flex items-center gap-1"
            >
              <Sparkles className="w-3 h-3 text-amber-500" />
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      )}
      {jobId && accountType !== "employer" && (
        <div className="mt-3 flex items-center justify-end">
          <Link
            href={`/apply/${jobId}`}
            className="inline-flex items-center gap-2 text-xs font-semibold text-green-800 bg-white border border-green-300 px-3 py-1.5 rounded-full hover:bg-green-50 transition-colors"
          >
            Apply now
            <Send className="w-3 h-3" />
          </Link>
        </div>
      )}
    </div>
  );
}

function MessageBubble({
  message,
}: {
  message: ChatMessage;
}): ReactElement | null {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";
  const bubbleText = (() => {
    if (typeof message.text === "string" && message.text.trim().length > 0) {
      return message.text.trim();
    }
    if (message.payload_type === "matches") {
      const structured = message.structured as
        | { summary?: unknown }
        | undefined;
      const summary = structured?.summary;
      if (typeof summary === "string" && summary.trim()) {
        return summary.trim();
      }
      return "I found some matches for you.";
    }
    if (message.structured && typeof message.structured === "object") {
      try {
        return JSON.stringify(message.structured);
      } catch (error) {
        console.warn("Failed to render structured message", error);
      }
    }
    return null;
  })();

  if (!bubbleText) {
    return null;
  }

  const textBlocks: string[] = bubbleText
    .split(/\n{2,}|\r\n{2,}/)
    .flatMap((block: string) => block.split(/\n/))
    .map((segment: string) => segment.trim())
    .filter((line: string) => line.length > 0);

  return (
    <div
      className={clsx("flex", isUser ? "justify-end" : "justify-start")}
      aria-live="polite"
    >
      <div
        className={clsx(
          "max-w-[88%] rounded-2xl px-4 py-3 text-sm shadow-lg border transition-all",
          isUser
            ? "bg-gradient-to-r from-green-600 to-emerald-500 text-white border-green-600"
            : "bg-gradient-to-r from-white via-green-50/80 to-emerald-50/70 text-green-900 border-green-200"
        )}
      >
        {isAssistant && (
          <div className="flex items-center gap-2 mb-2 text-xs font-semibold uppercase tracking-wide text-green-700">
            <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-green-100">
              <Bot className="h-3.5 w-3.5" />
            </span>
            Harmony says
          </div>
        )}
        <div
          className={clsx(
            "space-y-2",
            isUser ? "text-white" : "text-green-900"
          )}
        >
          {textBlocks.map((line: string, idx: number) => (
            <p
              key={`${line}-${idx}`}
              className="leading-relaxed whitespace-pre-line"
            >
              {line}
            </p>
          ))}
        </div>
        <span
          className={clsx(
            "mt-1 block text-[11px] uppercase tracking-wide",
            isUser ? "text-green-50/80" : "text-green-500"
          )}
        >
          {isUser ? "You" : "Harmony"} • {formatTimestamp(message.created_at)}
        </span>
      </div>
    </div>
  );
}

export default function HarmonyChatbot({
  isOpen,
  onOpen,
  onClose,
}: HarmonyChatbotProps): ReactElement {
  const [token, setToken] = useState<string | undefined>();
  const [accountType, setAccountType] = useState<AccountType>("unknown");
  const [input, setInput] = useState("");
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  const {
    status,
    matches,
    messages,
    streamingText,
    error,
    connect,
    disconnect,
    sendMessage,
    navigateTo,
    clearNavigation,
  } = useChatStream({ token, autoConnect: false });
  const router = useRouter();

  const scrollContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const syncAuthFromStorage = (): void => {
      const accessToken = getAccessToken() ?? undefined;
      setToken(accessToken);

      const currentUser: AuthUser | null = getCurrentUser();
      if (currentUser?.account_type === "employer") {
        setAccountType("employer");
      } else if (currentUser?.account_type === "job_seeker") {
        setAccountType("job_seeker");
      } else {
        setAccountType("unknown");
      }
    };

    syncAuthFromStorage();
    window.addEventListener("storage", syncAuthFromStorage);
    return () => {
      window.removeEventListener("storage", syncAuthFromStorage);
    };
  }, []);

  useEffect(() => {
    if (!isOpen) {
      disconnect();
      return;
    }
    if (!token) {
      return;
    }
    connect();
    return () => {
      disconnect();
    };
  }, [isOpen, token, connect, disconnect]);

  useEffect(() => {
    if (!isOpen) {
      setInput("");
      setSubmissionError(null);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!navigateTo) {
      return;
    }
    router.push(navigateTo);
    clearNavigation();
  }, [navigateTo, router, clearNavigation]);

  const transcript = useMemo(
    () =>
      messages.filter(
        (message) => message.role === "user" || message.role === "assistant"
      ),
    [messages]
  );

  useEffect(() => {
    if (!isOpen) {
      return;
    }
    const container = scrollContainerRef.current;
    if (!container) {
      return;
    }
    container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
  }, [isOpen, transcript, streamingText, matches, error, submissionError]);

  const connectionStatus = useMemo(() => {
    switch (status) {
      case "connecting":
        return {
          label: "Connecting",
          tone: "text-amber-600",
          dot: "bg-amber-400",
        } as const;
      case "open":
        return {
          label: "Online",
          tone: "text-green-600",
          dot: "bg-green-500",
        } as const;
      case "closed":
        return {
          label: "Reconnecting",
          tone: "text-amber-600",
          dot: "bg-amber-400",
        } as const;
      default:
        return {
          label: "Idle",
          tone: "text-slate-500",
          dot: "bg-slate-400",
        } as const;
    }
  }, [status]);

  const showMatches = matches.length > 0;
  const isAuthenticated = Boolean(token);
  const isSendingDisabled = !isAuthenticated || status !== "open";

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) {
      return;
    }
    if (!isAuthenticated) {
      setSubmissionError("Please sign in again to chat.");
      return;
    }

    try {
      sendMessage(trimmed);
      setInput("");
      setSubmissionError(null);
    } catch (sendError) {
      console.error("Failed to send chat message", sendError);
      setSubmissionError("We couldn't deliver that. Please try again.");
    }
  };

  const matchesHeading =
    accountType === "employer" ? "Recommended candidates" : "Recommended roles";

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {!isOpen ? (
        <button
          type="button"
          onClick={onOpen}
          className="flex items-center gap-2 rounded-full bg-gradient-to-r from-green-600 to-emerald-500 text-white px-5 py-3 shadow-lg shadow-green-500/30 hover:shadow-green-600/40 transition-all"
        >
          <MessageCircle className="w-5 h-5" />
          <span className="text-sm font-semibold">Chat with Harmony</span>
        </button>
      ) : (
        <div className="w-[380px] sm:w-[420px] h-[560px] bg-white border border-green-200 rounded-3xl shadow-2xl flex flex-col overflow-hidden">
          <header className="px-5 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-white/15">
                  <Bot className="w-5 h-5" />
                </span>
                <div>
                  <p className="text-base font-semibold">Harmony Assist</p>
                  <div className="flex items-center gap-2 text-xs">
                    <span
                      className={clsx(
                        "w-2 h-2 rounded-full",
                        connectionStatus.dot
                      )}
                    />
                    <span>{connectionStatus.label}</span>
                  </div>
                </div>
              </div>
              <p className="mt-3 text-xs text-white/80">
                {accountType === "employer"
                  ? "Ask for qualified candidates, status updates, or next steps for applicants."
                  : "Ask for matching roles, application tips, or follow-ups based on your resume."}
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                disconnect();
                onClose();
              }}
              className="rounded-full p-2 hover:bg-white/10 transition"
              aria-label="Close chat"
            >
              <X className="w-4 h-4" />
            </button>
          </header>

          <div
            ref={scrollContainerRef}
            className="flex-1 bg-green-50/60 px-4 py-3 overflow-y-auto space-y-3"
          >
            {!isAuthenticated && (
              <div className="bg-white border border-amber-300 text-amber-700 text-sm rounded-xl p-3">
                Please sign in again to start a conversation.
              </div>
            )}

            {transcript.length === 0 &&
              streamingText.length === 0 &&
              isAuthenticated && (
                <div className="bg-white border border-green-200 rounded-xl p-4 text-sm text-green-700 shadow-sm">
                  <p className="font-semibold flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-amber-500" />
                    Tip
                  </p>
                  <p className="mt-1">
                    Ask Harmony to find roles that match your profile or see
                    candidate recommendations for your open jobs.
                  </p>
                </div>
              )}

            {transcript.map((message, index) => {
              const key = message.created_at
                ? `${message.role}-${message.created_at}`
                : `${message.role}-${index}`;
              return <MessageBubble key={key} message={message} />;
            })}

            {streamingText && (
              <div className="flex justify-start">
                <div className="max-w-[88%] rounded-2xl px-4 py-2 text-sm bg-white text-green-900 border border-green-200 shadow-sm">
                  <p className="whitespace-pre-wrap leading-relaxed">
                    {streamingText}
                    <Loader2 className="w-3 h-3 inline animate-spin ml-1" />
                  </p>
                  <span className="mt-1 block text-[11px] uppercase tracking-wide text-green-500">
                    Harmony • typing
                  </span>
                </div>
              </div>
            )}

            {(error || submissionError) && (
              <div className="bg-white border border-red-200 text-red-600 text-sm rounded-xl p-3">
                {error ?? submissionError}
              </div>
            )}

            {showMatches && (
              <div className="bg-white border border-green-200 rounded-xl p-3 shadow-sm space-y-3">
                <p className="text-sm font-semibold text-green-900 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  {matchesHeading}
                </p>
                <div className="space-y-2">
                  {matches.map((match) => (
                    <MatchCard
                      key={match.id}
                      match={match}
                      accountType={accountType}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          <form
            onSubmit={handleSubmit}
            className="border-t border-green-200 bg-white px-4 py-3"
          >
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder={
                  accountType === "employer"
                    ? "Ask for candidate matches or status updates..."
                    : "Ask for job matches or interview prep..."
                }
                className="flex-1 rounded-full border border-green-200 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-green-50/80 text-green-900"
                disabled={isSendingDisabled}
              />
              <button
                type="submit"
                className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-green-600 to-emerald-500 text-white p-2.5 shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isSendingDisabled}
                aria-label="Send message"
              >
                {isSendingDisabled ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
