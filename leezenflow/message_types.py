from datetime import timedelta
from typing import List
from pydantic import BaseModel, Field
from leezenflow.phase import TrafficLightPhase


class MovementEventRaw(BaseModel):
    min_time: int
    max_time: int
    likely_time: int  # the 1/10 seconds of the current or (edge case) following hour
    current_phase: str  # current phase of the traffic light
    confidence: int = Field(ge=0, le=15)


class MessageContentRaw(BaseModel):
    """Dataclass for the content of a SPATM message.
    Raw Values from XML without any transformation.
    You most likely want to work with MessageContentParsed"""

    signal_group: int
    time_stamp: int  # seconds of the minute + "000" (e.g. 25000 = 25s)
    moy: int  # minute of the year
    lsa_id: int
    movement_events: List[MovementEventRaw]


class MovementEventParsed(BaseModel):
    min_time: timedelta
    max_time: timedelta
    likely_time: timedelta
    current_phase: TrafficLightPhase  # current phase of the traffic lighttimedelta
    confidence: int = Field(ge=0, le=100)  # percenttimedelta


class MessageContentParsed(BaseModel):
    """Dataclass for the content of a SPATM message.
    Parsed Values that are easier to work with"""

    signal_group: int
    time_stamp: int  # seconds of the minute + "000" (e.g. 25000 = 25s)
    moy: int
    lsa_id: int
    movement_events: List[MovementEventParsed]
