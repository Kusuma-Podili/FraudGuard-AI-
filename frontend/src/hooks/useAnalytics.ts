"use client";

import { useState, useEffect, useCallback } from "react";
import { DashboardKPIs, HourlyTrendPoint, MerchantRiskItem, GeoRiskItem } from "../types";
import { api } from "../lib/api";

export function useAnalytics(pollIntervalMs: number = 10000) {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [hourlyTrends, setHourlyTrends] = useState<HourlyTrendPoint[]>([]);
  const [merchants, setMerchants] = useState<MerchantRiskItem[]>([]);
  const [geoData, setGeoData] = useState<GeoRiskItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAllAnalytics = useCallback(async () => {
    try {
      const [kpiRes, trendsRes, merchRes, geoRes] = await Promise.all([
        api.getDashboardKPIs(),
        api.getHourlyTrends(),
        api.getTopMerchants(),
        api.getGeoRiskHeatmap(),
      ]);
      setKpis(kpiRes);
      setHourlyTrends(trendsRes);
      setMerchants(merchRes);
      setGeoData(geoRes);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to fetch analytics");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllAnalytics();
    const interval = setInterval(fetchAllAnalytics, pollIntervalMs);
    return () => clearInterval(interval);
  }, [fetchAllAnalytics, pollIntervalMs]);

  return {
    kpis,
    hourlyTrends,
    merchants,
    geoData,
    isLoading,
    error,
    refresh: fetchAllAnalytics,
  };
}
