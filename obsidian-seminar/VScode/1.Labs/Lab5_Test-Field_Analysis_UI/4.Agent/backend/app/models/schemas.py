from pydantic import BaseModel
from typing import Optional, List, Dict

class AnalysisRequest(BaseModel):
    lifetime_column: str = 'distance(km)'
    type_column: str = 'type'
    test_type_value: str = 'test'
    field_type_value: str = 'field'
    confidence_level: float = 0.95

class AnalysisResult(BaseModel):
    message: str
    report_url: Optional[str] = None
    plot_urls: Optional[List[str]] = None
    analysis_summary: Optional[Dict] = None
    error: Optional[str] = None
