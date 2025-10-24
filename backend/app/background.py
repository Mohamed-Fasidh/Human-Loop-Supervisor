from __future__ import annotations
import asyncio
import os
from datetime import datetime, timedelta
from sqlmodel import Session, select
from .models import HelpRequest, RequestStatus
from .notifications import Notifier

SLA_MINUTES = int(os.getenv("SLA_MINUTES", "15"))

async def sla_watcher(engine):
    notifier = Notifier()
    while True:
        try:
            with Session(engine) as session:
                cutoff = datetime.utcnow() - timedelta(minutes=SLA_MINUTES)
                q = select(HelpRequest).where(
                    HelpRequest.status == RequestStatus.PENDING,
                    HelpRequest.created_at < cutoff,
                )
                for hr in session.exec(q).all():
                    hr.status = RequestStatus.UNRESOLVED
                    hr.resolved_at = datetime.utcnow()
                    session.add(hr)
                    session.commit()
                    await notifier.notify_supervisor(
                        f"Request #{hr.id} from {hr.caller_id} timed out and was marked UNRESOLVED."
                    )
        except Exception as e:
            print(f"[SLA WATCHER ERROR] {e}")
        await asyncio.sleep(30)
