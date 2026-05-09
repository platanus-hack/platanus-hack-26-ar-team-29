"""PlanExecutor — confirm-once-fire-all step orchestration."""

from __future__ import annotations

import asyncio
import datetime as _dt
from typing import TYPE_CHECKING, Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.persistence.repositories.connections import ConnectionRepository
from app.persistence.repositories.plans import PlanRepository
from app.providers.wallbit.auth import WallbitCredentials

if TYPE_CHECKING:
    from app.agents.chat_agent import ChatAgent
    from app.api.ws.manager import ConnectionManager
    from app.providers.wallbit.capabilities import WallbitProvider

log = structlog.get_logger(__name__)


def _utcnow() -> _dt.datetime:
    return _dt.datetime.now(_dt.UTC)


class PlanExecutor:
    def __init__(
        self,
        wallbit_provider: WallbitProvider,
        manager: ConnectionManager,
        agent_tasks: set[asyncio.Task],
    ) -> None:
        self.wallbit = wallbit_provider
        self.manager = manager
        self.agent_tasks = agent_tasks

    def schedule(
        self,
        plan_id: UUID,
        user_id: UUID,
        sessionmaker: async_sessionmaker,
        agent: ChatAgent,
        session_id: UUID | None,
    ) -> None:
        task = asyncio.create_task(
            self.execute(
                plan_id=plan_id,
                user_id=user_id,
                sessionmaker=sessionmaker,
                agent=agent,
                session_id=session_id,
            )
        )
        self.agent_tasks.add(task)
        task.add_done_callback(self.agent_tasks.discard)

    async def execute(
        self,
        plan_id: UUID,
        user_id: UUID,
        sessionmaker: async_sessionmaker,
        agent: ChatAgent,
        session_id: UUID | None,
    ) -> None:
        await asyncio.sleep(0.05)
        try:
            await self._execute_inner(
                plan_id=plan_id,
                user_id=user_id,
                sessionmaker=sessionmaker,
                agent=agent,
                session_id=session_id,
            )
        except Exception as exc:
            log.exception("plan_execute_failed", plan_id=str(plan_id), err=str(exc))
            if session_id is not None:
                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "error",
                        "code": "INTERNAL_ERROR",
                        "message_es": "El plan falló inesperadamente.",
                        "message_en": str(exc),
                    },
                )

    async def _execute_inner(
        self,
        plan_id: UUID,
        user_id: UUID,
        sessionmaker: async_sessionmaker,
        agent: ChatAgent,
        session_id: UUID | None,
    ) -> None:
        async with sessionmaker() as db:
            repo = PlanRepository(db)
            plan = await repo.get_plan_by_id(plan_id)
            if plan is None:
                return
            await repo.set_plan_state(plan_id, "executing", started_at=_utcnow())
            await db.commit()
            steps = list(plan.steps)

        if session_id is None and plan.origin_session_id is not None:
            session_id = plan.origin_session_id

        if session_id is not None:
            await self.manager.broadcast_to_session(
                session_id,
                {
                    "type": "plan_update",
                    "session_id": str(session_id),
                    "plan_id": str(plan_id),
                    "step_id": None,
                    "state": "executing",
                    "ts": _utcnow().isoformat().replace("+00:00", "Z"),
                },
            )

        any_failed = False
        steps_summary: list[dict[str, Any]] = []
        for step in steps:
            async with sessionmaker() as db:
                repo = PlanRepository(db)
                conn_repo = ConnectionRepository(db)

                wallbit_conn = None
                if step.connection_id is not None:
                    wallbit_conn = await conn_repo.get_by_id(step.connection_id, user_id)
                if wallbit_conn is None:
                    wallbit_conn = await conn_repo.get_active_wallbit(user_id)

                if wallbit_conn is None:
                    err_msg = "No hay una conexión Wallbit activa."
                    await repo.update_step_state(
                        step.id,
                        "failed",
                        result_summary=err_msg,
                        result_payload={"error": err_msg},
                        completed_at=_utcnow(),
                    )
                    await db.commit()
                    if session_id is not None:
                        await self.manager.broadcast_to_session(
                            session_id,
                            {
                                "type": "plan_update",
                                "session_id": str(session_id),
                                "plan_id": str(plan_id),
                                "step_id": str(step.id),
                                "state": "failed",
                                "error": err_msg,
                                "ts": _utcnow().isoformat().replace("+00:00", "Z"),
                            },
                        )
                    any_failed = True
                    steps_summary.append({"id": str(step.id), "state": "failed"})
                    break

                # Mark executing.
                await repo.update_step_state(step.id, "executing", started_at=_utcnow())
                await db.commit()
                if session_id is not None:
                    await self.manager.broadcast_to_session(
                        session_id,
                        {
                            "type": "plan_update",
                            "session_id": str(session_id),
                            "plan_id": str(plan_id),
                            "step_id": str(step.id),
                            "state": "executing",
                            "ts": _utcnow().isoformat().replace("+00:00", "Z"),
                        },
                    )

                creds = WallbitCredentials.from_blob(bytes(wallbit_conn.credentials_encrypted))

            # Run the actual provider call OUTSIDE the DB session.
            try:
                if step.tool_name == "place_trade":
                    result = await self.wallbit.place_trade(
                        creds=creds,
                        args=dict(step.args or {}),
                        idempotency_key=step.id,
                    )
                else:
                    raise RuntimeError(f"Unsupported step tool '{step.tool_name}'.")
                step_state = "ok"
                summary = (
                    f"Wallbit: {step.tool_name} ok"
                    if isinstance(result, dict)
                    else str(result)[:140]
                )
                payload = result if isinstance(result, dict) else {"raw": result}
            except Exception as exc:
                log.warning("step_exec_failed", step_id=str(step.id), err=str(exc))
                step_state = "failed"
                summary = f"Falló: {exc}"
                payload = {"error": str(exc)}

            async with sessionmaker() as db:
                repo = PlanRepository(db)
                await repo.update_step_state(
                    step.id,
                    step_state,
                    result_summary=summary,
                    result_payload=payload,
                    completed_at=_utcnow(),
                )
                await db.commit()

            steps_summary.append({"id": str(step.id), "state": step_state})
            if session_id is not None:
                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "plan_update",
                        "session_id": str(session_id),
                        "plan_id": str(plan_id),
                        "step_id": str(step.id),
                        "state": step_state,
                        "summary": summary,
                        "ts": _utcnow().isoformat().replace("+00:00", "Z"),
                    },
                )

            if step_state == "failed":
                any_failed = True
                break  # stop-on-first-error per 02-1 §6.1

        final_state = "partially_failed" if any_failed else "completed"
        async with sessionmaker() as db:
            repo = PlanRepository(db)
            await repo.set_plan_state(plan_id, final_state, completed_at=_utcnow())
            await db.commit()

        if session_id is not None:
            await self.manager.broadcast_to_session(
                session_id,
                {
                    "type": "plan_update",
                    "session_id": str(session_id),
                    "plan_id": str(plan_id),
                    "step_id": None,
                    "state": final_state,
                    "ts": _utcnow().isoformat().replace("+00:00", "Z"),
                },
            )

            await agent.continue_after_plan(
                session_id=session_id,
                user_id=user_id,
                plan_id=plan_id,
                outcome=final_state,
                steps_summary=steps_summary,
                sessionmaker=sessionmaker,
            )
