export function sseHeaders() {
  return {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
  };
}

export function runtimeError(message: string) {
  return new Response(
    JSON.stringify({error: message}),
    {
      status: 500,
      headers: {"Content-Type": "application/json"},
    }
  );
}