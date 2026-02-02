"""
Evacuatie Calculator - Streamlit Web Applicatie
BBL Art. 4.80/4.81 - Opvang- en doorstroomcapaciteit trappenhuizen

Volledig werkende web versie van de desktop applicatie.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import json
import io

# Import bestaande modules
from models.constanten import (
    DoorgangType, LocatieType, VerlaatTijdType,
    ONTRUIMINGSTIJDEN, VERLAAT_TIJDEN,
    STANDAARD_HOOGTEVERSCHIL, STANDAARD_TRAPBREEDTE,
    STANDAARD_AANTAL_TREDEN, STANDAARD_BORDES_OPP,
    STANDAARD_TUSSENBORDES_OPP, STANDAARD_DOORGANG_BREEDTE,
)
from models.trap import Trap, TrapVerdieping
from models.project import Project, Verdieping
from berekeningen.simulatie import SimulatieEngine, simuleer_alle_trappen
from berekeningen.toetsing import toets_alle_resultaten, ToetsStatus

# Pagina configuratie
st.set_page_config(
    page_title="Evacuatie Calculator - BBL 4.80/4.81",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS voor professionele uitstraling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1565C0, #0D47A1);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1565C0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e7f3ff;
        border: 1px solid #b8daff;
        border-left: 4px solid #1565C0;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    div[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
    }
    .step {
        flex: 1;
        text-align: center;
        padding: 0.5rem;
        border-bottom: 3px solid #e0e0e0;
    }
    .step.active {
        border-bottom-color: #1565C0;
        font-weight: bold;
    }
    .step.completed {
        border-bottom-color: #28a745;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialiseer session state variabelen"""
    if 'stap' not in st.session_state:
        st.session_state.stap = 1

    if 'project' not in st.session_state:
        st.session_state.project = {
            'projectnaam': 'Nieuw Project',
            'datum': date.today(),
            'aantal_trappen': 1,
            'aantal_bouwlagen': 10,
            'laagste_verdieping': 0,
            'voorportalen': False,
        }

    if 'personen' not in st.session_state:
        st.session_state.personen = {}

    if 'trappen' not in st.session_state:
        st.session_state.trappen = {}

    if 'resultaten' not in st.session_state:
        st.session_state.resultaten = None

    if 'toetsingen' not in st.session_state:
        st.session_state.toetsingen = None


def render_header():
    """Render de header met titel en stappen indicator"""
    st.markdown("""
    <div class="main-header">
        <h1>🏢 Evacuatie Calculator</h1>
        <p>BBL Art. 4.80/4.81 - Opvang- en doorstroomcapaciteit trappenhuizen</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render de sidebar met navigatie"""
    with st.sidebar:
        st.markdown("### 📋 Navigatie")

        stappen = ["Project", "Personen", "Trappen", "Resultaten"]

        for i, stap_naam in enumerate(stappen, 1):
            if i < st.session_state.stap:
                icon = "✅"
            elif i == st.session_state.stap:
                icon = "▶️"
            else:
                icon = "⬜"

            if st.button(f"{icon} {i}. {stap_naam}", key=f"nav_{i}",
                        disabled=(i > st.session_state.stap + 1),
                        width="stretch"):
                st.session_state.stap = i
                st.rerun()

        st.markdown("---")
        st.markdown("### ℹ️ BBL Referentie")
        st.markdown("""
        - **Art. 4.80**: Doorstroomcapaciteit
        - **Art. 4.81**: Opvangcapaciteit
        - **Lid 1**: Ontruimingstijd (15/20/30 min)
        - **Lid 2**: Compartiment < 1 min
        - **Lid 3**: Verdieping < 3,5 min
        """)

        st.markdown("---")
        st.markdown("### 📥 Project")

        # Download project als JSON
        if st.button("💾 Project opslaan", width="stretch"):
            project_data = {
                'project': st.session_state.project,
                'personen': st.session_state.personen,
                'trappen': st.session_state.trappen,
            }
            # Convert date to string
            project_data['project']['datum'] = str(project_data['project']['datum'])

            json_str = json.dumps(project_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_str,
                file_name=f"{st.session_state.project['projectnaam']}.json",
                mime="application/json",
                width="stretch"
            )

        # Upload project
        uploaded_file = st.file_uploader("📂 Project laden", type=['json'])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                st.session_state.project = data['project']
                st.session_state.project['datum'] = date.fromisoformat(data['project']['datum'])
                st.session_state.personen = data.get('personen', {})
                st.session_state.trappen = data.get('trappen', {})
                st.success("Project geladen!")
                st.rerun()
            except Exception as e:
                st.error(f"Fout bij laden: {e}")


def render_stap1_project():
    """Render stap 1: Projectgegevens"""
    st.markdown("## 📁 Stap 1: Projectgegevens")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Projectinformatie")

        st.session_state.project['projectnaam'] = st.text_input(
            "Projectnaam",
            value=st.session_state.project['projectnaam'],
            placeholder="Bijv. Kantoorgebouw Amsterdam"
        )

        st.session_state.project['datum'] = st.date_input(
            "Datum berekeningen",
            value=st.session_state.project['datum']
        )

    with col2:
        st.markdown("### Gebouwconfiguratie")

        st.session_state.project['aantal_trappen'] = st.number_input(
            "Aantal trappenhuizen",
            min_value=1,
            max_value=10,
            value=st.session_state.project['aantal_trappen'],
            help="Aantal trappenhuizen in het gebouw"
        )

        st.session_state.project['aantal_bouwlagen'] = st.number_input(
            "Aantal bouwlagen",
            min_value=1,
            max_value=60,
            value=st.session_state.project['aantal_bouwlagen'],
            help="Totaal aantal bouwlagen (inclusief begane grond)"
        )

        st.session_state.project['laagste_verdieping'] = st.number_input(
            "Laagste verdieping",
            min_value=-10,
            max_value=0,
            value=st.session_state.project['laagste_verdieping'],
            help="0 = begane grond, -1 = kelder"
        )

        st.session_state.project['voorportalen'] = st.checkbox(
            "Voorportalen aanwezig",
            value=st.session_state.project['voorportalen'],
            help="Zijn er voorportalen tussen verdieping en trappenhuis?"
        )

    # Info box
    hoogste = st.session_state.project['laagste_verdieping'] + st.session_state.project['aantal_bouwlagen'] - 1
    st.markdown(f"""
    <div class="info-box">
        <strong>Samenvatting:</strong><br>
        Verdiepingen: {st.session_state.project['laagste_verdieping']} t/m {hoogste}<br>
        Aantal trappenhuizen: {st.session_state.project['aantal_trappen']}
    </div>
    """, unsafe_allow_html=True)

    # Navigatie
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("Volgende ➡️", type="primary", width="stretch"):
            # Initialiseer personen als nodig
            laagste = st.session_state.project['laagste_verdieping']
            hoogste = laagste + st.session_state.project['aantal_bouwlagen'] - 1
            for v in range(hoogste, laagste - 1, -1):
                if str(v) not in st.session_state.personen:
                    st.session_state.personen[str(v)] = 0

            st.session_state.stap = 2
            st.rerun()


def render_stap2_personen():
    """Render stap 2: Personen per verdieping"""
    st.markdown("## 👥 Stap 2: Personen per Verdieping")

    laagste = st.session_state.project['laagste_verdieping']
    hoogste = laagste + st.session_state.project['aantal_bouwlagen'] - 1

    # Initialiseer reset counter als die niet bestaat
    if 'personen_reset_counter' not in st.session_state:
        st.session_state.personen_reset_counter = 0

    st.markdown("""
    <div class="info-box">
        Voer het aantal personen in per verdieping.
        De begane grond (verdieping 0) telt meestal niet mee omdat mensen daar direct naar buiten kunnen.
    </div>
    """, unsafe_allow_html=True)

    # Snelle invoer opties
    st.markdown("### ⚡ Snelle invoer")
    col1, col2, col3 = st.columns(3)

    with col1:
        default_personen = st.number_input("Standaard per verdieping", min_value=0, value=50, key="default_pers")
    with col2:
        if st.button("Toepassen op alle verdiepingen"):
            for v in range(hoogste, laagste - 1, -1):
                if v != 0:  # Skip begane grond
                    st.session_state.personen[str(v)] = default_personen
            st.session_state.personen_reset_counter += 1
            st.rerun()
    with col3:
        if st.button("Reset naar 0"):
            for v in range(hoogste, laagste - 1, -1):
                st.session_state.personen[str(v)] = 0
            st.session_state.personen_reset_counter += 1
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Personen per verdieping")

    # Maak kolommen voor invoer
    cols = st.columns(4)

    # Gebruik counter in key zodat widgets opnieuw worden aangemaakt na reset
    counter = st.session_state.personen_reset_counter

    for i, v in enumerate(range(hoogste, laagste - 1, -1)):
        col_idx = i % 4
        with cols[col_idx]:
            label = f"Verdieping {v}" if v != 0 else "Begane grond (0)"
            st.session_state.personen[str(v)] = st.number_input(
                label,
                min_value=0,
                max_value=1000,
                value=st.session_state.personen.get(str(v), 0),
                key=f"pers_{v}_{counter}"
            )

    # Totaal
    totaal = sum(st.session_state.personen.values())
    st.markdown(f"""
    <div class="info-box">
        <strong>Totaal aantal personen: {totaal}</strong>
    </div>
    """, unsafe_allow_html=True)

    # Navigatie
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Terug", width="stretch"):
            st.session_state.stap = 1
            st.rerun()
    with col3:
        if st.button("Volgende ➡️", type="primary", width="stretch"):
            if totaal == 0:
                st.warning("Voer minimaal 1 persoon in!")
            else:
                # Initialiseer trappen
                init_trappen()
                st.session_state.stap = 3
                st.rerun()


def init_trappen():
    """Initialiseer trap configuratie"""
    trap_letters = "ABCDEFGHIJ"
    laagste = st.session_state.project['laagste_verdieping']
    hoogste = laagste + st.session_state.project['aantal_bouwlagen'] - 1

    for i in range(st.session_state.project['aantal_trappen']):
        letter = trap_letters[i] if i < len(trap_letters) else str(i + 1)
        trap_key = f"Trap {letter}"

        if trap_key not in st.session_state.trappen:
            st.session_state.trappen[trap_key] = {
                'locatie': 'BESCHERMD',
                'verlaat_tijd': 'STANDAARD',
                'doorgang_uitgang': 0.9,
                'type_uitgang': 'ENKELE_DEUR_LT135',
                'verdiepingen': {}
            }

            # Initialiseer verdiepingen
            for v in range(hoogste, laagste - 1, -1):
                st.session_state.trappen[trap_key]['verdiepingen'][str(v)] = {
                    'doorgang_trap': STANDAARD_DOORGANG_BREEDTE,
                    'type_doorgang': 'ENKELE_DEUR_LT135',
                    'bordes': STANDAARD_BORDES_OPP,
                    'tussenbordes': STANDAARD_TUSSENBORDES_OPP,
                    'hoogteverschil': STANDAARD_HOOGTEVERSCHIL,
                    'trapbreedte': STANDAARD_TRAPBREEDTE,
                    'treden': STANDAARD_AANTAL_TREDEN,
                }


def render_stap3_trappen():
    """Render stap 3: Trap configuratie"""
    st.markdown("## 🚪 Stap 3: Trap Configuratie")

    trap_namen = list(st.session_state.trappen.keys())

    if not trap_namen:
        init_trappen()
        trap_namen = list(st.session_state.trappen.keys())

    # Selecteer trap
    geselecteerde_trap = st.selectbox(
        "Selecteer trappenhuis",
        trap_namen,
        key="trap_select"
    )

    trap_data = st.session_state.trappen[geselecteerde_trap]

    # Trap algemeen
    st.markdown("### 🏢 Trappenhuis algemeen")
    col1, col2 = st.columns(2)

    with col1:
        locatie_opties = {
            'VEILIGHEIDSVLUCHTROUTE': 'Veiligheidsvluchtroute (30 min)',
            'EXTRA_BESCHERMD': 'Extra beschermde vluchtroute (20 min)',
            'BESCHERMD': 'Beschermde vluchtroute (15 min)',
        }
        trap_data['locatie'] = st.selectbox(
            "Type vluchtroute",
            list(locatie_opties.keys()),
            format_func=lambda x: locatie_opties[x],
            index=list(locatie_opties.keys()).index(trap_data.get('locatie', 'BESCHERMD')),
            key=f"locatie_{geselecteerde_trap}"
        )

        verlaat_opties = {
            'STANDAARD': 'Standaard (3,5 min)',
            'VERLENGD': 'Verlengd (6 min) - WBDBO>=30 + R200',
        }
        trap_data['verlaat_tijd'] = st.selectbox(
            "Max tijd verlaten verdieping (BBL 4.81 lid 3)",
            list(verlaat_opties.keys()),
            format_func=lambda x: verlaat_opties[x],
            index=list(verlaat_opties.keys()).index(trap_data.get('verlaat_tijd', 'STANDAARD')),
            key=f"verlaat_{geselecteerde_trap}"
        )

    with col2:
        trap_data['doorgang_uitgang'] = st.number_input(
            "Breedte uitgang trappenhuis (m)",
            min_value=0.5,
            max_value=5.0,
            value=float(trap_data.get('doorgang_uitgang', 0.9)),
            step=0.05,
            key=f"uitgang_{geselecteerde_trap}"
        )

        uitgang_opties = {
            'ENKELE_DEUR_LT135': 'Enkele deur < 135° (110 p/m/min)',
            'DUBBELE_DEUR_LT135': 'Dubbele deur < 135° (90 p/m/min)',
            'ANDERE_DOORGANG': 'Andere doorgang ≥ 135° (135 p/m/min)',
        }
        trap_data['type_uitgang'] = st.selectbox(
            "Type uitgang",
            list(uitgang_opties.keys()),
            format_func=lambda x: uitgang_opties[x],
            index=list(uitgang_opties.keys()).index(trap_data.get('type_uitgang', 'ENKELE_DEUR_LT135')),
            key=f"type_uitgang_{geselecteerde_trap}"
        )

    st.markdown("---")
    st.markdown("### 📐 Verdieping configuratie")

    # Kopieer naar alle functie
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("*Tip: Configureer één verdieping en kopieer naar alle andere.*")
    with col2:
        bron_verd = st.selectbox(
            "Kopieer van verdieping",
            list(trap_data['verdiepingen'].keys()),
            key=f"bron_verd_{geselecteerde_trap}"
        )
        if st.button("📋 Kopieer naar alle", key=f"kopieer_{geselecteerde_trap}"):
            bron_data = trap_data['verdiepingen'][bron_verd]
            for v in trap_data['verdiepingen']:
                if v != bron_verd:
                    trap_data['verdiepingen'][v] = bron_data.copy()
            st.success("Gekopieerd!")
            st.rerun()

    # Verdieping selectie
    geselecteerde_verd = st.selectbox(
        "Selecteer verdieping",
        list(trap_data['verdiepingen'].keys()),
        format_func=lambda x: f"Verdieping {x}" if x != "0" else "Begane grond (0)",
        key=f"verd_select_{geselecteerde_trap}"
    )

    verd_data = trap_data['verdiepingen'][geselecteerde_verd]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Toegang tot trap**")
        verd_data['doorgang_trap'] = st.number_input(
            "Breedte toegangsdeur (m)",
            min_value=0.5,
            max_value=3.0,
            value=float(verd_data.get('doorgang_trap', STANDAARD_DOORGANG_BREEDTE)),
            step=0.05,
            key=f"doorgang_{geselecteerde_trap}_{geselecteerde_verd}"
        )

        doorgang_opties = {
            'ENKELE_DEUR_LT135': 'Enkele deur < 135°',
            'DUBBELE_DEUR_LT135': 'Dubbele deur < 135°',
            'ANDERE_DOORGANG': 'Andere doorgang ≥ 135°',
        }
        verd_data['type_doorgang'] = st.selectbox(
            "Type toegangsdeur",
            list(doorgang_opties.keys()),
            format_func=lambda x: doorgang_opties[x],
            index=list(doorgang_opties.keys()).index(verd_data.get('type_doorgang', 'ENKELE_DEUR_LT135')),
            key=f"type_{geselecteerde_trap}_{geselecteerde_verd}"
        )

    with col2:
        st.markdown("**Trappenhuis**")
        verd_data['trapbreedte'] = st.number_input(
            "Breedte trap (m)",
            min_value=0.8,
            max_value=3.0,
            value=float(verd_data.get('trapbreedte', STANDAARD_TRAPBREEDTE)),
            step=0.05,
            key=f"trapbr_{geselecteerde_trap}_{geselecteerde_verd}"
        )

        verd_data['treden'] = st.number_input(
            "Aantal treden",
            min_value=10,
            max_value=40,
            value=int(verd_data.get('treden', STANDAARD_AANTAL_TREDEN)),
            key=f"treden_{geselecteerde_trap}_{geselecteerde_verd}"
        )

        verd_data['hoogteverschil'] = st.number_input(
            "Hoogteverschil (m)",
            min_value=2.1,
            max_value=4.0,
            value=float(verd_data.get('hoogteverschil', STANDAARD_HOOGTEVERSCHIL)),
            step=0.1,
            key=f"hoogte_{geselecteerde_trap}_{geselecteerde_verd}"
        )

    with col3:
        st.markdown("**Bordessen**")
        verd_data['bordes'] = st.number_input(
            "Oppervlakte bordes (m²)",
            min_value=0.0,
            max_value=20.0,
            value=float(verd_data.get('bordes', STANDAARD_BORDES_OPP)),
            step=0.5,
            key=f"bordes_{geselecteerde_trap}_{geselecteerde_verd}"
        )

        verd_data['tussenbordes'] = st.number_input(
            "Oppervlakte tussenbordessen (m²)",
            min_value=0.0,
            max_value=20.0,
            value=float(verd_data.get('tussenbordes', STANDAARD_TUSSENBORDES_OPP)),
            step=0.5,
            key=f"tussenbordes_{geselecteerde_trap}_{geselecteerde_verd}"
        )

    # Update trap data
    st.session_state.trappen[geselecteerde_trap] = trap_data

    # Navigatie
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Terug", width="stretch"):
            st.session_state.stap = 2
            st.rerun()
    with col3:
        if st.button("🧮 Bereken", type="primary", width="stretch"):
            with st.spinner("Berekening uitvoeren..."):
                voer_berekening_uit()
            st.session_state.stap = 4
            st.rerun()


def voer_berekening_uit():
    """Voer de simulatie en toetsing uit"""
    # Bouw Project object
    project = Project(
        projectnaam=st.session_state.project['projectnaam'],
        aantal_trappen=st.session_state.project['aantal_trappen'],
        aantal_bouwlagen=st.session_state.project['aantal_bouwlagen'],
        laagste_verdieping=st.session_state.project['laagste_verdieping'],
        voorportalen_aanwezig=st.session_state.project['voorportalen'],
    )

    # Update personen
    for v in project.verdiepingen:
        v.aantal_personen = st.session_state.personen.get(str(v.nummer), 0)

    # Bouw Trap objecten
    project.trappen = []

    for trap_naam, trap_data in st.session_state.trappen.items():
        # Bepaal locatie type
        locatie_map = {
            'VEILIGHEIDSVLUCHTROUTE': LocatieType.VEILIGHEIDSVLUCHTROUTE,
            'EXTRA_BESCHERMD': LocatieType.EXTRA_BESCHERMD,
            'BESCHERMD': LocatieType.BESCHERMD,
        }
        locatie = locatie_map.get(trap_data['locatie'], LocatieType.BESCHERMD)

        verlaat_map = {
            'STANDAARD': VerlaatTijdType.STANDAARD,
            'VERLENGD': VerlaatTijdType.VERLENGD,
        }
        verlaat_tijd = verlaat_map.get(trap_data['verlaat_tijd'], VerlaatTijdType.STANDAARD)

        uitgang_map = {
            'ENKELE_DEUR_LT135': DoorgangType.ENKELE_DEUR_LT135,
            'DUBBELE_DEUR_LT135': DoorgangType.DUBBELE_DEUR_LT135,
            'ANDERE_DOORGANG': DoorgangType.ANDERE_DOORGANG,
        }
        type_uitgang = uitgang_map.get(trap_data['type_uitgang'], DoorgangType.ENKELE_DEUR_LT135)

        trap = Trap(
            aanduiding=trap_naam,
            locatie=locatie,
            verlaat_tijd_type=verlaat_tijd,
            doorgang_uitgang_m=trap_data['doorgang_uitgang'],
            type_uitgang=type_uitgang,
        )

        # Bouw verdiepingen
        trap.verdiepingen = []
        for verd_str, verd_data in trap_data['verdiepingen'].items():
            verd_nr = int(verd_str)

            type_doorgang = uitgang_map.get(verd_data['type_doorgang'], DoorgangType.ENKELE_DEUR_LT135)

            tv = TrapVerdieping(
                verdieping=verd_nr,
                doorgang_naar_trap_m=verd_data['doorgang_trap'],
                type_doorgang=type_doorgang,
                oppervlakte_bordes_m2=verd_data['bordes'],
                oppervlakte_tussenbordessen_m2=verd_data['tussenbordes'],
                hoogteverschil_m=verd_data['hoogteverschil'],
                breedte_trap_m=verd_data['trapbreedte'],
                aantal_treden=verd_data['treden'],
            )
            trap.verdiepingen.append(tv)

        trap.sorteer_verdiepingen()
        project.trappen.append(trap)

    # Verdeel personen over trappen
    project.verdeel_personen_over_trappen()

    # Voer simulatie uit
    resultaten = simuleer_alle_trappen(project.trappen)
    toetsingen = toets_alle_resultaten(resultaten, trappen=project.trappen)

    st.session_state.resultaten = resultaten
    st.session_state.toetsingen = toetsingen
    st.session_state.project_obj = project


def render_stap4_resultaten():
    """Render stap 4: Resultaten"""
    st.markdown("## 📊 Stap 4: Resultaten")

    if st.session_state.resultaten is None:
        st.warning("Nog geen berekening uitgevoerd. Ga terug naar stap 3 en klik op 'Bereken'.")
        if st.button("⬅️ Terug naar configuratie"):
            st.session_state.stap = 3
            st.rerun()
        return

    resultaten = st.session_state.resultaten
    toetsingen = st.session_state.toetsingen

    # Overzicht metrics
    st.markdown("### 📈 Samenvatting")

    cols = st.columns(len(resultaten))
    for i, (trap_naam, res) in enumerate(resultaten.items()):
        toets = toetsingen[trap_naam]
        with cols[i]:
            status = "✅" if toets.alle_criteria_voldaan else "❌"
            st.metric(
                label=f"{trap_naam} {status}",
                value=f"{res.totaal_personen} pers",
                delta=f"Klaar in {res.voltooide_ontruiming_min or res.ontruimingstijd_min:.1f} min"
            )

    # Tabs voor verschillende views
    tab1, tab2, tab3 = st.tabs(["📊 Grafieken", "✅ Normtoetsing", "📋 Details"])

    with tab1:
        render_grafieken(resultaten)

    with tab2:
        render_normtoetsing(toetsingen)

    with tab3:
        render_details(resultaten)

    # Navigatie
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Terug", width="stretch"):
            st.session_state.stap = 3
            st.rerun()
    with col2:
        if st.button("🔄 Herbereken", width="stretch"):
            with st.spinner("Berekening uitvoeren..."):
                voer_berekening_uit()
            st.rerun()


def render_grafieken(resultaten):
    """Render grafieken van de resultaten"""
    st.markdown("### 📈 Ontruimingsverloop")

    # Maak Plotly figuur
    fig = go.Figure()

    colors = px.colors.qualitative.Set2

    for i, (trap_naam, res) in enumerate(resultaten.items()):
        tijden = [ts.tijd_min for ts in res.tijdstappen]
        buiten = [ts.cumulatief_buiten for ts in res.tijdstappen]

        fig.add_trace(go.Scatter(
            x=tijden,
            y=buiten,
            mode='lines+markers',
            name=trap_naam,
            line=dict(color=colors[i % len(colors)], width=2),
            marker=dict(size=4)
        ))

        # Voeg horizontale lijn toe voor totaal personen
        fig.add_hline(
            y=res.totaal_personen,
            line_dash="dash",
            line_color=colors[i % len(colors)],
            annotation_text=f"{trap_naam}: {res.totaal_personen}",
            annotation_position="right"
        )

    fig.update_layout(
        title="Cumulatief aantal personen buiten",
        xaxis_title="Tijd (minuten)",
        yaxis_title="Aantal personen",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )

    st.plotly_chart(fig, width="stretch")

    # Tweede grafiek: personen in trap
    st.markdown("### 🚶 Personen in trappenhuis")

    fig2 = go.Figure()

    for i, (trap_naam, res) in enumerate(resultaten.items()):
        tijden = [ts.tijd_min for ts in res.tijdstappen]
        in_trap = [ts.totaal_in_trap for ts in res.tijdstappen]

        fig2.add_trace(go.Scatter(
            x=tijden,
            y=in_trap,
            mode='lines',
            name=trap_naam,
            fill='tozeroy',
            line=dict(color=colors[i % len(colors)])
        ))

    fig2.update_layout(
        title="Personen in trappenhuis over tijd",
        xaxis_title="Tijd (minuten)",
        yaxis_title="Aantal personen in trap",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig2, width="stretch")


def render_normtoetsing(toetsingen):
    """Render normtoetsing resultaten"""
    st.markdown("### ✅ BBL Art. 4.81 Normtoetsing")

    for trap_naam, toets in toetsingen.items():
        with st.expander(f"**{trap_naam}** - {'✅ Voldoet' if toets.alle_criteria_voldaan else '❌ Voldoet niet'}", expanded=True):

            for criterium in toets.criteria:
                if criterium.status == ToetsStatus.VOLDOET:
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>✅ {criterium.naam}</strong><br>
                        {criterium.beschrijving}<br>
                        <em>Eis: {criterium.eis} {criterium.eenheid} | Berekend: {criterium.berekend:.1f} {criterium.eenheid}</em><br>
                        {criterium.toelichting}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="error-box">
                        <strong>❌ {criterium.naam}</strong><br>
                        {criterium.beschrijving}<br>
                        <em>Eis: {criterium.eis} {criterium.eenheid} | Berekend: {criterium.berekend:.1f} {criterium.eenheid}</em><br>
                        {criterium.toelichting}
                    </div>
                    """, unsafe_allow_html=True)


def render_details(resultaten):
    """Render gedetailleerde resultaten"""
    st.markdown("### 📋 Gedetailleerde tijdstapdata")

    for trap_naam, res in resultaten.items():
        with st.expander(f"**{trap_naam}** - Tijdstap data"):
            # Maak tabel data
            data = []
            for ts in res.tijdstappen:
                row = {
                    'Tijd (min)': ts.tijd_min,
                    'Naar buiten': f"{ts.naar_buiten:.0f}",
                    'Cumulatief buiten': f"{ts.cumulatief_buiten:.0f}",
                    'In trap': f"{ts.totaal_in_trap:.0f}",
                    'Op verdiepingen': f"{ts.totaal_op_verdiepingen:.0f}",
                }
                data.append(row)

            st.dataframe(data, width="stretch", height=400)

            # Download optie
            import pandas as pd
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"{trap_naam}_data.csv",
                mime="text/csv"
            )


def main():
    """Hoofdfunctie"""
    init_session_state()
    render_header()
    render_sidebar()

    # Render huidige stap
    if st.session_state.stap == 1:
        render_stap1_project()
    elif st.session_state.stap == 2:
        render_stap2_personen()
    elif st.session_state.stap == 3:
        render_stap3_trappen()
    elif st.session_state.stap == 4:
        render_stap4_resultaten()


if __name__ == "__main__":
    main()
