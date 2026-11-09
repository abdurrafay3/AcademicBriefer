import type { BriefingResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function generateBriefing(): Promise<BriefingResponse> {
  const res = await fetch(`${API_URL}/briefing/generate`, { method: "POST" });

  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ?? `Request failed with status ${res.status}`);
  }

  return res.json();
}
