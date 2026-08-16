import { describe, expect, test, vi } from "vitest";
import { getJson, requestGate } from "@/api";

vi.stubGlobal("location", { origin: "https://example.test" });

describe("requestGate", () => {
  test("aborts stale requests", () => {
    const gate = requestGate(), first = gate.next(), second = gate.next();
    expect(first.signal.aborted).toBe(true);
    expect(gate.isCurrent(first)).toBe(false);
    expect(gate.isCurrent(second)).toBe(true);
  });
});

describe("getJson", () => {
  test("normalizes API errors", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ error: "bad query" }), {
      status: 400, headers: { "content-type": "application/json" },
    })));
    await expect(getJson("api/mesh", { limit: 0 })).rejects.toThrow("bad query");
  });
});
