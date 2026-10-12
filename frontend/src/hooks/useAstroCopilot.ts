"use client";

import {useAgentStream} from "./useAgentStream";

export function useAstroCopilot() {
  const stream = useAgentStream();

  async function ask(question: string) {
    await stream.run(question);
  }

  return {
    ask,
    events: stream.events,
    running: stream.running,
  };
}