#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                          QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                          QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt, QDateTime
from history import HistoryManager

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_manager = HistoryManager()
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        """Configura a interface do histórico"""
        self.setWindowTitle("Histórico de Navegação")
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        layout = QVBoxLayout(self)

        # Área de pesquisa
        search_layout = QHBoxLayout()
        search_label = QLabel("Pesquisar:")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_history)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Tabela de histórico
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Título", "URL", "Data", "Visitas"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        # Botões
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Limpar Histórico")
        self.clear_button.clicked.connect(self.clear_history)
        
        self.delete_button = QPushButton("Excluir Item")
        self.delete_button.clicked.connect(self.delete_selected)
        
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)

    def load_history(self):
        """Carrega o histórico na tabela"""
        history = self.history_manager.get_history()
        self.table.setRowCount(len(history))
        
        for row, (url, title, timestamp, count) in enumerate(history):
            # Título
            title_item = QTableWidgetItem(title or "Sem título")
            title_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, title_item)
            
            # URL
            url_item = QTableWidgetItem(url)
            url_item.setFlags(url_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, url_item)
            
            # Data
            date = QDateTime.fromString(timestamp, Qt.DateFormat.ISODate)
            date_item = QTableWidgetItem(date.toString("dd/MM/yyyy HH:mm"))
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, date_item)
            
            # Contagem
            count_item = QTableWidgetItem(str(count))
            count_item.setFlags(count_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, count_item)

    def search_history(self):
        """Pesquisa no histórico"""
        query = self.search_input.text()
        if query:
            results = self.history_manager.search_history(query)
        else:
            results = self.history_manager.get_history()
            
        self.table.setRowCount(len(results))
        for row, (url, title, timestamp, count) in enumerate(results):
            self.table.setItem(row, 0, QTableWidgetItem(title or "Sem título"))
            self.table.setItem(row, 1, QTableWidgetItem(url))
            date = QDateTime.fromString(timestamp, Qt.DateFormat.ISODate)
            self.table.setItem(row, 2, QTableWidgetItem(date.toString("dd/MM/yyyy HH:mm")))
            self.table.setItem(row, 3, QTableWidgetItem(str(count)))

    def clear_history(self):
        """Limpa todo o histórico"""
        reply = QMessageBox.question(
            self,
            "Limpar Histórico",
            "Tem certeza que deseja limpar todo o histórico?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history_manager.clear_history()
            self.load_history()

    def delete_selected(self):
        """Deleta os itens selecionados"""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            return
            
        reply = QMessageBox.question(
            self,
            "Excluir Itens",
            f"Tem certeza que deseja excluir {len(selected_rows)} item(ns)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for row in sorted(selected_rows, reverse=True):
                url = self.table.item(row, 1).text()
                self.history_manager.delete_entry(url)
            self.load_history() 