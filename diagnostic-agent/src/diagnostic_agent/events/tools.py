"""Herramientas de eventos para el Tool Registry del runtime (docs/ei/10, ADR-0016).

Registra las consultas de eventos como herramientas auditadas READ_ONLY. Los resultados
son RESÚMENES destilados (context engineering, docs/agent-runtime/08): el agente recibe
tipo/contexto/confianza/evidencias, nunca la telemetría cruda del evento.
"""

from typing import Any

from diagnostic_agent.runtime.tools import RiskLevel, ToolRegistry, ToolSpec
from diagnostic_agent.storage import schema as dbs
from diagnostic_agent.storage.store import EdgeStoreV2

_ROLES = ("supervisor", "recall", "telemetry", "diagnostic")


def _event_summary(row: Any) -> dict[str, Any]:
    return {
        "event_id": row.event_id,
        "event_type": row.event_type,
        "event_class": row.event_class,
        "seq": [row.seq_start, row.seq_end],
        "duration_ms": row.duration_ms,
        "confidence": row.confidence,
        "detection_method": row.detection_method,
        "evidence": list(row.evidence or []),
    }


def register_event_tools(registry: ToolRegistry, store: EdgeStoreV2) -> None:
    """Añade get_vehicle_state / query_vehicle_events / find_comparable_events."""

    def get_vehicle_state(session_id: str) -> dict[str, Any]:
        rows = store.raw_rows(dbs.EventRow, session_id=session_id)
        leaf = [r for r in rows if r.event_type != "TRIP"]
        if not leaf:
            return {"state": "UNKNOWN", "reason": "sin eventos detectados en la sesión"}
        last = max(
            leaf,
            key=lambda r: (
                r.seq_end if r.seq_end is not None else -1,
                r.seq_start if r.seq_start is not None else -1,
            ),
        )
        return {
            "state": last.event_type,
            "since_seq": last.seq_start,
            "event": _event_summary(last),
        }

    def query_vehicle_events(
        session_id: str | None = None,
        event_type: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        filters: dict[str, Any] = {}
        if session_id:
            filters["session_id"] = session_id
        if event_type:
            filters["event_type"] = event_type
        rows = store.raw_rows(dbs.EventRow, **filters)
        rows.sort(key=lambda r: (r.session_id, r.seq_start or 0))
        return [_event_summary(r) for r in rows[:limit]]

    def find_comparable_events(
        context_signature: str, exclude_event_id: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        rows = store.raw_rows(dbs.EventFeatureRow, context_signature=context_signature)
        out = []
        for r in rows:
            if r.event_id == exclude_event_id:
                continue
            out.append(
                {
                    "event_id": r.event_id,
                    "session_id": r.session_id,
                    "context_signature": r.context_signature,
                    "values": dict(r.values),
                }
            )
        return out[:limit]

    registry.register(
        ToolSpec(
            name="get_vehicle_state",
            description="Estado vehicular vigente (último evento cerrado de la sesión)",
            input_schema={"session_id": "str"},
            output_schema={"state": "str", "event": "dict"},
            timeout_s=5.0,
            permissions=_ROLES,
            side_effects="none",
            idempotent=True,
            risk_level=RiskLevel.READ_ONLY,
            handler=get_vehicle_state,
        )
    )
    registry.register(
        ToolSpec(
            name="query_vehicle_events",
            description="Eventos detectados filtrables por sesión/tipo (resúmenes destilados)",
            input_schema={"session_id": "str?", "event_type": "str?", "limit": "int"},
            output_schema={"events": "list[dict]"},
            timeout_s=5.0,
            permissions=_ROLES,
            side_effects="none",
            idempotent=True,
            risk_level=RiskLevel.READ_ONLY,
            handler=query_vehicle_events,
        )
    )
    registry.register(
        ToolSpec(
            name="find_comparable_events",
            description="EFVs de eventos equivalentes (misma context_signature) para comparar",
            input_schema={"context_signature": "str", "exclude_event_id": "str?", "limit": "int"},
            output_schema={"events": "list[dict]"},
            timeout_s=5.0,
            permissions=_ROLES,
            side_effects="none",
            idempotent=True,
            risk_level=RiskLevel.READ_ONLY,
            handler=find_comparable_events,
        )
    )
