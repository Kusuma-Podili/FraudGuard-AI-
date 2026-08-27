"use client";

import { useState, useEffect, useCallback } from "react";
import { InvestigationCase } from "../types";
import { api } from "../lib/api";

export function useCases(initialPage: number = 1, initialStatus?: string) {
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(initialPage);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(initialStatus);
  const [severityFilter, setSeverityFilter] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchCases = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await api.listCases({
        page,
        page_size: 15,
        status: statusFilter,
        severity: severityFilter,
      });
      setCases(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (e) {
      console.error("Failed to load cases", e);
    } finally {
      setIsLoading(false);
    }
  }, [page, statusFilter, severityFilter]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const updateStatus = async (caseId: string, status: string, reason?: string, note?: string) => {
    const updated = await api.updateCaseStatus(caseId, status, reason, note);
    setCases((prev) => prev.map((c) => (c.id === caseId ? updated : c)));
    return updated;
  };

  const assignAnalyst = async (caseId: string, analystId: string, analystName: string) => {
    const updated = await api.assignCase(caseId, analystId, analystName);
    setCases((prev) => prev.map((c) => (c.id === caseId ? updated : c)));
    return updated;
  };

  return {
    cases,
    total,
    page,
    setPage,
    totalPages,
    statusFilter,
    setStatusFilter,
    severityFilter,
    setSeverityFilter,
    isLoading,
    refresh: fetchCases,
    updateStatus,
    assignAnalyst,
  };
}
