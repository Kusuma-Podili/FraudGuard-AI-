"use client";

import { useState, useEffect, useCallback } from "react";
import { FraudRule, RuleDryRunResult, RuleBacktestResult } from "../types";
import { api } from "../lib/api";

export function useRules() {
  const [rules, setRules] = useState<FraudRule[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchRules = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.listRules();
      setRules(data);
    } catch (e) {
      console.error("Failed to load rules", e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRules();
  }, [fetchRules]);

  const createRule = async (payload: Partial<FraudRule>) => {
    const created = await api.createRule(payload);
    setRules((prev) => [...prev, created]);
    return created;
  };

  const dryRun = async (condition: string, sampleTx: Record<string, any>): Promise<RuleDryRunResult> => {
    return await api.dryRunRule(condition, sampleTx);
  };

  const backtest = async (condition: string, samples: number = 500): Promise<RuleBacktestResult> => {
    return await api.backtestRule(condition, samples);
  };

  return {
    rules,
    isLoading,
    refresh: fetchRules,
    createRule,
    dryRun,
    backtest,
  };
}
