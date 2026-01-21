from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class CheckResult:
    check_type: str
    dataset: str
    passed: bool
    message: str
    details: Dict[str, Any]

class BaseCheck:
    check_type: str = "base"

    def __init__(self, dataset_name: str, **kwargs: Any):
        self.dataset_name = dataset_name
        self.kwargs = kwargs

    def run(self, context: "RunContext") -> CheckResult:  # noqa: F821
        raise NotImplementedError
