"use client";

import AstroRuntimeStatus from "./AstroRuntimeStatus";

export default function AstroProductStatus() {
  return (
    <section className="space-y-4">
      <h2 className="text-lg font-semibold">
        Astro Runtime
      </h2>
      <AstroRuntimeStatus />
    </section>
  );
}