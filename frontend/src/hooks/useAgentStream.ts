"use client";

import { useState } from "react";
import { streamAgentQuery, type AgentEvent } from "@/api/stream";

export function useAgentStream() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(query: string) {
    setEvents([]);
    setError(null);
    setRunning(true);

    try {
      await streamAgentQuery(query, (event) => {
        setEvents((previous) => [...previous, event]);
      });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Stream failed");
      throw cause;
    } finally {
      setRunning(false);
    }
  }

  return { events, running, error, run };
}
