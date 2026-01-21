from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Dict, List, Any

class CheckSpec(BaseModel):
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)

    @staticmethod
    def from_raw(raw: Dict[str, Any]) -> "CheckSpec":
        raw = dict(raw)
        t = raw.pop("type")
        return CheckSpec(type=t, payload=raw)

class DatasetSpec(BaseModel):
    name: str
    path: str
    checks: List[CheckSpec] = Field(default_factory=list)

class SuiteSpec(BaseModel):
    suite_name: str
    datasets: List[DatasetSpec] = Field(default_factory=list)

def load_suite_from_dict(d: Dict[str, Any]) -> SuiteSpec:
    datasets = []
    for ds in d.get("datasets", []):
        checks = [CheckSpec.from_raw(c) for c in ds.get("checks", [])]
        datasets.append(DatasetSpec(name=ds["name"], path=ds["path"], checks=checks))
    return SuiteSpec(suite_name=d["suite_name"], datasets=datasets)
