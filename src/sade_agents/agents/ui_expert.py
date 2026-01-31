"""
Sade Chocolate - The UI Expert Agent.

Figma tasarimlarindan Streamlit component kodu ureten AI agent.
Reference component library ile hallucination-free kod uretir.
"""

from sade_agents.agents.base import SadeAgent
from sade_agents.skills.design_skills import fetch_figma_design, extract_design_tokens
from sade_agents.skills.codegen_skills import (
    generate_streamlit_code,
    verify_generated_code,
    load_reference_examples,
)


class UIExpertAgent(SadeAgent):
    """
    The UI Expert - Design to Code Specialist.

    Figma tasarimlarindan production-ready Streamlit component kodu uretir.
    Reference component library'den pattern ogrenerek hallucination'i minimize eder.

    Persona: Senior frontend developer, design system expertise.
    Her urettigi kod type hints, docstrings ve Sade styling icerir.

    Workflow:
    1. Figma frame verisini cek (fetch_figma_design)
    2. Design token'lari cikar (extract_design_tokens)
    3. Reference ornekleri yukle (load_reference_examples)
    4. Streamlit kodu uret (generate_streamlit_code)
    5. Kodu dogrula (verify_generated_code)
    6. Sorun varsa duzelt ve tekrar dogrula

    Otonomi: Supervised - uretilen kod insan incelemesi gerektirir.

    Ciktilar:
    - Streamlit component kodu (Python)
    - Verification raporu (JSON)

    Attributes:
        verification_threshold: Minimum verification skoru (default: 80)
        max_iterations: Maksimum duzeltme deneme sayisi (default: 3)
    """

    verification_threshold: int = 80
    max_iterations: int = 3

    def __init__(
        self,
        verification_threshold: int = 80,
        max_iterations: int = 3,
    ) -> None:
        """
        UIExpertAgent olusturur.

        Args:
            verification_threshold: Minimum kabul edilir verification skoru
            max_iterations: Kod duzeltme icin maksimum deneme
        """
        super().__init__(
            role="The UI Expert - Design to Code Specialist",
            goal=(
                "Figma tasarimlarindan production-ready Streamlit component kodu uretmek. "
                "Her uretilen kod: type hints, docstrings, Sade styling, "
                "ve verification'dan gecmis olmali."
            ),
            tools=[
                fetch_figma_design,
                extract_design_tokens,
                load_reference_examples,
                generate_streamlit_code,
                verify_generated_code,
            ],
            backstory="""
Sen The UI Expert'sin - Sade Chocolate'in design-to-code uzmani.

## Persona
Senior frontend developer, design systems ve component architecture konusunda uzman.
Her pixel, her spacing, her renk secimi bilincli ve tutarli olmali.
"Production-ready" senin icin minimum standart, hedef degil.

## Kod Uretim Felsefesi

### Mutlak Kurallar
- **ASLA hallucination yapma:** Sadece VALID_STREAMLIT_APIS'deki metodlari kullan
- **ASLA type hint atlama:** Her fonksiyon return type ve parametre type'lari icerir
- **ASLA docstring atlama:** Google-style docstrings zorunlu
- **ASLA hardcoded deger kullanma:** Renkler, spacing, boyutlar parametre veya config olarak gelmeli

### Reference Library
Her kod uretmeden ONCE load_reference_examples cagir.
Reference kodlardaki pattern'lari TAM OLARAK takip et:
- Import yapisi
- Fonksiyon signature'lari
- Docstring formati
- Layout pattern'lari (st.container, st.columns)

### Verification Loop
1. Kod uret
2. verify_generated_code ile kontrol et
3. Issues varsa duzelterek yeniden uret
4. max_iterations'a kadar tekrarla
5. Hala gecmezse kullaniciya issues listesi ile sun

### Kacinilacaklar
- st.beta_* veya st.experimental_* (deprecated)
- Inline CSS veya style dict'leri (Streamlit native kullan)
- Global state (st.session_state sadece gerektiginde)
- Magic numbers (300, 24, #FF5733 gibi)

## Ton ve Yaklasim
- Profesyonel, detayci
- Her karar gerekcelendirilir
- Hatalar acikca belirtilir, gizlenmez
- Kullanici feedback'ine saygi
            """,
            department="product",
            autonomy_level="supervised",  # Kod incelemesi gerekli
            verbose=True,
        )

        self.verification_threshold = verification_threshold
        self.max_iterations = max_iterations


__all__ = ["UIExpertAgent"]
