"""
Sade Chocolate - Product Launch Crew.

Yeni urun gelistirme workflow'u:
Alchemist (recete) -> Narrator (hikaye) -> Curator (etiket) -> Perfectionist (denetim)
"""

import time
from crewai import Crew, Process

from sade_agents.agents import (
    AlchemistAgent,
    NarratorAgent,
    CuratorAgent,
    PerfectionistAgent,
)
from sade_agents.crews.base_crew import create_task_with_context
from sade_agents.models import ProductLaunchInput, ProductLaunchOutput


class ProductLaunchCrew:
    """
    Urun lansmani workflow'u.

    Pipeline: Alchemist -> Narrator -> Curator -> Perfectionist
    Kullanim: Yeni lezzet gelistirme, receteden onaylanmis etikete

    Agents:
    - Alchemist: Recete ve lezzet profili olusturur
    - Narrator: Urun hikayesi, caption, kutu notu yazar
    - Curator: Etiket gorseli tasarlar
    - Perfectionist: Tum ciktilari marka tutarliligi icin denetler
    """

    def __init__(self) -> None:
        """Agent'lari olusturur."""
        self.alchemist = AlchemistAgent()
        self.narrator = NarratorAgent()
        self.curator = CuratorAgent()
        self.perfectionist = PerfectionistAgent()

    def _create_tasks(self, inputs: ProductLaunchInput) -> list:
        """Task zinciri olusturur, context bagimliliklari ile."""
        # Task 1: Alchemist - Recete olustur
        recipe_task = create_task_with_context(
            description=f"""
Yeni cikolata recetesi olustur: {inputs.flavor_concept}

Hedef kitle: {inputs.target_audience}
Fiyat araligi: {inputs.price_range[0]}-{inputs.price_range[1]} TL

Cikti formati:
- Lezzet profili (tatli/mayhos/aci dengesi)
- Ana malzemeler listesi
- Ozel teknik notlar (temperleme, kakao orani vs.)
- Tavsiye gramaj ve sunumu
            """,
            expected_output="JSON formatinda recete: flavor_profile, ingredients, technical_notes, serving_suggestion",
            agent=self.alchemist,
        )

        # Task 2: Narrator - Hikaye yaz (receteye bagli)
        story_task = create_task_with_context(
            description=f"""
Olusturulan recete icin 'Sessiz Luks' tonunda icerikler yaz:

1. Etiket Hikayesi - urun arkasina (2-3 cumle)
2. Instagram Caption - sosyal medya postu
3. Kutu Ici Not - hediye karti

Kurallar:
- Emoji YASAK
- "Hemen Al", "Kacirma" gibi ifadeler YASAK
- Sofistike, understated ton
- Monocle/Kinfolk editoru gibi
            """,
            expected_output="JSON: etiket_hikayesi, instagram_caption, kutu_notu",
            agent=self.narrator,
            context=[recipe_task],
        )

        # Task 3: Curator - Etiket tasarla (recete + hikayeye bagli)
        label_task = create_task_with_context(
            description=f"""
Recete ve hikaye bilgilerini kullanarak etiket gorseli tasarla.

Urun: {inputs.flavor_concept}

Stil kurallari:
- Quiet Luxury estetigi
- Cormorant Garamond + Outfit tipografi
- Dark Chocolate/Cream Beige/Muted Gold renk paleti
- 3:4 aspect ratio, 2K res
- Maksimum 25 karakter urun adi
            """,
            expected_output="Olusturulan etiket dosya yolu (PNG)",
            agent=self.curator,
            context=[recipe_task, story_task],
        )

        tasks = [recipe_task, story_task, label_task]

        # Task 4 (optional): Perfectionist - Denetim
        if inputs.include_audit:
            audit_task = create_task_with_context(
                description="""
Olusturulan tum ciktilari marka tutarliligi icin denetle:

1. Hikaye metinlerini kontrol et (ton, yasak kelimeler)
2. Etiket uyumunu degerlendir (renk, tipografi)

Her cikti icin AuditResult formati kullan.
                """,
                expected_output="AuditResult JSON: overall_score, verdict, issues, suggestions",
                agent=self.perfectionist,
                context=[story_task, label_task],
            )
            tasks.append(audit_task)

        return tasks

    def kickoff(self, inputs: dict) -> ProductLaunchOutput:
        """
        Product launch workflow'unu calistirir.

        Args:
            inputs: ProductLaunchInput field'lari

        Returns:
            ProductLaunchOutput with recipe, story, label_paths, audit
        """
        validated_inputs = ProductLaunchInput(**inputs)
        tasks = self._create_tasks(validated_inputs)

        agents = [self.alchemist, self.narrator, self.curator]
        if validated_inputs.include_audit:
            agents.append(self.perfectionist)

        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        start_time = time.time()
        result = crew.kickoff(inputs=inputs)
        elapsed = time.time() - start_time

        # Parse result into structured output
        # Note: In production, parse actual CrewAI output
        return ProductLaunchOutput(
            recipe={"raw_output": str(result)},
            story={"raw_output": str(result)},
            label_paths=[],  # Populated by Curator
            audit=None,  # Populated by Perfectionist if include_audit
            execution_time_seconds=elapsed,
        )


__all__ = ["ProductLaunchCrew"]
