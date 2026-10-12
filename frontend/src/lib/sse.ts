export type SSEMessage = {
  event?: string;
  data: string;
};

export class SSEDecoder {
  private buffer = "";

  push(chunk: string): SSEMessage[] {
    this.buffer += chunk.replace(/\r\n/g, "\n");
    const messages: SSEMessage[] = [];

    while (true) {
      const boundary = this.buffer.indexOf("\n\n");
      if (boundary < 0) break;
      const block = this.buffer.slice(0, boundary);
      this.buffer = this.buffer.slice(boundary + 2);
      const parsed = parseBlock(block);
      if (parsed) messages.push(parsed);
    }
    return messages;
  }

  finish(): SSEMessage[] {
    const trailing = this.buffer.trim();
    this.buffer = "";
    const parsed = trailing ? parseBlock(trailing) : null;
    return parsed ? [parsed] : [];
  }
}

function parseBlock(block: string): SSEMessage | null {
  let event: string | undefined;
  const data: string[] = [];

  for (const line of block.split("\n")) {
    if (!line || line.startsWith(":")) continue;
    if (line.startsWith("event:")) {
      event = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      data.push(line.slice(5).trimStart());
    }
  }

  if (!data.length) return null;
  return { event, data: data.join("\n") };
}
