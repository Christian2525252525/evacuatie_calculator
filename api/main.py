"""
FastAPI Backend voor Evacuatie Calculator Web Versie
Biedt REST API voor BBL Art. 4.80/4.81 berekeningen
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import sys
import os

# Voeg parent directory toe voor imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    Project, Trap, TrapVerdieping, Verdieping,
    DoorgangType, LocatieType, VerlaatTijdType
)
from berekeningen import simuleer_alle_trappen, toets_alle_resultaten
from berekeningen.capaciteit import bereken_max_personen_trap

app = FastAPI(
    title="Evacuatie Calculator API",
    description="BBL Art. 4.80/4.81 - Berekening opvang- en doorstroomcapaciteit trappenhuizen",
    version="1.0.0"
)

# CORS configuratie voor frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In productie: specifieke origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Pydantic Models voor API ===

class DoorgangTypeEnum(str, Enum):
    ENKELE_DEUR = "Enkele deur < 1.2m"
    DUBBELE_DEUR = "Dubbele deur >= 1.2m"
    VRIJE_DOORGANG = "Vrije doorgang"


class LocatieTypeEnum(str, Enum):
    VEILIGHEIDSVLUCHTROUTE = "Veiligheidsvluchtroute"
    EXTRA_BESCHERMD = "Extra beschermde vluchtroute"
    BESCHERMD = "Beschermde vluchtroute"


class VerlaatTijdTypeEnum(str, Enum):
    STANDAARD = "Standaard (3,5 min)"
    VERLENGD = "Verlengd (6 min)"


class TrapVerdiepingInput(BaseModel):
    """Input voor verdieping-specifieke trap eigenschappen"""
    verdieping: int
    doorgang_naar_trap_m: float = Field(0.85, ge=0.5, le=5.0, description="Breedte toegangsdeur naar trap [m]")
    type_doorgang: DoorgangTypeEnum = DoorgangTypeEnum.ENKELE_DEUR
    oppervlakte_bordes_m2: float = Field(2.0, ge=0, description="Oppervlakte bordes [m²]")
    oppervlakte_tussenbordessen_m2: float = Field(1.5, ge=0, description="Oppervlakte tussenbordessen [m²]")
    hoogteverschil_m: float = Field(3.0, ge=2.0, le=6.0, description="Hoogteverschil [m]")
    breedte_trap_m: float = Field(1.1, ge=0.8, le=3.0, description="Breedte trap [m]")
    aantal_treden: int = Field(20, ge=10, le=40, description="Aantal treden")
    verdeling_fractie: float = Field(1.0, ge=0, le=1, description="Verdeling percentage (0-1)")
    aantal_personen: int = Field(0, ge=0, description="Aantal personen op deze verdieping")


class TrapInput(BaseModel):
    """Input voor een trappenhuis"""
    aanduiding: str = Field("Trap A", description="Naam/aanduiding van de trap")
    locatie: LocatieTypeEnum = LocatieTypeEnum.BESCHERMD
    doorgang_uitgang_m: float = Field(1.2, ge=0.5, le=5.0, description="Breedte uitgang [m]")
    type_uitgang: DoorgangTypeEnum = DoorgangTypeEnum.DUBBELE_DEUR
    verlaat_tijd_type: VerlaatTijdTypeEnum = VerlaatTijdTypeEnum.STANDAARD
    verdiepingen_onder_uitgang: int = Field(0, ge=0, le=10)
    voorportaal_aanwezig: bool = False
    verdiepingen: List[TrapVerdiepingInput]


class ProjectInput(BaseModel):
    """Input voor een compleet project"""
    projectnaam: str = Field("Nieuw Project", description="Projectnaam")
    trappen: List[TrapInput]


class SnelleBerekening(BaseModel):
    """Input voor snelle capaciteitsberekening (zonder volledige simulatie)"""
    doorgang_uitgang_m: float = Field(1.2, ge=0.5, le=5.0)
    type_uitgang: DoorgangTypeEnum = DoorgangTypeEnum.DUBBELE_DEUR
    locatie: LocatieTypeEnum = LocatieTypeEnum.BESCHERMD
    aantal_verdiepingen: int = Field(10, ge=1, le=60)
    breedte_trap_m: float = Field(1.1, ge=0.8, le=3.0)
    oppervlakte_bordes_m2: float = Field(2.0, ge=0)
    doorgang_naar_trap_m: float = Field(0.85, ge=0.5, le=5.0)
    type_doorgang: DoorgangTypeEnum = DoorgangTypeEnum.ENKELE_DEUR


# === Helper functies ===

def _convert_doorgang_type(dt: DoorgangTypeEnum) -> DoorgangType:
    """Converteer API enum naar model enum"""
    mapping = {
        DoorgangTypeEnum.ENKELE_DEUR: DoorgangType.ENKELE_DEUR,
        DoorgangTypeEnum.DUBBELE_DEUR: DoorgangType.DUBBELE_DEUR,
        DoorgangTypeEnum.VRIJE_DOORGANG: DoorgangType.VRIJE_DOORGANG,
    }
    return mapping[dt]


def _convert_locatie_type(lt: LocatieTypeEnum) -> LocatieType:
    """Converteer API enum naar model enum"""
    mapping = {
        LocatieTypeEnum.VEILIGHEIDSVLUCHTROUTE: LocatieType.VEILIGHEIDSVLUCHTROUTE,
        LocatieTypeEnum.EXTRA_BESCHERMD: LocatieType.EXTRA_BESCHERMD,
        LocatieTypeEnum.BESCHERMD: LocatieType.BESCHERMD,
    }
    return mapping[lt]


def _convert_verlaat_tijd_type(vt: VerlaatTijdTypeEnum) -> VerlaatTijdType:
    """Converteer API enum naar model enum"""
    mapping = {
        VerlaatTijdTypeEnum.STANDAARD: VerlaatTijdType.STANDAARD,
        VerlaatTijdTypeEnum.VERLENGD: VerlaatTijdType.VERLENGD,
    }
    return mapping[vt]


def _create_trap_from_input(trap_input: TrapInput) -> Trap:
    """Maak een Trap object van API input"""
    trap = Trap(aanduiding=trap_input.aanduiding)
    trap.locatie = _convert_locatie_type(trap_input.locatie)
    trap.doorgang_uitgang_m = trap_input.doorgang_uitgang_m
    trap.type_uitgang = _convert_doorgang_type(trap_input.type_uitgang)
    trap.verlaat_tijd_type = _convert_verlaat_tijd_type(trap_input.verlaat_tijd_type)
    trap.verdiepingen_onder_uitgang = trap_input.verdiepingen_onder_uitgang
    trap.voorportaal_aanwezig = trap_input.voorportaal_aanwezig

    # Voeg verdiepingen toe
    trap.verdiepingen = []
    for tv_input in trap_input.verdiepingen:
        tv = TrapVerdieping(verdieping=tv_input.verdieping)
        tv.doorgang_naar_trap_m = tv_input.doorgang_naar_trap_m
        tv.type_doorgang = _convert_doorgang_type(tv_input.type_doorgang)
        tv.oppervlakte_bordes_m2 = tv_input.oppervlakte_bordes_m2
        tv.oppervlakte_tussenbordessen_m2 = tv_input.oppervlakte_tussenbordessen_m2
        tv.hoogteverschil_m = tv_input.hoogteverschil_m
        tv.breedte_trap_m = tv_input.breedte_trap_m
        tv.aantal_treden = tv_input.aantal_treden
        tv.verdeling_fractie = tv_input.verdeling_fractie
        tv.aantal_personen = tv_input.aantal_personen
        tv.voorportaal_actief = trap_input.voorportaal_aanwezig
        trap.verdiepingen.append(tv)

    return trap


# === API Endpoints ===

@app.get("/")
async def root():
    """API status check"""
    return {
        "status": "online",
        "app": "Evacuatie Calculator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/enums")
async def get_enums():
    """Haal beschikbare enum waarden op voor dropdowns"""
    return {
        "doorgang_types": [
            {"value": dt.value, "label": dt.value} for dt in DoorgangTypeEnum
        ],
        "locatie_types": [
            {"value": lt.value, "label": lt.value} for lt in LocatieTypeEnum
        ],
        "verlaat_tijd_types": [
            {"value": vt.value, "label": vt.value} for vt in VerlaatTijdTypeEnum
        ],
        "ontruimingstijden": {
            LocatieTypeEnum.VEILIGHEIDSVLUCHTROUTE.value: 30,
            LocatieTypeEnum.EXTRA_BESCHERMD.value: 20,
            LocatieTypeEnum.BESCHERMD.value: 15,
        }
    }


@app.post("/api/bereken/snel")
async def bereken_snel(input: SnelleBerekening):
    """
    Snelle capaciteitsberekening zonder volledige simulatie.
    Geeft max personen volgens BBL lid 1 en lid 2.
    """
    try:
        # Maak dummy verdiepingen voor berekening
        verdiepingen = []
        for i in range(input.aantal_verdiepingen):
            tv = TrapVerdieping(verdieping=i)
            tv.doorgang_naar_trap_m = input.doorgang_naar_trap_m
            tv.type_doorgang = _convert_doorgang_type(input.type_doorgang)
            tv.oppervlakte_bordes_m2 = input.oppervlakte_bordes_m2
            tv.breedte_trap_m = input.breedte_trap_m
            verdiepingen.append(tv)

        # Bepaal ontruimingstijd op basis van locatie
        ontruimingstijd_map = {
            LocatieTypeEnum.VEILIGHEIDSVLUCHTROUTE: 30,
            LocatieTypeEnum.EXTRA_BESCHERMD: 20,
            LocatieTypeEnum.BESCHERMD: 15,
        }
        ontruimingstijd = ontruimingstijd_map[input.locatie]

        # Bereken max capaciteit
        result = bereken_max_personen_trap(
            input.doorgang_uitgang_m,
            _convert_doorgang_type(input.type_uitgang),
            ontruimingstijd,
            verdiepingen
        )

        return {
            "success": True,
            "max_personen_totaal": result['max_personen'],
            "max_personen_per_verdieping": result.get('max_per_verdieping'),
            "bottleneck": result['bottleneck'],
            "doorstroom_uitgang_per_min": result['doorstroom_uitgang_per_min'],
            "ontruimingstijd_min": ontruimingstijd,
            "details": result.get('details', [])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/bereken/volledig")
async def bereken_volledig(project: ProjectInput):
    """
    Volledige simulatie met toetsing aan BBL Art. 4.81.
    """
    try:
        # Converteer input naar Trap objecten
        trappen = [_create_trap_from_input(t) for t in project.trappen]

        # Voer simulatie uit
        resultaten = simuleer_alle_trappen(trappen)

        # Toets resultaten
        toetsingen = toets_alle_resultaten(resultaten, trappen=trappen)

        # Formatteer response
        response = {
            "success": True,
            "projectnaam": project.projectnaam,
            "trappen": []
        }

        for trap in trappen:
            naam = trap.aanduiding
            sim_res = resultaten.get(naam)
            toets_res = toetsingen.get(naam)

            # Bereken max capaciteit
            max_info = bereken_max_personen_trap(
                trap.doorgang_uitgang_m,
                trap.type_uitgang,
                trap.ontruimingstijd_min,
                trap.verdiepingen
            )

            trap_result = {
                "naam": naam,
                "totaal_personen": sim_res.totaal_personen if sim_res else 0,
                "ontruimingstijd_min": trap.ontruimingstijd_min,
                "max_personen_totaal": max_info['max_personen'],
                "max_personen_per_verdieping": max_info.get('max_per_verdieping'),
                "bottleneck": max_info['bottleneck'],
                "doorstroom_uitgang_per_min": max_info['doorstroom_uitgang_per_min'],
                "eindstand_buiten": sim_res.eindstand_buiten if sim_res else 0,
                "voldoet": toets_res.alle_criteria_voldaan if toets_res else False,
                "toetsing": []
            }

            # Voeg toetscriteria toe
            if toets_res:
                for criterium in toets_res.criteria:
                    trap_result["toetsing"].append({
                        "naam": criterium.naam,
                        "beschrijving": criterium.beschrijving,
                        "eis": criterium.eis,
                        "berekend": criterium.berekend,
                        "eenheid": criterium.eenheid,
                        "voldoet": criterium.status.value == "voldoet",
                        "toelichting": criterium.toelichting
                    })

            # Voeg details per verdieping toe
            if max_info.get('details'):
                trap_result["details_per_verdieping"] = max_info['details']

            response["trappen"].append(trap_result)

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/standaardwaarden")
async def get_standaardwaarden():
    """Haal BBL standaardwaarden op"""
    return {
        "doorstroomcapaciteit": {
            "enkele_deur": "45 personen per meter per minuut",
            "dubbele_deur": "90 personen per meter per minuut",
            "vrije_doorgang": "90 personen per meter per minuut",
            "trap": "60 personen per meter per minuut"
        },
        "opvangcapaciteit": {
            "bordes": "3 personen per m²",
            "treden": "2 personen per trede per meter breedte"
        },
        "ontruimingstijden": {
            "veiligheidsvluchtroute": "30 minuten",
            "extra_beschermde_vluchtroute": "20 minuten",
            "beschermde_vluchtroute": "15 minuten"
        },
        "verlaten_verdieping": {
            "standaard": "3,5 minuten",
            "verlengd": "6 minuten (WBDBO >= 30 min + R200)"
        },
        "verlaten_compartiment": "1 minuut"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
