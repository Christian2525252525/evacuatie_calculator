"""
PDF Rapport Generator
Genereert professionele PDF rapporten van evacuatieberekeningen
"""

import sys
import os
from typing import Dict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Project
from berekeningen import SimulatieResultaat, ToetsResultaat, ToetsStatus


def genereer_pdf_rapport(
    bestandsnaam: str,
    project: Project,
    resultaten: Dict[str, SimulatieResultaat],
    toetsingen: Dict[str, ToetsResultaat]
):
    """
    Genereer een PDF rapport van de evacuatieberekening.
    
    Args:
        bestandsnaam: Pad naar output PDF bestand
        project: Project met gebouwgegevens
        resultaten: Simulatieresultaten per trap
        toetsingen: Toetsresultaten per trap
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, Image
        )
        from reportlab.lib import colors
    except ImportError:
        # Fallback: genereer simpel tekst rapport
        _genereer_tekst_rapport(bestandsnaam, project, resultaten, toetsingen)
        return
    
    # Document setup
    doc = SimpleDocTemplate(
        bestandsnaam,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    titel_style = ParagraphStyle(
        'Titel',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=10*mm,
        textColor=HexColor('#1a5276')
    )
    
    subtitel_style = ParagraphStyle(
        'Subtitel',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=5*mm,
        spaceAfter=3*mm,
        textColor=HexColor('#2874a6')
    )
    
    normaal_style = styles['Normal']
    
    # Content
    content = []
    
    # Titel
    content.append(Paragraph(
        "Evacuatie Doorstroom Capaciteitsberekening",
        titel_style
    ))
    
    # Projectgegevens
    content.append(Paragraph("Projectgegevens", subtitel_style))
    
    project_data = [
        ["Projectnaam:", project.projectnaam],
        ["Scenario:", project.omschrijving],
        ["Projectnummer:", project.projectnummer],
        ["Gebruiker:", project.gebruiker],
        ["Datum berekeningen:", project.datum_berekeningen.strftime("%d-%m-%Y")],
    ]
    
    project_tabel = Table(project_data, colWidths=[50*mm, 100*mm])
    project_tabel.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
    ]))
    content.append(project_tabel)
    content.append(Spacer(1, 5*mm))
    
    # Gebouwconfiguratie
    content.append(Paragraph("Gebouwconfiguratie", subtitel_style))
    
    gebouw_data = [
        ["Aantal bouwlagen:", str(project.aantal_bouwlagen)],
        ["Laagste verdieping:", str(project.laagste_verdieping)],
        ["Aantal trappen:", str(project.aantal_trappen)],
        ["Totaal personen:", str(project.totaal_personen)],
    ]
    
    gebouw_tabel = Table(gebouw_data, colWidths=[50*mm, 100*mm])
    gebouw_tabel.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
    ]))
    content.append(gebouw_tabel)
    content.append(Spacer(1, 10*mm))
    
    # Resultaten samenvatting
    content.append(Paragraph("Resultaten Samenvatting", subtitel_style))
    
    # Samenvatting tabel
    sam_header = ["Trap", "Personen", "Ontruimingstijd", "Buiten", "Status"]
    sam_data = [sam_header]
    
    for naam, res in resultaten.items():
        toets = toetsingen.get(naam)
        status = "Voldoet" if toets and toets.alle_criteria_voldaan else "Voldoet niet"
        
        sam_data.append([
            naam,
            str(res.totaal_personen),
            f"{res.ontruimingstijd_min} min",
            f"{res.eindstand_buiten:.0f}",
            status
        ])
    
    sam_tabel = Table(sam_data, colWidths=[35*mm, 25*mm, 35*mm, 25*mm, 30*mm])
    sam_tabel.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2874a6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
    ]))
    content.append(sam_tabel)
    
    # Toetsing per trap
    content.append(PageBreak())
    content.append(Paragraph("Toetsing aan Normen", titel_style))
    
    for naam, toets in toetsingen.items():
        content.append(Paragraph(f"Trap: {naam}", subtitel_style))
        
        toets_data = [["Criterium", "Eis", "Berekend", "Status"]]
        
        for crit in toets.criteria:
            status = "✓" if crit.voldoet else "✗"
            toets_data.append([
                crit.naam,
                f"{crit.eis} {crit.eenheid}",
                f"{crit.berekend:.1f} {crit.eenheid}",
                status
            ])
        
        toets_tabel = Table(toets_data, colWidths=[60*mm, 35*mm, 35*mm, 20*mm])
        toets_tabel.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2874a6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
        ]))
        content.append(toets_tabel)
        content.append(Spacer(1, 5*mm))
    
    # Detail resultaten
    content.append(PageBreak())
    content.append(Paragraph("Gedetailleerde Resultaten", titel_style))
    
    for naam, res in resultaten.items():
        content.append(Paragraph(f"Trap: {naam}", subtitel_style))
        
        # Eerste 30 tijdstappen (of minder)
        detail_data = [["Tijd", "Naar buiten", "Cumulatief", "In trap", "Op verd."]]
        
        for ts in res.tijdstappen[:30]:
            detail_data.append([
                f"{ts.tijd_min:.1f}",
                f"{ts.naar_buiten:.1f}",
                f"{ts.cumulatief_buiten:.1f}",
                f"{ts.totaal_in_trap:.1f}",
                f"{ts.totaal_op_verdiepingen:.1f}"
            ])
        
        detail_tabel = Table(detail_data, colWidths=[25*mm, 30*mm, 30*mm, 30*mm, 30*mm])
        detail_tabel.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#d5d8dc')),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5*mm),
        ]))
        content.append(detail_tabel)
        content.append(Spacer(1, 5*mm))
        
        if len(res.tijdstappen) > 30:
            content.append(Paragraph(
                f"... en nog {len(res.tijdstappen) - 30} tijdstappen (zie Excel export voor volledig overzicht)",
                normaal_style
            ))
        
        content.append(PageBreak())
    
    # Footer met datum
    content.append(Spacer(1, 10*mm))
    content.append(Paragraph(
        f"Rapport gegenereerd op: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        ParagraphStyle('Footer', parent=normaal_style, fontSize=8, textColor=colors.grey)
    ))
    
    # Build document
    doc.build(content)


def _genereer_tekst_rapport(
    bestandsnaam: str,
    project: Project,
    resultaten: Dict[str, SimulatieResultaat],
    toetsingen: Dict[str, ToetsResultaat]
):
    """Fallback: genereer simpel tekst rapport als reportlab niet beschikbaar is"""
    
    # Vervang .pdf met .txt
    if bestandsnaam.endswith('.pdf'):
        bestandsnaam = bestandsnaam[:-4] + '.txt'
    
    with open(bestandsnaam, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("EVACUATIE DOORSTROOM CAPACITEITSBEREKENING\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("PROJECTGEGEVENS\n")
        f.write("-" * 30 + "\n")
        f.write(f"Projectnaam:      {project.projectnaam}\n")
        f.write(f"Scenario:         {project.omschrijving}\n")
        f.write(f"Projectnummer:    {project.projectnummer}\n")
        f.write(f"Gebruiker:        {project.gebruiker}\n")
        f.write(f"Datum:            {project.datum_berekeningen}\n")
        f.write("\n")
        
        f.write("GEBOUWCONFIGURATIE\n")
        f.write("-" * 30 + "\n")
        f.write(f"Aantal bouwlagen: {project.aantal_bouwlagen}\n")
        f.write(f"Laagste verd.:    {project.laagste_verdieping}\n")
        f.write(f"Aantal trappen:   {project.aantal_trappen}\n")
        f.write(f"Totaal personen:  {project.totaal_personen}\n")
        f.write("\n")
        
        f.write("RESULTATEN\n")
        f.write("-" * 30 + "\n")
        for naam, res in resultaten.items():
            toets = toetsingen.get(naam)
            status = "VOLDOET" if toets and toets.alle_criteria_voldaan else "VOLDOET NIET"
            f.write(f"\n{naam}:\n")
            f.write(f"  Personen:         {res.totaal_personen}\n")
            f.write(f"  Ontruimingstijd:  {res.ontruimingstijd_min} min\n")
            f.write(f"  Buiten na tijd:   {res.eindstand_buiten:.0f}\n")
            f.write(f"  Status:           {status}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"Rapport gegenereerd: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n")
