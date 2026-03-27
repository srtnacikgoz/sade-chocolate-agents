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
Fiyat araligi: {inputs.price_range_min}-{inputs.price_range_max} TL

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
            inputs: ProductLaunchInput field'lari (scalar degerler)

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

        # Input Sanitization: CrewAI tuple/list sevmez, sadece str/float/int/bool
        # Tuple veya List gelirse string'e cevir
        crewai_inputs = {}
        for k, v in inputs.items():
            if isinstance(v, (list, tuple)):
                # Tuple ise (100, 200) -> "100-200" formatina cevir (ozel mantik)
                if k == "price_range" and len(v) == 2:
                     crewai_inputs[k] = f"{v[0]}-{v[1]}"
                else:
                     crewai_inputs[k] = str(v)
            else:
                crewai_inputs[k] = v
        
        # Explicit type casting for known fields
        crewai_inputs["flavor_concept"] = str(inputs.get("flavor_concept", ""))
        crewai_inputs["target_audience"] = str(inputs.get("target_audience", ""))
        crewai_inputs["price_range_min"] = float(inputs.get("price_range_min", 100.0))
        crewai_inputs["price_range_max"] = float(inputs.get("price_range_max", 200.0))
        crewai_inputs["include_audit"] = bool(inputs.get("include_audit", True))

        result = crew.kickoff(inputs=crewai_inputs)
        elapsed = time.time() - start_time

        return ProductLaunchOutput(
            recipe={"raw_output": str(result)},
            story={"raw_output": str(result)},
            label_paths=[],
            audit=None,
            execution_time_seconds=elapsed,
        )


__all__ = ["ProductLaunchCrew"]
