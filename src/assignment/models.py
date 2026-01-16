from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, field_validator

class CriterionType(str, Enum):
    MINIMIZE = "minimize"
    CONSTRAINT = "constraint"
    BEST_MIN = "best_min"
    WORST_MIN = "worst_min"

class CriterionConfig(BaseModel):
    type: CriterionType
    # For constraint type: at least this ratio of students must meet the criteria
    min_ratio: Optional[float] = None
    # For minimize/maximize: the threshold y
    target: Optional[float] = None

class GroupConfig(BaseModel):
    id: int
    size: int
    criteria: Dict[str, Union[CriterionConfig, List[CriterionConfig]]]

    @field_validator('criteria', mode='after')
    @classmethod
    def ensure_list_configs(cls, v):
        # Normalize all criteria to lists for internal processing
        return {
            name: [config] if isinstance(config, CriterionConfig) else config
            for name, config in v.items()
        }

class StudentConfig(BaseModel):
    id: int
    possible_groups: List[int]
    # Mapping of criterion name to value (0.0 to 1.0)
    values: Dict[str, float]

class ProblemInput(BaseModel):
    num_students: int
    num_groups: int
    groups: List[GroupConfig]
    students: List[StudentConfig]
    exclude: List[List[int]] = []  # List of student_id pairs that cannot be in the same group

class AssignmentResult(BaseModel):
    student_id: int
    group_id: int

class ProblemOutput(BaseModel):
    assignments: List[AssignmentResult]
    status: str
