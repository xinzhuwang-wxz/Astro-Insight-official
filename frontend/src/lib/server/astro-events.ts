export type AstroEvent = {
  type: string;
  name?: string;
  payload?: unknown;
};

export function createAstroEvent(raw: any): AstroEvent {
  return {
    type: raw?.event || "message",
    name: raw?.name,
    payload: raw?.data,
  };
}