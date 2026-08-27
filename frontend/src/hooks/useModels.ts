"use client";

import { useState, useEffect, useCallback } from "react";
import { ModelRegistryRecord } from "../types";
import { api } from "../lib/api";

export function useModels() {
  const [models, setModels] = useState<ModelRegistryRecord[]>([]);
  const [liveMetrics, setLiveMetrics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchModelData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [modelList, metrics] = await Promise.all([
        api.listModels(),
        api.getLiveModelMetrics(),
      ]);
      setModels(modelList);
      setLiveMetrics(metrics);
    } catch (e) {
      console.error("Failed to load models", e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchModelData();
  }, [fetchModelData]);

  const promoteModel = async (modelId: string) => {
    const updated = await api.promoteModel(modelId);
    await fetchModelData();
    return updated;
  };

  return {
    models,
    liveMetrics,
    isLoading,
    refresh: fetchModelData,
    promoteModel,
  };
}
