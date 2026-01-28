"""
Personen invoer widget
Invoer van aantal personen per verdieping
"""

import sys
import os
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QFileDialog, QMessageBox,
    QGroupBox, QSpinBox
)
from PyQt6.QtCore import Qt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Project
from ui.thema import get_button_style_secundair, get_button_style_tertiair


class PersonenInvoerWidget(QWidget):
    """Widget voor invoer van personen per verdieping"""
    
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self._setup_ui()
        self._vul_tabel()
    
    def _setup_ui(self):
        """Setup de user interface"""
        layout = QVBoxLayout(self)
        
        # Instructie
        instructie = QLabel(
            "Voer het aantal personen in per verdieping. "
            "Deze personen worden verdeeld over de beschikbare trappen."
        )
        instructie.setWordWrap(True)
        layout.addWidget(instructie)
        
        # Tabel
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(2)
        self.tabel.setHorizontalHeaderLabels(["Verdieping", "Aantal personen"])
        
        header = self.tabel.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.tabel.setAlternatingRowColors(True)
        layout.addWidget(self.tabel)
        
        # Totaal label
        self.lbl_totaal = QLabel("Totaal: 0 personen")
        self.lbl_totaal.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.lbl_totaal)
        
        # Snelle invoer groep
        snelle_groep = QGroupBox("Snelle invoer")
        snelle_layout = QHBoxLayout()
        
        snelle_layout.addWidget(QLabel("Alle verdiepingen:"))
        self.spin_alle = QSpinBox()
        self.spin_alle.setRange(0, 10000)
        self.spin_alle.setValue(100)
        snelle_layout.addWidget(self.spin_alle)
        
        btn_toepassen = QPushButton("Toepassen op alle")
        btn_toepassen.setStyleSheet(get_button_style_secundair())
        btn_toepassen.clicked.connect(self._pas_toe_op_alle)
        snelle_layout.addWidget(btn_toepassen)

        snelle_layout.addStretch()

        snelle_groep.setLayout(snelle_layout)
        layout.addWidget(snelle_groep)

        # Knoppen
        btn_layout = QHBoxLayout()

        btn_import = QPushButton("📥 Importeer CSV")
        btn_import.setStyleSheet(get_button_style_secundair())
        btn_import.clicked.connect(self._importeer_csv)
        btn_layout.addWidget(btn_import)

        btn_wis = QPushButton("🗑️ Wis alles")
        btn_wis.setStyleSheet(get_button_style_tertiair())
        btn_wis.clicked.connect(self._wis_alles)
        btn_layout.addWidget(btn_wis)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Connect signalen
        self.tabel.cellChanged.connect(self._update_totaal)
    
    def _vul_tabel(self):
        """Vul de tabel met verdiepingen"""
        self.tabel.blockSignals(True)
        
        self.tabel.setRowCount(len(self.project.verdiepingen))
        
        for row, verd in enumerate(self.project.verdiepingen):
            # Verdieping nummer (read-only)
            item_verd = QTableWidgetItem(str(verd.nummer))
            item_verd.setFlags(item_verd.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_verd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, 0, item_verd)
            
            # Aantal personen (editable)
            item_personen = QTableWidgetItem(str(verd.aantal_personen))
            item_personen.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabel.setItem(row, 1, item_personen)
        
        self.tabel.blockSignals(False)
        self._update_totaal()
    
    def _update_totaal(self):
        """Update het totaal label"""
        totaal = 0
        for row in range(self.tabel.rowCount()):
            item = self.tabel.item(row, 1)
            if item:
                try:
                    totaal += int(item.text())
                except ValueError:
                    pass
        
        self.lbl_totaal.setText(f"Totaal: {totaal} personen")
    
    def _pas_toe_op_alle(self):
        """Pas waarde toe op alle verdiepingen"""
        waarde = self.spin_alle.value()
        
        self.tabel.blockSignals(True)
        for row in range(self.tabel.rowCount()):
            self.tabel.item(row, 1).setText(str(waarde))
        self.tabel.blockSignals(False)
        
        self._update_totaal()
    
    def _wis_alles(self):
        """Wis alle personen aantallen"""
        self.tabel.blockSignals(True)
        for row in range(self.tabel.rowCount()):
            self.tabel.item(row, 1).setText("0")
        self.tabel.blockSignals(False)
        
        self._update_totaal()
    
    def _importeer_csv(self):
        """Importeer data van CSV"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Importeer CSV",
            "", "CSV bestanden (*.csv);;Alle bestanden (*)"
        )
        
        if not filename:
            return
        
        try:
            import csv
            
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                data = {}
                
                for row in reader:
                    if len(row) >= 2:
                        try:
                            verd = int(row[0])
                            personen = int(row[1])
                            data[verd] = personen
                        except ValueError:
                            continue
            
            # Pas data toe
            self.tabel.blockSignals(True)
            for row in range(self.tabel.rowCount()):
                verd_item = self.tabel.item(row, 0)
                if verd_item:
                    verd = int(verd_item.text())
                    if verd in data:
                        self.tabel.item(row, 1).setText(str(data[verd]))
            self.tabel.blockSignals(False)
            
            self._update_totaal()
            
        except Exception as e:
            QMessageBox.critical(
                self, "Fout",
                f"Kon CSV niet importeren:\n{str(e)}"
            )
    
    def update_project(self, project: Project):
        """Update met nieuw project"""
        self.project = project
        self._vul_tabel()
    
    def sla_op(self):
        """Sla tabel data op naar project"""
        for row in range(self.tabel.rowCount()):
            verd_item = self.tabel.item(row, 0)
            personen_item = self.tabel.item(row, 1)
            
            if verd_item and personen_item:
                verd_nr = int(verd_item.text())
                
                try:
                    personen = int(personen_item.text())
                except ValueError:
                    personen = 0
                
                # Update project verdieping
                verd = self.project.get_verdieping(verd_nr)
                if verd:
                    verd.aantal_personen = max(0, personen)
