"""
Trap configuratie widget
Configuratie van trappenhuizen en verdieping-specifieke eigenschappen
"""

import sys
import os
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QLabel, QPushButton, QGroupBox,
    QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox,
    QCheckBox, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Project, Trap, TrapVerdieping, DoorgangType, LocatieType, VerlaatTijdType
from ui.thema import get_button_style_secundair


class TrapVerdiepingEditor(QWidget):
    """Editor voor verdieping-specifieke trap eigenschappen"""
    
    def __init__(self, trap: Trap, parent=None):
        super().__init__(parent)
        self.trap = trap
        self._setup_ui()
        self._vul_tabel()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Tabel voor verdieping eigenschappen
        self.tabel = QTableWidget()

        # Kolommen definiëren
        kolommen = [
            "Verd", "Doorgang [m]", "Type", "Bordes [m²]",
            "Tussen [m²]", "Hoogte [m]", "Breedte [m]", "Treden",
            "Verdeling [%]", "Vertraging [min]"
        ]

        self.tabel.setColumnCount(len(kolommen))
        self.tabel.setHorizontalHeaderLabels(kolommen)

        header = self.tabel.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Eerste kolom (verdieping) smaller
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        # Zorg voor voldoende rijhoogte en minimaal 10 rijen zichtbaar
        self.tabel.verticalHeader().setDefaultSectionSize(24)
        self.tabel.verticalHeader().setVisible(False)

        # Minimale hoogte voor ~10 rijen (header + 10 rijen van 24px + marge)
        min_hoogte = 24 + (10 * 24) + 10  # header + 10 rijen + marge
        self.tabel.setMinimumHeight(min_hoogte)

        self.tabel.setAlternatingRowColors(True)
        layout.addWidget(self.tabel)

        # Knoppen - in apart frame om overlap te voorkomen
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 2, 0, 2)

        btn_kopieer = QPushButton("📋 Kopieer eerste rij naar alle")
        btn_kopieer.setStyleSheet(get_button_style_secundair())
        btn_kopieer.clicked.connect(self._kopieer_naar_alle)
        btn_layout.addWidget(btn_kopieer)

        btn_layout.addStretch()

        layout.addWidget(btn_frame)
    
    def _vul_tabel(self):
        """Vul de tabel met verdieping data"""
        self.tabel.blockSignals(True)
        self.tabel.setRowCount(len(self.trap.verdiepingen))
        
        for row, tv in enumerate(self.trap.verdiepingen):
            col = 0
            
            # Verdieping nummer (read-only)
            item = QTableWidgetItem(str(tv.verdieping))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, col, item)
            col += 1
            
            # Doorgang naar trap
            item = QTableWidgetItem(f"{tv.doorgang_naar_trap_m:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, col, item)
            col += 1
            
            # Type doorgang (dropdown via combo box in cell)
            combo = QComboBox()
            # BBL Artikel 4.80 lid 1 doorgang types
            combo.addItems([dt.value for dt in DoorgangType])
            combo.setCurrentText(tv.type_doorgang.value)
            self.tabel.setCellWidget(row, col, combo)
            col += 1
            
            # Bordes oppervlakte
            item = QTableWidgetItem(f"{tv.oppervlakte_bordes_m2:.1f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, col, item)
            col += 1
            
            # Tussenbordes oppervlakte
            item = QTableWidgetItem(f"{tv.oppervlakte_tussenbordessen_m2:.1f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, col, item)
            col += 1
            
            # Hoogteverschil
            item = QTableWidgetItem(f"{tv.hoogteverschil_m:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, col, item)
            col += 1
            
            # Breedte trap
            item = QTableWidgetItem(f"{tv.breedte_trap_m:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, col, item)
            col += 1
            
            # Aantal treden
            item = QTableWidgetItem(str(tv.aantal_treden))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, col, item)
            col += 1
            
            # Verdeling percentage
            item = QTableWidgetItem(f"{tv.verdeling_fractie * 100:.0f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, col, item)
            col += 1
            
            # Gefaseerde vertraging
            item = QTableWidgetItem(f"{tv.gefaseerde_vertraging_min:.1f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, col, item)
        
        self.tabel.blockSignals(False)
    
    def _kopieer_naar_alle(self):
        """Kopieer eerste rij naar alle andere rijen"""
        if self.tabel.rowCount() < 2:
            return
        
        # Lees eerste rij
        eerste_rij = self._lees_rij(0)
        if eerste_rij is None:
            return
        
        # Pas toe op alle andere rijen (behoud verdieping nummer)
        self.tabel.blockSignals(True)
        
        for row in range(1, self.tabel.rowCount()):
            col = 1  # Skip verdieping nummer
            
            self.tabel.item(row, col).setText(f"{eerste_rij['doorgang']:.2f}")
            col += 1
            
            combo = self.tabel.cellWidget(row, col)
            combo.setCurrentText(eerste_rij['type_doorgang'])
            col += 1
            
            self.tabel.item(row, col).setText(f"{eerste_rij['bordes']:.1f}")
            col += 1
            
            self.tabel.item(row, col).setText(f"{eerste_rij['tussen']:.1f}")
            col += 1
            
            self.tabel.item(row, col).setText(f"{eerste_rij['hoogte']:.2f}")
            col += 1
            
            self.tabel.item(row, col).setText(f"{eerste_rij['breedte']:.2f}")
            col += 1
            
            self.tabel.item(row, col).setText(str(eerste_rij['treden']))
            col += 1
            
            self.tabel.item(row, col).setText(f"{eerste_rij['verdeling']:.0f}")
            col += 1
            
            self.tabel.item(row, col).setText(f"{eerste_rij['vertraging']:.1f}")
        
        self.tabel.blockSignals(False)
    
    def _lees_rij(self, row: int) -> Optional[dict]:
        """Lees data van een rij"""
        try:
            col = 1
            doorgang = float(self.tabel.item(row, col).text())
            col += 1
            
            combo = self.tabel.cellWidget(row, col)
            type_doorgang = combo.currentText()
            col += 1
            
            bordes = float(self.tabel.item(row, col).text())
            col += 1
            
            tussen = float(self.tabel.item(row, col).text())
            col += 1
            
            hoogte = float(self.tabel.item(row, col).text())
            col += 1
            
            breedte = float(self.tabel.item(row, col).text())
            col += 1
            
            treden = int(self.tabel.item(row, col).text())
            col += 1
            
            verdeling = float(self.tabel.item(row, col).text())
            col += 1
            
            vertraging = float(self.tabel.item(row, col).text())
            
            return {
                'doorgang': doorgang,
                'type_doorgang': type_doorgang,
                'bordes': bordes,
                'tussen': tussen,
                'hoogte': hoogte,
                'breedte': breedte,
                'treden': treden,
                'verdeling': verdeling,
                'vertraging': vertraging
            }
        except (ValueError, AttributeError):
            return None
    
    def sla_op(self):
        """Sla tabel data op naar trap"""
        for row in range(self.tabel.rowCount()):
            data = self._lees_rij(row)
            if data is None:
                continue
            
            verd_nr = int(self.tabel.item(row, 0).text())
            tv = self.trap.get_verdieping(verd_nr)
            
            if tv:
                tv.doorgang_naar_trap_m = data['doorgang']
                tv.type_doorgang = DoorgangType(data['type_doorgang'])
                tv.oppervlakte_bordes_m2 = data['bordes']
                tv.oppervlakte_tussenbordessen_m2 = data['tussen']
                tv.hoogteverschil_m = data['hoogte']
                tv.breedte_trap_m = data['breedte']
                tv.aantal_treden = data['treden']
                tv.verdeling_fractie = data['verdeling'] / 100.0
                tv.gefaseerde_vertraging_min = data['vertraging']
                tv.reset_cache()


class TrapEditor(QWidget):
    """Editor voor een enkele trap"""
    
    def __init__(self, trap: Trap, parent=None):
        super().__init__(parent)
        self.trap = trap
        self._setup_ui()
        self._vul_velden()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)

        # Algemene instellingen
        algemeen_groep = QGroupBox("Algemene instellingen")
        algemeen_layout = QFormLayout()
        algemeen_layout.setSpacing(6)
        algemeen_layout.setContentsMargins(8, 12, 8, 8)
        
        # Type vluchtroute (bepaalt automatisch ontruimingstijd volgens BBL 4.81 lid 1)
        self.cmb_locatie = QComboBox()
        self.cmb_locatie.addItems([loc.value for loc in LocatieType])
        self.cmb_locatie.setToolTip(
            "BBL Art. 4.81 lid 1 - Type vluchtroute bepaalt de ontruimingstijd:\n"
            "• Veiligheidsvluchtroute: 30 minuten\n"
            "• Extra beschermde vluchtroute: 20 minuten\n"
            "• Beschermde vluchtroute: 15 minuten"
        )
        algemeen_layout.addRow("Type vluchtroute:", self.cmb_locatie)

        # Uitgang instellingen
        uitgang_layout = QHBoxLayout()
        self.spin_uitgang_breedte = QDoubleSpinBox()
        self.spin_uitgang_breedte.setRange(0.5, 5.0)
        self.spin_uitgang_breedte.setDecimals(2)
        self.spin_uitgang_breedte.setSingleStep(0.1)
        uitgang_layout.addWidget(self.spin_uitgang_breedte)
        uitgang_layout.addWidget(QLabel("m, Type:"))
        self.cmb_uitgang_type = QComboBox()
        # BBL Artikel 4.80 lid 1 doorgang types
        self.cmb_uitgang_type.addItems([dt.value for dt in DoorgangType])
        uitgang_layout.addWidget(self.cmb_uitgang_type)
        algemeen_layout.addRow("Doorgang uitgang:", uitgang_layout)
        
        self.spin_onder_uitgang = QSpinBox()
        self.spin_onder_uitgang.setRange(0, 10)
        algemeen_layout.addRow("Verdiepingen onder uitgang:", self.spin_onder_uitgang)

        # Tijd verlaten verdieping (BBL Art. 4.81 lid 3)
        self.cmb_verlaat_tijd = QComboBox()
        self.cmb_verlaat_tijd.addItems([vt.value for vt in VerlaatTijdType])
        self.cmb_verlaat_tijd.setToolTip(
            "BBL Art. 4.81 lid 3 - Tijd om verdieping te verlaten:\n"
            "• Standaard (3,5 min): voor alle ruimtes\n"
            "• Verlengd (6 min): alleen als BEIDE voorwaarden gelden:\n"
            "  1. WBDBO ≥ 30 min (NEN 6068)\n"
            "  2. Rookwerendheid R200 (NEN 6075)"
        )
        algemeen_layout.addRow("Tijd verlaten verdieping:", self.cmb_verlaat_tijd)
        
        self.chk_voorportaal = QCheckBox("Voorportalen actief voor deze trap")
        algemeen_layout.addRow("", self.chk_voorportaal)
        
        algemeen_groep.setLayout(algemeen_layout)
        layout.addWidget(algemeen_groep)

        # Verdieping instellingen - geef dit de meeste ruimte
        verd_groep = QGroupBox("Per verdieping")
        verd_layout = QVBoxLayout()
        verd_layout.setContentsMargins(4, 8, 4, 4)
        verd_layout.setSpacing(4)

        self.verd_editor = TrapVerdiepingEditor(self.trap)
        verd_layout.addWidget(self.verd_editor, 1)  # stretch factor 1

        verd_groep.setLayout(verd_layout)
        layout.addWidget(verd_groep, 1)  # stretch factor 1 om ruimte te vullen
    
    def _vul_velden(self):
        """Vul de velden met trap data"""
        self.cmb_locatie.setCurrentText(self.trap.locatie.value)
        self.spin_uitgang_breedte.setValue(self.trap.doorgang_uitgang_m)
        self.cmb_uitgang_type.setCurrentText(self.trap.type_uitgang.value)
        # Ontruimingstijd wordt automatisch afgeleid van locatie (BBL 4.81 lid 1)
        self.spin_onder_uitgang.setValue(self.trap.verdiepingen_onder_uitgang)
        # Tijd verlaten verdieping wordt automatisch afgeleid van verlaat_tijd_type (BBL 4.81 lid 3)
        self.cmb_verlaat_tijd.setCurrentText(self.trap.verlaat_tijd_type.value)
        self.chk_voorportaal.setChecked(self.trap.voorportaal_aanwezig)

    def sla_op(self):
        """Sla alle instellingen op"""
        self.trap.locatie = LocatieType(self.cmb_locatie.currentText())
        self.trap.doorgang_uitgang_m = self.spin_uitgang_breedte.value()
        self.trap.type_uitgang = DoorgangType(self.cmb_uitgang_type.currentText())
        # Ontruimingstijd wordt automatisch afgeleid van locatie (BBL 4.81 lid 1)
        self.trap.verdiepingen_onder_uitgang = self.spin_onder_uitgang.value()
        # Tijd verlaten verdieping wordt automatisch afgeleid van verlaat_tijd_type (BBL 4.81 lid 3)
        self.trap.verlaat_tijd_type = VerlaatTijdType(self.cmb_verlaat_tijd.currentText())
        self.trap.voorportaal_aanwezig = self.chk_voorportaal.isChecked()
        self.trap.reset_cache()
        
        # Update voorportaal actief voor alle verdiepingen
        for tv in self.trap.verdiepingen:
            tv.voorportaal_actief = self.trap.voorportaal_aanwezig
        
        # Sla verdieping data op
        self.verd_editor.sla_op()


class TrapConfigWidget(QWidget):
    """Widget voor configuratie van alle trappen"""
    
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.trap_editors = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)
        
        # Instructie
        instructie = QLabel(
            "Configureer de eigenschappen van elke trap. "
            "De verdieping-specifieke instellingen bepalen de doorstroomcapaciteit."
        )
        instructie.setWordWrap(True)
        layout.addWidget(instructie)
        
        # Tab widget voor trappen
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self._maak_tabs()
    
    def _maak_tabs(self):
        """Maak tabs voor elke trap"""
        self.tabs.clear()
        self.trap_editors.clear()

        for trap in self.project.trappen:
            editor = TrapEditor(trap)
            self.trap_editors.append(editor)

            # Voeg editor direct toe (tabel heeft eigen scroll)
            self.tabs.addTab(editor, trap.aanduiding)
    
    def update_project(self, project: Project):
        """Update met nieuw project"""
        self.project = project
        self._maak_tabs()
    
    def sla_op(self):
        """Sla alle trap configuraties op"""
        for editor in self.trap_editors:
            editor.sla_op()
