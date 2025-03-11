#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface do analisador de tráfego
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QLabel, QComboBox,
                           QSpinBox, QTabWidget, QTextEdit)
from PyQt6.QtCore import Qt, QTimer
import time

class TrafficAnalyzerWidget(QWidget):
    """Widget do analisador de tráfego"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.is_capturing = False
        self.packet_count = 0
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        layout = QVBoxLayout(self)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        # Botão de captura
        self.capture_button = QPushButton("Iniciar Captura")
        self.capture_button.clicked.connect(self.toggle_capture)
        controls_layout.addWidget(self.capture_button)
        
        # Botão de limpar
        self.clear_button = QPushButton("Limpar")
        self.clear_button.clicked.connect(self.clear_data)
        controls_layout.addWidget(self.clear_button)
        
        # Filtros
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["Todos", "TCP", "UDP"])
        controls_layout.addWidget(QLabel("Protocolo:"))
        controls_layout.addWidget(self.protocol_combo)
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(0, 65535)
        controls_layout.addWidget(QLabel("Porta:"))
        controls_layout.addWidget(self.port_spin)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Abas
        self.tabs = QTabWidget()
        
        # Aba de pacotes
        self.packets_table = QTableWidget()
        self.packets_table.setColumnCount(7)
        self.packets_table.setHorizontalHeaderLabels([
            "Timestamp", "Origem", "Destino", "Protocolo", 
            "Porta Origem", "Porta Destino", "Tamanho"
        ])
        self.tabs.addTab(self.packets_table, "Pacotes")
        
        # Aba de estatísticas
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.tabs.addTab(self.stats_text, "Estatísticas")
        
        layout.addWidget(self.tabs)
        
        # Timer para atualizar estatísticas
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(1000)  # Atualiza a cada segundo
        
    def packet_handler(self, packet_info):
        """Manipula pacotes capturados"""
        self.packet_count += 1
        
        # Adiciona pacote à tabela
        row = self.packets_table.rowCount()
        self.packets_table.insertRow(row)
        
        # Formata timestamp
        timestamp = time.strftime('%H:%M:%S', time.localtime(packet_info['timestamp']))
        
        # Preenche as colunas
        self.packets_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.packets_table.setItem(row, 1, QTableWidgetItem(packet_info['src']))
        self.packets_table.setItem(row, 2, QTableWidgetItem(packet_info['dst']))
        self.packets_table.setItem(row, 3, QTableWidgetItem(packet_info['type']))
        
        if 'sport' in packet_info:
            self.packets_table.setItem(row, 4, QTableWidgetItem(str(packet_info['sport'])))
        if 'dport' in packet_info:
            self.packets_table.setItem(row, 5, QTableWidgetItem(str(packet_info['dport'])))
            
        self.packets_table.setItem(row, 6, QTableWidgetItem(str(packet_info['size'])))
        
        # Rola para o último item
        self.packets_table.scrollToBottom()
        
    def toggle_capture(self):
        """Alterna a captura de pacotes"""
        if not self.is_capturing:
            self.capture_button.setText("Parar Captura")
            self.is_capturing = True
            self.parent().parent().traffic_analyzer.start_capture(callback=self.packet_handler)
        else:
            self.capture_button.setText("Iniciar Captura")
            self.is_capturing = False
            self.parent().parent().traffic_analyzer.stop_capture()
            
    def clear_data(self):
        """Limpa os dados capturados"""
        self.packets_table.setRowCount(0)
        self.packet_count = 0
        self.update_statistics()
        
    def update_statistics(self):
        """Atualiza as estatísticas"""
        if not self.is_capturing:
            return
            
        stats = self.parent().parent().traffic_analyzer.get_statistics()
        
        stats_text = f"""Estatísticas de Captura:
        
Total de Pacotes: {stats['total_packets']}
Pacotes TCP: {stats['tcp_packets']}
Pacotes UDP: {stats['udp_packets']}
Total de Bytes: {stats['total_bytes']}
Taxa de Pacotes: {self.packet_count} pacotes/s

Status: {'Capturando' if self.is_capturing else 'Parado'}
"""
        
        self.stats_text.setText(stats_text)
        self.packet_count = 0  # Reseta o contador para o próximo segundo 