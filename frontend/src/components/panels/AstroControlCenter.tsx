"use client";

import LLMSettingsPanel from "@/components/settings/LLMSettingsPanel";
import UsageDashboard from "@/components/dashboard/UsageDashboard";

export default function AstroControlCenter() {
  return (
    <div className="space-y-8">
      <section>
        <h2 className="text-xl font-semibold">LLM Configuration</h2>
        <LLMSettingsPanel />
      </section>

      <section>
        <h2 className="text-xl font-semibold">Usage</h2>
        <UsageDashboard />
      </section>
    </div>
  );
}