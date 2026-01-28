"""
Capaciteitsberekeningen volgens BBL methode
Gebaseerd op Besluit bouwwerken leefomgeving (BBL) Art. 4.80 en 4.81
§ 4.2.11 Vluchtroutes: inrichting en capaciteit
"""

from typing import Tuple
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.constanten import (
    DoorgangType,
    DOORGANG_FACTOREN,
    BEZETTING_DICHTHEID,
    TIJDSTAP,
    TRAP_FACTOR_HOOG,
    TRAP_FACTOR_LAAG,
    TRAP_BREEDTE_DREMPEL,
    TRAP_OPVANG_SMAL,
    TRAP_OPVANG_BREED,
    MIN_AANTREDE,
)


def bereken_doorstroomcapaciteit_deur(
    breedte_m: float,
    type_doorgang: DoorgangType
) -> float:
    """
    Berekent doorstroomcapaciteit door een deuropening per tijdstap.
    
    BBL Art. 4.80 lid 1:
    - b: 90 pers/m/min voor ruimte
    - c: 90 pers/m/min voor dubbele deur < 135°
    - d: 110 pers/m/min voor enkele deur < 135°
    - e: 135 pers/m/min voor andere doorgang
    
    BBL Art. 4.81 lid 4 onder l/m:
    - 37 personen per minuut per deur tegen vluchtrichting
    
    Formule: (factor × breedte) × tijdstap
    Voor tegen vluchtrichting: vast getal × tijdstap (onafhankelijk van breedte)
    
    Args:
        breedte_m: Breedte van de doorgang in meters
        type_doorgang: Type doorgang volgens BBL Art. 4.80
    
    Returns:
        Doorstroomcapaciteit in personen per tijdstap (0.5 min)
    
    Examples:
        >>> bereken_doorstroomcapaciteit_deur(0.9, DoorgangType.ENKELE_DEUR_LT135)
        49.5
        >>> bereken_doorstroomcapaciteit_deur(1.5, DoorgangType.DUBBELE_DEUR_LT135)
        67.5
    """
    if breedte_m <= 0:
        return 0.0
    
    if type_doorgang == DoorgangType.TEGEN_VLUCHTRICHTING:
        # BBL 4.81 lid 4 l/m: 37 personen per minuut per deur, onafhankelijk van breedte
        return DOORGANG_FACTOREN[DoorgangType.TEGEN_VLUCHTRICHTING] * TIJDSTAP
    
    factor = DOORGANG_FACTOREN[type_doorgang]
    return factor * breedte_m * TIJDSTAP


def bereken_doorstroomcapaciteit_trap(
    breedte_trap_m: float,
    hoogteverschil_m: float
) -> float:
    """
    Berekent doorstroomcapaciteit van een trap per tijdstap.
    
    BBL Art. 4.80 lid 1 onder a:
    "45 personen per meter vrije breedte van een trap bij het overbruggen van 
    een hoogteverschil van meer dan 1 m en 90 personen per meter vrije breedte 
    bij een hoogteverschil van ten hoogste 1 m, voor zover de aantrede van de 
    trap ten minste 0,17 m bedraagt"
    
    Formule: (breedte × factor) × tijdstap
    Factor = 45 bij hoogteverschil > 1m
    Factor = 90 bij hoogteverschil ≤ 1m
    
    Args:
        breedte_trap_m: Effectieve loopbreedte trap in meters
        hoogteverschil_m: Hoogteverschil te overbruggen in meters
    
    Returns:
        Doorstroomcapaciteit in personen per tijdstap
    
    Examples:
        >>> bereken_doorstroomcapaciteit_trap(1.1, 3.0)
        24.75
        >>> bereken_doorstroomcapaciteit_trap(1.1, 0.5)
        49.5
    """
    if breedte_trap_m <= 0:
        return 0.0
    
    # BBL Art. 4.80 lid 1a
    if hoogteverschil_m > 1.0:
        factor = TRAP_FACTOR_HOOG  # 45 pers/m/min
    else:
        factor = TRAP_FACTOR_LAAG  # 90 pers/m/min
    
    return breedte_trap_m * factor * TIJDSTAP


def bereken_opslagcapaciteit_trappenhuis(
    oppervlakte_bordes_m2: float,
    oppervlakte_tussenbordessen_m2: float,
    breedte_trap_m: float,
    aantal_treden: int,
    doorstroomcap_trap: float = None  # Niet meer gebruikt, behouden voor backwards compatibility
) -> float:
    """
    Berekent hoeveel personen kunnen wachten in het trappenhuis.

    BBL Art. 4.81 lid 4:
    - j: opvangcapaciteit vloer/hellingbaan is ten hoogste 4 pers/m²
    - h: opvangcapaciteit trap is 0,5 persoon per trede (breedte ≤ 1,1m)
    - i: opvangcapaciteit trap is 0,9 persoon per trede per m breedte (breedte > 1,1m)

    De opslagcapaciteit bestaat uit:
    1. Capaciteit op bordes: oppervlakte × bezettingsdichtheid (4 pers/m²)
    2. Capaciteit op trap deel: tussenbordes + trap_opslag

    Args:
        oppervlakte_bordes_m2: Oppervlakte bordes in m²
        oppervlakte_tussenbordessen_m2: Oppervlakte tussenbordessen in m²
        breedte_trap_m: Breedte van de trap in meters
        aantal_treden: Aantal treden in de trap
        doorstroomcap_trap: DEPRECATED - niet meer gebruikt

    Returns:
        Opslagcapaciteit in personen
    """
    if oppervlakte_bordes_m2 < 0:
        oppervlakte_bordes_m2 = 0
    if oppervlakte_tussenbordessen_m2 < 0:
        oppervlakte_tussenbordessen_m2 = 0
    
    # Capaciteit op bordes (BBL 4.81 lid 4j: 4 pers/m²)
    capaciteit_bordes = BEZETTING_DICHTHEID * oppervlakte_bordes_m2
    
    # Capaciteit op trap zelf (mensen op treden)
    # BBL 4.81 lid 4 h/i
    if breedte_trap_m > TRAP_BREEDTE_DREMPEL:
        # BBL 4.81 lid 4i: 0,9 persoon per trede per meter breedte
        trap_opslag = aantal_treden * breedte_trap_m * TRAP_OPVANG_BREED
    else:
        # BBL 4.81 lid 4h: 0,5 persoon per trede
        trap_opslag = aantal_treden * TRAP_OPVANG_SMAL
    
    # Totale capaciteit tussenbordes + trap
    # NB: Opslagcapaciteit is fysieke ruimte, niet gelimiteerd door doorstroom per tijdstap
    capaciteit_trap_deel = BEZETTING_DICHTHEID * oppervlakte_tussenbordessen_m2 + trap_opslag

    return capaciteit_bordes + capaciteit_trap_deel


def bereken_opslagcapaciteit_voorportaal(
    oppervlakte_m2: float,
    doorstroomcap_portaal: float,
    actief: bool = True
) -> float:
    """
    Berekent opslagcapaciteit van voorportaal.
    
    Gelimiteerd door kleinste van:
    - Oppervlakte × bezettingsdichtheid
    - Doorstroomcapaciteit portaal
    
    Args:
        oppervlakte_m2: Oppervlakte voorportaal in m²
        doorstroomcap_portaal: Doorstroomcapaciteit door portaal deur
        actief: Of voorportaal actief is
    
    Returns:
        Opslagcapaciteit in personen
    """
    if not actief or oppervlakte_m2 <= 0:
        return 0.0
    
    return min(
        oppervlakte_m2 * BEZETTING_DICHTHEID,
        doorstroomcap_portaal
    )


def bereken_voorportaal_capaciteiten(
    oppervlakte_m2: float,
    doorgang_m: float,
    type_doorgang: DoorgangType,
    voorportaal_actief: bool
) -> Tuple[float, float]:
    """
    Berekent zowel opslag- als doorstroomcapaciteit van voorportaal.
    
    Args:
        oppervlakte_m2: Oppervlakte voorportaal in m²
        doorgang_m: Breedte doorgang naar voorportaal
        type_doorgang: Type doorgang
        voorportaal_actief: Of voorportaal actief is
    
    Returns:
        Tuple van (opslagcapaciteit, doorstroomcapaciteit)
    """
    if not voorportaal_actief:
        return (0.0, 0.0)
    
    doorstroom = bereken_doorstroomcapaciteit_deur(doorgang_m, type_doorgang)
    opslag = bereken_opslagcapaciteit_voorportaal(oppervlakte_m2, doorstroom, True)
    
    return (opslag, doorstroom)


def bereken_alle_capaciteiten_verdieping(
    doorgang_naar_trap_m: float,
    type_doorgang: DoorgangType,
    oppervlakte_bordes_m2: float,
    oppervlakte_tussenbordessen_m2: float,
    hoogteverschil_m: float,
    breedte_trap_m: float,
    aantal_treden: int,
    voorportaal_actief: bool = False,
    oppervlakte_portaal_m2: float = 0.0,
    doorgang_portaal_m: float = 0.0,
    type_doorgang_portaal: DoorgangType = DoorgangType.ENKELE_DEUR_LT135
) -> dict:
    """
    Bereken alle capaciteiten voor een verdieping in één aanroep.
    
    Returns:
        Dict met alle berekende capaciteiten:
        - doorstroomcap_deur: Doorstroomcapaciteit deur naar trap
        - doorstroomcap_trap: Doorstroomcapaciteit trap omlaag
        - opslagcapaciteit: Opslagcapaciteit trappenhuis
        - doorstroomcap_portaal: Doorstroomcapaciteit voorportaal
        - opslagcap_portaal: Opslagcapaciteit voorportaal
    """
    doorstroomcap_deur = bereken_doorstroomcapaciteit_deur(
        doorgang_naar_trap_m, type_doorgang
    )
    
    doorstroomcap_trap = bereken_doorstroomcapaciteit_trap(
        breedte_trap_m, hoogteverschil_m
    )
    
    opslagcapaciteit = bereken_opslagcapaciteit_trappenhuis(
        oppervlakte_bordes_m2,
        oppervlakte_tussenbordessen_m2,
        breedte_trap_m,
        aantal_treden,
        doorstroomcap_trap
    )
    
    opslagcap_portaal, doorstroomcap_portaal = bereken_voorportaal_capaciteiten(
        oppervlakte_portaal_m2,
        doorgang_portaal_m,
        type_doorgang_portaal,
        voorportaal_actief
    )
    
    return {
        'doorstroomcap_deur': doorstroomcap_deur,
        'doorstroomcap_trap': doorstroomcap_trap,
        'opslagcapaciteit': opslagcapaciteit,
        'doorstroomcap_portaal': doorstroomcap_portaal,
        'opslagcap_portaal': opslagcap_portaal,
    }


def bereken_max_personen_trap(
    doorgang_uitgang_m: float,
    type_uitgang: DoorgangType,
    ontruimingstijd_min: float,
    verdiepingen: list = None
) -> dict:
    """
    Berekent het maximaal aantal personen dat via een trap kan ontruimen
    binnen de gegeven ontruimingstijd.

    Let op: Dit berekent de TOTALE doorstroomcapaciteit (BBL lid 1).
    Voor de maximale personen PER VERDIEPING (BBL lid 2) is de opvangcapaciteit
    vaak de beperkende factor - zie max_per_verdieping in de output.

    Args:
        doorgang_uitgang_m: Breedte uitgang in meters
        type_uitgang: Type doorgang uitgang
        ontruimingstijd_min: Maximale ontruimingstijd in minuten
        verdiepingen: Optioneel - lijst met TrapVerdieping objecten voor detail

    Returns:
        Dict met:
        - max_personen: Maximaal aantal personen totaal (BBL lid 1)
        - max_per_verdieping: Max personen per verdieping voor BBL lid 2 (1 min verlaten)
        - bottleneck: Beschrijving van de beperkende factor voor totaal
        - bottleneck_per_verdieping: Beperkende factor per verdieping
        - doorstroom_uitgang_per_min: Doorstroomcapaciteit uitgang per minuut
        - details: Extra details per verdieping (indien verdiepingen gegeven)
    """
    # Bereken doorstroomcapaciteit uitgang per tijdstap
    doorstroom_uitgang_per_tijdstap = bereken_doorstroomcapaciteit_deur(
        doorgang_uitgang_m, type_uitgang
    )

    # Omrekenen naar per minuut
    doorstroom_uitgang_per_min = doorstroom_uitgang_per_tijdstap / TIJDSTAP

    # Maximaal aantal personen op basis van uitgang (voor totale ontruiming)
    max_personen_uitgang = doorstroom_uitgang_per_min * ontruimingstijd_min

    bottleneck = f"Uitgang trappenhuis ({doorgang_uitgang_m:.2f}m)"
    max_personen = max_personen_uitgang

    # Voor BBL lid 2: max personen per verdieping (binnen 1 minuut verlaten)
    max_per_verdieping = None
    bottleneck_per_verdieping = None

    details = []

    # Check ook de verdiepingen als die gegeven zijn
    if verdiepingen:
        for verd in verdiepingen:
            # Doorstroomcapaciteit deur naar trap per minuut
            doorstroom_deur = bereken_doorstroomcapaciteit_deur(
                verd.doorgang_naar_trap_m, verd.type_doorgang
            ) / TIJDSTAP

            # Doorstroomcapaciteit trap per minuut
            doorstroom_trap = bereken_doorstroomcapaciteit_trap(
                verd.breedte_trap_m, verd.hoogteverschil_m
            ) / TIJDSTAP

            # Opvangcapaciteit trappenhuis (BBL Art. 4.81 lid 4 h/i/j)
            opvangcap = bereken_opslagcapaciteit_trappenhuis(
                verd.oppervlakte_bordes_m2,
                verd.oppervlakte_tussenbordessen_m2,
                verd.breedte_trap_m,
                verd.aantal_treden
            )

            # De kleinste van doorstroom deur/trap is bottleneck voor doorstroom
            min_doorstroom = min(doorstroom_deur, doorstroom_trap)

            # Voor BBL lid 2 (1 min verlaten): kleinste van opvangcap en doorstroom*1min
            max_lid2 = min(opvangcap, doorstroom_deur * 1.0)  # 1 minuut

            details.append({
                'verdieping': verd.verdieping,
                'doorstroom_deur_per_min': doorstroom_deur,
                'doorstroom_trap_per_min': doorstroom_trap,
                'opvangcapaciteit': opvangcap,
                'min_doorstroom_per_min': min_doorstroom,
                'max_lid2': int(max_lid2),
            })

            # Check of dit een nieuwe bottleneck is voor totale doorstroom
            max_via_deze_verd = min_doorstroom * ontruimingstijd_min
            if max_via_deze_verd < max_personen:
                max_personen = max_via_deze_verd
                if doorstroom_deur < doorstroom_trap:
                    bottleneck = f"Toegangsdeur trappenhuis verd. {verd.verdieping} ({verd.doorgang_naar_trap_m:.2f}m)"
                else:
                    bottleneck = f"Trap verdieping {verd.verdieping} ({verd.breedte_trap_m:.2f}m)"

            # Bepaal max per verdieping voor BBL lid 2
            if max_per_verdieping is None or max_lid2 < max_per_verdieping:
                max_per_verdieping = int(max_lid2)
                if opvangcap <= doorstroom_deur * 1.0:
                    bottleneck_per_verdieping = f"Opvangcapaciteit trappenhuis ({opvangcap:.0f} pers)"
                else:
                    bottleneck_per_verdieping = f"Toegangsdeur trappenhuis ({doorstroom_deur:.0f} pers/min)"

    return {
        'max_personen': int(max_personen),
        'max_per_verdieping': max_per_verdieping,
        'bottleneck': bottleneck,
        'bottleneck_per_verdieping': bottleneck_per_verdieping,
        'doorstroom_uitgang_per_min': doorstroom_uitgang_per_min,
        'ontruimingstijd_min': ontruimingstijd_min,
        'details': details,
    }
