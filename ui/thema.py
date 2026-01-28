"""
Thema en styling voor de Evacuatie Calculator
Professionele uitstraling met consistent kleurenpalet
Ondersteunt zowel light als dark mode
"""

from enum import Enum


class ThemaModus(Enum):
    """Beschikbare thema modi"""
    LIGHT = "light"
    DARK = "dark"


# Huidige thema modus (standaard light)
_huidige_modus = ThemaModus.LIGHT


# Kleuren palet - Light mode (zachter, minder plat)
KLEUREN_LIGHT = {
    'primair': '#1565C0',           # Donkerblauw - hoofdkleur
    'primair_licht': '#42A5F5',     # Lichtblauw
    'primair_donker': '#0D47A1',    # Extra donkerblauw
    'accent': '#FF6F00',            # Oranje - accent
    'accent_licht': '#FFB74D',      # Licht oranje
    'succes': '#2E7D32',            # Groen
    'succes_licht': '#A5D6A7',      # Licht groen
    'waarschuwing': '#F57C00',      # Oranje waarschuwing
    'waarschuwing_licht': '#FFE0B2', # Licht oranje
    'fout': '#C62828',              # Rood
    'fout_licht': '#FFCDD2',        # Licht rood
    'achtergrond': '#F0F4F8',       # Zacht blauwgrijs achtergrond
    'achtergrond_alt': '#E8EDF2',   # Alternerende rij kleur
    'kaart': '#FFFFFF',             # Wit voor kaarten
    'tekst': '#2D3748',             # Donkergrijs tekst (zachter dan zwart)
    'tekst_licht': '#718096',       # Middengrijs tekst
    'rand': '#CBD5E0',              # Zachtere rand kleur
}

# Kleuren palet - Dark mode
KLEUREN_DARK = {
    'primair': '#64B5F6',           # Lichter blauw voor dark mode
    'primair_licht': '#90CAF9',     # Extra licht blauw
    'primair_donker': '#1976D2',    # Donkerblauw
    'accent': '#FFB74D',            # Lichter oranje
    'accent_licht': '#FFCC80',      # Extra licht oranje
    'succes': '#81C784',            # Lichter groen
    'succes_licht': '#A5D6A7',      # Licht groen
    'waarschuwing': '#FFB74D',      # Oranje waarschuwing
    'waarschuwing_licht': '#FFE0B2', # Licht oranje
    'fout': '#EF5350',              # Lichter rood
    'fout_licht': '#FFCDD2',        # Licht rood
    'achtergrond': '#1A1A2E',       # Donkerblauw achtergrond (zachter dan puur zwart)
    'achtergrond_alt': '#252542',   # Alternerende rij kleur
    'kaart': '#16213E',             # Donkerblauw voor kaarten
    'tekst': '#E8E8E8',             # Lichtgrijs tekst (zachter dan wit)
    'tekst_licht': '#A0A0A0',       # Grijs tekst
    'rand': '#3A3A5C',              # Donkerblauwe rand
}

# Standaard KLEUREN verwijst naar huidige modus
KLEUREN = KLEUREN_LIGHT.copy()

def _genereer_stylesheet(kleuren: dict) -> str:
    """Genereer stylesheet op basis van kleurenpalet"""
    return f"""
/* ===== Algemene stijlen ===== */
QMainWindow {{
    background-color: {kleuren['achtergrond']};
}}

QWidget {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11px;
    color: {kleuren['tekst']};
}}

/* ===== Labels ===== */
QLabel {{
    color: {kleuren['tekst']};
}}

QLabel[class="titel"] {{
    font-size: 20px;
    font-weight: bold;
    color: {kleuren['primair']};
}}

QLabel[class="subtitel"] {{
    font-size: 13px;
    color: {kleuren['tekst_licht']};
}}

QLabel[class="stap"] {{
    font-size: 12px;
    font-weight: bold;
    color: {kleuren['primair']};
    padding: 6px;
    background-color: {kleuren['kaart']};
    border-bottom: 2px solid {kleuren['primair']};
}}

/* ===== GroupBox ===== */
QGroupBox {{
    font-weight: bold;
    font-size: 11px;
    color: {kleuren['primair']};
    border: 1px solid {kleuren['rand']};
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 6px;
    background-color: {kleuren['kaart']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    background-color: {kleuren['kaart']};
    color: {kleuren['primair']};
}}

/* ===== Knoppen ===== */
QPushButton {{
    background-color: {kleuren['primair']};
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
    font-size: 11px;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {kleuren['primair_licht']};
    color: #FFFFFF;
}}

QPushButton:pressed {{
    background-color: {kleuren['primair_donker']};
    color: #FFFFFF;
}}

QPushButton:disabled {{
    background-color: {kleuren['rand']};
    color: {kleuren['tekst_licht']};
}}

QPushButton[class="accent"] {{
    background-color: {kleuren['accent']};
}}

QPushButton[class="accent"]:hover {{
    background-color: {kleuren['accent_licht']};
}}

QPushButton[class="succes"] {{
    background-color: {kleuren['succes']};
}}

QPushButton[class="succes"]:hover {{
    background-color: #43A047;
}}

/* Secundaire knoppen - lichte achtergrond met gekleurde tekst */
QPushButton[class="secundair"] {{
    background-color: {kleuren['kaart']};
    color: {kleuren['primair']};
    border: 1px solid {kleuren['primair']};
}}

QPushButton[class="secundair"]:hover {{
    background-color: {kleuren['primair_licht']};
    color: #FFFFFF;
}}

QPushButton[class="secundair"]:pressed {{
    background-color: {kleuren['primair']};
    color: #FFFFFF;
}}

/* Tertiaire knoppen - subtiel met rand */
QPushButton[class="tertiair"] {{
    background-color: {kleuren['kaart']};
    color: {kleuren['tekst']};
    border: 1px solid {kleuren['rand']};
}}

QPushButton[class="tertiair"]:hover {{
    background-color: {kleuren['achtergrond_alt']};
    color: {kleuren['tekst']};
}}

/* ===== Invoervelden ===== */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {{
    border: 1px solid {kleuren['rand']};
    border-radius: 4px;
    padding: 3px 4px;
    background-color: {kleuren['kaart']};
    selection-background-color: {kleuren['primair_licht']};
    font-size: 11px;
    min-height: 18px;
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QDateEdit:focus {{
    border: 2px solid {kleuren['primair']};
}}

QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
    background-color: {kleuren['achtergrond']};
    color: {kleuren['tekst_licht']};
}}

QComboBox {{
    color: {kleuren['tekst']};
}}

QComboBox QAbstractItemView {{
    background-color: {kleuren['kaart']};
    color: {kleuren['tekst']};
    selection-background-color: {kleuren['primair']};
    selection-color: white;
    border: 1px solid {kleuren['rand']};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}

QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}

/* ===== Tabellen ===== */
QTableWidget {{
    border: 1px solid {kleuren['rand']};
    border-radius: 6px;
    background-color: {kleuren['kaart']};
    gridline-color: {kleuren['rand']};
    selection-background-color: {kleuren['primair_licht']};
    alternate-background-color: {kleuren['achtergrond_alt']};
    color: {kleuren['tekst']};
    font-size: 11px;
}}

QTableWidget::item {{
    padding: 2px 4px;
    background-color: {kleuren['kaart']};
    color: {kleuren['tekst']};
}}

QTableWidget::item:alternate {{
    background-color: {kleuren['achtergrond_alt']};
    color: {kleuren['tekst']};
}}

QTableWidget::item:selected {{
    background-color: {kleuren['primair_licht']};
    color: white;
}}

/* ComboBox in tabel */
QTableWidget QComboBox {{
    background-color: transparent;
    border: none;
    padding: 1px 2px;
    color: {kleuren['tekst']};
    font-size: 11px;
}}

QTableWidget QComboBox:hover {{
    background-color: {kleuren['achtergrond_alt']};
}}

QTableWidget QComboBox::drop-down {{
    border: none;
}}

QHeaderView::section {{
    background-color: {kleuren['primair']};
    color: white;
    font-weight: bold;
    padding: 4px 2px;
    border: none;
    font-size: 11px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 7px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 7px;
}}

/* ===== TabWidget ===== */
QTabWidget::pane {{
    border: 1px solid {kleuren['rand']};
    border-radius: 8px;
    background-color: {kleuren['kaart']};
    top: -1px;
}}

QTabBar::tab {{
    background-color: {kleuren['achtergrond']};
    border: 1px solid {kleuren['rand']};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 12px;
    margin-right: 2px;
    font-weight: bold;
    font-size: 11px;
}}

QTabBar::tab:selected {{
    background-color: {kleuren['kaart']};
    border-bottom: 2px solid {kleuren['primair']};
    color: {kleuren['primair']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {kleuren['primair_licht']};
    color: white;
}}

/* ===== ScrollArea ===== */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {kleuren['achtergrond']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {kleuren['rand']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {kleuren['tekst_licht']};
}}

/* ===== CheckBox ===== */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {kleuren['rand']};
    border-radius: 4px;
    background-color: {kleuren['kaart']};
}}

QCheckBox::indicator:checked {{
    background-color: {kleuren['primair']};
    border-color: {kleuren['primair']};
}}

/* ===== StatusBar ===== */
QStatusBar {{
    background-color: {kleuren['kaart']};
    border-top: 1px solid {kleuren['rand']};
    padding: 5px;
}}

/* ===== MenuBar ===== */
QMenuBar {{
    background-color: {kleuren['kaart']};
    border-bottom: 1px solid {kleuren['rand']};
    padding: 5px;
}}

QMenuBar::item {{
    padding: 8px 15px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {kleuren['primair_licht']};
    color: white;
}}

QMenu {{
    background-color: {kleuren['kaart']};
    border: 1px solid {kleuren['rand']};
    border-radius: 8px;
    padding: 5px;
}}

QMenu::item {{
    padding: 10px 30px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {kleuren['primair']};
    color: white;
}}

/* ===== ToolTip ===== */
QToolTip {{
    background-color: {kleuren['tekst']};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px;
}}

/* ===== SpinBox pijlen ===== */
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    background-color: {kleuren['achtergrond']};
    border: none;
    border-left: 1px solid {kleuren['rand']};
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: {kleuren['achtergrond']};
    border: none;
    border-left: 1px solid {kleuren['rand']};
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {kleuren['primair_licht']};
}}

/* ===== Frame ===== */
QFrame {{
    color: {kleuren['tekst']};
}}
"""


# Genereer stylesheets voor beide modi
STYLESHEET_LIGHT = _genereer_stylesheet(KLEUREN_LIGHT)
STYLESHEET_DARK = _genereer_stylesheet(KLEUREN_DARK)

# Standaard stylesheet (voor backwards compatibility)
STYLESHEET = STYLESHEET_LIGHT


def get_kleuren(modus: ThemaModus = None) -> dict:
    """Haal kleurenpalet op voor gegeven modus"""
    if modus is None:
        modus = _huidige_modus
    return KLEUREN_DARK if modus == ThemaModus.DARK else KLEUREN_LIGHT


def get_stylesheet(modus: ThemaModus = None) -> str:
    """Haal stylesheet op voor gegeven modus"""
    if modus is None:
        modus = _huidige_modus
    return STYLESHEET_DARK if modus == ThemaModus.DARK else STYLESHEET_LIGHT


def set_thema_modus(modus: ThemaModus):
    """Stel de huidige thema modus in"""
    global _huidige_modus, KLEUREN, STYLESHEET
    _huidige_modus = modus
    KLEUREN = get_kleuren(modus)
    STYLESHEET = get_stylesheet(modus)


def get_huidige_modus() -> ThemaModus:
    """Haal de huidige thema modus op"""
    return _huidige_modus


def toggle_thema() -> ThemaModus:
    """Wissel tussen light en dark mode"""
    nieuwe_modus = ThemaModus.DARK if _huidige_modus == ThemaModus.LIGHT else ThemaModus.LIGHT
    set_thema_modus(nieuwe_modus)
    return nieuwe_modus


def get_button_style_secundair() -> str:
    """Krijg stylesheet voor secundaire knop (outline stijl)"""
    kleuren = get_kleuren()
    return f"""
        QPushButton {{
            background-color: {kleuren['kaart']};
            color: {kleuren['primair']};
            border: 1px solid {kleuren['primair']};
            border-radius: 4px;
            padding: 5px 10px;
            font-weight: bold;
            font-size: 11px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: {kleuren['primair_licht']};
            color: #FFFFFF;
        }}
        QPushButton:pressed {{
            background-color: {kleuren['primair']};
            color: #FFFFFF;
        }}
    """


def get_button_style_tertiair() -> str:
    """Krijg stylesheet voor tertiaire knop (subtiele stijl)"""
    kleuren = get_kleuren()
    return f"""
        QPushButton {{
            background-color: {kleuren['kaart']};
            color: {kleuren['tekst']};
            border: 1px solid {kleuren['rand']};
            border-radius: 4px;
            padding: 5px 10px;
            font-weight: bold;
            font-size: 11px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            background-color: {kleuren['achtergrond_alt']};
            color: {kleuren['tekst']};
        }}
    """


# SVG icoon van een gebouw met vluchtende mensen
GEBOUW_ICOON_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <!-- Gebouw -->
  <rect x="12" y="16" width="40" height="44" fill="#1565C0" rx="2"/>

  <!-- Ramen -->
  <rect x="16" y="20" width="8" height="6" fill="#E3F2FD" rx="1"/>
  <rect x="28" y="20" width="8" height="6" fill="#E3F2FD" rx="1"/>
  <rect x="40" y="20" width="8" height="6" fill="#E3F2FD" rx="1"/>

  <rect x="16" y="30" width="8" height="6" fill="#E3F2FD" rx="1"/>
  <rect x="28" y="30" width="8" height="6" fill="#E3F2FD" rx="1"/>
  <rect x="40" y="30" width="8" height="6" fill="#E3F2FD" rx="1"/>

  <rect x="16" y="40" width="8" height="6" fill="#E3F2FD" rx="1"/>
  <rect x="28" y="40" width="8" height="6" fill="#E3F2FD" rx="1"/>
  <rect x="40" y="40" width="8" height="6" fill="#FFE0B2" rx="1"/>

  <!-- Deur -->
  <rect x="26" y="50" width="12" height="10" fill="#0D47A1" rx="1"/>

  <!-- Trap symbool -->
  <path d="M54 48 L58 48 L58 52 L62 52 L62 56 L54 56 Z" fill="#FF6F00"/>

  <!-- Pijl (evacuatie) -->
  <path d="M56 36 L62 42 L59 42 L59 46 L53 46 L53 42 L50 42 Z" fill="#2E7D32"/>
</svg>
"""

# Grote versie voor welkomstscherm
GEBOUW_ICOON_GROOT_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
  <!-- Achtergrond cirkel -->
  <circle cx="64" cy="64" r="60" fill="#E3F2FD"/>

  <!-- Gebouw -->
  <rect x="28" y="32" width="72" height="80" fill="#1565C0" rx="4"/>

  <!-- Dak -->
  <rect x="24" y="28" width="80" height="8" fill="#0D47A1" rx="2"/>

  <!-- Ramen rij 1 -->
  <rect x="34" y="40" width="12" height="10" fill="#E3F2FD" rx="2"/>
  <rect x="52" y="40" width="12" height="10" fill="#E3F2FD" rx="2"/>
  <rect x="70" y="40" width="12" height="10" fill="#E3F2FD" rx="2"/>
  <rect x="88" y="40" width="6" height="10" fill="#E3F2FD" rx="2"/>

  <!-- Ramen rij 2 -->
  <rect x="34" y="56" width="12" height="10" fill="#E3F2FD" rx="2"/>
  <rect x="52" y="56" width="12" height="10" fill="#E3F2FD" rx="2"/>
  <rect x="70" y="56" width="12" height="10" fill="#E3F2FD" rx="2"/>
  <rect x="88" y="56" width="6" height="10" fill="#E3F2FD" rx="2"/>

  <!-- Ramen rij 3 -->
  <rect x="34" y="72" width="12" height="10" fill="#E3F2FD" rx="2"/>
  <rect x="52" y="72" width="12" height="10" fill="#E3F2FD" rx="2"/>
  <rect x="70" y="72" width="12" height="10" fill="#FFE0B2" rx="2"/>
  <rect x="88" y="72" width="6" height="10" fill="#FFE0B2" rx="2"/>

  <!-- Deur -->
  <rect x="50" y="92" width="18" height="20" fill="#0D47A1" rx="2"/>
  <circle cx="64" cy="102" r="2" fill="#FFD54F"/>

  <!-- Trap symbool rechts -->
  <path d="M100 84 L108 84 L108 92 L116 92 L116 100 L108 100 L108 108 L100 108 Z" fill="#FF6F00"/>

  <!-- Evacuatie pijl -->
  <path d="M106 68 L118 80 L112 80 L112 82 L100 82 L100 80 L94 80 Z" fill="#2E7D32"/>

  <!-- Persoon symbool -->
  <circle cx="106" cy="100" r="4" fill="#2E7D32"/>
  <path d="M106 104 L106 112 M102 108 L110 108" stroke="#2E7D32" stroke-width="2" stroke-linecap="round"/>
</svg>
"""

# SVG icoon - Dark mode versie (aangepast aan nieuwe kleuren)
GEBOUW_ICOON_SVG_DARK = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <!-- Gebouw -->
  <rect x="12" y="16" width="40" height="44" fill="#64B5F6" rx="2"/>

  <!-- Ramen -->
  <rect x="16" y="20" width="8" height="6" fill="#16213E" rx="1"/>
  <rect x="28" y="20" width="8" height="6" fill="#16213E" rx="1"/>
  <rect x="40" y="20" width="8" height="6" fill="#16213E" rx="1"/>

  <rect x="16" y="30" width="8" height="6" fill="#16213E" rx="1"/>
  <rect x="28" y="30" width="8" height="6" fill="#16213E" rx="1"/>
  <rect x="40" y="30" width="8" height="6" fill="#16213E" rx="1"/>

  <rect x="16" y="40" width="8" height="6" fill="#16213E" rx="1"/>
  <rect x="28" y="40" width="8" height="6" fill="#16213E" rx="1"/>
  <rect x="40" y="40" width="8" height="6" fill="#FFB74D" rx="1"/>

  <!-- Deur -->
  <rect x="26" y="50" width="12" height="10" fill="#1976D2" rx="1"/>

  <!-- Trap symbool -->
  <path d="M54 48 L58 48 L58 52 L62 52 L62 56 L54 56 Z" fill="#FFB74D"/>

  <!-- Pijl (evacuatie) -->
  <path d="M56 36 L62 42 L59 42 L59 46 L53 46 L53 42 L50 42 Z" fill="#81C784"/>
</svg>
"""

# Grote versie voor welkomstscherm - Dark mode (aangepast aan nieuwe kleuren)
GEBOUW_ICOON_GROOT_SVG_DARK = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">
  <!-- Achtergrond cirkel -->
  <circle cx="64" cy="64" r="60" fill="#252542"/>

  <!-- Gebouw -->
  <rect x="28" y="32" width="72" height="80" fill="#64B5F6" rx="4"/>

  <!-- Dak -->
  <rect x="24" y="28" width="80" height="8" fill="#1976D2" rx="2"/>

  <!-- Ramen rij 1 -->
  <rect x="34" y="40" width="12" height="10" fill="#16213E" rx="2"/>
  <rect x="52" y="40" width="12" height="10" fill="#16213E" rx="2"/>
  <rect x="70" y="40" width="12" height="10" fill="#16213E" rx="2"/>
  <rect x="88" y="40" width="6" height="10" fill="#16213E" rx="2"/>

  <!-- Ramen rij 2 -->
  <rect x="34" y="56" width="12" height="10" fill="#16213E" rx="2"/>
  <rect x="52" y="56" width="12" height="10" fill="#16213E" rx="2"/>
  <rect x="70" y="56" width="12" height="10" fill="#16213E" rx="2"/>
  <rect x="88" y="56" width="6" height="10" fill="#16213E" rx="2"/>

  <!-- Ramen rij 3 -->
  <rect x="34" y="72" width="12" height="10" fill="#16213E" rx="2"/>
  <rect x="52" y="72" width="12" height="10" fill="#16213E" rx="2"/>
  <rect x="70" y="72" width="12" height="10" fill="#FFB74D" rx="2"/>
  <rect x="88" y="72" width="6" height="10" fill="#FFB74D" rx="2"/>

  <!-- Deur -->
  <rect x="50" y="92" width="18" height="20" fill="#1976D2" rx="2"/>
  <circle cx="64" cy="102" r="2" fill="#FFD54F"/>

  <!-- Trap symbool rechts -->
  <path d="M100 84 L108 84 L108 92 L116 92 L116 100 L108 100 L108 108 L100 108 Z" fill="#FFB74D"/>

  <!-- Evacuatie pijl -->
  <path d="M106 68 L118 80 L112 80 L112 82 L100 82 L100 80 L94 80 Z" fill="#81C784"/>

  <!-- Persoon symbool -->
  <circle cx="106" cy="100" r="4" fill="#81C784"/>
  <path d="M106 104 L106 112 M102 108 L110 108" stroke="#81C784" stroke-width="2" stroke-linecap="round"/>
</svg>
"""


def get_welkom_html(kleuren: dict = None):
    """Genereer HTML voor welkomstscherm"""
    if kleuren is None:
        kleuren = get_kleuren()
    return f"""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: {kleuren['primair']}; font-size: 28px; margin-bottom: 10px;">
            Evacuatie Doorstroom Calculator
        </h1>
        <p style="color: {kleuren['tekst_licht']}; font-size: 14px; margin-bottom: 30px;">
            Berekening van opvang- en doorstroomcapaciteit volgens BBL Art. 4.80/4.81
        </p>
    </div>
    """


def get_gebouw_icoon_svg(modus: ThemaModus = None) -> str:
    """Haal gebouw icoon SVG op, aangepast aan thema"""
    if modus is None:
        modus = _huidige_modus

    if modus == ThemaModus.DARK:
        return GEBOUW_ICOON_SVG_DARK
    return GEBOUW_ICOON_SVG


def get_gebouw_icoon_groot_svg(modus: ThemaModus = None) -> str:
    """Haal groot gebouw icoon SVG op, aangepast aan thema"""
    if modus is None:
        modus = _huidige_modus

    if modus == ThemaModus.DARK:
        return GEBOUW_ICOON_GROOT_SVG_DARK
    return GEBOUW_ICOON_GROOT_SVG
