"""Real-Time WebSocket Connection Manager and Broadcast Hub.

Maintains active WebSocket connections with the frontend dashboard and streams
live transactions, alerts, metrics, and simulation telemetry.
"""

from __future__ import annotations
import json
import asyncio
from typing import Dict, List, Set, Any, Optional
from starlette.websockets import WebSocket, WebSocketState
from backend.app.core.logging import get_logger

logger = get_logger("fraudguard.websocket")


class WebSocketManager:
    """Manages WebSocket client connections and channel subscriptions."""

    def __init__(self):
        # Active connections by topic channel
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "transactions": set(),
            "alerts": set(),
            "metrics": set(),
            "simulation": set(),
        }
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: str = "transactions") -> None:
        """Accept connection and register under channel."""
        await websocket.accept()
        async with self._lock:
            if channel not in self.active_connections:
                self.active_connections[channel] = set()
            self.active_connections[channel].add(websocket)
        logger.info(f"WebSocket client connected to channel '{channel}'. Total: {len(self.active_connections[channel])}")

    async def disconnect(self, websocket: WebSocket, channel: str = "transactions") -> None:
        """Remove connection from registry."""
        async with self._lock:
            if channel in self.active_connections and websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
        logger.info(f"WebSocket client disconnected from '{channel}'")

    async def broadcast(self, channel: str, message: Dict[str, Any]) -> None:
        """Broadcast JSON message to all active subscribers on a channel."""
        if channel not in self.active_connections:
            return

        payload = json.dumps(message)
        dead_connections: List[WebSocket] = []

        # Read copy of connections set
        connections = list(self.active_connections[channel])
        for ws in connections:
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_text(payload)
                else:
                    dead_connections.append(ws)
            except Exception:
                dead_connections.append(ws)

        # Cleanup dead sockets
        if dead_connections:
            async with self._lock:
                for dead_ws in dead_connections:
                    if dead_ws in self.active_connections[channel]:
                        self.active_connections[channel].remove(dead_ws)


# Global singleton manager
ws_manager = WebSocketManager()
