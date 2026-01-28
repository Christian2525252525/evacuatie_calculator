"""
Resultaten widget
Weergave van simulatieresultaten en toetsing
"""

import sys
import os
from typing import Dict, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QGroupBox, QGridLayout,
    QScrollArea, QFrame, QSplitter, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Project
from berekeningen import SimulatieResultaat, ToetsResultaat, ToetsStatus, bereken_max_personen_trap


class SamenvattingWidget(QWidget):
    """Widget voor samenvatting van resultaten"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)
        
        # Project info
        self.lbl_project = QLabel("Project: -")
        self.lbl_project.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_project)
        
        self.lbl_totaal = QLabel("Totaal personen: -")
        layout.addWidget(self.lbl_totaal)
        
        # Samenvatting tabel
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(8)
        self.tabel.setHorizontalHeaderLabels([
            "Trap", "Personen", "Max totaal", "Max/verd.",
            "Bottleneck", "Ontruimingstijd", "Buiten na ontruimingstijd [pers]", "Status"
        ])

        header = self.tabel.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.tabel.setAlternatingRowColors(True)
        layout.addWidget(self.tabel)

        # Legenda voor max capaciteit
        legenda = QLabel(
            "💡 <b>Max totaal</b>: BBL lid 1 - Totaal binnen ontruimingstijd via uitgang trappenhuis | "
            "<b>Max/verd.</b>: BBL lid 2 - Max personen per verdieping binnen 1 min via toegangsdeur"
        )
        legenda.setWordWrap(True)
        legenda.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(legenda)
    
    def update_data(self, project: Project, resultaten: Dict[str, SimulatieResultaat],
                   toetsingen: Dict[str, ToetsResultaat]):
        """Update de weergave met nieuwe data"""
        self.lbl_project.setText(f"Project: {project.projectnaam}")
        self.lbl_totaal.setText(f"Totaal personen: {project.totaal_personen}")

        self.tabel.setRowCount(len(resultaten))

        for row, (naam, res) in enumerate(resultaten.items()):
            # Zoek bijbehorende trap voor max berekening
            trap = None
            for t in project.trappen:
                if t.aanduiding == naam:
                    trap = t
                    break

            # Bereken max personen
            if trap:
                max_info = bereken_max_personen_trap(
                    trap.doorgang_uitgang_m,
                    trap.type_uitgang,
                    trap.ontruimingstijd_min,
                    trap.verdiepingen
                )
                max_personen = max_info['max_personen']
                max_per_verd = max_info.get('max_per_verdieping')
                bottleneck = max_info['bottleneck']
            else:
                max_personen = "-"
                max_per_verd = "-"
                bottleneck = "-"

            # Trap naam
            item = QTableWidgetItem(naam)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, 0, item)

            # Personen
            item = QTableWidgetItem(str(res.totaal_personen))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Kleur rood als boven max capaciteit
            if isinstance(max_personen, int) and res.totaal_personen > max_personen:
                item.setBackground(QColor(255, 200, 200))
            self.tabel.setItem(row, 1, item)

            # Max totaal (lid 1)
            item = QTableWidgetItem(str(max_personen))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(QColor(230, 240, 255))
            item.setToolTip("BBL lid 1: Max totaal binnen ontruimingstijd via uitgang trappenhuis")
            self.tabel.setItem(row, 2, item)

            # Max per verdieping (lid 2)
            item = QTableWidgetItem(str(max_per_verd) if max_per_verd else "-")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(QColor(255, 240, 220))
            item.setToolTip("BBL lid 2: Max personen per verdieping binnen 1 min via toegangsdeur")
            self.tabel.setItem(row, 3, item)

            # Bottleneck
            item = QTableWidgetItem(bottleneck)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setToolTip(f"Beperkende factor totaal: {bottleneck}")
            self.tabel.setItem(row, 4, item)

            # Ontruimingstijd
            item = QTableWidgetItem(f"{res.ontruimingstijd_min} min")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, 5, item)

            # Buiten na ontruimingstijd
            buiten = res.eindstand_buiten
            item = QTableWidgetItem(f"{buiten:.0f} personen")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setToolTip(
                f"Aantal personen dat binnen {res.ontruimingstijd_min} minuten "
                f"het gebouw heeft verlaten via de uitgang van het trappenhuis"
            )
            self.tabel.setItem(row, 6, item)

            # Status
            toets = toetsingen.get(naam)
            if toets and toets.alle_criteria_voldaan:
                item = QTableWidgetItem("✅ Voldoet")
                item.setBackground(QColor(200, 255, 200))
            else:
                item = QTableWidgetItem("❌ Voldoet niet")
                item.setBackground(QColor(255, 200, 200))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, 7, item)


class GrafiekWidget(QWidget):
    """Widget voor grafische weergave van resultaten"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)
        
        # Chart
        self.chart = QChart()
        self.chart.setTitle("Cumulatief personen buiten over tijd")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # Assen
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Tijd (minuten)")
        self.axis_x.setLabelFormat("%.1f")
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Personen buiten")
        self.axis_y.setLabelFormat("%d")
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        
        # Chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.chart_view)
    
    def update_data(self, resultaten: Dict[str, SimulatieResultaat]):
        """Update de grafiek met nieuwe data"""
        # Verwijder oude series
        self.chart.removeAllSeries()
        
        if not resultaten:
            return
        
        max_tijd = 0
        max_personen = 0
        
        colors = [
            QColor(31, 119, 180),   # Blauw
            QColor(255, 127, 14),   # Oranje
            QColor(44, 160, 44),    # Groen
            QColor(214, 39, 40),    # Rood
            QColor(148, 103, 189),  # Paars
        ]
        
        for idx, (naam, res) in enumerate(resultaten.items()):
            series = QLineSeries()
            series.setName(naam)
            
            if idx < len(colors):
                pen = series.pen()
                pen.setColor(colors[idx])
                pen.setWidth(2)
                series.setPen(pen)
            
            for ts in res.tijdstappen:
                series.append(ts.tijd_min, ts.cumulatief_buiten)
                max_tijd = max(max_tijd, ts.tijd_min)
                max_personen = max(max_personen, ts.cumulatief_buiten)
            
            self.chart.addSeries(series)
            series.attachAxis(self.axis_x)
            series.attachAxis(self.axis_y)
        
        # Update assen
        self.axis_x.setRange(0, max_tijd * 1.05)
        self.axis_y.setRange(0, max_personen * 1.1)


class ToetsResultaatWidget(QWidget):
    """Widget voor weergave van toetsresultaten"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)
        
        # Tabs per trap
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
    
    def update_data(self, toetsingen: Dict[str, ToetsResultaat]):
        """Update de weergave met toetsresultaten"""
        self.tabs.clear()
        
        for naam, toets in toetsingen.items():
            widget = QWidget()
            vlayout = QVBoxLayout(widget)
            
            # Status header
            if toets.alle_criteria_voldaan:
                status = QLabel("✅ Alle criteria voldaan")
                status.setStyleSheet("font-size: 14px; font-weight: bold; color: green; padding: 10px;")
            else:
                status = QLabel(f"❌ {toets.aantal_voldoet_niet} criterium(s) voldoet niet")
                status.setStyleSheet("font-size: 14px; font-weight: bold; color: red; padding: 10px;")
            vlayout.addWidget(status)
            
            # Criteria lijst
            for crit in toets.criteria:
                groep = QGroupBox(crit.naam)
                glayout = QGridLayout()
                
                glayout.addWidget(QLabel("Beschrijving:"), 0, 0)
                glayout.addWidget(QLabel(crit.beschrijving), 0, 1)
                
                glayout.addWidget(QLabel("Eis:"), 1, 0)
                glayout.addWidget(QLabel(f"{crit.eis} {crit.eenheid}"), 1, 1)
                
                glayout.addWidget(QLabel("Berekend:"), 2, 0)
                glayout.addWidget(QLabel(f"{crit.berekend:.1f} {crit.eenheid}"), 2, 1)
                
                glayout.addWidget(QLabel("Status:"), 3, 0)
                if crit.voldoet:
                    status_lbl = QLabel("✅ Voldoet")
                    status_lbl.setStyleSheet("color: green;")
                else:
                    status_lbl = QLabel("❌ Voldoet niet")
                    status_lbl.setStyleSheet("color: red;")
                glayout.addWidget(status_lbl, 3, 1)
                
                if crit.toelichting:
                    glayout.addWidget(QLabel("Toelichting:"), 4, 0)
                    toel = QLabel(crit.toelichting)
                    toel.setWordWrap(True)
                    glayout.addWidget(toel, 4, 1)
                
                groep.setLayout(glayout)
                vlayout.addWidget(groep)
            
            vlayout.addStretch()
            
            scroll = QScrollArea()
            scroll.setWidget(widget)
            scroll.setWidgetResizable(True)
            
            self.tabs.addTab(scroll, naam)


class MaxCapaciteitWidget(QWidget):
    """Widget voor weergave van maximale capaciteit per trap"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)

        # Tabs per trap
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
    
    def update_data(self, project: Project):
        """Update de weergave met capaciteitsberekeningen"""
        self.tabs.clear()
        
        for trap in project.trappen:
            widget = QWidget()
            vlayout = QVBoxLayout(widget)
            
            # Bereken max personen
            max_info = bereken_max_personen_trap(
                trap.doorgang_uitgang_m,
                trap.type_uitgang,
                trap.ontruimingstijd_min,
                trap.verdiepingen
            )
            
            # Resultaat header - BBL lid 1 (totale ontruiming)
            resultaat_groep = QGroupBox("BBL Art. 4.81 lid 1 - Totale ontruiming")
            res_layout = QGridLayout()

            # Max personen groot weergeven
            max_lbl = QLabel(f"{max_info['max_personen']}")
            max_lbl.setStyleSheet("font-size: 48px; font-weight: bold; color: #2196F3;")
            max_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            res_layout.addWidget(QLabel("Max totaal personen:"), 0, 0)
            res_layout.addWidget(max_lbl, 0, 1)

            # Berekening uitleg
            doorstroom = max_info['doorstroom_uitgang_per_min']
            tijd = max_info['ontruimingstijd_min']
            uitleg_lid1 = QLabel(
                f"= {doorstroom:.0f} pers/min × {tijd} min = {int(doorstroom * tijd)} personen"
            )
            uitleg_lid1.setStyleSheet("color: #666; font-style: italic;")
            res_layout.addWidget(QLabel("Berekening:"), 1, 0)
            res_layout.addWidget(uitleg_lid1, 1, 1)

            res_layout.addWidget(QLabel("Bottleneck:"), 2, 0)
            bottleneck_lbl = QLabel(max_info['bottleneck'])
            bottleneck_lbl.setStyleSheet("font-weight: bold; color: #f44336;")
            res_layout.addWidget(bottleneck_lbl, 2, 1)

            resultaat_groep.setLayout(res_layout)
            vlayout.addWidget(resultaat_groep)

            # BBL lid 2 - Max per verdieping (binnen 1 minuut verlaten)
            if max_info.get('max_per_verdieping') is not None:
                lid2_groep = QGroupBox("BBL Art. 4.81 lid 2 - Verlaten brandcompartiment binnen 1 min")
                lid2_layout = QGridLayout()

                # Max per verdieping
                max_verd = max_info['max_per_verdieping']
                max_verd_lbl = QLabel(f"{max_verd}")
                max_verd_lbl.setStyleSheet("font-size: 36px; font-weight: bold; color: #FF9800;")
                max_verd_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lid2_layout.addWidget(QLabel("Max personen per verdieping:"), 0, 0)
                lid2_layout.addWidget(max_verd_lbl, 0, 1)

                # Uitleg wat dit betekent
                uitleg_lid2 = QLabel(
                    f"= hoeveel personen fysiek in trappenhuis passen (bordes + treden)"
                )
                uitleg_lid2.setStyleSheet("color: #666; font-style: italic;")
                lid2_layout.addWidget(QLabel("Berekening:"), 1, 0)
                lid2_layout.addWidget(uitleg_lid2, 1, 1)

                lid2_layout.addWidget(QLabel("Bottleneck:"), 2, 0)
                bottleneck_verd_lbl = QLabel(max_info.get('bottleneck_per_verdieping', '-'))
                bottleneck_verd_lbl.setStyleSheet("font-weight: bold; color: #f44336;")
                lid2_layout.addWidget(bottleneck_verd_lbl, 2, 1)

                lid2_groep.setLayout(lid2_layout)
                vlayout.addWidget(lid2_groep)

                # Waarschuwing als lid 2 veel lager is dan lid 1
                if max_verd < max_info['max_personen']:
                    waarschuwing = QLabel(
                        f"Lid 1 ({max_info['max_personen']}) > Lid 2 ({max_verd}): "
                        f"Bij meer dan {max_verd} personen per verdieping voldoe je niet aan lid 2, "
                        f"ook al is het totaal onder de {max_info['max_personen']}."
                    )
                    waarschuwing.setWordWrap(True)
                    waarschuwing.setStyleSheet(
                        "color: #856404; background-color: #fff3cd; "
                        "padding: 8px; border-radius: 3px; margin-top: 5px;"
                    )
                    vlayout.addWidget(waarschuwing)

            # Uitgang info
            uitgang_groep = QGroupBox("Uitgang eigenschappen")
            uit_layout = QGridLayout()
            uit_layout.addWidget(QLabel("Breedte:"), 0, 0)
            uit_layout.addWidget(QLabel(f"{trap.doorgang_uitgang_m:.2f} m"), 0, 1)
            uit_layout.addWidget(QLabel("Type:"), 1, 0)
            uit_layout.addWidget(QLabel(trap.type_uitgang.value), 1, 1)
            uitgang_groep.setLayout(uit_layout)
            vlayout.addWidget(uitgang_groep)
            
            # Details per verdieping
            if max_info['details']:
                detail_groep = QGroupBox("Capaciteiten per verdieping")
                detail_tabel = QTableWidget()
                detail_tabel.setColumnCount(6)
                detail_tabel.setHorizontalHeaderLabels([
                    "Verdieping", "Deur [pers/min]", "Trap [pers/min]",
                    "Opvang [pers]", "Max lid 2 [pers]", "Min doorstr. [pers/min]"
                ])
                detail_tabel.setRowCount(len(max_info['details']))

                header = detail_tabel.horizontalHeader()
                for i in range(6):
                    header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

                # Vind minimum waarden voor markering
                min_doorstroom = min(d['min_doorstroom_per_min'] for d in max_info['details'])
                min_lid2 = min(d['max_lid2'] for d in max_info['details'])

                for row, detail in enumerate(max_info['details']):
                    item = QTableWidgetItem(str(detail['verdieping']))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    detail_tabel.setItem(row, 0, item)

                    item = QTableWidgetItem(f"{detail['doorstroom_deur_per_min']:.1f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    detail_tabel.setItem(row, 1, item)

                    item = QTableWidgetItem(f"{detail['doorstroom_trap_per_min']:.1f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    detail_tabel.setItem(row, 2, item)

                    # Opvangcapaciteit
                    item = QTableWidgetItem(f"{detail['opvangcapaciteit']:.0f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setToolTip("Opvangcapaciteit trappenhuis (bordes + tussenbordes + treden)")
                    detail_tabel.setItem(row, 3, item)

                    # Max lid 2 (binnen 1 min verlaten)
                    item = QTableWidgetItem(f"{detail['max_lid2']}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setToolTip("Max personen per verdieping voor BBL lid 2 (1 min verlaten)")
                    # Markeer de bottleneck voor lid 2
                    if detail['max_lid2'] == min_lid2:
                        item.setBackground(QColor(255, 220, 180))
                    detail_tabel.setItem(row, 4, item)

                    item = QTableWidgetItem(f"{detail['min_doorstroom_per_min']:.1f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    # Markeer de bottleneck voor doorstroom
                    if detail['min_doorstroom_per_min'] == min_doorstroom:
                        item.setBackground(QColor(255, 230, 200))
                    detail_tabel.setItem(row, 5, item)

                detail_layout = QVBoxLayout()
                detail_layout.addWidget(detail_tabel)

                # Legenda
                legenda = QLabel(
                    "💡 <b>Opvang</b>: Fysieke opslagcapaciteit in trappenhuis | "
                    "<b>Max lid 2</b>: Max personen per verdieping binnen 1 min (kleinste van opvang/doorstroom)"
                )
                legenda.setStyleSheet("color: #666; font-size: 10px; padding: 3px;")
                detail_layout.addWidget(legenda)

                detail_groep.setLayout(detail_layout)
                vlayout.addWidget(detail_groep)
            
            # Vergelijking met huidig aantal
            huidig = trap.totaal_personen
            if huidig > 0:
                vgl_groep = QGroupBox("Vergelijking met huidige bezetting")
                vgl_layout = QGridLayout()
                
                vgl_layout.addWidget(QLabel("Huidig aantal personen:"), 0, 0)
                vgl_layout.addWidget(QLabel(str(huidig)), 0, 1)
                
                vgl_layout.addWidget(QLabel("Maximale capaciteit:"), 1, 0)
                vgl_layout.addWidget(QLabel(str(max_info['max_personen'])), 1, 1)
                
                verschil = max_info['max_personen'] - huidig
                vgl_layout.addWidget(QLabel("Verschil:"), 2, 0)
                
                if verschil >= 0:
                    verschil_lbl = QLabel(f"+{verschil} (ruimte over)")
                    verschil_lbl.setStyleSheet("color: green; font-weight: bold;")
                else:
                    verschil_lbl = QLabel(f"{verschil} (te veel!)")
                    verschil_lbl.setStyleSheet("color: red; font-weight: bold;")
                vgl_layout.addWidget(verschil_lbl, 2, 1)
                
                # Benutting percentage
                benutting = (huidig / max_info['max_personen'] * 100) if max_info['max_personen'] > 0 else 0
                vgl_layout.addWidget(QLabel("Benutting:"), 3, 0)
                benutting_lbl = QLabel(f"{benutting:.1f}%")
                if benutting > 100:
                    benutting_lbl.setStyleSheet("color: red; font-weight: bold;")
                elif benutting > 90:
                    benutting_lbl.setStyleSheet("color: orange; font-weight: bold;")
                else:
                    benutting_lbl.setStyleSheet("color: green;")
                vgl_layout.addWidget(benutting_lbl, 3, 1)
                
                vgl_groep.setLayout(vgl_layout)
                vlayout.addWidget(vgl_groep)
            
            vlayout.addStretch()
            
            scroll = QScrollArea()
            scroll.setWidget(widget)
            scroll.setWidgetResizable(True)
            
            # Tab titel met status indicator
            if huidig > max_info['max_personen']:
                tab_titel = f"❌ {trap.aanduiding}"
            else:
                tab_titel = f"✅ {trap.aanduiding}"
            
            self.tabs.addTab(scroll, tab_titel)


class DetailTabelWidget(QWidget):
    """Widget voor gedetailleerde resultaten tabel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)
        
        # Tabs per trap
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
    
    def update_data(self, resultaten: Dict[str, SimulatieResultaat]):
        """Update de tabellen met resultaten"""
        self.tabs.clear()
        
        for naam, res in resultaten.items():
            tabel = QTableWidget()
            
            # Kolommen: Tijdstap, Tijd, Naar buiten, Cumulatief, In trap, Op verd.
            tabel.setColumnCount(6)
            tabel.setHorizontalHeaderLabels([
                "Tijdstap", "Tijd [min]", "Naar buiten", "Cumulatief buiten",
                "In trap", "Op verdiepingen"
            ])
            
            header = tabel.horizontalHeader()
            for i in range(6):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            
            tabel.setRowCount(len(res.tijdstappen))
            tabel.setAlternatingRowColors(True)
            
            for row, ts in enumerate(res.tijdstappen):
                col = 0
                
                item = QTableWidgetItem(str(ts.tijdstap))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabel.setItem(row, col, item)
                col += 1
                
                item = QTableWidgetItem(f"{ts.tijd_min:.1f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabel.setItem(row, col, item)
                col += 1
                
                item = QTableWidgetItem(f"{ts.naar_buiten:.2f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabel.setItem(row, col, item)
                col += 1
                
                item = QTableWidgetItem(f"{ts.cumulatief_buiten:.2f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabel.setItem(row, col, item)
                col += 1
                
                item = QTableWidgetItem(f"{ts.totaal_in_trap:.2f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabel.setItem(row, col, item)
                col += 1
                
                item = QTableWidgetItem(f"{ts.totaal_op_verdiepingen:.2f}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabel.setItem(row, col, item)
            
            self.tabs.addTab(tabel, naam)


class ResultatenWidget(QWidget):
    """Hoofdwidget voor alle resultaten"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resultaten = {}
        self.toetsingen = {}
        self.project = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)
        
        # Tabs voor verschillende weergaven
        self.tabs = QTabWidget()
        
        # Samenvatting
        self.samenvatting = SamenvattingWidget()
        self.tabs.addTab(self.samenvatting, "📊 Samenvatting")
        
        # Maximale capaciteit
        self.max_capaciteit = MaxCapaciteitWidget()
        self.tabs.addTab(self.max_capaciteit, "📐 Max. Capaciteit")
        
        # Grafiek
        self.grafiek = GrafiekWidget()
        self.tabs.addTab(self.grafiek, "📈 Grafiek")
        
        # Toetsing
        self.toetsing = ToetsResultaatWidget()
        self.tabs.addTab(self.toetsing, "✅ Toetsing")
        
        # Detail tabel
        self.detail = DetailTabelWidget()
        self.tabs.addTab(self.detail, "📋 Details")
        
        layout.addWidget(self.tabs)
    
    def toon_resultaten(self, project: Project, resultaten: Dict[str, SimulatieResultaat],
                        toetsingen: Dict[str, ToetsResultaat]):
        """Toon de resultaten"""
        self.project = project
        self.resultaten = resultaten
        self.toetsingen = toetsingen
        
        self.samenvatting.update_data(project, resultaten, toetsingen)
        self.max_capaciteit.update_data(project)
        self.grafiek.update_data(resultaten)
        self.toetsing.update_data(toetsingen)
        self.detail.update_data(resultaten)
