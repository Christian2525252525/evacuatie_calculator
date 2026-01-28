"""
Hoofdscherm van de Evacuatie Calculator
"""

import sys
import os
from datetime import date
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QGroupBox, QFormLayout, QLineEdit, QSpinBox, QCheckBox,
    QPushButton, QLabel, QDateEdit, QMessageBox, QFileDialog,
    QStatusBar, QMenuBar, QMenu, QApplication, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QByteArray
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Project
from ui.thema import (
    STYLESHEET, KLEUREN, GEBOUW_ICOON_GROOT_SVG,
    ThemaModus, get_kleuren, get_stylesheet, toggle_thema,
    get_huidige_modus, get_gebouw_icoon_groot_svg
)


def svg_to_pixmap(svg_string: str, width: int, height: int) -> QPixmap:
    """Converteer SVG string naar QPixmap"""
    renderer = QSvgRenderer(QByteArray(svg_string.encode()))
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


class HoofdScherm(QMainWindow):
    """Hoofdvenster van de applicatie"""

    def __init__(self, project: Project = None):
        super().__init__()

        self.project = project or Project()
        self.huidige_stap = 0

        self._setup_ui()
        self._setup_menu()
        self._laad_project_data()

    def _setup_ui(self):
        """Setup de user interface"""
        self.setWindowTitle("Evacuatie Doorstroom Calculator")
        self.setMinimumSize(1000, 700)
        self.resize(1100, 800)

        # Pas thema toe
        self.setStyleSheet(get_stylesheet())

        # Centrale widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header met stappen indicator
        kleuren = get_kleuren()
        header = QFrame()
        header.setObjectName("header_frame")
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {kleuren['kaart']};
                border-bottom: 2px solid {kleuren['primair']};
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # Icoon in header
        icoon_label = QLabel()
        icoon_label.setPixmap(svg_to_pixmap(get_gebouw_icoon_groot_svg(), 48, 48))
        header_layout.addWidget(icoon_label)

        # Titel en stap
        titel_layout = QVBoxLayout()
        titel_layout.setSpacing(2)

        self.app_titel = QLabel("Evacuatie Doorstroom Calculator")
        self.app_titel.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {kleuren['primair']};")
        titel_layout.addWidget(self.app_titel)

        self.stappen_label = QLabel("Stap 1 van 4: Project")
        self.stappen_label.setStyleSheet(f"font-size: 13px; color: {kleuren['tekst_licht']};")
        titel_layout.addWidget(self.stappen_label)

        header_layout.addLayout(titel_layout)
        header_layout.addStretch()

        # Stappen indicators
        self.stap_indicators = []
        stappen = ["Project", "Personen", "Trappen", "Resultaten"]
        for i, stap in enumerate(stappen):
            indicator = QLabel(f" {i+1}. {stap} ")
            indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            indicator.setStyleSheet(self._get_stap_style(i, 0))
            header_layout.addWidget(indicator)
            self.stap_indicators.append(indicator)

        main_layout.addWidget(header)

        # Content area
        content_frame = QFrame()
        content_frame.setObjectName("content_frame")
        content_frame.setStyleSheet(f"background-color: {kleuren['achtergrond']};")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Stacked widget voor de verschillende schermen
        self.stacked = QStackedWidget()
        content_layout.addWidget(self.stacked)

        main_layout.addWidget(content_frame, 1)

        # Maak de verschillende pagina's
        self._maak_project_pagina()
        self._maak_personen_pagina()
        self._maak_trappen_pagina()
        self._maak_resultaten_pagina()

        # Footer met navigatie knoppen
        footer = QFrame()
        footer.setObjectName("footer_frame")
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: {kleuren['kaart']};
                border-top: 1px solid {kleuren['rand']};
            }}
        """)
        nav_layout = QHBoxLayout(footer)
        nav_layout.setContentsMargins(20, 15, 20, 15)

        self.btn_terug = QPushButton("Terug")
        self.btn_terug.clicked.connect(self._ga_terug)
        self.btn_terug.setEnabled(False)
        self.btn_terug.setStyleSheet(f"""
            QPushButton {{
                background-color: {kleuren['achtergrond']};
                color: {kleuren['tekst']};
                border: 1px solid {kleuren['rand']};
            }}
            QPushButton:hover {{
                background-color: {kleuren['rand']};
            }}
        """)
        nav_layout.addWidget(self.btn_terug)

        nav_layout.addStretch()

        self.btn_volgende = QPushButton("Volgende")
        self.btn_volgende.clicked.connect(self._ga_volgende)
        nav_layout.addWidget(self.btn_volgende)

        self.btn_bereken = QPushButton("Herbereken")
        self.btn_bereken.clicked.connect(self._start_berekening)
        self.btn_bereken.setVisible(False)
        self.btn_bereken.setStyleSheet(f"""
            QPushButton {{
                background-color: {kleuren['succes']};
            }}
            QPushButton:hover {{
                background-color: #43A047;
            }}
        """)
        nav_layout.addWidget(self.btn_bereken)

        main_layout.addWidget(footer)

        # Status bar
        self.statusBar().showMessage("Welkom bij de Evacuatie Doorstroom Calculator")

    def _get_stap_style(self, stap_nr: int, huidige: int) -> str:
        """Krijg de stijl voor een stap indicator"""
        kleuren = get_kleuren()
        if stap_nr < huidige:
            # Voltooid
            return f"""
                background-color: {kleuren['succes']};
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            """
        elif stap_nr == huidige:
            # Huidig
            return f"""
                background-color: {kleuren['primair']};
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            """
        else:
            # Toekomstig
            return f"""
                background-color: {kleuren['rand']};
                color: {kleuren['tekst_licht']};
                border-radius: 4px;
                padding: 5px 10px;
            """

    def _update_stap_indicators(self):
        """Update alle stap indicators"""
        for i, indicator in enumerate(self.stap_indicators):
            indicator.setStyleSheet(self._get_stap_style(i, self.huidige_stap))

    def _setup_menu(self):
        """Setup het menu"""
        menubar = self.menuBar()

        # Bestand menu
        bestand_menu = menubar.addMenu("Bestand")

        nieuw_action = QAction("Nieuw project", self)
        nieuw_action.setShortcut("Ctrl+N")
        nieuw_action.triggered.connect(self._nieuw_project)
        bestand_menu.addAction(nieuw_action)

        openen_action = QAction("Project openen...", self)
        openen_action.setShortcut("Ctrl+O")
        openen_action.triggered.connect(self._open_project)
        bestand_menu.addAction(openen_action)

        opslaan_action = QAction("Project opslaan", self)
        opslaan_action.setShortcut("Ctrl+S")
        opslaan_action.triggered.connect(self._opslaan_project)
        bestand_menu.addAction(opslaan_action)

        bestand_menu.addSeparator()

        export_menu = bestand_menu.addMenu("Exporteren")
        export_pdf = QAction("PDF Rapport...", self)
        export_pdf.triggered.connect(self._export_pdf)
        export_menu.addAction(export_pdf)

        export_excel = QAction("Excel...", self)
        export_excel.triggered.connect(self._export_excel)
        export_menu.addAction(export_excel)

        bestand_menu.addSeparator()

        afsluiten_action = QAction("Afsluiten", self)
        afsluiten_action.setShortcut("Ctrl+Q")
        afsluiten_action.triggered.connect(self.close)
        bestand_menu.addAction(afsluiten_action)

        # Weergave menu
        weergave_menu = menubar.addMenu("Weergave")

        self.dark_mode_action = QAction("Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(get_huidige_modus() == ThemaModus.DARK)
        self.dark_mode_action.setShortcut("Ctrl+D")
        self.dark_mode_action.triggered.connect(self._toggle_thema)
        weergave_menu.addAction(self.dark_mode_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        over_action = QAction("Over Evacuatie Calculator", self)
        over_action.triggered.connect(self._toon_over)
        help_menu.addAction(over_action)

    def _maak_project_pagina(self):
        """Maak de project gegevens pagina"""
        kleuren = get_kleuren()
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setSpacing(20)

        # Welkom sectie met icoon
        welkom_frame = QFrame()
        welkom_frame.setObjectName("welkom_frame")
        welkom_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {kleuren['kaart']};
                border-radius: 12px;
                border: 1px solid {kleuren['rand']};
            }}
        """)
        welkom_layout = QHBoxLayout(welkom_frame)
        welkom_layout.setContentsMargins(30, 30, 30, 30)

        # Groot icoon
        icoon_groot = QLabel()
        icoon_groot.setPixmap(svg_to_pixmap(get_gebouw_icoon_groot_svg(), 120, 120))
        welkom_layout.addWidget(icoon_groot)

        # Welkom tekst
        tekst_layout = QVBoxLayout()
        tekst_layout.setSpacing(10)

        self.welkom_titel = QLabel("Welkom")
        self.welkom_titel.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {kleuren['primair']};")
        tekst_layout.addWidget(self.welkom_titel)

        self.welkom_subtitel = QLabel(
            "Bereken de opvang- en doorstroomcapaciteit van trappenhuizen\n"
            "volgens BBL Artikel 4.80 en 4.81"
        )
        self.welkom_subtitel.setStyleSheet(f"font-size: 14px; color: {kleuren['tekst_licht']}; line-height: 1.5;")
        tekst_layout.addWidget(self.welkom_subtitel)

        tekst_layout.addStretch()
        welkom_layout.addLayout(tekst_layout, 1)

        layout.addWidget(welkom_frame)

        # Twee kolommen layout
        kolommen_layout = QHBoxLayout()
        kolommen_layout.setSpacing(20)

        # Linker kolom: Project gegevens (vereenvoudigd)
        project_groep = QGroupBox("Projectgegevens")
        project_layout = QFormLayout()
        project_layout.setSpacing(15)
        project_layout.setContentsMargins(20, 25, 20, 20)

        self.txt_projectnaam = QLineEdit()
        self.txt_projectnaam.setPlaceholderText("Bijv. Kantoorgebouw Amsterdam")
        project_layout.addRow("Projectnaam:", self.txt_projectnaam)

        self.date_berekeningen = QDateEdit()
        self.date_berekeningen.setCalendarPopup(True)
        self.date_berekeningen.setDate(QDate.currentDate())
        project_layout.addRow("Datum:", self.date_berekeningen)

        # Verborgen velden (voor compatibiliteit)
        self.txt_omschrijving = QLineEdit()
        self.txt_projectnummer = QLineEdit()
        self.txt_gebruiker = QLineEdit()
        self.date_tekeningen = QDateEdit()

        project_groep.setLayout(project_layout)
        kolommen_layout.addWidget(project_groep)

        # Rechter kolom: Gebouw configuratie
        gebouw_groep = QGroupBox("Gebouwconfiguratie")
        gebouw_layout = QFormLayout()
        gebouw_layout.setSpacing(15)
        gebouw_layout.setContentsMargins(20, 25, 20, 20)

        self.spin_trappen = QSpinBox()
        self.spin_trappen.setRange(1, 10)
        self.spin_trappen.setValue(1)
        self.spin_trappen.setToolTip("Aantal trappenhuizen in het gebouw")
        gebouw_layout.addRow("Aantal trappen:", self.spin_trappen)

        self.spin_bouwlagen = QSpinBox()
        self.spin_bouwlagen.setRange(1, 60)
        self.spin_bouwlagen.setValue(10)
        self.spin_bouwlagen.setToolTip("Totaal aantal bouwlagen (inclusief begane grond)")
        gebouw_layout.addRow("Aantal bouwlagen:", self.spin_bouwlagen)

        self.spin_laagste = QSpinBox()
        self.spin_laagste.setRange(-10, 0)
        self.spin_laagste.setValue(0)
        self.spin_laagste.setToolTip("Laagste verdiepingnummer (0 = begane grond, -1 = kelder)")
        gebouw_layout.addRow("Laagste verdieping:", self.spin_laagste)

        self.chk_voorportalen = QCheckBox("Voorportalen aanwezig")
        self.chk_voorportalen.setToolTip("Zijn er voorportalen tussen verdieping en trappenhuis?")
        gebouw_layout.addRow("", self.chk_voorportalen)

        gebouw_groep.setLayout(gebouw_layout)
        kolommen_layout.addWidget(gebouw_groep)

        layout.addLayout(kolommen_layout)
        layout.addStretch()

        self.stacked.addWidget(pagina)

    def _maak_personen_pagina(self):
        """Maak de personen invoer pagina"""
        from ui.personen_invoer import PersonenInvoerWidget

        self.personen_widget = PersonenInvoerWidget(self.project)
        self.stacked.addWidget(self.personen_widget)

    def _maak_trappen_pagina(self):
        """Maak de trap configuratie pagina"""
        from ui.trap_config import TrapConfigWidget

        self.trap_widget = TrapConfigWidget(self.project)
        self.stacked.addWidget(self.trap_widget)

    def _maak_resultaten_pagina(self):
        """Maak de resultaten pagina"""
        from ui.resultaten import ResultatenWidget

        self.resultaten_widget = ResultatenWidget()
        self.stacked.addWidget(self.resultaten_widget)

    def _laad_project_data(self):
        """Laad project data in de velden"""
        self.txt_projectnaam.setText(self.project.projectnaam)
        self.txt_omschrijving.setText(self.project.omschrijving)
        self.txt_projectnummer.setText(self.project.projectnummer)
        self.txt_gebruiker.setText(self.project.gebruiker)

        self.spin_trappen.setValue(self.project.aantal_trappen)
        self.spin_bouwlagen.setValue(self.project.aantal_bouwlagen)
        self.spin_laagste.setValue(self.project.laagste_verdieping)
        self.chk_voorportalen.setChecked(self.project.voorportalen_aanwezig)

    def _sla_project_data_op(self):
        """Sla velden op naar project"""
        self.project.projectnaam = self.txt_projectnaam.text() or "Nieuw Project"
        self.project.omschrijving = self.txt_omschrijving.text()
        self.project.projectnummer = self.txt_projectnummer.text()
        self.project.gebruiker = self.txt_gebruiker.text()

        # Update configuratie (kan trappen/verdiepingen herinitialiseren)
        self.project.update_configuratie(
            self.spin_trappen.value(),
            self.spin_bouwlagen.value(),
            self.spin_laagste.value(),
            self.chk_voorportalen.isChecked()
        )

    def _update_stap_label(self):
        """Update het stappen label"""
        stap_namen = [
            "Project",
            "Personen invoeren",
            "Trappen configureren",
            "Resultaten"
        ]
        self.stappen_label.setText(f"Stap {self.huidige_stap + 1} van 4: {stap_namen[self.huidige_stap]}")
        self._update_stap_indicators()

    def _ga_volgende(self):
        """Ga naar volgende stap"""
        if self.huidige_stap == 0:
            # Van project naar personen: sla data op
            self._sla_project_data_op()
            self.personen_widget.update_project(self.project)

        elif self.huidige_stap == 1:
            # Van personen naar trappen
            self.personen_widget.sla_op()
            self.project.verdeel_personen_over_trappen()
            self.trap_widget.update_project(self.project)

        elif self.huidige_stap == 2:
            # Van trappen naar resultaten: voer berekening uit
            self.trap_widget.sla_op()
            self._start_berekening()
            return

        self.huidige_stap += 1
        self.stacked.setCurrentIndex(self.huidige_stap)
        self._update_navigatie()

    def _ga_terug(self):
        """Ga naar vorige stap"""
        if self.huidige_stap > 0:
            self.huidige_stap -= 1
            self.stacked.setCurrentIndex(self.huidige_stap)
            self._update_navigatie()

    def _update_navigatie(self):
        """Update navigatie knoppen"""
        self._update_stap_label()

        self.btn_terug.setEnabled(self.huidige_stap > 0)

        if self.huidige_stap == 2:
            kleuren = get_kleuren()
            self.btn_volgende.setText("Bereken")
            self.btn_volgende.setStyleSheet(f"""
                QPushButton {{
                    background-color: {kleuren['succes']};
                }}
                QPushButton:hover {{
                    background-color: #43A047;
                }}
            """)
        elif self.huidige_stap == 3:
            self.btn_volgende.setVisible(False)
            self.btn_bereken.setVisible(True)
        else:
            self.btn_volgende.setText("Volgende")
            self.btn_volgende.setStyleSheet("")  # Reset naar standaard
            self.btn_volgende.setVisible(True)
            self.btn_bereken.setVisible(False)

    def _start_berekening(self):
        """Start de berekening"""
        self.statusBar().showMessage("Berekening uitvoeren...")
        QApplication.processEvents()

        try:
            # Zorg dat alle data is opgeslagen
            if self.huidige_stap < 3:
                self.trap_widget.sla_op()

            # Voer simulatie uit
            from berekeningen import simuleer_alle_trappen, toets_alle_resultaten

            resultaten = simuleer_alle_trappen(self.project.trappen)
            # Geef trappen door zodat trap-specifieke parameters gebruikt worden
            toetsingen = toets_alle_resultaten(resultaten, trappen=self.project.trappen)

            # Update resultaten widget
            self.resultaten_widget.toon_resultaten(self.project, resultaten, toetsingen)

            # Ga naar resultaten pagina
            self.huidige_stap = 3
            self.stacked.setCurrentIndex(3)
            self._update_navigatie()

            self.statusBar().showMessage("Berekening voltooid")

        except Exception as e:
            QMessageBox.critical(
                self, "Fout",
                f"Er is een fout opgetreden tijdens de berekening:\n{str(e)}"
            )
            self.statusBar().showMessage("Berekening mislukt")

    def _nieuw_project(self):
        """Start nieuw project"""
        reply = QMessageBox.question(
            self, "Nieuw project",
            "Weet u zeker dat u een nieuw project wilt starten?\nNiet opgeslagen wijzigingen gaan verloren.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.project = Project()
            self.huidige_stap = 0
            self.stacked.setCurrentIndex(0)
            self._laad_project_data()
            self._update_navigatie()

    def _open_project(self):
        """Open bestaand project"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Project openen",
            "", "Evacuatie Project (*.evac);;JSON bestanden (*.json)"
        )

        if filename:
            try:
                import json
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.project = Project.from_dict(data)
                self._laad_project_data()
                self.huidige_stap = 0
                self.stacked.setCurrentIndex(0)
                self._update_navigatie()

                self.statusBar().showMessage(f"Project geladen: {filename}")

            except Exception as e:
                QMessageBox.critical(
                    self, "Fout",
                    f"Kon project niet laden:\n{str(e)}"
                )

    def _opslaan_project(self):
        """Sla project op"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Project opslaan",
            f"{self.project.projectnaam}.evac",
            "Evacuatie Project (*.evac);;JSON bestanden (*.json)"
        )

        if filename:
            try:
                self._sla_project_data_op()

                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.project.to_dict(), f, indent=2, ensure_ascii=False)

                self.statusBar().showMessage(f"Project opgeslagen: {filename}")

            except Exception as e:
                QMessageBox.critical(
                    self, "Fout",
                    f"Kon project niet opslaan:\n{str(e)}"
                )

    def _export_pdf(self):
        """Exporteer naar PDF"""
        if self.huidige_stap != 3:
            QMessageBox.information(
                self, "Export",
                "Voer eerst een berekening uit voordat u kunt exporteren."
            )
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporteren naar PDF",
            f"{self.project.projectnaam}_rapport.pdf",
            "PDF bestanden (*.pdf)"
        )

        if filename:
            try:
                from export.pdf_rapport import genereer_pdf_rapport
                genereer_pdf_rapport(
                    filename,
                    self.project,
                    self.resultaten_widget.resultaten,
                    self.resultaten_widget.toetsingen
                )
                self.statusBar().showMessage(f"PDF geëxporteerd: {filename}")

            except Exception as e:
                QMessageBox.critical(
                    self, "Fout",
                    f"Kon PDF niet genereren:\n{str(e)}"
                )

    def _export_excel(self):
        """Exporteer naar Excel"""
        if self.huidige_stap != 3:
            QMessageBox.information(
                self, "Export",
                "Voer eerst een berekening uit voordat u kunt exporteren."
            )
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Exporteren naar Excel",
            f"{self.project.projectnaam}_data.xlsx",
            "Excel bestanden (*.xlsx)"
        )

        if filename:
            try:
                from export.excel_export import genereer_excel_export
                genereer_excel_export(
                    filename,
                    self.project,
                    self.resultaten_widget.resultaten
                )
                self.statusBar().showMessage(f"Excel geëxporteerd: {filename}")

            except Exception as e:
                QMessageBox.critical(
                    self, "Fout",
                    f"Kon Excel niet genereren:\n{str(e)}"
                )

    def _toggle_thema(self):
        """Wissel tussen light en dark mode"""
        nieuwe_modus = toggle_thema()
        self.dark_mode_action.setChecked(nieuwe_modus == ThemaModus.DARK)
        self._pas_thema_toe()

    def _pas_thema_toe(self):
        """Pas het huidige thema toe op de hele applicatie"""
        kleuren = get_kleuren()
        stylesheet = get_stylesheet()

        # Pas stylesheet toe op hoofdvenster
        self.setStyleSheet(stylesheet)

        # Update header styling
        header = self.findChild(QFrame, "header_frame")
        if header:
            header.setStyleSheet(f"""
                QFrame {{
                    background-color: {kleuren['kaart']};
                    border-bottom: 2px solid {kleuren['primair']};
                }}
            """)

        # Update content frame
        content = self.findChild(QFrame, "content_frame")
        if content:
            content.setStyleSheet(f"background-color: {kleuren['achtergrond']};")

        # Update footer styling
        footer = self.findChild(QFrame, "footer_frame")
        if footer:
            footer.setStyleSheet(f"""
                QFrame {{
                    background-color: {kleuren['kaart']};
                    border-top: 1px solid {kleuren['rand']};
                }}
            """)

        # Update welkom frame
        welkom = self.findChild(QFrame, "welkom_frame")
        if welkom:
            welkom.setStyleSheet(f"""
                QFrame {{
                    background-color: {kleuren['kaart']};
                    border-radius: 12px;
                    border: 1px solid {kleuren['rand']};
                }}
            """)

        # Update stap indicators
        self._update_stap_indicators()

        # Update iconen
        icoon_svg = get_gebouw_icoon_groot_svg()
        for widget in self.findChildren(QLabel):
            if widget.pixmap() and not widget.pixmap().isNull():
                # Check grootte om te bepalen welk icoon
                if widget.pixmap().width() == 48:
                    widget.setPixmap(svg_to_pixmap(icoon_svg, 48, 48))
                elif widget.pixmap().width() == 120:
                    widget.setPixmap(svg_to_pixmap(icoon_svg, 120, 120))

        # Update app titel
        if hasattr(self, 'app_titel'):
            self.app_titel.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {kleuren['primair']};")

        # Update stappen label
        if hasattr(self, 'stappen_label'):
            self.stappen_label.setStyleSheet(f"font-size: 13px; color: {kleuren['tekst_licht']};")

        # Update welkom titels
        if hasattr(self, 'welkom_titel'):
            self.welkom_titel.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {kleuren['primair']};")
        if hasattr(self, 'welkom_subtitel'):
            self.welkom_subtitel.setStyleSheet(f"font-size: 14px; color: {kleuren['tekst_licht']}; line-height: 1.5;")

        # Update footer knoppen
        self.btn_terug.setStyleSheet(f"""
            QPushButton {{
                background-color: {kleuren['achtergrond']};
                color: {kleuren['tekst']};
                border: 1px solid {kleuren['rand']};
            }}
            QPushButton:hover {{
                background-color: {kleuren['rand']};
            }}
        """)

        # Update bereken knop
        self.btn_bereken.setStyleSheet(f"""
            QPushButton {{
                background-color: {kleuren['succes']};
            }}
            QPushButton:hover {{
                background-color: #43A047;
            }}
        """)

        # Update volgende knop als we op stap 2 zijn
        if self.huidige_stap == 2:
            self.btn_volgende.setStyleSheet(f"""
                QPushButton {{
                    background-color: {kleuren['succes']};
                }}
                QPushButton:hover {{
                    background-color: #43A047;
                }}
            """)

        # Update statusbar
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: {kleuren['kaart']};
                color: {kleuren['tekst']};
                border-top: 1px solid {kleuren['rand']};
            }}
        """)

    def _toon_over(self):
        """Toon over dialoog"""
        kleuren = get_kleuren()
        QMessageBox.about(
            self, "Over Evacuatie Calculator",
            f"""<h2 style="color: {kleuren['primair']};">Evacuatie Doorstroom Calculator</h2>
            <p style="color: {kleuren['tekst_licht']};">Versie 1.0</p>
            <p>Berekening van opvang- en doorstroomcapaciteit van trappenhuizen
            bij gebouwontruiming volgens Nederlandse brandveiligheidsnormen.</p>
            <p><b>Gebaseerd op:</b><br>
            - BBL Art. 4.80 - Doorstroomcapaciteit<br>
            - BBL Art. 4.81 - Opvangcapaciteit</p>
            <p style="color: {kleuren['tekst_licht']};">2024</p>"""
        )
