"use client";

import {useState} from "react";
import {askAstro} from "@/lib/astro-chat-controller";

export default function AstroChatBridge() {
  const [events, setEvents] = useState<any[]>([]);

  async function ask(message: string) {
    await askAstro(message, {
      onEvent: (event) => {
        setEvents((old) => [...old, event]);
      },
    });
  }

  return {
    ask,
    events,
  };
}