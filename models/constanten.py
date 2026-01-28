"""
Constanten en enumeraties voor evacuatieberekeningen
Gebaseerd op Besluit bouwwerken leefomgeving (BBL)
§ 4.2.11 Vluchtroutes: inrichting en capaciteit
Artikelen 4.80 en 4.81

Referentie: https://wetten.overheid.nl/BWBR0041297
"""

from enum import Enum
from typing import Dict


class DoorgangType(Enum):
    """
    Type doorgang met bijbehorende doorstroomfactoren
    
    BBL Artikel 4.80 lid 1 - Bij de bepaling van de doorstroomcapaciteit 
    wordt uitgegaan van:
    
    b. 90 personen per meter vrije breedte van een ruimte
    c. 90 personen per meter vrije breedte van een doorgang als zich in de 
       doorgang een dubbele deur of vergelijkbaar beweegbaar constructieonderdeel 
       bevindt met een maximale openingshoek van minder dan 135 graden
    d. 110 personen per meter vrije breedte van een doorgang als zich in de 
       doorgang een enkele deur of vergelijkbaar beweegbaar constructieonderdeel 
       bevindt met een maximale openingshoek van minder dan 135 graden
    e. 135 personen per meter vrije breedte van een andere doorgang
    
    BBL Artikel 4.81 lid 4 onder l/m:
    - 37 personen per minuut per deur tegen vluchtrichting
    """
    RUIMTE = "Ruimte"                                    # b: 90 pers/m
    DUBBELE_DEUR_LT135 = "Dubbele deur < 135°"          # c: 90 pers/m  
    ENKELE_DEUR_LT135 = "Enkele deur < 135°"            # d: 110 pers/m
    ANDERE_DOORGANG = "Andere doorgang ≥ 135°"          # e: 135 pers/m
    TEGEN_VLUCHTRICHTING = "Tegen vluchtrichting"       # 37 pers/min/deur


class LocatieType(Enum):
    """
    Type vluchtroute volgens BBL Artikel 4.81 lid 1

    De ontruimingstijd is gekoppeld aan het type vluchtroute:
    a. 30 minuten - veiligheidsvluchtroute
    b. 20 minuten - extra beschermde vluchtroute (via afzonderlijke ruimte ≥ 2m)
    c. 15 minuten - beschermde vluchtroute (andere vluchtroute)

    NB: "Binnentrap" en "Buitentrap" zijn geen BBL-categorieën voor ontruimingstijden.
    Het BBL maakt onderscheid op basis van beschermingsniveau, niet locatie.
    """
    VEILIGHEIDSVLUCHTROUTE = "Veiligheidsvluchtroute (30 min)"      # lid 1a
    EXTRA_BESCHERMD = "Extra beschermde vluchtroute (20 min)"       # lid 1b
    BESCHERMD = "Beschermde vluchtroute (15 min)"                   # lid 1c


class VerlaatTijdType(Enum):
    """
    Maximale tijd om verdieping/ruimte te verlaten volgens BBL Artikel 4.81 lid 3

    a. 3,5 minuten - standaard voor alle ruimtes
    b. 6 minuten - alleen als aan BEIDE voorwaarden is voldaan:
       1. WBDBO >= 30 min (NEN 6068) vanuit bedreigd subbrandcompartiment
       2. Rookwerendheid R200 (NEN 6075) vanuit bedreigd compartiment of
          ruimtes waardoor vluchtroute voert
    """
    STANDAARD = "Standaard (3,5 min)"                  # lid 3a
    VERLENGD = "Verlengd (6 min) - WBDBO>=30 + R200"   # lid 3b


# =============================================================================
# DOORSTROOMCAPACITEIT - BBL Artikel 4.80
# =============================================================================

# Doorstroomfactoren per type doorgang [personen/meter/minuut]
# BBL Artikel 4.80 lid 1
DOORGANG_FACTOREN: Dict[DoorgangType, int] = {
    DoorgangType.RUIMTE: 90,                    # lid b
    DoorgangType.DUBBELE_DEUR_LT135: 90,        # lid c
    DoorgangType.ENKELE_DEUR_LT135: 110,        # lid d
    DoorgangType.ANDERE_DOORGANG: 135,          # lid e
    DoorgangType.TEGEN_VLUCHTRICHTING: 37,      # lid l/m - per deur (niet per meter!)
}

# Trap doorstroomfactoren [personen/meter/minuut]
# BBL Artikel 4.80 lid 1 onder a:
# "45 personen per meter vrije breedte van een trap bij het overbruggen van 
#  een hoogteverschil van meer dan 1 m en 90 personen per meter vrije breedte 
#  bij een hoogteverschil van ten hoogste 1 m, voor zover de aantrede van de 
#  trap ten minste 0,17 m bedraagt"
TRAP_FACTOR_HOOG: int = 45   # Bij hoogteverschil > 1m
TRAP_FACTOR_LAAG: int = 90   # Bij hoogteverschil ≤ 1m

# Minimale aantrede voor trapberekening [meter]
# BBL Artikel 4.80 lid 1 onder a
MIN_AANTREDE: float = 0.17


# =============================================================================
# OPVANGCAPACITEIT - BBL Artikel 4.81
# =============================================================================

# Bezettingsdichtheid vloer/hellingbaan [personen/m²]
# BBL Artikel 4.81 lid 4 onder j:
# "de opvangcapaciteit van een vloer of hellingbaan is ten hoogste 
#  vier personen per m² vrije vloeroppervlakte"
BEZETTING_DICHTHEID: float = 4.0

# Bezettingsdichtheid bij bijeenkomstfunctie > 200 personen [personen/m²]
# BBL Artikel 4.81 lid 5:
# "Bij toepassing van het vierde lid, onder j, geldt voor een bijeenkomstfunctie 
#  een opvangcapaciteit van ten hoogste twee personen per m² vrije vloeroppervlakte 
#  als bij een tijdstap [...] meer dan 200 personen aanwezig zijn en die ruimte 
#  niet door alle personen binnen 3,5 minuut kan worden verlaten."
BEZETTING_DICHTHEID_BIJEENKOMST: float = 2.0

# Opvangcapaciteit trap [personen per trede]
# BBL Artikel 4.81 lid 4:
# h. "de opvangcapaciteit van een trap is 0,5 persoon per trede, voor zover 
#     de breedte van de trap niet groter is dan 1,1 m"
# i. "de opvangcapaciteit van een trap is 0,9 persoon per trede per m breedte 
#     van die trede, voor zover de breedte van de trap groter is dan 1,1 m en 
#     de breedte van het tredevlak groter is dan 0,17 m"
TRAP_OPVANG_SMAL: float = 0.5    # per trede, breedte ≤ 1,1m
TRAP_OPVANG_BREED: float = 0.9   # per trede per meter breedte, breedte > 1,1m

# Breedte drempel voor trap berekening [meter]
# BBL Artikel 4.81 lid 4 onder h/i
TRAP_BREEDTE_DREMPEL: float = 1.1


# =============================================================================
# ONTRUIMINGSTIJDEN - BBL Artikel 4.81 lid 1
# =============================================================================

# Ontruimingstijden per type vluchtroute [minuten]
# BBL Artikel 4.81 lid 1:
# a. 30 minuten - veiligheidsvluchtroute
# b. 20 minuten - extra beschermde vluchtroute
# c. 15 minuten - beschermde vluchtroute (andere vluchtroute)
ONTRUIMINGSTIJDEN: Dict[LocatieType, int] = {
    LocatieType.VEILIGHEIDSVLUCHTROUTE: 30,    # lid 1a
    LocatieType.EXTRA_BESCHERMD: 20,           # lid 1b
    LocatieType.BESCHERMD: 15,                 # lid 1c
}

# Beschikbare ontruimingstijden voor selectie [minuten]
ONTRUIMINGSTIJD_OPTIES: list = [15, 20, 30]


# =============================================================================
# TOETSINGSCRITERIA - BBL Artikel 4.81 lid 2 en 3
# =============================================================================

# Tijd om subbrandcompartiment te verlaten [minuten]
# BBL Artikel 4.81 lid 2:
# "De opvang- en doorstroomcapaciteit van de in het eerste lid bedoelde gedeelten 
#  van de vluchtroute is zodanig dat het bedreigde subbrandcompartiment waarin een 
#  vluchtroute begint binnen 1 minuut na aanvang van het vluchten kan worden verlaten."
TIJD_VERLATEN_COMPARTIMENT: float = 1.0

# Tijd om verdieping/ruimte te verlaten [minuten]
# BBL Artikel 4.81 lid 3:
# a. 3,5 minuten - standaard
# b. 6 minuten - als WBDBO ≥ 30 min (NEN 6068) EN rookwerendheid R200 (NEN 6075)
TIJD_VERLATEN_VERDIEPING: float = 3.5          # lid 3a - standaard
TIJD_VERLATEN_VERDIEPING_VERLENGD: float = 6.0  # lid 3b - met WBDBO en R200

# Mapping van VerlaatTijdType naar tijd in minuten
VERLAAT_TIJDEN: Dict[VerlaatTijdType, float] = {
    VerlaatTijdType.STANDAARD: 3.5,   # lid 3a
    VerlaatTijdType.VERLENGD: 6.0,    # lid 3b
}


# =============================================================================
# SIMULATIE PARAMETERS - BBL Artikel 4.81 lid 4
# =============================================================================

# Tijdstap lengte voor simulatie [minuten]
# BBL Artikel 4.81 lid 4 onder a:
# "een tijdstap is 0,5 minuut"
TIJDSTAP: float = 0.5

# Daalsnelheid per bouwlaag [seconden]
# BBL Artikel 4.81 lid 4 onder g:
# "de daalsnelheid is 30 seconden per bouwlaag voor zover de vluchtroute 
#  over een trap of door een trappenhuis voert"
DAALSNELHEID_PER_BOUWLAAG: float = 30.0  # seconden

# Hoogteverschil tussen bouwlagen [meter]
# BBL Artikel 4.81 lid 4 onder f:
# "het hoogteverschil tussen bouwlagen in het trappenhuis is ten minste 2,1 m 
#  en ten hoogste 4 m"
MIN_HOOGTEVERSCHIL_BOUWLAAG: float = 2.1
MAX_HOOGTEVERSCHIL_BOUWLAAG: float = 4.0

# Capaciteitsverdeling bij samenkomende routes
# BBL Artikel 4.81 lid 4 onder e:
# "bij samenkomst in een trappenhuis wordt 50% van de beschikbare capaciteit 
#  toegedeeld aan het bovengelegen deel van het trappenhuis"
VERDELING_TRAPPENHUIS: float = 0.5


# =============================================================================
# STANDAARD WAARDEN VOOR INVOER
# =============================================================================

STANDAARD_HOOGTEVERSCHIL: float = 3.0       # meter
STANDAARD_TRAPBREEDTE: float = 1.1          # meter  
STANDAARD_AANTAL_TREDEN: int = 18           # treden
STANDAARD_BORDES_OPP: float = 4.0           # m²
STANDAARD_TUSSENBORDES_OPP: float = 3.0     # m²
STANDAARD_DOORGANG_BREEDTE: float = 0.9     # meter
