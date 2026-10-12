import { sendAstroQuery } from "@/lib/astro-runtime";

export async function runAstroConversation(
  message: string,
  onEvent: (event: unknown) => void
) {
  const response = await sendAstroQuery(message);

  if (!response.body) {
    throw new Error("Streaming response missing");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const {value, done} = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    for (const line of chunk.split("\n")) {
      if (line.startsWith("data:")) {
        onEvent(line.slice(5).trim());
      }
    }
  }
}