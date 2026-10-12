export type RuntimeCheck = {
  backendUrl: string;
  configured: boolean;
};

export function getRuntimeCheck(): RuntimeCheck {
  const backendUrl =
    process.env.NEXT_PUBLIC_ASTRO_BACKEND_URL || "";

  return {
    backendUrl,
    configured: backendUrl.length > 0,
  };
}