# Evacuatie Doorstroom Calculator v1.0

Desktop applicatie voor het berekenen van opvang- en doorstroomcapaciteit van trappenhuizen bij gebouwontruiming volgens het **Besluit bouwwerken leefomgeving (BBL)**.

## 📋 Overzicht

Deze applicatie helpt brandveiligheidsadviseurs bij het berekenen en toetsen van ontruimingsscenario's voor gebouwen met meerdere trappenhuizen. De berekeningen zijn gebaseerd op:

- **Besluit bouwwerken leefomgeving (BBL)** - § 4.2.11 Vluchtroutes: inrichting en capaciteit
  - Artikel 4.80: Doorstroomcapaciteit zonder opvangcapaciteit
  - Artikel 4.81: Doorstroomcapaciteit bij opvangcapaciteit
- **NEN 6089**: Bepaling van de vuurlast

Referentie: https://wetten.overheid.nl/BWBR0041297

## 🚀 Installatie

### Vereisten
- Python 3.10 of hoger
- PyQt6 voor de grafische interface

### Installatie stappen

```bash
# 1. Clone of download het project
cd evacuatie_calculator

# 2. Installeer dependencies
pip install -r requirements.txt

# 3. Start de applicatie
python main.py
```

## 🖥️ Gebruik

### Stap 1: Projectgegevens
Voer de algemene projectinformatie in:
- Projectnaam en nummer
- Scenario/omschrijving
- Gebouwconfiguratie (aantal trappen, bouwlagen)

### Stap 2: Personen per Verdieping
Voer het aantal personen per verdieping in. Het totaal wordt automatisch berekend.

### Stap 3: Trap Configuratie
Configureer elke trap met:
- Doorgang naar veilig terrein
- Type doorgang (A/B/C/D)
- Ontruimingstijd
- Per verdieping: bordesmaten, trapbreedte, etc.

### Stap 4: Resultaten
Bekijk de resultaten:
- Samenvatting tabel
- Grafiek van ontruimingsverloop
- Normtoetsing (Lid 1, 2, 3)
- Gedetailleerde tijdstaptabel

## 📊 Berekeningsformules

### Doorstroomfactoren (BBL Art. 4.80 lid 1)

| Type | Beschrijving | Factor |
|------|--------------|--------|
| b | Ruimte | 90 pers/m/min |
| c | Dubbele deur < 135° | 90 pers/m/min |
| d | Enkele deur < 135° | 110 pers/m/min |
| e | Andere doorgang ≥ 135° | 135 pers/m/min |
| l/m | Tegen vluchtrichting | 37 pers/min/deur |

### Trapdoorstroomfactoren (BBL Art. 4.80 lid 1a)

| Hoogteverschil | Factor |
|----------------|--------|
| > 1 meter | 45 pers/m/min |
| ≤ 1 meter | 90 pers/m/min |

### Opvangcapaciteit (BBL Art. 4.81 lid 4)

| Element | Capaciteit |
|---------|------------|
| Vloer/hellingbaan | 4 pers/m² |
| Trap ≤ 1,1m breed | 0,5 pers/trede |
| Trap > 1,1m breed | 0,9 pers/trede/m |

### Ontruimingstijden (BBL Art. 4.81 lid 1)

| Type vluchtroute | Max. tijd |
|------------------|-----------|
| Veiligheidsvluchtroute | 30 min |
| Extra beschermde vluchtroute | 20 min |
| Andere vluchtroute | 15 min |

### Capaciteitsberekeningen

**Doorstroomcapaciteit deur (per 0.5 min):**
```
FX = factor × breedte × 0.5
```

**Doorstroomcapaciteit trap (per 0.5 min):**
```
FY = breedte × (45 als hoogte>1m, anders 90) × 0.5
```

**Opslagcapaciteit trappenhuis:**
```
Capaciteit = bordes×4 + min(tussen×4 + trap_opslag, FY)
```

## 📁 Projectstructuur

```
evacuatie_calculator/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── models/
│   ├── constanten.py      # Constanten en enums
│   ├── trap.py            # Trap en TrapVerdieping
│   └── project.py         # Project datamodel
├── berekeningen/
│   ├── capaciteit.py      # Capaciteitsberekeningen
│   ├── simulatie.py       # Tijdstap simulatie engine
│   └── toetsing.py        # Normtoetsing
├── ui/
│   ├── hoofdscherm.py     # Main window
│   ├── personen_invoer.py # Personen invoer widget
│   ├── trap_config.py     # Trap configuratie
│   └── resultaten.py      # Resultaten weergave
└── export/
    ├── pdf_rapport.py     # PDF export
    └── excel_export.py    # Excel export
```

## 📤 Export

### PDF Rapport
Genereert een professioneel rapport met:
- Projectgegevens
- Gebouwconfiguratie
- Samenvatting per trap
- Normtoetsing resultaten
- Gedetailleerde tijdstapdata

### Excel Export
Exporteert ruwe data naar Excel met meerdere tabbladen:
- Projectgegevens
- Samenvatting
- Detail per trap
- Personen per verdieping

## ⚖️ Normtoetsing (BBL Art. 4.81)

De applicatie toetst automatisch aan drie criteria:

| Criterium | BBL Artikel | Omschrijving | Eis |
|-----------|-------------|--------------|-----|
| Lid 1 | 4.81 lid 1 | Volledige ontruiming | Binnen 15/20/30 min |
| Lid 2 | 4.81 lid 2 | Compartiment ontruiming | < 1 min |
| Lid 3 | 4.81 lid 3 | Verlaten verdieping | < 3,5 min |

## 🔧 Ontwikkeling

### Tests uitvoeren
```bash
cd tests
python -m pytest
```

### Code stijl
Het project volgt PEP 8 richtlijnen. Gebruik `black` voor automatische formattering:
```bash
black .
```

## 📝 Licentie

© 2024 - Alle rechten voorbehouden

## 🤝 Bijdragen

Bijdragen zijn welkom! Open een issue of pull request voor:
- Bug fixes
- Nieuwe features
- Documentatie verbeteringen
