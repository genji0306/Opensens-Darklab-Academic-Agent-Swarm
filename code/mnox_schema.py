from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Optional

from jsonschema import ValidationError, validate

PHASES = ("alpha", "gamma", "delta", "epsilon")

SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["meta", "descriptors"],
    "properties": {
        "meta": {
            "type": "object",
            "required": [
                "sample_id",
                "phase",
                "synthesis_route",
                "electrolyte",
                "reference_electrode",
                "working_electrode",
                "substrate",
                "loading_mg_cm2",
                "geometric_area_cm2",
            ],
            "properties": {
                "sample_id": {"type": "string", "minLength": 1},
                "phase": {"type": "string", "enum": list(PHASES)},
                "synthesis_route": {"type": "string", "minLength": 1},
                "calcination_temp_C": {"type": ["number", "null"]},
                "electrolyte": {"type": "string", "minLength": 1},
                "reference_electrode": {"type": "string", "minLength": 1},
                "working_electrode": {"type": "string", "minLength": 1},
                "substrate": {"type": "string", "minLength": 1},
                "loading_mg_cm2": {"type": "number"},
                "geometric_area_cm2": {"type": "number"},
            },
            "additionalProperties": False,
        },
        "descriptors": {
            "type": "object",
            "properties": {
                "phase_ambiguous": {"type": ["boolean", "null"]},
                "rs_ohm": {"type": ["number", "null"]},
                "rct_ohm": {"type": ["number", "null"]},
                "cdl_F": {"type": ["number", "null"]},
                "cpe_alpha": {"type": ["number", "null"]},
                "warburg_coeff": {"type": ["number", "null"]},
                "b_value_mean": {"type": ["number", "null"]},
                "sensitivity_mA_uM_cm2": {"type": ["number", "null"]},
                "lod_uM": {"type": ["number", "null"]},
                "linear_range_uM": {"type": ["number", "null"]},
                "operational_potential_V": {"type": ["number", "null"]},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}


@dataclass
class SampleMeta:
    """Sample-level immutable metadata for a MnO2 sample.

    Attributes:
        sample_id: Sample identifier from samples.csv.
        phase: MnO2 polymorph label.
        synthesis_route: Synthesis recipe identifier.
        calcination_temp_C: Calcination temperature in degree Celsius.
        electrolyte: Electrolyte composition label.
        reference_electrode: Reference electrode label.
        working_electrode: Working electrode label.
        substrate: Substrate identity.
        loading_mg_cm2: Catalyst loading in mg/cm^2.
        geometric_area_cm2: Electrode area in cm^2.
    """

    sample_id: str
    phase: str
    synthesis_route: str
    calcination_temp_C: Optional[float]
    electrolyte: str
    reference_electrode: str
    working_electrode: str
    substrate: str
    loading_mg_cm2: float
    geometric_area_cm2: float


@dataclass
class Descriptors:
    """Canonical descriptor record for multimodal MnO2 characterization."""

    phase_ambiguous: Optional[bool] = None
    rs_ohm: Optional[float] = None
    rct_ohm: Optional[float] = None
    cdl_F: Optional[float] = None
    cpe_alpha: Optional[float] = None
    warburg_coeff: Optional[float] = None
    b_value_mean: Optional[float] = None
    sensitivity_mA_uM_cm2: Optional[float] = None
    lod_uM: Optional[float] = None
    linear_range_uM: Optional[float] = None
    operational_potential_V: Optional[float] = None


def validate_record(record: dict[str, Any]) -> None:
    """Validate a record against the canonical JSON schema.

    Args:
        record: Record containing top-level ``meta`` and ``descriptors`` keys.

    Raises:
        ValueError: If schema validation fails.
    """

    try:
        validate(instance=record, schema=SCHEMA)
    except ValidationError as exc:
        raise ValueError(f"Descriptor schema validation failed: {exc.message}") from exc


def save_record(meta: SampleMeta, desc: Descriptors, outpath: Path) -> None:
    """Serialize and validate a descriptor record to JSON.

    Args:
        meta: Sample metadata object.
        desc: Descriptor object.
        outpath: Output JSON path.

    Raises:
        ValueError: If the generated JSON record fails schema validation.
    """

    record = {"meta": asdict(meta), "descriptors": asdict(desc)}
    validate_record(record)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(record, indent=2), encoding="utf-8")


def load_record(inpath: Path) -> tuple[SampleMeta, Descriptors]:
    """Load and validate a descriptor record from JSON.

    Args:
        inpath: Path to JSON descriptor record.

    Returns:
        Tuple containing parsed ``SampleMeta`` and ``Descriptors`` objects.

    Raises:
        FileNotFoundError: If ``inpath`` does not exist.
        ValueError: If parsed JSON fails schema validation.
    """

    if not inpath.exists():
        raise FileNotFoundError(f"Descriptor record not found at: {inpath}")

    payload = json.loads(inpath.read_text(encoding="utf-8"))
    validate_record(payload)
    return SampleMeta(**payload["meta"]), Descriptors(**payload["descriptors"])
