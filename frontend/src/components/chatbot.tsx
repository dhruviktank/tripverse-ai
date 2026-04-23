"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

const SUGGESTIONS = [
  "Best time to visit Bali?",
  "Budget tips for Europe?",
  "Hidden gems in Japan?",
  "Solo travel safety tips?",
];

export default function TripChatbot() {
  const [open, setOpen] = useState(false);
  const [minimized, setMinimized] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hey there, explorer! 🌍 I'm your AI travel companion. Ask me anything — destinations, budgets, hidden gems, visa tips, or let me help you plan your next adventure.",
      timestamp: new Date(),
    },
  ]);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open && !minimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, open, minimized]);

  useEffect(() => {
    if (open && !minimized) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [open, minimized]);

  function handleSend() {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    // ── Plug your RAG / API call here ──
    // Example:
    // const reply = await ragApi.chat({ message: trimmed, history: messages });
    // setMessages(prev => [...prev, { id: ..., role: "assistant", content: reply }]);
    // setLoading(false);

    // Placeholder timeout to simulate streaming feel
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: `ai-${Date.now()}`,
          role: "assistant",
          content:
            "I'm ready to help with that! Connect me to your RAG backend and I'll give you a real answer. For now, imagine something brilliantly helpful here. ✈️",
          timestamp: new Date(),
        },
      ]);
      setLoading(false);
    }, 1200);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleSuggestion(text: string) {
    setInput(text);
    inputRef.current?.focus();
  }

  function handleClear() {
    setMessages([
      {
        id: "welcome-reset",
        role: "assistant",
        content: "Fresh start! What adventure are we planning today? 🗺️",
        timestamp: new Date(),
      },
    ]);
  }

  const formatTime = (date: Date) =>
    date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });

  return (
    <>
      {/* ── FAB Trigger Button ── */}
      <button
        onClick={() => {
          setOpen(true);
          setMinimized(false);
        }}
        aria-label="Open AI travel assistant"
        className={`fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full shadow-[0_8px_32px_-8px_rgba(79,70,229,0.7)] transition-all duration-300 hover:scale-110 active:scale-95 ${
          open
            ? "scale-0 opacity-0 pointer-events-none"
            : "scale-100 opacity-100"
        }`}
        style={{
          background: "linear-gradient(135deg, #6366f1, #4f46e5)",
        }}
      >
        {/* Pulse ring */}
        <span className="absolute inset-0 rounded-full bg-indigo-400/30 animate-ping" />
        <svg
          className="relative h-6 w-6 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </button>

      {/* ── Chat Panel ── */}
      <div
        className={`fixed z-50 flex flex-col overflow-hidden rounded-3xl border border-[var(--outline-variant)] bg-white shadow-[0_32px_80px_-20px_rgba(53,37,205,0.45)] transition-all duration-300 ease-out
          /* Mobile: full-screen sheet from bottom */
          bottom-0 right-0 left-0 w-full
          /* Desktop: floating panel bottom-right */
          sm:bottom-6 sm:right-6 sm:left-auto sm:w-[380px]
          ${
            open
              ? minimized
                ? "h-[60px] sm:h-[60px]"
                : "h-[85dvh] sm:h-[560px]"
              : "h-0 opacity-0 pointer-events-none translate-y-4 sm:translate-y-0 sm:scale-95"
          }
        `}
        style={{ maxWidth: "100vw" }}
      >
        {/* ── Header ── */}
        <div
          className="flex shrink-0 cursor-pointer items-center justify-between px-5 py-4"
          style={{
            background: "linear-gradient(135deg, #4f46e5 0%, #2f23bd 100%)",
          }}
          onClick={() => setMinimized((m) => !m)}
        >
          <div className="flex items-center gap-3">
            {/* Avatar */}
            <div className="relative flex h-9 w-9 items-center justify-center rounded-full bg-white/20 text-lg">
              🌐
              <span className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white bg-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-bold text-white leading-tight">
                TripVerse AI
              </p>
              <p className="text-[11px] text-white/70">
                {loading ? "Thinking…" : "Travel companion · Online"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleClear();
              }}
              className="flex h-7 w-7 items-center justify-center rounded-lg text-white/70 transition hover:bg-white/10 hover:text-white"
              title="Clear chat"
              aria-label="Clear chat"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setMinimized((m) => !m);
              }}
              className="flex h-7 w-7 items-center justify-center rounded-lg text-white/70 transition hover:bg-white/10 hover:text-white"
              title={minimized ? "Expand" : "Minimize"}
              aria-label={minimized ? "Expand chat" : "Minimize chat"}
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d={minimized ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"}
                />
              </svg>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setOpen(false);
              }}
              className="flex h-7 w-7 items-center justify-center rounded-lg text-white/70 transition hover:bg-white/10 hover:text-white"
              title="Close"
              aria-label="Close chat"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* ── Body (hidden when minimized) ── */}
        {!minimized && (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-[var(--surface-container-low,#f6f7fb)]">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-2 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
                >
                  {/* Avatar dot */}
                  {msg.role === "assistant" && (
                    <div
                      className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm"
                      style={{
                        background: "linear-gradient(135deg,#6366f1,#4f46e5)",
                      }}
                    >
                      🌐
                    </div>
                  )}

                  <div
                    className={`flex flex-col gap-1 max-w-[80%] ${msg.role === "user" ? "items-end" : "items-start"}`}
                  >
                    <div
                      className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                        msg.role === "user"
                          ? "rounded-tr-sm text-white shadow-[0_4px_14px_-4px_rgba(79,70,229,0.5)]"
                          : "rounded-tl-sm bg-white text-[var(--on-surface,#1a1a2e)] shadow-[0_4px_14px_-6px_rgba(0,0,0,0.1)]"
                      }`}
                      style={
                        msg.role === "user"
                          ? {
                              background:
                                "linear-gradient(135deg,#6366f1,#4f46e5)",
                            }
                          : {}
                      }
                    >
                      {msg.content}
                    </div>
                    <span className="text-[10px] text-[var(--on-surface-variant,#888)] px-1">
                      {formatTime(msg.timestamp)}
                    </span>
                  </div>
                </div>
              ))}

              {/* Typing indicator */}
              {loading && (
                <div className="flex gap-2">
                  <div
                    className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm"
                    style={{
                      background: "linear-gradient(135deg,#6366f1,#4f46e5)",
                    }}
                  >
                    🌐
                  </div>
                  <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-white px-4 py-3 shadow-[0_4px_14px_-6px_rgba(0,0,0,0.1)]">
                    <span className="h-2 w-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0ms]" />
                    <span className="h-2 w-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:150ms]" />
                    <span className="h-2 w-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:300ms]" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Suggestion chips (only when just welcome message) */}
            {messages.length === 1 && (
              <div className="shrink-0 flex gap-2 overflow-x-auto px-4 py-2 bg-[var(--surface-container-low,#f6f7fb)] scrollbar-none">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => handleSuggestion(s)}
                    className="shrink-0 rounded-full border border-[var(--outline-variant,#dde1f0)] bg-white px-3 py-1.5 text-xs font-semibold text-[var(--primary,#4f46e5)] transition hover:bg-indigo-50 whitespace-nowrap"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}

            {/* ── Input Bar ── */}
            <div className="shrink-0 border-t border-[var(--outline-variant,#dde1f0)] bg-white px-4 py-3">
              <div className="flex items-center gap-2 rounded-2xl border border-[var(--outline-variant,#dde1f0)] bg-[var(--surface-container-low,#f6f7fb)] px-4 py-2 transition focus-within:border-indigo-400 focus-within:ring-2 focus-within:ring-indigo-100">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about destinations, tips…"
                  disabled={loading}
                  className="flex-1 bg-transparent text-sm text-[var(--on-surface,#1a1a2e)] outline-none placeholder:text-[var(--on-surface-variant,#aaa)] disabled:opacity-50"
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || loading}
                  aria-label="Send message"
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl transition disabled:opacity-30 hover:scale-105 active:scale-95"
                  style={{
                    background: "linear-gradient(135deg,#6366f1,#4f46e5)",
                  }}
                >
                  <svg
                    className="h-4 w-4 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.269 20.876L5.999 12zm0 0h7.5"
                    />
                  </svg>
                </button>
              </div>
              <p className="mt-2 text-center text-[10px] text-[var(--on-surface-variant,#aaa)]">
                Powered by TripVerse RAG · Ask anything travel
              </p>
            </div>
          </>
        )}
      </div>
    </>
  );
}
