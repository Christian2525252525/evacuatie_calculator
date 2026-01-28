#!/usr/bin/env python3
"""
Evacuatie Doorstroom Calculator
Hoofdprogramma

Berekening van opvang- en doorstroomcapaciteit van trappenhuizen
bij gebouwontruiming volgens Nederlandse brandveiligheidsnormen (Bouwbesluit).

Gebaseerd op:
- Bouwbesluit 2012, Afdeling 2.12 Vluchtroutes
- FSS methode voor ontruimingsberekeningen
"""

import sys
import os

# Voeg het project pad toe aan sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

from models.project import Project
from ui.hoofdscherm import HoofdScherm


def configureer_applicatie(app: QApplication) -> None:
    """Configureer applicatie-brede instellingen"""
    app.setApplicationName("Evacuatie Calculator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Brandveiligheid")
    app.setOrganizationDomain("evacuatie-calculator.nl")
    
    # Stel standaard font in
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Stel stijl in
    app.setStyle("Fusion")
    
    # Optioneel: donker thema ondersteuning detecteren
    palette = app.palette()
    
    # Moderne kleuren
    palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(33, 33, 33))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(33, 33, 33))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(33, 33, 33))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 100, 200))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)


def main():
    """Hoofdfunctie - start de applicatie"""
    # High DPI ondersteuning
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Maak applicatie
    app = QApplication(sys.argv)
    
    # Configureer
    configureer_applicatie(app)
    
    # Maak nieuw project
    project = Project()
    
    # Start hoofdscherm
    window = HoofdScherm(project)
    window.show()
    
    # Start event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
