"""
FlameScope - Step 2 Pydantic Schema
Defines the validated data model for each extracted NASA PSI investigation.
"""

from __future__ import annotations

from typing import List, Literal, Optional, Union

from pydantic import BaseModel, field_validator, model_validator


# ---------------------------------------------------------------------------
# Primitive building block
# ---------------------------------------------------------------------------

StatusLiteral = Literal["verified", "extracted", "inferred", "unavailable"]

class FieldValue(BaseModel):
    """
    Container for a single extracted field.
    Every field carries its value, unit, extraction status, and
    a verbatim quote + location from the source document.
    """

    value: Optional[Union[str, float, int, List[str]]] = None
    unit: Optional[str] = None
    status: StatusLiteral = "unavailable"
    evidence_quote: Optional[str] = None
    evidence_location: Optional[str] = None

    model_config = {"extra": "ignore"}


# ---------------------------------------------------------------------------
# Enum helpers (validated as FieldValue.value)
# ---------------------------------------------------------------------------

FUEL_STATES: set[str] = {"solid", "liquid", "gas"}
GRAVITY_CONDITIONS: set[str] = {"microgravity", "normal_gravity", "partial_gravity"}
SAFETY_CATEGORIES: set[str] = {"prevention", "detection", "suppression"}


# ---------------------------------------------------------------------------
# Main schema
# ---------------------------------------------------------------------------

class InvestigationExtracted(BaseModel):
    """Full structured record for one NASA PSI combustion investigation."""

    # ---- Identity ----
    investigation_id: str
    title: str
    acronym: Optional[str] = None
    doi: Optional[str] = None
    source_url: str

    # ---- Narrative ----
    objective: FieldValue = FieldValue()

    # ---- Hardware ----
    hardware: FieldValue = FieldValue()

    # ---- Fuel ----
    fuel_type: FieldValue = FieldValue()
    fuel_state: FieldValue = FieldValue()         # enum: solid | liquid | gas

    # ---- Sample geometry ----
    sample_shape: FieldValue = FieldValue()
    sample_size: FieldValue = FieldValue()

    # ---- Ambient conditions ----
    oxygen_percent_min: FieldValue = FieldValue()
    oxygen_percent_max: FieldValue = FieldValue()
    pressure_psi: FieldValue = FieldValue()
    airflow_speed_min: FieldValue = FieldValue()
    airflow_speed_max: FieldValue = FieldValue()
    diluents: FieldValue = FieldValue()

    # ---- Gravity ----
    gravity_condition: FieldValue = FieldValue()  # enum: microgravity | normal_gravity | partial_gravity

    # ---- Instrumentation ----
    sensors_and_measurements: FieldValue = FieldValue()

    # ---- Classification ----
    safety_category: FieldValue = FieldValue()    # list from: prevention | detection | suppression

    # ------------------------------------------------------------------ #
    # Validators                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_fv_value(v: object) -> object:
        """Pull .value out of a FieldValue instance or a dict."""
        if isinstance(v, FieldValue):
            return v.value
        if isinstance(v, dict):
            return v.get("value")
        return v   # raw scalar passed directly

    @field_validator("oxygen_percent_min", "oxygen_percent_max", mode="before")
    @classmethod
    def _validate_oxygen(cls, v: object) -> object:
        """Reject oxygen values outside [0, 100]."""
        raw = cls._extract_fv_value(v)
        if raw is not None:
            try:
                val = float(raw)
            except (TypeError, ValueError):
                return v   # non-numeric; leave as-is
            if not (0.0 <= val <= 100.0):
                raise ValueError(
                    f"Oxygen value {val} is outside the valid range [0, 100]. "
                    "Check whether the source is in mole fraction (multiply × 100)."
                )
        return v

    @field_validator("fuel_state", mode="before")
    @classmethod
    def _validate_fuel_state(cls, v: object) -> object:
        raw = cls._extract_fv_value(v)
        if raw is not None and str(raw).lower() not in FUEL_STATES:
            raise ValueError(
                f"fuel_state '{raw}' not in allowed set {FUEL_STATES}"
            )
        return v

    @field_validator("gravity_condition", mode="before")
    @classmethod
    def _validate_gravity(cls, v: object) -> object:
        raw = cls._extract_fv_value(v)
        if raw is not None and str(raw).lower() not in GRAVITY_CONDITIONS:
            raise ValueError(
                f"gravity_condition '{raw}' not in allowed set {GRAVITY_CONDITIONS}"
            )
        return v

    @field_validator("safety_category", mode="before")
    @classmethod
    def _validate_safety(cls, v: object) -> object:
        raw = cls._extract_fv_value(v)
        if raw is not None:
            items = raw if isinstance(raw, list) else [raw]
            bad = [i for i in items if str(i).lower() not in SAFETY_CATEGORIES]
            if bad:
                raise ValueError(
                    f"safety_category items {bad} not in allowed set {SAFETY_CATEGORIES}"
                )
        return v

    model_config = {"extra": "ignore"}
