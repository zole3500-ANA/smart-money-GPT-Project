from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class VerificationResult(BaseModel):
    source: str
    is_fresh: bool
    confidence: float = Field(ge=0, le=1)
    notes: List[str] = Field(default_factory=list)


class SignalScore(BaseModel):
    smart_money_flow: float = Field(ge=0, le=100)
    technical_trend: float = Field(ge=0, le=100)
    options_flow: float = Field(ge=0, le=100)
    short_pressure: float = Field(ge=0, le=100)
    fundamental_quality: float = Field(ge=0, le=100)
    institutional_flow: float = Field(ge=0, le=100)
    insider_flow: float = Field(ge=0, le=100)
    dark_pool_flow: float = Field(ge=0, le=100)
    relative_strength: float = Field(ge=0, le=100)
    psychology: float = Field(ge=0, le=100)
    catalyst_risk: float = Field(ge=0, le=100)
    composite: float = Field(ge=0, le=100)
    label: str


class Forecast(BaseModel):
    ticker: str
    next_day_bias: str
    probability_up: float = Field(ge=0, le=1)
    expected_range_low: Optional[float] = None
    expected_range_high: Optional[float] = None
    risk_notes: List[str] = Field(default_factory=list)


class AgentReport(BaseModel):
    ticker: str
    current_price: Optional[float]
    verification: List[VerificationResult]
    indicators: Dict[str, Any]
    score: SignalScore
    three_view_analysis: Dict[str, str]
    forecast: Forecast
