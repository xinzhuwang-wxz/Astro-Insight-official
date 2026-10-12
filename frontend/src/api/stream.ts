import { ASTRO_BACKEND } from "@/config/backend";
import { SSEDecoder } from "@/lib/sse";

export type AgentEvent = {
  event?: string;
  name?: string;
  data?: unknown;
  message?: string;
};

export async function streamAgentQuery(
  query: string,
  onEvent: (event: AgentEvent) => void,
) {
  const response = await fetch(`${ASTRO_BACKEND}/query/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`Stream request failed: HTTP ${response.status}`);
  }
  if (!response.body) {
    throw new Error("No stream returned");
  }

  const reader = response.body.getReader();
  const textDecoder = new TextDecoder();
  const sse = new SSEDecoder();

  const handle = (data: string) => {
    try {
      onEvent(JSON.parse(data) as AgentEvent);
    } catch {
      onEvent({ event: "message", data });
    }
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunk = textDecoder.decode(value, { stream: true });
    for (const message of sse.push(chunk)) {
      handle(message.data);
    }
  }

  const finalChunk = textDecoder.decode();
  for (const message of sse.push(finalChunk)) handle(message.data);
  for (const message of sse.finish()) handle(message.data);
}
