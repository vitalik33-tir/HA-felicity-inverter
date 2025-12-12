from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Dict, List

_LOGGER = logging.getLogger(__name__)


class FelicityApiError(Exception):
    """Error while communicating with Felicity inverter."""


class FelicityClient:
    """TCP client for Felicity inverter local API."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

    async def async_get_data(self) -> dict:
        """Send commands and combine all data into one dict.

        Commands:
          - wifilocalMonitor:get dev real infor   -> runtime telemetry (JSON)
          - wifilocalMonitor:get dev basice infor -> versions / type (JSON)
          - wifilocalMonitor:get dev set infor    -> settings (can be multiple JSON objects glued)
        """
        data: Dict[str, Any] = {}

        # 1) Runtime
        real_raw = await self._async_read_raw(b"wifilocalMonitor:get dev real infor")
        real = self._parse_first_json_object(real_raw)
        if not isinstance(real, dict):
            raise FelicityApiError(f"Unexpected runtime payload: {real_raw!r}")
        data.update(real)

        # 2) Basic info
        try:
            basic_raw = await self._async_read_raw(
                b"wifilocalMonitor:get dev basice infor"
            )
            basic = self._parse_first_json_object(basic_raw)
            if isinstance(basic, dict):
                data["_basic"] = basic
        except Exception as err:
            _LOGGER.debug("Failed to read basic info: %s", err)

        # 3) Settings (may be multiple JSON objects in one response)
        try:
            set_raw = await self._async_read_raw(b"wifilocalMonitor:get dev set infor")
            parts = self._parse_all_json_objects(set_raw)
            merged: Dict[str, Any] = {}
            for p in parts:
                if isinstance(p, dict):
                    merged.update(p)
            if merged:
                data["_settings"] = merged
        except Exception as err:
            _LOGGER.debug("Failed to read settings info: %s", err)

        return data

    async def _async_read_raw(self, command: bytes) -> str:
        """Open TCP, send command, read response as text."""
        try:
            reader, writer = await asyncio.open_connection(self._host, self._port)
        except Exception as err:
            raise FelicityApiError(
                f"Error connecting to {self._host}:{self._port}: {err}"
            ) from err

        try:
            writer.write(command)
            await writer.drain()

            data = b""
            # Some devices send one or several JSON objects back-to-back.
            for _ in range(40):
                try:
                    chunk = await asyncio.wait_for(reader.read(2048), timeout=0.5)
                except asyncio.TimeoutError:
                    break
                if not chunk:
                    break
                data += chunk
        except Exception as err:
            raise FelicityApiError(
                f"Error talking to {self._host}:{self._port}: {err}"
            ) from err
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

        if not data:
            raise FelicityApiError("No data received from inverter")

        text = data.decode("ascii", errors="ignore").strip()
        _LOGGER.debug("Raw Felicity response for %r: %r", command, text)
        return text

    # ------------------------- JSON helpers -------------------------

    @staticmethod
    def _normalize_payload(text: str) -> str:
        # Device sometimes returns single quotes or Python-ish None.
        norm = text.strip().replace("\r", "").replace("\n", "")
        norm = norm.replace("'", '"')
        norm = re.sub(r"\bNone\b", "null", norm)
        return norm

    def _parse_all_json_objects(self, text: str) -> List[Any]:
        norm = self._normalize_payload(text)

        # Fast path: whole payload is one JSON object.
        try:
            return [json.loads(norm)]
        except Exception:
            pass

        # Extract multiple JSON objects using brace depth.
        objs: List[str] = []
        depth = 0
        start = None
        for i, ch in enumerate(norm):
            if ch == "{":
                if depth == 0:
                    start = i
                depth += 1
            elif ch == "}":
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start is not None:
                        objs.append(norm[start : i + 1])
                        start = None

        if not objs:
            # Fallback: non-greedy
            objs = re.findall(r"\{.*?\}", norm)

        parsed: List[Any] = []
        for obj in objs:
            try:
                parsed.append(json.loads(obj))
            except Exception as err:
                _LOGGER.debug("Skip invalid JSON chunk %r: %s", obj, err)
        return parsed

    def _parse_first_json_object(self, text: str) -> Any:
        parts = self._parse_all_json_objects(text)
        return parts[0] if parts else None
