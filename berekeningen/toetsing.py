"""
Toetsing aan brandveiligheidsnormen
Controleert simulatieresultaten tegen BBL eisen (Art. 4.81)

BBL Artikel 4.81:
- Lid 1: Ontruimingstijden (15/20/30 min afhankelijk van type vluchtroute)
- Lid 2: Subbrandcompartiment binnen 1 minuut verlaten
- Lid 3: Verdieping/ruimte binnen 3,5 minuut verlaten
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from berekeningen.simulatie import SimulatieResultaat
from models.constanten import TIJD_VERLATEN_COMPARTIMENT, TIJD_VERLATEN_VERDIEPING


class ToetsStatus(Enum):
    """Status van een toetscriterium"""
    VOLDOET = "voldoet"
    VOLDOET_NIET = "voldoet_niet"
    NIET_GETOETST = "niet_getoetst"


@dataclass
class ToetsCriterium:
    """Resultaat van één toetscriterium"""
    naam: str
    beschrijving: str
    eis: float
    berekend: float
    eenheid: str
    status: ToetsStatus
    toelichting: str = ""
    
    @property
    def voldoet(self) -> bool:
        return self.status == ToetsStatus.VOLDOET


@dataclass
class ToetsResultaat:
    """Volledige toetsing voor één trap"""
    trap_aanduiding: str
    criteria: List[ToetsCriterium] = field(default_factory=list)
    
    @property
    def alle_criteria_voldaan(self) -> bool:
        """Voldoen alle criteria?"""
        return all(c.voldoet for c in self.criteria if c.status != ToetsStatus.NIET_GETOETST)
    
    @property
    def aantal_voldoet(self) -> int:
        """Aantal criteria dat voldoet"""
        return sum(1 for c in self.criteria if c.voldoet)
    
    @property
    def aantal_voldoet_niet(self) -> int:
        """Aantal criteria dat niet voldoet"""
        return sum(1 for c in self.criteria if c.status == ToetsStatus.VOLDOET_NIET)


def toets_lid1_volledige_ontruiming(
    sim_resultaat: SimulatieResultaat,
    max_ontruimingstijd_min: float
) -> ToetsCriterium:
    """
    BBL Art. 4.81 lid 1: Volledige ontruiming binnen maximale ontruimingstijd

    Ontruimingstijden volgens Art. 4.81 lid 1:
    - a: 30 minuten voor veiligheidsvluchtroute
    - b: 20 minuten voor extra beschermde vluchtroute
    - c: 15 minuten voor andere vluchtroute
    """
    totaal = sim_resultaat.totaal_personen
    buiten_op_tijd = sim_resultaat.get_personen_buiten_op_tijd(max_ontruimingstijd_min)

    percentage = (buiten_op_tijd / totaal * 100) if totaal > 0 else 100

    # Gebruik kleine tolerantie voor floating-point vergelijking
    if buiten_op_tijd >= totaal - 0.01:
        status = ToetsStatus.VOLDOET
        toelichting = (
            f"Alle {totaal} personen verlaten het gebouw via de uitgang van het trappenhuis "
            f"binnen {max_ontruimingstijd_min} minuten."
        )
    else:
        status = ToetsStatus.VOLDOET_NIET
        tekort = totaal - buiten_op_tijd
        toelichting = (
            f"Slechts {buiten_op_tijd:.0f} van {totaal} personen verlaten het gebouw via de "
            f"uitgang van het trappenhuis binnen {max_ontruimingstijd_min} minuten ({percentage:.1f}%). "
            f"Tekort: {tekort:.0f} personen. Vergroot de uitgang van het trappenhuis of "
            f"verminder het aantal personen."
        )

    return ToetsCriterium(
        naam="BBL Art. 4.81 lid 1 - Volledige ontruiming via trappenhuis",
        beschrijving=f"Alle personen binnen {max_ontruimingstijd_min} minuten buiten via uitgang trappenhuis",
        eis=totaal,
        berekend=buiten_op_tijd,
        eenheid="personen",
        status=status,
        toelichting=toelichting
    )


def toets_lid2_compartiment_ontruiming(
    sim_resultaat: SimulatieResultaat,
    max_tijd_per_verdieping_min: float = TIJD_VERLATEN_COMPARTIMENT,
    trap: 'Trap' = None
) -> ToetsCriterium:
    """
    BBL Art. 4.81 lid 2: Verlaten brandcompartiment

    "De opvang- en doorstroomcapaciteit [...] is zodanig dat het bedreigde
    subbrandcompartiment waarin een vluchtroute begint binnen 1 minuut na
    aanvang van het vluchten kan worden verlaten."

    Dit toetst of personen via de toegangsdeur naar het trappenhuis
    het brandcompartiment binnen 1 minuut kunnen verlaten.
    """
    langzaamste_verdieping = None
    langzaamste_tijd = 0.0
    langzaamste_personen = 0

    for ts in sim_resultaat.tijdstappen:
        for vn, state in ts.verdieping_states.items():
            if state.personen_op_verdieping > 0:
                if ts.tijd_min > langzaamste_tijd:
                    langzaamste_tijd = ts.tijd_min
                    langzaamste_verdieping = vn
                    langzaamste_personen = int(state.personen_op_verdieping)

    if langzaamste_verdieping is None:
        # Geen personen op verdiepingen = alles leeg
        status = ToetsStatus.VOLDOET
        toelichting = (
            "Alle personen verlaten het brandcompartiment direct via de "
            "toegangsdeur naar het trappenhuis."
        )
        berekend = 0.0
    elif langzaamste_tijd <= max_tijd_per_verdieping_min:
        status = ToetsStatus.VOLDOET
        toelichting = (
            f"Alle personen verlaten het brandcompartiment binnen {max_tijd_per_verdieping_min} minuut "
            f"via de toegangsdeur naar het trappenhuis."
        )
        berekend = langzaamste_tijd
    else:
        status = ToetsStatus.VOLDOET_NIET
        # Bepaal de bottleneck: opslagcapaciteit of doorstroomcapaciteit
        toelichting = _bepaal_bottleneck_toelichting(
            langzaamste_verdieping, langzaamste_personen, langzaamste_tijd, trap, "lid2"
        )
        berekend = langzaamste_tijd

    return ToetsCriterium(
        naam="BBL Art. 4.81 lid 2 - Verlaten brandcompartiment",
        beschrijving=f"Brandcompartiment binnen {max_tijd_per_verdieping_min} minuut verlaten via toegangsdeur trappenhuis",
        eis=max_tijd_per_verdieping_min,
        berekend=berekend,
        eenheid="minuten",
        status=status,
        toelichting=toelichting
    )


def _bepaal_bottleneck_toelichting(
    verdieping: int,
    personen_wachtend: int,
    wachttijd: float,
    trap: 'Trap' = None,
    context: str = "lid3"
) -> str:
    """
    Bepaal of de bottleneck de opslagcapaciteit of doorstroomcapaciteit is
    en genereer een informatieve toelichting.

    Args:
        verdieping: Verdiepingnummer
        personen_wachtend: Aantal personen nog wachtend
        wachttijd: Tijd in minuten
        trap: Trap object voor capaciteitsanalyse
        context: "lid2" voor brandcompartiment verlaten, "lid3" voor verdieping verlaten
    """
    if trap is None:
        return (
            f"Verdieping {verdieping}: nog {personen_wachtend} personen in brandcompartiment na {wachttijd:.1f} minuten. "
            f"Opvang- of doorstroomcapaciteit onvoldoende."
        )

    tv = trap.get_verdieping(verdieping)
    if tv is None:
        return (
            f"Verdieping {verdieping}: nog {personen_wachtend} personen in brandcompartiment na {wachttijd:.1f} minuten. "
            f"Opvang- of doorstroomcapaciteit onvoldoende."
        )

    # Haal capaciteiten op (deze zijn al berekend tijdens simulatie)
    opslagcap = tv._opslagcapaciteit if tv._opslagcapaciteit else 0
    doorstroomcap_deur = tv._doorstroomcap_deur if tv._doorstroomcap_deur else 0
    aantal_personen = tv.aantal_personen

    # Per tijdstap kunnen doorstroomcap_deur personen naar trap
    # Maar trap kan maximaal opslagcap personen tegelijk bevatten
    doorstroom_per_minuut = doorstroomcap_deur * 2  # 2 tijdstappen per minuut

    # Bepaal welke het eerst beperkend is
    if opslagcap < aantal_personen and opslagcap <= doorstroom_per_minuut:
        # Opslagcapaciteit is de bottleneck
        return (
            f"Verdieping {verdieping}: nog {personen_wachtend} personen in brandcompartiment na {wachttijd:.1f} minuten. "
            f"Opvangcapaciteit trappenhuis ({opslagcap:.0f} personen) is onvoldoende voor {aantal_personen} personen. "
            f"Oplossing: vergroot bordes/tussenbordessen of verhoog aantal treden in trappenhuis."
        )
    elif doorstroom_per_minuut < aantal_personen:
        # Doorstroomcapaciteit is de bottleneck
        return (
            f"Verdieping {verdieping}: nog {personen_wachtend} personen in brandcompartiment na {wachttijd:.1f} minuten. "
            f"Doorstroomcapaciteit toegangsdeur trappenhuis ({doorstroomcap_deur:.1f} pers/tijdstap = {doorstroom_per_minuut:.0f} pers/min) "
            f"is onvoldoende voor {aantal_personen} personen. "
            f"Oplossing: verbreed de toegangsdeur naar het trappenhuis."
        )
    else:
        # Combinatie van factoren of andere oorzaak (bijv. opstopping lager in trap)
        return (
            f"Verdieping {verdieping}: nog {personen_wachtend} personen in brandcompartiment na {wachttijd:.1f} minuten. "
            f"Opstopping in trappenhuis door onvoldoende capaciteit lager in het gebouw "
            f"of bij de uitgang van het trappenhuis op de vluchtverdieping."
        )


def toets_lid3_verlaten_verdieping(
    sim_resultaat: SimulatieResultaat,
    max_tijd_verlaten_min: float = TIJD_VERLATEN_VERDIEPING,
    trap: 'Trap' = None
) -> ToetsCriterium:
    """
    BBL Art. 4.81 lid 3: Maximale tijd om verdieping/ruimte te verlaten

    a. 3,5 minuten - standaard
    b. 6 minuten - als WBDBO >= 30 min (NEN 6068) EN rookwerendheid R200 (NEN 6075)
    """
    # Check hoelang het duurt voordat alle personen van verdieping naar trap zijn

    max_wachttijd = 0.0
    probleem_verdieping = None
    probleem_personen = 0

    for ts in sim_resultaat.tijdstappen:
        for vn, state in ts.verdieping_states.items():
            # Als er nog mensen wachten en het is al te lang
            if state.personen_op_verdieping > 0 and ts.tijd_min > max_tijd_verlaten_min:
                if ts.tijd_min > max_wachttijd:
                    max_wachttijd = ts.tijd_min
                    probleem_verdieping = vn
                    probleem_personen = int(state.personen_op_verdieping)

    if probleem_verdieping is None:
        status = ToetsStatus.VOLDOET
        toelichting = (
            f"Alle personen verlaten de verdieping binnen {max_tijd_verlaten_min} minuten "
            f"via de toegangsdeur naar het trappenhuis."
        )
        berekend = max_wachttijd if max_wachttijd > 0 else 0.0
    else:
        status = ToetsStatus.VOLDOET_NIET
        # Bepaal de bottleneck: opslagcapaciteit of doorstroomcapaciteit
        toelichting = _bepaal_bottleneck_toelichting(
            probleem_verdieping, probleem_personen, max_wachttijd, trap, "lid3"
        )
        berekend = max_wachttijd

    # Voeg context toe over welke eis wordt gebruikt
    if max_tijd_verlaten_min == 6.0:
        beschrijving = (
            f"Verdieping verlaten binnen {max_tijd_verlaten_min} minuten via toegangsdeur trappenhuis "
            f"(verlengd: WBDBO>=30 + R200)"
        )
    else:
        beschrijving = (
            f"Verdieping verlaten binnen {max_tijd_verlaten_min} minuten via toegangsdeur trappenhuis "
            f"(standaard)"
        )

    return ToetsCriterium(
        naam="BBL Art. 4.81 lid 3 - Verlaten verdieping via trappenhuis",
        beschrijving=beschrijving,
        eis=max_tijd_verlaten_min,
        berekend=berekend,
        eenheid="minuten",
        status=status,
        toelichting=toelichting
    )


def toets_simulatie_resultaat(
    sim_resultaat: SimulatieResultaat,
    max_ontruimingstijd_min: float = None,
    max_tijd_per_verdieping_min: float = TIJD_VERLATEN_COMPARTIMENT,
    max_tijd_verlaten_min: float = TIJD_VERLATEN_VERDIEPING,
    trap: 'Trap' = None
) -> ToetsResultaat:
    """
    Voer volledige toetsing uit op simulatieresultaat tegen BBL Art. 4.81.

    Args:
        sim_resultaat: Resultaat van simulatie
        max_ontruimingstijd_min: Maximale ontruimingstijd (standaard: van simulatie)
        max_tijd_per_verdieping_min: Max tijd per verdieping (BBL 4.81 lid 2: 1 min)
        max_tijd_verlaten_min: Max tijd om verdieping te verlaten (BBL 4.81 lid 3: 3.5 min)
        trap: Trap object voor het bepalen van bottlenecks in toelichting

    Returns:
        ToetsResultaat met alle getoetste criteria
    """
    if max_ontruimingstijd_min is None:
        max_ontruimingstijd_min = sim_resultaat.ontruimingstijd_min

    toets = ToetsResultaat(trap_aanduiding=sim_resultaat.trap_aanduiding)

    # BBL Art. 4.81 lid 1: Volledige ontruiming
    toets.criteria.append(
        toets_lid1_volledige_ontruiming(sim_resultaat, max_ontruimingstijd_min)
    )

    # BBL Art. 4.81 lid 2: Compartiment ontruiming
    toets.criteria.append(
        toets_lid2_compartiment_ontruiming(sim_resultaat, max_tijd_per_verdieping_min, trap)
    )

    # BBL Art. 4.81 lid 3: Verlaten verdieping
    toets.criteria.append(
        toets_lid3_verlaten_verdieping(sim_resultaat, max_tijd_verlaten_min, trap)
    )

    return toets


def toets_alle_resultaten(
    resultaten: Dict[str, SimulatieResultaat],
    trappen: List = None,
    **kwargs
) -> Dict[str, ToetsResultaat]:
    """
    Toets alle simulatieresultaten.

    Args:
        resultaten: Dict met trap aanduiding -> SimulatieResultaat
        trappen: Optionele lijst van Trap objecten voor trap-specifieke parameters
        **kwargs: Parameters voor toetsing (overschrijft trap-specifieke waarden)

    Returns:
        Dict met trap aanduiding -> ToetsResultaat
    """
    toets_resultaten = {}

    for naam, res in resultaten.items():
        # Haal trap-specifieke waarden op indien beschikbaar
        trap_kwargs = kwargs.copy()
        gevonden_trap = None

        if trappen:
            # Zoek de juiste trap
            for trap in trappen:
                if trap.aanduiding == naam:
                    gevonden_trap = trap
                    # Gebruik trap-specifieke waarden tenzij expliciet overschreven
                    if 'max_tijd_verlaten_min' not in kwargs:
                        trap_kwargs['max_tijd_verlaten_min'] = trap.verlaten_verdieping_min
                    break

        # Geef trap mee voor bottleneck analyse
        trap_kwargs['trap'] = gevonden_trap
        toets_resultaten[naam] = toets_simulatie_resultaat(res, **trap_kwargs)

    return toets_resultaten
