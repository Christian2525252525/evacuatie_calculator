"""
Simulatie Engine voor Evacuatieberekeningen
Discrete tijdstap simulatie (0.5 minuten per stap)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.constanten import TIJDSTAP, DoorgangType, DAALSNELHEID_PER_BOUWLAAG
from models.trap import Trap, TrapVerdieping
from berekeningen.capaciteit import (
    bereken_doorstroomcapaciteit_deur,
    bereken_doorstroomcapaciteit_trap,
    bereken_opslagcapaciteit_trappenhuis,
    bereken_voorportaal_capaciteiten,
)


@dataclass
class VerdiepingState:
    """Status van een verdieping op een bepaald moment"""
    verdieping: int
    personen_op_verdieping: float = 0.0
    personen_in_portaal: float = 0.0
    personen_in_trap: float = 0.0
    instroom_naar_trap: float = 0.0
    uitstroom_van_trap: float = 0.0


@dataclass
class TijdstapResultaat:
    """Resultaat van één tijdstap"""
    tijdstap: int
    tijd_min: float
    naar_buiten: float = 0.0
    cumulatief_buiten: float = 0.0
    verdieping_states: Dict[int, VerdiepingState] = field(default_factory=dict)
    totaal_in_trap: float = 0.0
    totaal_op_verdiepingen: float = 0.0
    totaal_in_portalen: float = 0.0


@dataclass
class SimulatieResultaat:
    """Volledig resultaat van een simulatie"""
    trap_aanduiding: str
    ontruimingstijd_min: float
    totaal_personen: int
    tijdstappen: List[TijdstapResultaat] = field(default_factory=list)
    voltooide_ontruiming_min: Optional[float] = None
    
    @property
    def eindstand_buiten(self) -> float:
        """Aantal personen buiten aan einde simulatie"""
        if self.tijdstappen:
            return self.tijdstappen[-1].cumulatief_buiten
        return 0.0
    
    @property
    def is_voltooid(self) -> bool:
        """Is de ontruiming voltooid binnen de tijd?"""
        # Gebruik kleine tolerantie voor floating-point vergelijking
        return self.eindstand_buiten >= self.totaal_personen - 0.01
    
    def get_personen_buiten_op_tijd(self, tijd_min: float) -> float:
        """Haal aantal personen buiten op specifiek tijdstip"""
        for ts in self.tijdstappen:
            if ts.tijd_min >= tijd_min:
                return ts.cumulatief_buiten
        return self.eindstand_buiten


class SimulatieEngine:
    """
    Engine voor het simuleren van evacuatie door trappenhuizen.
    
    De simulatie werkt in discrete tijdstappen van 0.5 minuten.
    Per tijdstap worden personen verplaatst door het systeem:
    
    1. Van verdieping -> voorportaal (indien aanwezig)
    2. Van voorportaal/verdieping -> trappenhuis
    3. Door trappenhuis omlaag
    4. Uit trappenhuis naar buiten
    """
    
    def __init__(self, trap: Trap):
        self.trap = trap
        self._bereken_capaciteiten()
        self._initialiseer_state()
    
    def _bereken_capaciteiten(self):
        """Bereken alle capaciteiten voor alle verdiepingen"""
        for v in self.trap.verdiepingen:
            # Doorstroomcapaciteit deur naar trap (× aantal deuren)
            v._doorstroomcap_deur = bereken_doorstroomcapaciteit_deur(
                v.doorgang_naar_trap_m, v.type_doorgang
            ) * v.aantal_deuren_naar_trap
            
            # Doorstroomcapaciteit trap
            v._doorstroomcap_trap = bereken_doorstroomcapaciteit_trap(
                v.breedte_trap_m, v.hoogteverschil_m
            )
            
            # Opslagcapaciteit trappenhuis
            v._opslagcapaciteit = bereken_opslagcapaciteit_trappenhuis(
                v.oppervlakte_bordes_m2,
                v.oppervlakte_tussenbordessen_m2,
                v.breedte_trap_m,
                v.aantal_treden,
                v._doorstroomcap_trap
            )
            
            # Voorportaal capaciteiten
            v._opslagcap_portaal, v._doorstroomcap_portaal = bereken_voorportaal_capaciteiten(
                v.oppervlakte_portaal_m2,
                v.doorgang_portaal_m,
                v.type_doorgang_portaal,
                v.voorportaal_actief
            )
        
        # Doorstroomcapaciteit uitgang (× aantal deuren)
        self.trap._doorstroomcap_uitgang = bereken_doorstroomcapaciteit_deur(
            self.trap.doorgang_uitgang_m, self.trap.type_uitgang
        ) * self.trap.aantal_deuren_uitgang
    
    def _initialiseer_state(self):
        """Initialiseer simulatie state"""
        self.personen_op_verdieping = {}
        self.personen_in_portaal = {}
        self.personen_in_trap = {}
        
        for v in self.trap.verdiepingen:
            vn = v.verdieping
            self.personen_op_verdieping[vn] = float(v.aantal_personen)
            self.personen_in_portaal[vn] = 0.0
            self.personen_in_trap[vn] = 0.0
        
        self.cumulatief_buiten = 0.0
    
    def _get_verdieping(self, nummer: int) -> Optional[TrapVerdieping]:
        """Haal verdieping configuratie"""
        return self.trap.get_verdieping(nummer)
    
    def _get_verdiepingen_gesorteerd(self) -> List[int]:
        """Haal verdieping nummers, gesorteerd van laag naar hoog"""
        return sorted([v.verdieping for v in self.trap.verdiepingen])
    
    def _bereken_beschikbare_ruimte(self, verdieping: int, instroom_van_boven: float) -> float:
        """
        Bereken hoeveel ruimte er is in de trap op deze verdieping.
        
        Houdt rekening met:
        - Huidige bezetting
        - Opslagcapaciteit
        - Doorstroomcapaciteit
        - Instroom van hogere verdiepingen
        """
        v = self._get_verdieping(verdieping)
        if v is None:
            return 0.0
        
        huidige_bezetting = self.personen_in_trap.get(verdieping, 0.0)
        
        # Totale beschikbare ruimte
        totale_ruimte = v._opslagcapaciteit + v._doorstroomcap_trap - huidige_bezetting
        
        if totale_ruimte <= 0:
            return 0.0
        
        # Als er veel instroom van boven is, halveer beschikbare ruimte
        if instroom_van_boven > totale_ruimte / 2:
            return max(0.0, totale_ruimte / 2)
        else:
            return max(0.0, totale_ruimte - instroom_van_boven)
    
    def _simuleer_tijdstap(self, stap: int, tijd_min: float) -> TijdstapResultaat:
        """
        Simuleer één tijdstap.

        De volgorde van verwerking implementeert de daalvertraging volgens BBL 4.81 lid 4g:
        - Daalsnelheid is 30 seconden (0.5 min = 1 tijdstap) per bouwlaag
        - Personen moeten eerst een tijdstap in de trap zijn voordat ze kunnen doorstromen

        Volgorde:
        1. Uitstroom naar buiten (personen die al in trap waren)
        2. Doorstroom door trap (van hoog naar laag, 1 verdieping per tijdstap)
        3. Instroom in trap (nieuwe personen van verdiepingen)
        """
        resultaat = TijdstapResultaat(tijdstap=stap, tijd_min=tijd_min)

        verdiepingen = self._get_verdiepingen_gesorteerd()
        uitgang_verd = self.trap.uitgang_verdieping

        # ===== FASE 1: Uitstroom naar buiten =====
        # Alleen personen die al in de trap zaten (van vorige tijdstap) kunnen naar buiten
        beschikbaar_voor_uitgang = self.personen_in_trap.get(uitgang_verd, 0.0)

        naar_buiten = min(self.trap._doorstroomcap_uitgang, beschikbaar_voor_uitgang)

        # Update: haal personen uit trap op uitgang niveau
        self.personen_in_trap[uitgang_verd] = max(
            0.0,
            self.personen_in_trap.get(uitgang_verd, 0.0) - naar_buiten
        )

        self.cumulatief_buiten += naar_buiten
        resultaat.naar_buiten = naar_buiten
        resultaat.cumulatief_buiten = self.cumulatief_buiten

        # ===== FASE 2: Doorstroom door trap (van hoog naar laag) =====
        # Personen in de trap bewegen naar beneden (max 1 verdieping per tijdstap = daalsnelheid)
        for vn in reversed(verdiepingen):
            if vn <= uitgang_verd:
                # Op of onder uitgang niveau - geen verdere doorstroom door trap
                continue

            v = self._get_verdieping(vn)
            if v is None:
                continue

            in_trap = self.personen_in_trap.get(vn, 0.0)
            if in_trap <= 0:
                continue

            # Doorstroom capaciteit trap
            max_doorstroom = v._doorstroomcap_trap

            # Werkelijke doorstroom
            doorstroom = min(in_trap, max_doorstroom)

            # Verplaats naar lagere verdieping
            lagere_verd = vn - 1

            # Check beschikbare ruimte op lagere verdieping
            lagere_v = self._get_verdieping(lagere_verd)
            if lagere_v:
                bezetting_lager = self.personen_in_trap.get(lagere_verd, 0.0)
                if lagere_verd == uitgang_verd:
                    # Uitgang niveau: cascade model - gebruik FE_cap als capaciteitsgrens
                    # ipv opslagcap van het bordes. Personen stromen direct door naar de
                    # uitgang, beperkt door de breedte van de uitgangsdeur (BBL cascade).
                    ruimte_lager = max(0.0, self.trap._doorstroomcap_uitgang - bezetting_lager)
                else:
                    ruimte_lager = max(0.0, lagere_v._opslagcapaciteit - bezetting_lager)
                doorstroom = min(doorstroom, ruimte_lager)

            # Update bezettingen
            self.personen_in_trap[vn] -= doorstroom
            self.personen_in_trap[lagere_verd] = self.personen_in_trap.get(lagere_verd, 0.0) + doorstroom

        # ===== FASE 3: Instroom in trap (van hoog naar laag) =====
        # Personen gaan van verdieping/portaal naar trap
        for vn in reversed(verdiepingen):
            v = self._get_verdieping(vn)
            if v is None:
                continue

            # Check gefaseerde ontruiming vertraging
            if v.gefaseerde_vertraging_min > tijd_min:
                continue

            # Hoeveel personen zijn er op deze verdieping?
            op_verdieping = self.personen_op_verdieping.get(vn, 0.0)
            in_portaal = self.personen_in_portaal.get(vn, 0.0)

            if op_verdieping <= 0 and in_portaal <= 0:
                continue

            # Bereken beschikbare ruimte in trap
            huidige_bezetting = self.personen_in_trap.get(vn, 0.0)
            ruimte_in_trap = max(0.0, v._opslagcapaciteit - huidige_bezetting)

            if v.voorportaal_actief and v._doorstroomcap_portaal > 0:
                # Met voorportaal: personen gaan eerst naar portaal, dan naar trap

                # Stap 3a: Van verdieping naar portaal
                ruimte_in_portaal = max(0.0, v._opslagcap_portaal - in_portaal)
                naar_portaal = min(
                    v._doorstroomcap_portaal,
                    op_verdieping,
                    ruimte_in_portaal
                )

                self.personen_op_verdieping[vn] -= naar_portaal
                self.personen_in_portaal[vn] += naar_portaal
                in_portaal += naar_portaal

                # Stap 3b: Van portaal naar trap
                naar_trap = min(
                    v._doorstroomcap_deur,
                    in_portaal,
                    ruimte_in_trap
                )

                self.personen_in_portaal[vn] -= naar_trap
                self.personen_in_trap[vn] += naar_trap

            else:
                # Zonder voorportaal: direct van verdieping naar trap
                naar_trap = min(
                    v._doorstroomcap_deur,
                    op_verdieping,
                    ruimte_in_trap
                )

                self.personen_op_verdieping[vn] -= naar_trap
                self.personen_in_trap[vn] += naar_trap
        
        # ===== Verzamel resultaten =====
        for vn in verdiepingen:
            resultaat.verdieping_states[vn] = VerdiepingState(
                verdieping=vn,
                personen_op_verdieping=self.personen_op_verdieping.get(vn, 0.0),
                personen_in_portaal=self.personen_in_portaal.get(vn, 0.0),
                personen_in_trap=self.personen_in_trap.get(vn, 0.0),
            )
        
        resultaat.totaal_in_trap = sum(self.personen_in_trap.values())
        resultaat.totaal_op_verdiepingen = sum(self.personen_op_verdieping.values())
        resultaat.totaal_in_portalen = sum(self.personen_in_portaal.values())
        
        return resultaat
    
    def simuleer(self, max_tijd_min: float = None) -> SimulatieResultaat:
        """
        Voer volledige simulatie uit.
        
        Args:
            max_tijd_min: Maximale simulatietijd in minuten. 
                         Standaard: ontruimingstijd van trap.
        
        Returns:
            SimulatieResultaat met alle tijdstappen
        """
        if max_tijd_min is None:
            max_tijd_min = self.trap.ontruimingstijd_min
        
        # Reset state
        self._initialiseer_state()
        
        totaal_personen = self.trap.totaal_personen
        
        resultaat = SimulatieResultaat(
            trap_aanduiding=self.trap.aanduiding,
            ontruimingstijd_min=max_tijd_min,
            totaal_personen=totaal_personen
        )
        
        # Aantal tijdstappen
        aantal_stappen = int(max_tijd_min / TIJDSTAP) + 1
        
        for stap in range(aantal_stappen):
            tijd = stap * TIJDSTAP
            
            ts_resultaat = self._simuleer_tijdstap(stap, tijd)
            resultaat.tijdstappen.append(ts_resultaat)
            
            # Check of ontruiming voltooid is (met kleine tolerantie voor floating-point)
            if (ts_resultaat.cumulatief_buiten >= totaal_personen - 0.01 and
                resultaat.voltooide_ontruiming_min is None):
                resultaat.voltooide_ontruiming_min = tijd
        
        return resultaat


def simuleer_alle_trappen(trappen: List[Trap], max_tijd_min: float = None) -> Dict[str, SimulatieResultaat]:
    """
    Simuleer alle trappen.
    
    Args:
        trappen: Lijst van Trap objecten
        max_tijd_min: Maximale simulatietijd (gebruikt langste ontruimingstijd indien None)
    
    Returns:
        Dict met trap aanduiding als key en SimulatieResultaat als value
    """
    resultaten = {}
    
    for trap in trappen:
        tijd = max_tijd_min if max_tijd_min else trap.ontruimingstijd_min
        engine = SimulatieEngine(trap)
        resultaten[trap.aanduiding] = engine.simuleer(tijd)
    
    return resultaten
