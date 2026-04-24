/**
 * TripVerse Chat API Client
 * Utility functions for interacting with the backend chat API
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatMessage {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  reply: string;
  session_id: string;
  context?: {
    source?: string | null;
    destinations?: string[];
    preferences?: string[];
    budget?: string | null;
    pace?: string | null;
    duration_days?: number | null;
    trip_description?: string | null;
  };
  requires_clarification?: boolean;
  suggested_action?: string | null;
}

export interface ChatStreamEvent {
  event_type: "start" | "chunk" | "end" | "error";
  session_id: string;
  data?: string;
  context?: ChatResponse["context"];
  suggested_action?: string | null;
}

export interface PlanResponse {
  success: boolean;
  session_id: string;
  plan?: any;
  error?: string;
}

export interface SessionInfo {
  session_id: string;
  message_count: number;
  context?: ChatResponse["context"];
  messages?: Array<{
    role: string;
    content: string;
  }>;
}

/**
 * Send a chat message and get a response
 * @param sessionId - Unique session identifier
 * @param message - User message text
 * @returns Chat response with reply and context
 */
export async function sendChatMessage(
  sessionId: string,
  message: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat API error: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Stream a chat message response
 * @param sessionId - Unique session identifier
 * @param message - User message text
 * @param onEvent - Callback for each event
 */
export async function streamChatMessage(
  sessionId: string,
  message: string,
  onEvent: (event: ChatStreamEvent) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
    }),
  });

  if (!response.ok) {
    throw new Error(`Stream API error: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Response body is not readable");
  }

  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n").filter((line) => line.trim());

      for (const line of lines) {
        try {
          const event = JSON.parse(line) as ChatStreamEvent;
          onEvent(event);
        } catch (e) {
          console.error("Failed to parse event:", e, line);
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Get session information
 * @param sessionId - Unique session identifier
 * @returns Session info including message count and context
 */
export async function getSessionInfo(sessionId: string): Promise<SessionInfo> {
  const response = await fetch(`${API_BASE_URL}/api/chat/session/${sessionId}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Session not found: ${sessionId}`);
    }
    throw new Error(`Session API error: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Clear a chat session
 * @param sessionId - Unique session identifier
 * @returns Success status
 */
export async function clearSession(
  sessionId: string
): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/chat/session/${sessionId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error(`Clear session API error: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Generate a trip plan from chat context
 * @param sessionId - Unique session identifier
 * @returns Generated plan
 */
export async function generatePlanFromChat(
  sessionId: string
): Promise<PlanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat/plan/${sessionId}`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`Plan generation API error: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Check chat service health
 * @returns Health status
 */
export async function checkChatHealth(): Promise<{
  status: string;
  service: string;
}> {
  const response = await fetch(`${API_BASE_URL}/api/chat/health`);

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Generate a unique session ID
 * @returns New session ID
 */
export function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Get session ID from localStorage or create new one
 * @returns Session ID
 */
export function getOrCreateSessionId(): string {
  let sessionId = localStorage.getItem("chatSessionId");
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem("chatSessionId", sessionId);
  }
  return sessionId;
}

/**
 * Clear session ID from localStorage
 */
export function clearSessionStorage(): void {
  localStorage.removeItem("chatSessionId");
}
