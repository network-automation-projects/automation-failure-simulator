"""
models.py

Data models for devices and task results in the automation failure simulator.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class FailureType(Enum):
    """Types of failures that can be simulated."""

    NONE = "none"
    TIMEOUT = "timeout"
    FLAKY = "flaky"
    PARTIAL = "partial"


class TaskStatus(Enum):
    """Status of a task execution."""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    PARTIAL = "partial"


@dataclass
class Device:
    """Represents a device with configurable failure profile."""

    name: str
    ip: str
    failure_type: FailureType = FailureType.NONE
    failure_rate: float = 0.0  # 0.0-1.0 for flaky devices
    timeout_seconds: int = 5


@dataclass
class TaskResult:
    """Result of executing a task on a device."""

    device: Device
    status: TaskStatus
    attempts: int = 0
    elapsed_time: float = 0.0
    error_message: Optional[str] = None
    partial_results: List[str] = field(default_factory=list)
