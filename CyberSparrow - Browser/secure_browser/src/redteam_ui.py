#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                          QTabWidget, QWidget, QLabel, QLineEdit, QTextEdit,
                          QMessageBox, QComboBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from redteam import RedTeamTools
import json

class ScanThread(QThread):
    """Thread para executar as ferramentas em segundo plano"""
    finished = pyqtSignal(str, str)  # sinal: (resultado, tipo_operacao)
    error = pyqtSignal(str)  # sinal para erros
    
    def __init__(self, tool_type, target, *args):
        super().__init__()
        self.tool_type = tool_type
        self.target = target
        self.args = args
        self.tools = RedTeamTools()
        
    def run(self):
        try:
            result = None
            if self.tool_type == "whois":
                result = self.tools.get_whois(self.target)
            elif self.tool_type == "dns":
                result = self.tools.dns_enumeration(self.target)
            elif self.tool_type == "subdomains":
                result = self.tools.find_subdomains(self.target)
            elif self.tool_type == "ports":
                result = self.tools.scan_ports(self.target, self.args[0])
            elif self.tool_type == "crawl":
                result = self.tools.crawl_site(self.target)
            elif self.tool_type == "waf":
                result = self.tools.check_waf(self.target)
            elif self.tool_type == "headers":
                result = self.tools.check_headers(self.target)
            elif self.tool_type == "cors":
                result = self.tools.check_cors(self.target)
                
            if isinstance(result, dict) and "error" in result:
                self.error.emit(str(result["error"]))
            else:
                self.finished.emit(json.dumps(result, indent=2, default=str), self.tool_type)
        except Exception as e:
            self.error.emit(str(e))

class RedTeamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tools = RedTeamTools()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface das ferramentas Red Team"""
        self.setWindowTitle("Ferramentas Red Team")
        self.setGeometry(100, 100, 1000, 700)
        
        layout = QVBoxLayout(self)
        
        # Tabs para diferentes ferramentas
        self.tabs = QTabWidget()
        
        # Tab de Reconhecimento
        recon_tab = QWidget()
        recon_layout = QVBoxLayout(recon_tab)
        
        # Campo de entrada para domínio/IP
        target_layout = QHBoxLayout()
        target_label = QLabel("Alvo:")
        self.target_input = QLineEdit()
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_input)
        recon_layout.addLayout(target_layout)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.whois_button = QPushButton("WHOIS")
        self.whois_button.clicked.connect(lambda: self.start_scan("whois"))
        
        self.dns_button = QPushButton("Enumeração DNS")
        self.dns_button.clicked.connect(lambda: self.start_scan("dns"))
        
        self.subdomain_button = QPushButton("Buscar Subdomínios")
        self.subdomain_button.clicked.connect(lambda: self.start_scan("subdomains"))
        
        button_layout.addWidget(self.whois_button)
        button_layout.addWidget(self.dns_button)
        button_layout.addWidget(self.subdomain_button)
        recon_layout.addLayout(button_layout)
        
        # Área de resultados
        self.recon_output = QTextEdit()
        self.recon_output.setReadOnly(True)
        recon_layout.addWidget(self.recon_output)
        
        self.tabs.addTab(recon_tab, "Reconhecimento")
        
        # Tab de Scanner
        scanner_tab = QWidget()
        scanner_layout = QVBoxLayout(scanner_tab)
        
        # Configurações do scanner
        port_layout = QHBoxLayout()
        port_label = QLabel("Portas:")
        self.port_input = QLineEdit("1-1000")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        scanner_layout.addLayout(port_layout)
        
        # Botão de scan
        self.scan_button = QPushButton("Iniciar Scan")
        self.scan_button.clicked.connect(lambda: self.start_scan("ports"))
        scanner_layout.addWidget(self.scan_button)
        
        # Resultados do scan
        self.scan_output = QTextEdit()
        self.scan_output.setReadOnly(True)
        scanner_layout.addWidget(self.scan_output)
        
        self.tabs.addTab(scanner_tab, "Scanner")
        
        # Tab de Análise Web
        web_tab = QWidget()
        web_layout = QVBoxLayout(web_tab)
        
        # Botões de análise web
        web_button_layout = QHBoxLayout()
        
        self.crawl_button = QPushButton("Crawling")
        self.crawl_button.clicked.connect(lambda: self.start_scan("crawl"))
        
        self.waf_button = QPushButton("Detectar WAF")
        self.waf_button.clicked.connect(lambda: self.start_scan("waf"))
        
        self.headers_button = QPushButton("Analisar Headers")
        self.headers_button.clicked.connect(lambda: self.start_scan("headers"))
        
        self.cors_button = QPushButton("Verificar CORS")
        self.cors_button.clicked.connect(lambda: self.start_scan("cors"))
        
        web_button_layout.addWidget(self.crawl_button)
        web_button_layout.addWidget(self.waf_button)
        web_button_layout.addWidget(self.headers_button)
        web_button_layout.addWidget(self.cors_button)
        web_layout.addLayout(web_button_layout)
        
        # Resultados da análise web
        self.web_output = QTextEdit()
        self.web_output.setReadOnly(True)
        web_layout.addWidget(self.web_output)
        
        self.tabs.addTab(web_tab, "Análise Web")
        
        # Adicionar tabs ao layout principal
        layout.addWidget(self.tabs)
        
        # Barra de progresso
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        
        # Botão de fechar
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)
        
    def start_scan(self, scan_type):
        """Inicia uma operação de scan"""
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "Erro", "Digite um domínio válido")
            return
            
        # Desabilitar botões durante o scan
        self.set_buttons_enabled(False)
        self.progress.setRange(0, 0)  # Modo indeterminado
        
        # Criar e iniciar thread
        self.scan_thread = ScanThread(scan_type, target, self.port_input.text())
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.error.connect(self.on_scan_error)
        self.scan_thread.start()
        
    def on_scan_finished(self, result, scan_type):
        """Chamado quando o scan é concluído"""
        # Reabilitar botões
        self.set_buttons_enabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        
        # Exibir resultados na área apropriada
        if self.tabs.currentIndex() == 0:  # Aba Reconhecimento
            self.recon_output.append(f"\n=== Resultado {scan_type.upper()} ===\n{result}")
        elif self.tabs.currentIndex() == 1:  # Aba Scanner
            self.scan_output.append(f"\n=== Resultado do Scan ===\n{result}")
        else:  # Aba Análise Web
            self.web_output.append(f"\n=== Resultado {scan_type.upper()} ===\n{result}")
            
    def on_scan_error(self, error_msg):
        """Chamado quando ocorre um erro durante o scan"""
        self.set_buttons_enabled(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        QMessageBox.warning(self, "Erro", f"Ocorreu um erro: {error_msg}")
        
    def set_buttons_enabled(self, enabled):
        """Habilita/desabilita todos os botões"""
        self.whois_button.setEnabled(enabled)
        self.dns_button.setEnabled(enabled)
        self.subdomain_button.setEnabled(enabled)
        self.scan_button.setEnabled(enabled)
        self.crawl_button.setEnabled(enabled)
        self.waf_button.setEnabled(enabled)
        self.headers_button.setEnabled(enabled)
        self.cors_button.setEnabled(enabled)
        
    def closeEvent(self, event):
        """Chamado quando o diálogo é fechado"""
        # Garantir que todas as threads sejam encerradas
        if hasattr(self, 'scan_thread') and self.scan_thread.isRunning():
            self.scan_thread.terminate()
            self.scan_thread.wait()
        event.accept() 