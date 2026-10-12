import { runAstroConversation } from "@/lib/chat-runtime";
import { formatAgentEvent } from "@/lib/agent-events";

export async function askAstro(
  message: string,
  handlers: {
    onEvent?: (event: ReturnType<typeof formatAgentEvent>) => void;
    onRaw?: (event: unknown) => void;
  } = {}
) {
  return runAstroConversation(message, (raw) => {
    handlers.onRaw?.(raw);

    try {
      const parsed =
        typeof raw === "string" ? JSON.parse(raw) : raw;

      handlers.onEvent?.(formatAgentEvent(parsed));
    } catch {
      // Ignore non-json stream fragments
    }
  });
}