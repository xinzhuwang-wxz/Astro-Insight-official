export function formatAgentEvent(event: any) {
  const name = event?.name || "agent";
  const map: Record<string,string> = {
    planner: "Planning",
    retriever: "Retrieving data",
    coder: "Generating code",
    explainer: "Explaining result",
  };

  return {
    name,
    label: map[name] || name,
    status: event?.event || "running",
  };
}