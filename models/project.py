"""
Gebouw en Project datamodellen
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date
from .trap import Trap, TrapVerdieping
from .constanten import DoorgangType


@dataclass
class Verdieping:
    """Verdieping van het gebouw met aantal personen"""
    nummer: int
    aantal_personen: int = 0
    
    def __post_init__(self):
        if self.aantal_personen < 0:
            self.aantal_personen = 0


@dataclass
class Project:
    """Projectgegevens en gebouwconfiguratie"""
    # Projectgegevens
    projectnaam: str = "Nieuw Project"
    omschrijving: str = ""
    projectnummer: str = ""
    gebruiker: str = ""
    datum_berekeningen: date = field(default_factory=date.today)
    datum_tekeningen: Optional[date] = None
    
    # Gebouwconfiguratie
    aantal_trappen: int = 1
    aantal_bouwlagen: int = 10
    laagste_verdieping: int = 0
    voorportalen_aanwezig: bool = False
    
    # Data
    verdiepingen: List[Verdieping] = field(default_factory=list)
    trappen: List[Trap] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialiseer verdiepingen en trappen indien leeg"""
        if not self.verdiepingen:
            self.initialiseer_verdiepingen()
        if not self.trappen:
            self.initialiseer_trappen()
    
    @property
    def hoogste_verdieping(self) -> int:
        """Hoogste verdieping nummer"""
        return self.laagste_verdieping + self.aantal_bouwlagen - 1
    
    @property
    def totaal_personen(self) -> int:
        """Totaal aantal personen in gebouw"""
        return sum(v.aantal_personen for v in self.verdiepingen)
    
    def initialiseer_verdiepingen(self):
        """Maak verdiepingen aan op basis van configuratie"""
        self.verdiepingen = []
        for i in range(self.hoogste_verdieping, self.laagste_verdieping - 1, -1):
            self.verdiepingen.append(Verdieping(nummer=i, aantal_personen=0))
    
    def initialiseer_trappen(self):
        """Maak trappen aan op basis van configuratie"""
        self.trappen = []
        trap_letters = "ABCDEFGHIJ"
        for i in range(self.aantal_trappen):
            letter = trap_letters[i] if i < len(trap_letters) else str(i + 1)
            trap = Trap(
                aanduiding=f"Trap {letter}",
                voorportaal_aanwezig=self.voorportalen_aanwezig
            )
            trap.initialiseer_verdiepingen(
                self.laagste_verdieping,
                self.hoogste_verdieping
            )
            self.trappen.append(trap)
    
    def update_configuratie(self, aantal_trappen: int, aantal_bouwlagen: int,
                           laagste_verdieping: int, voorportalen: bool):
        """Update gebouwconfiguratie en herinitialiseer indien nodig"""
        configuratie_gewijzigd = (
            aantal_trappen != self.aantal_trappen or
            aantal_bouwlagen != self.aantal_bouwlagen or
            laagste_verdieping != self.laagste_verdieping
        )
        
        self.aantal_trappen = aantal_trappen
        self.aantal_bouwlagen = aantal_bouwlagen
        self.laagste_verdieping = laagste_verdieping
        self.voorportalen_aanwezig = voorportalen
        
        if configuratie_gewijzigd:
            # Bewaar oude data waar mogelijk
            oude_personen = {v.nummer: v.aantal_personen for v in self.verdiepingen}
            
            self.initialiseer_verdiepingen()
            self.initialiseer_trappen()
            
            # Herstel personen aantallen
            for v in self.verdiepingen:
                if v.nummer in oude_personen:
                    v.aantal_personen = oude_personen[v.nummer]
        
        # Update voorportaal setting voor alle trappen
        for trap in self.trappen:
            trap.voorportaal_aanwezig = voorportalen
            for tv in trap.verdiepingen:
                tv.voorportaal_actief = voorportalen
    
    def get_verdieping(self, nummer: int) -> Optional[Verdieping]:
        """Haal verdieping op nummer"""
        for v in self.verdiepingen:
            if v.nummer == nummer:
                return v
        return None
    
    def verdeel_personen_over_trappen(self, verdeling: str = "gelijk"):
        """
        Verdeel personen over trappen
        
        Args:
            verdeling: 'gelijk' voor gelijke verdeling, of dict met percentages per trap
        """
        if not self.trappen:
            return
        
        if verdeling == "gelijk":
            # Gelijke verdeling over alle trappen
            fractie = 1.0 / len(self.trappen)
            for trap in self.trappen:
                for tv in trap.verdiepingen:
                    tv.verdeling_fractie = fractie
        
        # Bereken aantal personen per trap verdieping
        for trap in self.trappen:
            for tv in trap.verdiepingen:
                gebouw_verd = self.get_verdieping(tv.verdieping)
                if gebouw_verd:
                    tv.aantal_personen = int(
                        gebouw_verd.aantal_personen * tv.verdeling_fractie
                    )
    
    def to_dict(self) -> dict:
        """Converteer naar dictionary voor opslag"""
        return {
            'projectnaam': self.projectnaam,
            'omschrijving': self.omschrijving,
            'projectnummer': self.projectnummer,
            'gebruiker': self.gebruiker,
            'datum_berekeningen': self.datum_berekeningen.isoformat(),
            'datum_tekeningen': self.datum_tekeningen.isoformat() if self.datum_tekeningen else None,
            'aantal_trappen': self.aantal_trappen,
            'aantal_bouwlagen': self.aantal_bouwlagen,
            'laagste_verdieping': self.laagste_verdieping,
            'voorportalen_aanwezig': self.voorportalen_aanwezig,
            'verdiepingen': [
                {'nummer': v.nummer, 'aantal_personen': v.aantal_personen}
                for v in self.verdiepingen
            ],
            # Trappen worden apart opgeslagen vanwege complexiteit
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        """Laad project van dictionary"""
        project = cls(
            projectnaam=data.get('projectnaam', 'Nieuw Project'),
            omschrijving=data.get('omschrijving', ''),
            projectnummer=data.get('projectnummer', ''),
            gebruiker=data.get('gebruiker', ''),
            datum_berekeningen=date.fromisoformat(data['datum_berekeningen']) if data.get('datum_berekeningen') else date.today(),
            datum_tekeningen=date.fromisoformat(data['datum_tekeningen']) if data.get('datum_tekeningen') else None,
            aantal_trappen=data.get('aantal_trappen', 1),
            aantal_bouwlagen=data.get('aantal_bouwlagen', 10),
            laagste_verdieping=data.get('laagste_verdieping', 0),
            voorportalen_aanwezig=data.get('voorportalen_aanwezig', False),
        )
        
        # Laad verdiepingen
        if 'verdiepingen' in data:
            project.verdiepingen = [
                Verdieping(nummer=v['nummer'], aantal_personen=v['aantal_personen'])
                for v in data['verdiepingen']
            ]
        
        return project
