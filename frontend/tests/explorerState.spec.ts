import { describe, expect, it } from "vitest";
import { explorerQuery, pickIdentifier } from "@/explorerState";

describe("Explorer recovered state", () => {
  it("keeps search and identifier in the URL", () => {
    expect(explorerQuery("asthma", "DECS")).toEqual({ search: "asthma", identifier: "DECS" });
    expect(explorerQuery("", null)).toEqual({});
  });

  it("keeps an explicit identifier or falls back to the last available one", () => {
    expect(pickIdentifier("MESH", ["DECS"])).toBe("MESH");
    expect(pickIdentifier(null, ["MESH", "DECS"])).toBe("DECS");
    expect(pickIdentifier(null, [])).toBeNull();
  });
});
