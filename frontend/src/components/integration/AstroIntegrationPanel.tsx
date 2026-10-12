"use client";

import AstroControlCenter from "@/components/panels/AstroControlCenter";

/**
 * Safe integration mount point.
 *
 * This component can be inserted into the real Settings/Dashboard route
 * after route ownership is confirmed.
 */
export default function AstroIntegrationPanel() {
  return <AstroControlCenter />;
}