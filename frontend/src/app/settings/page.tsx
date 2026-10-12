"use client";

import AstroIntegrationPanel from "@/components/integration/AstroIntegrationPanel";

export default function SettingsPage() {
  return (
    <div className="min-h-dvh py-6 text-white">
      <h1 className="mb-6 text-2xl font-semibold tracking-wide">设置</h1>
      <AstroIntegrationPanel />
    </div>
  );
}
