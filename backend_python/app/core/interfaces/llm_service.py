from abc import ABC, abstractmethod
from app.models.diagnosis import DiagnosisResult, StitchPromptResult
from app.models.triage import FullTriageReport


class LLMService(ABC):
    """Interface for LLM processing: Diagnostic Recommendations (Stage 3) and Stitch Prompt Generation (Stage 4)."""

    @abstractmethod
    async def generate_diagnosis(self, report: FullTriageReport) -> DiagnosisResult:
        """Cross-reference triage metrics and generate natural language recommendations."""
        pass

    @abstractmethod
    async def generate_stitch_prompt(self, report: FullTriageReport, diagnosis: DiagnosisResult) -> StitchPromptResult:
        """Generate a complete, structured prompt for Google Stitch site generator."""
        pass
