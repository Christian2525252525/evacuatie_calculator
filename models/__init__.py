"""
Models package - Datamodellen voor evacuatieberekeningen
Gebaseerd op Besluit bouwwerken leefomgeving (BBL)
"""

from .constanten import (
    DoorgangType,
    LocatieType,
    VerlaatTijdType,
    DOORGANG_FACTOREN,
    BEZETTING_DICHTHEID,
    BEZETTING_DICHTHEID_BIJEENKOMST,
    TIJDSTAP,
    ONTRUIMINGSTIJDEN,
    ONTRUIMINGSTIJD_OPTIES,
    VERLAAT_TIJDEN,
    TRAP_FACTOR_HOOG,
    TRAP_FACTOR_LAAG,
    TRAP_BREEDTE_DREMPEL,
    TRAP_OPVANG_SMAL,
    TRAP_OPVANG_BREED,
    MIN_AANTREDE,
    TIJD_VERLATEN_COMPARTIMENT,
    TIJD_VERLATEN_VERDIEPING,
    TIJD_VERLATEN_VERDIEPING_VERLENGD,
    DAALSNELHEID_PER_BOUWLAAG,
    VERDELING_TRAPPENHUIS,
)
from .trap import Trap, TrapVerdieping
from .project import Project, Verdieping

__all__ = [
    'DoorgangType',
    'LocatieType',
    'VerlaatTijdType',
    'DOORGANG_FACTOREN',
    'BEZETTING_DICHTHEID',
    'BEZETTING_DICHTHEID_BIJEENKOMST',
    'TIJDSTAP',
    'ONTRUIMINGSTIJDEN',
    'ONTRUIMINGSTIJD_OPTIES',
    'VERLAAT_TIJDEN',
    'TRAP_FACTOR_HOOG',
    'TRAP_FACTOR_LAAG',
    'TRAP_BREEDTE_DREMPEL',
    'TRAP_OPVANG_SMAL',
    'TRAP_OPVANG_BREED',
    'MIN_AANTREDE',
    'TIJD_VERLATEN_COMPARTIMENT',
    'TIJD_VERLATEN_VERDIEPING',
    'TIJD_VERLATEN_VERDIEPING_VERLENGD',
    'DAALSNELHEID_PER_BOUWLAAG',
    'VERDELING_TRAPPENHUIS',
    'Trap',
    'TrapVerdieping',
    'Project',
    'Verdieping',
]
