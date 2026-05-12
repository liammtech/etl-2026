from dataclasses import dataclass
from datetime import date
from typing import Optional

# For pre-configured table row defaults, see /config/defaults/zinvextra_defaults.yml

@dataclass
class WipJobAllLabRow:
    Job: str
    Operation: int
    PlannedQueueDate: date
    PlannedStartDate: date
    PlannedEndDate: date
    WorkCentre: str
    WorkCentreDesc: str
    Milestone: str
    QueueTime: int
    Priority: Optional[int]
    ProductionYrWeek: str