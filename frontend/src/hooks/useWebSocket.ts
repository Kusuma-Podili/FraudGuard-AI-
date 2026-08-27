"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { WS_BASE_URL } from "../lib/constants";
import { StreamTransactionEvent } from "../types";

export function useWebSocket(maxBufferSize: number = 100) {
  const [events, setEvents] = useState<StreamTransactionEvent[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isPausedRef = useRef<boolean>(false);
  isPausedRef.current = isPaused;

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_BASE_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        if (isPausedRef.current) return;
        try {
          const data = JSON.parse(event.data);
          if (data.event === "TRANSACTION_PROCESSED" || data.event === "TRANSACTION_STREAMED") {
            setEvents((prev) => [data as StreamTransactionEvent, ...prev.slice(0, maxBufferSize - 1)]);
          }
        } catch (e) {
          console.error("Failed to parse WebSocket message", e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Exponential / fixed reconnect
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      ws.onerror = (err) => {
        setError("WebSocket connection error");
      };
    } catch (err: any) {
      setError(err.message || "Failed to initialize WebSocket");
    }
  }, [maxBufferSize]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  const clearEvents = useCallback(() => setEvents([]), []);
  const togglePause = useCallback(() => setIsPaused((prev) => !prev), []);

  return {
    events,
    isConnected,
    isPaused,
    error,
    clearEvents,
    togglePause,
  };
}
