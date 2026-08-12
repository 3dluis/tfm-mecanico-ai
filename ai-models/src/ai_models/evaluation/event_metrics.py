"""Métricas de detección de eventos (F6, docs/event-intelligence/11).

Protocolo: un evento predicho acierta si existe un evento de ground truth del MISMO tipo
con IoU temporal ≥ umbral (0.5 por defecto); el emparejamiento es greedy por IoU
descendente y uno-a-uno. Para eventos puntuales (seq_start == seq_end) el criterio es
distancia de onset ≤ tolerancia. Se reportan P/R/F1 por tipo + errores de onset/fin.
"""

from dataclasses import dataclass, field

from mecanico_contracts import VehicleEvent

DEFAULT_IOU = 0.5
POINT_TOLERANCE_TICKS = 5


def temporal_iou(a: VehicleEvent, b: VehicleEvent) -> float:
    """IoU sobre los rangos de seq (ambos inclusive). 0 si falta seq en alguno."""
    if a.seq_start is None or a.seq_end is None or b.seq_start is None or b.seq_end is None:
        return 0.0
    inter = min(a.seq_end, b.seq_end) - max(a.seq_start, b.seq_start) + 1
    union = max(a.seq_end, b.seq_end) - min(a.seq_start, b.seq_start) + 1
    return max(0, inter) / union if union > 0 else 0.0


def _is_point(e: VehicleEvent) -> bool:
    return e.seq_start is not None and e.seq_start == e.seq_end


@dataclass
class TypeReport:
    """Métricas de un tipo de evento."""

    tp: int = 0
    fp: int = 0
    fn: int = 0
    ious: list[float] = field(default_factory=list)
    onset_errors: list[int] = field(default_factory=list)
    end_errors: list[int] = field(default_factory=list)

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def mean_iou(self) -> float:
        return sum(self.ious) / len(self.ious) if self.ious else 0.0

    @property
    def mean_onset_error(self) -> float:
        return sum(self.onset_errors) / len(self.onset_errors) if self.onset_errors else 0.0


def match_events(
    predicted: list[VehicleEvent],
    ground_truth: list[VehicleEvent],
    iou_threshold: float = DEFAULT_IOU,
    point_tolerance: int = POINT_TOLERANCE_TICKS,
) -> list[tuple[VehicleEvent, VehicleEvent, float]]:
    """Empareja predicciones con GT (mismo tipo, greedy por IoU, uno-a-uno)."""
    candidates: list[tuple[float, VehicleEvent, VehicleEvent]] = []
    for p in predicted:
        for g in ground_truth:
            if p.event_type != g.event_type:
                continue
            if _is_point(g) or _is_point(p):
                if (
                    p.seq_start is not None
                    and g.seq_start is not None
                    and abs(p.seq_start - g.seq_start) <= point_tolerance
                ):
                    candidates.append((1.0, p, g))
                continue
            iou = temporal_iou(p, g)
            if iou >= iou_threshold:
                candidates.append((iou, p, g))
    candidates.sort(key=lambda c: -c[0])
    used_p: set[str] = set()
    used_g: set[str] = set()
    matches: list[tuple[VehicleEvent, VehicleEvent, float]] = []
    for iou, p, g in candidates:
        if p.event_id in used_p or g.event_id in used_g:
            continue
        used_p.add(p.event_id)
        used_g.add(g.event_id)
        matches.append((p, g, iou))
    return matches


def event_detection_report(
    predicted: list[VehicleEvent],
    ground_truth: list[VehicleEvent],
    iou_threshold: float = DEFAULT_IOU,
    exclude_types: tuple[str, ...] = (),
) -> dict[str, TypeReport]:
    """P/R/F1 + IoU medio + error de onset por tipo de evento (tipos en pred ∪ GT)."""
    pred = [p for p in predicted if p.event_type not in exclude_types]
    gt = [g for g in ground_truth if g.event_type not in exclude_types]
    matches = match_events(pred, gt, iou_threshold)
    matched_p = {p.event_id for p, _, _ in matches}
    matched_g = {g.event_id for _, g, _ in matches}
    report: dict[str, TypeReport] = {}

    def rep(etype: str) -> TypeReport:
        return report.setdefault(etype, TypeReport())

    for p, g, iou in matches:
        r = rep(g.event_type)
        r.tp += 1
        r.ious.append(iou)
        if p.seq_start is not None and g.seq_start is not None:
            r.onset_errors.append(abs(p.seq_start - g.seq_start))
        if p.seq_end is not None and g.seq_end is not None:
            r.end_errors.append(abs(p.seq_end - g.seq_end))
    for p in pred:
        if p.event_id not in matched_p:
            rep(p.event_type).fp += 1
    for g in gt:
        if g.event_id not in matched_g:
            rep(g.event_type).fn += 1
    return report
