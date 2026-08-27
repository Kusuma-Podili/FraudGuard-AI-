import { formatCurrency, formatRiskScore, getRiskColor, getActionBadge } from "../lib/utils";

describe("Frontend Formatting Utilities", () => {
  test("formats USD currency correctly", () => {
    expect(formatCurrency(1250.5)).toBe("$1,250.50");
    expect(formatCurrency(0)).toBe("$0.00");
  });

  test("formats risk score percentages", () => {
    expect(formatRiskScore(0.852)).toBe("85.2%");
    expect(formatRiskScore(0.04)).toBe("4.0%");
  });

  test("returns correct risk color classes", () => {
    const critical = getRiskColor("CRITICAL");
    expect(critical.text).toBe("text-red-400");

    const low = getRiskColor("LOW");
    expect(low.text).toBe("text-emerald-400");
  });

  test("returns correct action badges", () => {
    const decline = getActionBadge("DECLINE");
    expect(decline.label).toBe("DECLINED");

    const allow = getActionBadge("ALLOW");
    expect(allow.label).toBe("APPROVED");
  });
});
