from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


SPEC = importlib.util.spec_from_file_location(
    "mnox_schema", Path(__file__).resolve().parents[1] / "code" / "mnox_schema.py"
)
assert SPEC and SPEC.loader
MNOX_SCHEMA = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MNOX_SCHEMA
SPEC.loader.exec_module(MNOX_SCHEMA)

Descriptors = MNOX_SCHEMA.Descriptors
SampleMeta = MNOX_SCHEMA.SampleMeta
load_record = MNOX_SCHEMA.load_record
save_record = MNOX_SCHEMA.save_record
validate_record = MNOX_SCHEMA.validate_record


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    meta = SampleMeta(
        sample_id="alpha_01",
        phase="alpha",
        synthesis_route="hydrothermal_160C_12h",
        calcination_temp_C=None,
        electrolyte="0.1M_PBS",
        reference_electrode="Ag/AgCl",
        working_electrode="GCE",
        substrate="GCE",
        loading_mg_cm2=0.5,
        geometric_area_cm2=0.0707,
    )
    desc = Descriptors(rs_ohm=10.0, rct_ohm=500.0, cpe_alpha=0.85)

    outpath = tmp_path / "alpha_01.json"
    save_record(meta, desc, outpath)
    loaded_meta, loaded_desc = load_record(outpath)

    assert loaded_meta == meta
    assert loaded_desc == desc


def test_validate_rejects_invalid_phase() -> None:
    record = {
        "meta": {
            "sample_id": "alpha_01",
            "phase": "invalid",
            "synthesis_route": "route",
            "calcination_temp_C": None,
            "electrolyte": "0.1M_PBS",
            "reference_electrode": "Ag/AgCl",
            "working_electrode": "GCE",
            "substrate": "GCE",
            "loading_mg_cm2": 0.5,
            "geometric_area_cm2": 0.0707,
        },
        "descriptors": {},
    }

    with pytest.raises(ValueError, match="schema validation failed"):
        validate_record(record)


def test_load_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Descriptor record not found"):
        load_record(tmp_path / "missing.json")
