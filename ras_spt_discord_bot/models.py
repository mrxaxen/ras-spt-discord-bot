from enum import Enum
from pydantic import BaseModel, Field


class PlayerActivity(Enum):
    MENU = 0
    IN_RAID = 1
    IN_STASH = 2


class RaidInformation(BaseModel):
    location: str
    side: str
    time: str


class CurrentPlayer(BaseModel):
    nickname: str
    level: int
    activity: PlayerActivity
    activity_started_timestamp: int = Field(alias='activityStartedTImestamp')
    raid_info: RaidInformation = Field(alias='raidInformation')


class ServerTwoPartResponse(BaseModel):
    first: str
    final: str
