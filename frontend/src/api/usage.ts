import { ASTRO_BACKEND } from "@/config/backend";

export async function fetchUsageDashboard() {
  const response = await fetch(`${ASTRO_BACKEND}/api/usage`);
  if (!response.ok) {
    throw new Error("Failed to fetch usage data");
  }
  return response.json();
}