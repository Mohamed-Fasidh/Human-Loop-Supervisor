from __future__ import annotations
import os
import httpx
from dataclasses import dataclass

@dataclass
class Notifier:
    webhook_url: str | None = os.getenv("NOTIFY_WEBHOOK_URL")

    async def notify_supervisor(self, message: str):
        print(f"[SUPERVISOR NOTIFY] {message}")
        if self.webhook_url:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(self.webhook_url, json={"text": message})
            except Exception as e:
                print(f"[WARN] supervisor webhook failed: {e}")

    async def message_caller(self, caller_id: str, message: str):
        print(f"[TEXT BACK -> {caller_id}] {message}")
        if self.webhook_url:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(self.webhook_url, json={"to": caller_id, "text": message})
            except Exception as e:
                print(f"[WARN] caller webhook failed: {e}")
