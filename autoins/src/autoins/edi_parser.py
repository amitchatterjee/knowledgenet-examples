from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, get_origin, get_args
import csv

from autoins.entities import (
    Claim,
    Policy,
    Group,
    Driver,
    Automobile,
    IncidenceReport,
    Estimate,
    Request,
)


def _parse_datetime(s: str) -> Optional[datetime]:
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
    raise


def _convert_value(raw: str, outer_type: Any):
    raw = raw.strip()
    if raw == "":
        return None
    origin = get_origin(outer_type)
    if origin is not None:
        outer_type = get_args(outer_type)[0] if get_args(outer_type) else outer_type

    if outer_type is datetime:
        return _parse_datetime(raw)
    try:
        if issubclass(outer_type, Enum):
            return outer_type(raw)
    except Exception:
        pass
    if outer_type is int:
        return int(raw)
    if outer_type is float:
        return float(raw)
    if outer_type is bool:
        return raw.lower() in ("1", "true", "yes", "y")
    return raw


MODEL_MAP = {
    "CLA": Claim,
    "POL": Policy,
    "GRP": Group,
    "DRV": Driver,
    "AUT": Automobile,
    "INC": IncidenceReport,
    "EST": Estimate,
}

# segment ids that represent repeating claim history loops
COLLISION_SEG_ID = "CLH"
LIABILITY_SEG_ID = "LYH"

def parse_edi(payload: str) -> List[Request]:
    """Parse a payload containing one or more STX/ETX-delimited messages.

    - Each message block starts with a segment `STX` and ends with `ETX`.
    - Segments inside a block are CSV-formatted lines; first element is segment id.
    - Returns a list of `Request` objects, one per complete STX/ETX block.
    """
    results: List[Request] = []

    # accumulators for the current block
    in_block = False
    claim = None
    policy = None
    group = None
    driver = None
    automobile = None
    incidence_report = None
    estimates: List[Estimate] = []
    collision_history: List[Claim] = []
    liability_history: List[Claim] = []

    def _reset_block():
        return (None, None, None, None, None, None, [], [], [])

    for raw_line in payload.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        reader = csv.reader([line])
        parts = next(reader, None)
        if not parts:
            continue
        seg_id = parts[0].strip().upper()
        data = parts[1:]

        # start/end markers
        if seg_id == "STX":
            # start a new block; reset accumulators
            in_block = True
            claim, policy, group, driver, automobile, incidence_report, estimates, collision_history, liability_history = _reset_block()
            continue
        if seg_id == "ETX":
            # finish current block
            if in_block:
                if claim is None:
                    raise ValueError("CLAIM segment is required in STX/ETX block")
                results.append(Request(
                    claim=claim,
                    policy=policy,
                    group=group,
                    driver=driver,
                    automobile=automobile,
                    incidence_report=incidence_report,
                    estimates=estimates or None,
                    collision_history=collision_history or None,
                    liability_history=liability_history or None,
                ))
            in_block = False
            # reset after closing
            claim, policy, group, driver, automobile, incidence_report, estimates, collision_history, liability_history = _reset_block()
            continue

        if not in_block:
            # ignore segments outside STX/ETX
            continue

        # inside a block: process segment
        is_collision = seg_id == COLLISION_SEG_ID
        is_liability = seg_id == LIABILITY_SEG_ID

        model = None
        if is_collision or is_liability:
            model = Claim
        else:
            model = MODEL_MAP.get(seg_id)
            if model is None:
                continue

        
        fields = list(model.model_fields.items())
        kwargs = {}
        for (fname, finfo), raw_val in zip(fields, data):
            # Determine the field's declared type in a pydantic-version-agnostic way
            outer = None
            if hasattr(finfo, "annotation"):
                outer = getattr(finfo, "annotation")
            elif hasattr(finfo, "type_"):
                outer = getattr(finfo, "type_")
            elif hasattr(finfo, "outer_type_"):
                outer = getattr(finfo, "outer_type_")
            else:
                outer = getattr(model, "__annotations__", {}).get(fname)

            origin = get_origin(outer)
            if origin is list or origin is dict or origin is set:
                continue
            try:
                kwargs[fname] = _convert_value(raw_val, outer)
            except Exception:
                kwargs[fname] = raw_val

        try:
            inst = model(**kwargs)
        except Exception:
            # skip invalid segment
            continue

        if model is Claim:
            if is_collision:
                collision_history.append(inst)
            elif is_liability:
                liability_history.append(inst)
            else:
                claim = inst
        elif model is Policy:
            policy = inst
        elif model is Group:
            group = inst
        elif model is Driver:
            driver = inst
        elif model is Automobile:
            automobile = inst
        elif model is IncidenceReport:
            incidence_report = inst
        elif model is Estimate:
            estimates.append(inst)

    return results
