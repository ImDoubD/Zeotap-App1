from typing import Any, Dict, List
from pydantic import BaseModel


class CombineRulesRequest(BaseModel):
    rules: List[int]
    operator: str = "AND"

class EvaluateRuleRequest(BaseModel):
    rule_id: int
    user_data: Dict[str, Any]  
