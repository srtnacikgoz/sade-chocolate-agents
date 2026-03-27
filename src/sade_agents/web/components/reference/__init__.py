"""
Reference Component Library for AI Code Generation.

Bu moduldeki ornekler, UI Expert Agent'in Streamlit kod uretirken
referans olarak kullandigi "golden examples" dir.

## Purpose

AI hallucination'i minimize etmek icin production-ready Streamlit component
ornekleri saglar. Arastirmaya gore reference library %95'ten %15'e hata
oranini dusurur (6x iyilestirme).

## Kurallar

Her reference component su standartlara uyar:

1. **Type Hints**: Her parametre ve return type belirtilmis
2. **Docstring**: Google-style docstring (Args, Returns, Example)
3. **Usage Examples**: Her dosyanin sonunda AI training ornekleri
4. **No Hardcoding**: Parametreli, flexible design
5. **Sade Styling**: Minimal, clean, Sade Chocolate conventions

## Available Components

- **render_card**: Card component (title, content, icon, variant)
- **render_form**: Dynamic form (dict-based field config)
- **render_data_table**: Data table with download (DataFrame rendering)

## Usage

```python
from sade_agents.web.components.reference import render_card, render_form, render_data_table

# Card kullanimi
render_card(
    title="Analiz Tamamlandi",
    content="5 rakip, 127 urun tespit edildi",
    icon="✅",
    variant="primary"
)

# Form kullanimi
fields = [
    {"name": "name", "type": "text", "label": "Ad", "required": True}
]
data = render_form(title="Yeni Kayit", fields=fields)

# Table kullanimi
import pandas as pd
df = pd.DataFrame({"Col1": [1, 2], "Col2": [3, 4]})
render_data_table(data=df, title="Veriler", variant="compact")
```

## For AI Agents

Bu componentler AI code generation icin optimize edilmistir:

- Minimal hallucination risk (proven patterns)
- Clear parameter contracts (type hints)
- Comprehensive docstrings (AI context)
- Real-world usage examples (AI training data)

AI agent bu componentleri **aynen** kopyalayabilir veya **adapte** edebilir.
"""

from sade_agents.web.components.reference.card import render_card
from sade_agents.web.components.reference.form import render_form
from sade_agents.web.components.reference.data_table import render_data_table

__all__ = ["render_card", "render_form", "render_data_table"]
