#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                          QListWidget, QListWidgetItem, QLabel, QFileDialog,
                          QMessageBox, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from extensions import ExtensionManager

class ExtensionItem(QWidget):
    """Widget personalizado para exibir uma extensão"""
    def __init__(self, name, version, description, enabled, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Informações da extensão
        info_layout = QVBoxLayout()
        
        name_label = QLabel(f"<b>{name}</b> v{version}")
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout, stretch=1)
        
        # Botões
        self.toggle_button = QPushButton("Desativar" if enabled else "Ativar")
        self.toggle_button.setProperty("enabled", enabled)
        self.toggle_button.setFixedWidth(80)
        
        self.uninstall_button = QPushButton("Remover")
        self.uninstall_button.setFixedWidth(80)
        
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.uninstall_button)

class ExtensionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.extension_manager = ExtensionManager()
        self.setup_ui()
        self.load_extensions()

    def setup_ui(self):
        """Configura a interface de extensões"""
        self.setWindowTitle("Gerenciador de Extensões")
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        layout = QVBoxLayout(self)

        # Botão de instalar
        install_layout = QHBoxLayout()
        self.install_button = QPushButton("Instalar Nova Extensão")
        self.install_button.clicked.connect(self.install_extension)
        install_layout.addWidget(self.install_button)
        install_layout.addStretch()
        layout.addLayout(install_layout)

        # Lista de extensões
        self.extensions_list = QListWidget()
        self.extensions_list.setSpacing(2)
        layout.addWidget(self.extensions_list)

        # Botão de fechar
        button_layout = QHBoxLayout()
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

    def load_extensions(self):
        """Carrega a lista de extensões instaladas"""
        self.extensions_list.clear()
        extensions = self.extension_manager.get_installed_extensions()
        
        for name, info in extensions.items():
            item = QListWidgetItem()
            self.extensions_list.addItem(item)
            
            widget = ExtensionItem(
                name=name,
                version=info.get("version", "1.0"),
                description=info.get("description", "Sem descrição"),
                enabled=info.get("enabled", True)
            )
            
            # Conectar sinais dos botões
            widget.toggle_button.clicked.connect(lambda checked, n=name, w=widget:
                self.toggle_extension(n, w))
            widget.uninstall_button.clicked.connect(lambda checked, n=name:
                self.uninstall_extension(n))
            
            item.setSizeHint(widget.sizeHint())
            self.extensions_list.setItemWidget(item, widget)

    def install_extension(self):
        """Abre diálogo para instalar nova extensão"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Extensão",
            "",
            "Arquivos de Extensão (*.zip)"
        )
        
        if file_path:
            if self.extension_manager.install_extension(file_path):
                QMessageBox.information(
                    self,
                    "Sucesso",
                    "Extensão instalada com sucesso!"
                )
                self.load_extensions()
            else:
                QMessageBox.critical(
                    self,
                    "Erro",
                    "Erro ao instalar extensão. Verifique o arquivo e tente novamente."
                )

    def uninstall_extension(self, name):
        """Remove uma extensão"""
        reply = QMessageBox.question(
            self,
            "Remover Extensão",
            f"Tem certeza que deseja remover a extensão {name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.extension_manager.uninstall_extension(name):
                self.load_extensions()

    def toggle_extension(self, name, widget):
        """Ativa/desativa uma extensão"""
        current_state = widget.toggle_button.property("enabled")
        
        if current_state:
            success = self.extension_manager.disable_extension(name)
            new_state = False
            new_text = "Ativar"
        else:
            success = self.extension_manager.enable_extension(name)
            new_state = True
            new_text = "Desativar"
            
        if success:
            widget.toggle_button.setText(new_text)
            widget.toggle_button.setProperty("enabled", new_state) 