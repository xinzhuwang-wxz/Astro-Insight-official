"use client";

export default function AgentTimeline({
  events = [],
}: {
  events?: {name?: string; event?: string}[]
}) {
  return (
    <div className="space-y-2">
      {events.map((e, i) => (
        <div key={i} className="border rounded p-2">
          <b>{e.name || "agent"}</b>
          <span className="ml-2">{e.event}</span>
        </div>
      ))}
    </div>
  );
}