"use client";

import {useState} from "react";
import {ASTRO_BACKEND} from "@/config/backend";

export default function AstroRuntimeStatus() {
  const [status, setStatus] = useState("unknown");

  async function check() {
    try {
      const r = await fetch(`${ASTRO_BACKEND}/health`);
      setStatus(r.ok ? "online" : "offline");
    } catch {
      setStatus("offline");
    }
  }

  return (
    <div>
      <button onClick={check}>
        Check Astro Backend
      </button>
      <span className="ml-2">{status}</span>
    </div>
  );
}