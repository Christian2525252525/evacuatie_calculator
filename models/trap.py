"""
Trap en TrapVerdieping datamodellen
Gebaseerd op Besluit bouwwerken leefomgeving (BBL) Art. 4.80 en 4.81
"""

from dataclasses import dataclass, field
from typing import Optional, List
from .constanten import (
    DoorgangType, LocatieType, VerlaatTijdType,
    ONTRUIMINGSTIJDEN, VERLAAT_TIJDEN,
    STANDAARD_HOOGTEVERSCHIL, STANDAARD_TRAPBREEDTE,
    STANDAARD_AANTAL_TREDEN, STANDAARD_BORDES_OPP,
    STANDAARD_TUSSENBORDES_OPP, STANDAARD_DOORGANG_BREEDTE,
)


@dataclass
class TrapVerdieping:
    """Eigenschappen van een trap op een specifieke verdieping"""
    verdieping: int
    doorgang_naar_trap_m: float = STANDAARD_DOORGANG_BREEDTE
    type_doorgang: DoorgangType = DoorgangType.ENKELE_DEUR_LT135  # BBL 4.80 lid d: 110 pers/m
    aantal_deuren_naar_trap: int = 1  # Aantal aparte deuren naar trappenhuis op deze verdieping
    oppervlakte_bordes_m2: float = STANDAARD_BORDES_OPP
    oppervlakte_tussenbordessen_m2: float = STANDAARD_TUSSENBORDES_OPP
    hoogteverschil_m: float = STANDAARD_HOOGTEVERSCHIL
    breedte_trap_m: float = STANDAARD_TRAPBREEDTE
    aantal_treden: int = STANDAARD_AANTAL_TREDEN
    verdeling_fractie: float = 1.0
    gefaseerde_vertraging_min: float = 0.0
    
    # Voorportaal eigenschappen
    voorportaal_actief: bool = False
    oppervlakte_portaal_m2: float = 0.0
    doorgang_portaal_m: float = 0.0
    type_doorgang_portaal: DoorgangType = DoorgangType.ENKELE_DEUR_LT135
    
    # Berekende waarden (worden ingevuld tijdens simulatie)
    aantal_personen: int = 0
    
    # Gecachte capaciteiten (worden berekend)
    _opslagcapaciteit: Optional[float] = field(default=None, repr=False)
    _doorstroomcap_deur: Optional[float] = field(default=None, repr=False)
    _doorstroomcap_trap: Optional[float] = field(default=None, repr=False)
    _doorstroomcap_portaal: Optional[float] = field(default=None, repr=False)
    _opslagcap_portaal: Optional[float] = field(default=None, repr=False)
    
    def reset_cache(self):
        """Reset gecachte waarden"""
        self._opslagcapaciteit = None
        self._doorstroomcap_deur = None
        self._doorstroomcap_trap = None
        self._doorstroomcap_portaal = None
        self._opslagcap_portaal = None
    
    def copy(self) -> 'TrapVerdieping':
        """Maak een kopie van deze verdieping"""
        return TrapVerdieping(
            verdieping=self.verdieping,
            doorgang_naar_trap_m=self.doorgang_naar_trap_m,
            type_doorgang=self.type_doorgang,
            aantal_deuren_naar_trap=self.aantal_deuren_naar_trap,
            oppervlakte_bordes_m2=self.oppervlakte_bordes_m2,
            oppervlakte_tussenbordessen_m2=self.oppervlakte_tussenbordessen_m2,
            hoogteverschil_m=self.hoogteverschil_m,
            breedte_trap_m=self.breedte_trap_m,
            aantal_treden=self.aantal_treden,
            verdeling_fractie=self.verdeling_fractie,
            gefaseerde_vertraging_min=self.gefaseerde_vertraging_min,
            voorportaal_actief=self.voorportaal_actief,
            oppervlakte_portaal_m2=self.oppervlakte_portaal_m2,
            doorgang_portaal_m=self.doorgang_portaal_m,
            type_doorgang_portaal=self.type_doorgang_portaal,
            aantal_personen=self.aantal_personen
        )


@dataclass
class Trap:
    """
    Complete trap definitie
    Gebaseerd op BBL Art. 4.80 (doorstroomcapaciteit) en 4.81 (opvangcapaciteit)
    """
    aanduiding: str
    locatie: LocatieType = LocatieType.BESCHERMD  # Standaard: beschermde vluchtroute (15 min)
    verlaat_tijd_type: VerlaatTijdType = VerlaatTijdType.STANDAARD  # BBL Art. 4.81 lid 3

    # Uitgang eigenschappen
    doorgang_uitgang_m: float = STANDAARD_DOORGANG_BREEDTE
    type_uitgang: DoorgangType = DoorgangType.ENKELE_DEUR_LT135  # BBL 4.80 lid d
    aantal_deuren_uitgang: int = 1  # Aantal aparte deuren bij uitgang trappenhuis
    verdiepingen_onder_uitgang: int = 0

    # Voorportaal globaal
    voorportaal_aanwezig: bool = False

    # Verdiepingen
    verdiepingen: List[TrapVerdieping] = field(default_factory=list)

    # Gecachte uitgang capaciteit
    _doorstroomcap_uitgang: Optional[float] = field(default=None, repr=False)

    @property
    def ontruimingstijd_min(self) -> int:
        """
        Ontruimingstijd in minuten, afgeleid van het type vluchtroute.

        BBL Art. 4.81 lid 1:
        - a: 30 min voor veiligheidsvluchtroute
        - b: 20 min voor extra beschermde vluchtroute
        - c: 15 min voor beschermde vluchtroute
        """
        return ONTRUIMINGSTIJDEN.get(self.locatie, 15)

    @property
    def verlaten_verdieping_min(self) -> float:
        """
        Maximale tijd om verdieping te verlaten, afgeleid van verlaat_tijd_type.

        BBL Art. 4.81 lid 3:
        - a: 3,5 min standaard
        - b: 6 min als WBDBO ≥ 30 min EN rookwerendheid R200
        """
        return VERLAAT_TIJDEN.get(self.verlaat_tijd_type, 3.5)

    @property
    def uitgang_verdieping(self) -> int:
        """Verdieping waar de uitgang zich bevindt"""
        return -self.verdiepingen_onder_uitgang

    @property
    def totaal_personen(self) -> int:
        """Totaal aantal personen toegewezen aan deze trap"""
        return sum(v.aantal_personen for v in self.verdiepingen)
    
    def get_verdieping(self, verdieping_nr: int) -> Optional[TrapVerdieping]:
        """Haal verdieping op nummer"""
        for v in self.verdiepingen:
            if v.verdieping == verdieping_nr:
                return v
        return None
    
    def sorteer_verdiepingen(self):
        """Sorteer verdiepingen van hoog naar laag"""
        self.verdiepingen.sort(key=lambda v: v.verdieping, reverse=True)
    
    def reset_cache(self):
        """Reset alle gecachte waarden"""
        self._doorstroomcap_uitgang = None
        for v in self.verdiepingen:
            v.reset_cache()
    
    def initialiseer_verdiepingen(self, laagste: int, hoogste: int):
        """Initialiseer verdiepingen voor deze trap"""
        self.verdiepingen = []
        for verd in range(hoogste, laagste - 1, -1):
            self.verdiepingen.append(TrapVerdieping(verdieping=verd))
        self.sorteer_verdiepingen()
    
    def kopieer_naar_alle_verdiepingen(self, bron_verdieping: TrapVerdieping):
        """Kopieer instellingen van één verdieping naar alle anderen"""
        for v in self.verdiepingen:
            if v.verdieping != bron_verdieping.verdieping:
                v.doorgang_naar_trap_m = bron_verdieping.doorgang_naar_trap_m
                v.type_doorgang = bron_verdieping.type_doorgang
                v.aantal_deuren_naar_trap = bron_verdieping.aantal_deuren_naar_trap
                v.oppervlakte_bordes_m2 = bron_verdieping.oppervlakte_bordes_m2
                v.oppervlakte_tussenbordessen_m2 = bron_verdieping.oppervlakte_tussenbordessen_m2
                v.hoogteverschil_m = bron_verdieping.hoogteverschil_m
                v.breedte_trap_m = bron_verdieping.breedte_trap_m
                v.aantal_treden = bron_verdieping.aantal_treden
                v.voorportaal_actief = bron_verdieping.voorportaal_actief
                v.oppervlakte_portaal_m2 = bron_verdieping.oppervlakte_portaal_m2
                v.doorgang_portaal_m = bron_verdieping.doorgang_portaal_m
                v.type_doorgang_portaal = bron_verdieping.type_doorgang_portaal
                v.reset_cache()
