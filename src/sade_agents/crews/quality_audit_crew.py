"""
Sade Chocolate - Quality Audit Crew.

Kalite denetimi workflow'u:
Perfectionist (denetim)

Tek agent ile bagimsiz icerik denetimi yapar.
"""

import time
from crewai import Crew, Process

from sade_agents.agents import PerfectionistAgent
from sade_agents.crews.base_crew import create_task_with_context
from sade_agents.models import QualityAuditInput, QualityAuditOutput, AUDIT_CRITERIA_BY_TYPE


class QualityAuditCrew:
    """
    Kalite denetimi workflow'u.

    Pipeline: Perfectionist (single agent)
    Kullanim: Herhangi bir icerigin bagimsiz denetimi

    Agents:
    - Perfectionist: Marka tutarliligi ve kalite kontrolu
    """

    def __init__(self) -> None:
        """Agent'lari olusturur."""
        self.perfectionist = PerfectionistAgent()

    def _create_tasks(self, inputs: QualityAuditInput) -> list:
        """Task olusturur, icerik turune gore kriterler ile."""
        # Get threshold for content type
        threshold = AUDIT_CRITERIA_BY_TYPE.get(inputs.content_type, {}).get("threshold", 75)

        audit_task = create_task_with_context(
            description=f"""
Icerik kalite denetimi yap:

Icerik: {inputs.content}

Icerik Turu: {inputs.content_type}
Kaynak Agent: {inputs.source_agent}
Esik Degeri: {threshold}

Denetim kriterleri:
1. Ton uyumu - 'Sessiz Luks' tonunda mi?
2. Kelime kullanimi - Yasak kelimeler var mi?
3. Yapi - Format ve uzunluk uygun mu?
4. Marka tutarliligi - Sade estetigine uyuyor mu?

Cikti formati (AuditResult):
- content_type: Icerik turu
- source_agent: Kaynak agent
- overall_score: 0-100 arasi puan
- tone_score: Ton puani
- vocabulary_score: Kelime puani
- structure_score: Yapi puani
- verdict: onay/revizyon/ret
- issues: Tespit edilen sorunlar listesi
- suggestions: Iyilestirme onerileri
- summary_tr: Turkce ozet
            """,
            expected_output="AuditResult JSON with all fields",
            agent=self.perfectionist,
        )

        return [audit_task]

    def kickoff(self, inputs: dict) -> QualityAuditOutput:
        """
        Quality audit workflow'unu calistirir.

        Args:
            inputs: QualityAuditInput field'lari

        Returns:
            QualityAuditOutput with audit_result, passed, execution_time
        """
        validated_inputs = QualityAuditInput(**inputs)
        tasks = self._create_tasks(validated_inputs)

        crew = Crew(
            agents=[self.perfectionist],
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        start_time = time.time()
        result = crew.kickoff(inputs=inputs)
        elapsed = time.time() - start_time

        # Get threshold for pass/fail determination
        threshold = AUDIT_CRITERIA_BY_TYPE.get(validated_inputs.content_type, {}).get("threshold", 75)

        # Parse result into structured output
        # Note: In production, parse actual CrewAI output into AuditResult
        from sade_agents.models import AuditResult

        # Create placeholder audit result
        # In production, this would parse the actual LLM response
        audit_result = AuditResult(
            content_type=validated_inputs.content_type,
            source_agent=validated_inputs.source_agent,
            overall_score=0,  # Would be parsed from result
            tone_score=0,
            vocabulary_score=0,
            structure_score=0,
            verdict="revizyon",
            issues=[],
            suggestions=[],
            summary_tr=str(result),
        )

        return QualityAuditOutput(
            audit_result=audit_result,
            passed=audit_result.overall_score >= threshold,
            execution_time_seconds=elapsed,
        )


__all__ = ["QualityAuditCrew"]
