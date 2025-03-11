#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CyberSparrow - Um navegador web seguro para profissionais de cibersegurança
"""

import sys
import os
import logging
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                            QWidget, QToolBar, QStatusBar, QMenu, QMenuBar, 
                            QMessageBox, QDialog, QLineEdit, QPushButton, QHBoxLayout)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QSize
from PyQt6.QtGui import QIcon, QAction
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cybersparrow.log"),
        logging.StreamHandler()
    ]
)

# Importar módulos do navegador
try:
    from security import SecurityInterceptor, FirewallManager
    from privacy import PrivacyManager, DNSCache
    from traffic_analyzer import TrafficAnalyzer, PacketInspector
    from traffic_analyzer_ui import TrafficAnalyzerWidget
    from config_manager import ConfigManager
    from history import HistoryManager
    from history_ui import HistoryDialog
    from extensions import ExtensionManager
    from extensions_ui import ExtensionsDialog
    from redteam import RedTeamTools
    from redteam_ui import RedTeamDialog
except ImportError:
    # Ajustar caminho para importação
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from security import SecurityInterceptor, FirewallManager
    from privacy import PrivacyManager, DNSCache
    from traffic_analyzer import TrafficAnalyzer, PacketInspector
    from traffic_analyzer_ui import TrafficAnalyzerWidget
    from config_manager import ConfigManager
    from history import HistoryManager
    from history_ui import HistoryDialog
    from extensions import ExtensionManager
    from extensions_ui import ExtensionsDialog
    from redteam import RedTeamTools
    from redteam_ui import RedTeamDialog

class TrafficAnalyzerDialog(QDialog):
    """Diálogo do analisador de tráfego"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analisador de Tráfego")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout(self)
        self.analyzer_widget = TrafficAnalyzerWidget(self)
        layout.addWidget(self.analyzer_widget)

class SecureBrowser(QMainWindow):
    """Classe principal do navegador seguro"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("CyberSparrow")
        self.logger.info("Iniciando o CyberSparrow")
        
        # Configurar ícone do programa
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Inicializar componentes
        self.config_manager = ConfigManager()
        self.security_interceptor = SecurityInterceptor()
        self.firewall = FirewallManager()
        self.privacy_manager = PrivacyManager()
        self.traffic_analyzer = TrafficAnalyzer()
        self.history_manager = HistoryManager()
        self.extension_manager = ExtensionManager()
        
        # Configuração da interface
        self.setWindowTitle("CyberSparrow")
        self.setGeometry(100, 100, 1280, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Barra de navegação
        nav_layout = QHBoxLayout()
        
        # Campo de URL/Pesquisa
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.url_bar)
        
        layout.addLayout(nav_layout)
        
        # Barra de ferramentas
        self.toolbar = QToolBar("Navegação")
        self.toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.toolbar)
        
        # Ações da barra de ferramentas
        self.setup_toolbar_actions()
        
        # Configuração das abas
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        
        # Botão de nova aba
        new_tab_button = QPushButton("+")
        new_tab_button.setFixedSize(28, 28)
        new_tab_button.clicked.connect(lambda: self.add_new_tab())
        new_tab_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-size: 20px;
                font-weight: bold;
                color: #666;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 14px;
                color: #000;
            }
            QPushButton:pressed {
                background-color: #ccc;
            }
        """)
        
        # Adicionar o botão no canto direito das abas
        self.tabs.setCornerWidget(new_tab_button, Qt.Corner.TopRightCorner)
        
        # Adicionar abas ao layout principal
        layout.addWidget(self.tabs)
        
        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Menu principal
        self.create_menus()
        
        # Criar primeira aba
        self.add_new_tab()
        
        self.logger.info("Navegador seguro iniciado com sucesso")
        
    def setup_toolbar_actions(self):
        """Configura as ações da barra de ferramentas"""
        # Navegação
        self.back_action = QAction("Voltar", self)
        self.back_action.triggered.connect(self.navigate_back)
        self.toolbar.addAction(self.back_action)
        
        self.forward_action = QAction("Avançar", self)
        self.forward_action.triggered.connect(self.navigate_forward)
        self.toolbar.addAction(self.forward_action)
        
        self.reload_action = QAction("Recarregar", self)
        self.reload_action.triggered.connect(self.reload_page)
        self.toolbar.addAction(self.reload_action)
        
        self.home_action = QAction("Início", self)
        self.home_action.triggered.connect(self.navigate_home)
        self.toolbar.addAction(self.home_action)
        
        # Segurança
        self.toolbar.addSeparator()
        
        self.security_action = QAction("Segurança", self)
        self.security_action.setCheckable(True)
        self.security_action.setChecked(True)
        self.toolbar.addAction(self.security_action)
        
        self.privacy_action = QAction("Privacidade", self)
        self.privacy_action.setCheckable(True)
        self.privacy_action.setChecked(True)
        self.toolbar.addAction(self.privacy_action)
        
    def create_menus(self):
        """Cria os menus do navegador"""
        # Menu Arquivo
        file_menu = self.menuBar().addMenu("Arquivo")
        
        new_tab_action = QAction("Nova Aba", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        file_menu.addAction(new_tab_action)
        
        history_action = QAction("Histórico", self)
        history_action.setShortcut("Ctrl+H")
        history_action.triggered.connect(self.show_history)
        file_menu.addAction(history_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Segurança
        security_menu = self.menuBar().addMenu("Segurança")
        
        toggle_scripts_action = QAction("Bloquear Scripts", self)
        toggle_scripts_action.setCheckable(True)
        toggle_scripts_action.setChecked(True)
        security_menu.addAction(toggle_scripts_action)
        
        toggle_trackers_action = QAction("Bloquear Rastreadores", self)
        toggle_trackers_action.setCheckable(True)
        toggle_trackers_action.setChecked(True)
        security_menu.addAction(toggle_trackers_action)
        
        # Menu Red Team
        #redteam_menu = self.menuBar().addMenu("Red Team")
        

        
        # Menu Ferramentas
        tools_menu = self.menuBar().addMenu("Ferramentas")
        
        traffic_analyzer_action = QAction("Analisador de Tráfego", self)
        traffic_analyzer_action.triggered.connect(self.show_traffic_analyzer)
        tools_menu.addAction(traffic_analyzer_action)
        
        extensions_action = QAction("Extensões", self)
        extensions_action.triggered.connect(self.show_extensions)
        tools_menu.addAction(extensions_action)
        
        redteam_tools_action = QAction("Ferramentas Red Team", self)
        redteam_tools_action.setShortcut("Ctrl+R")
        redteam_tools_action.triggered.connect(self.show_redteam_tools)
        tools_menu.addAction(redteam_tools_action)
        # Menu Ajuda
        help_menu = self.menuBar().addMenu("Ajuda")
        
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def add_new_tab(self, url="https://www.duckduckgo.com"):
        """Adiciona uma nova aba ao navegador"""
        web_view = QWebEngineView()
        web_view.setUrl(QUrl(url))
        
        # Configurações de privacidade
        profile = web_view.page().profile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
        
        # Aplicar configurações de privacidade
        self.privacy_manager.block_fingerprinting(profile)
        self.privacy_manager.configure_doh(profile)
        
        # Conectar sinais
        web_view.loadStarted.connect(lambda: self.status_bar.showMessage("Carregando..."))
        web_view.loadFinished.connect(self.on_load_finished)
        web_view.urlChanged.connect(lambda url: self.update_url_bar(url))
        
        index = self.tabs.addTab(web_view, "Nova Aba")
        self.tabs.setCurrentIndex(index)
        
        # Atualizar título da aba quando a página carregar
        web_view.titleChanged.connect(lambda title: self.update_tab_title(index, title))
        
    def close_tab(self, index):
        """Fecha uma aba do navegador"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()
            
    def update_tab_title(self, index, title):
        """Atualiza o título da aba"""
        if title:
            self.tabs.setTabText(index, title)
        else:
            self.tabs.setTabText(index, "Nova Aba")
            
    def navigate_back(self):
        """Navega para a página anterior"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.back()
            
    def navigate_forward(self):
        """Navega para a próxima página"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.forward()
            
    def reload_page(self):
        """Recarrega a página atual"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.reload()
            
    def navigate_home(self):
        """Navega para a página inicial"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.setUrl(QUrl("https://www.duckduckgo.com"))
            
    def show_traffic_analyzer(self):
        """Exibe o analisador de tráfego"""
        dialog = TrafficAnalyzerDialog(self)
        dialog.exec()
        
    def show_about(self):
        """Exibe informações sobre o navegador"""
        about_text = """CyberSparrow v1.0

Um navegador web seguro para profissionais de cibersegurança.

FUNCIONALIDADES:

1. Navegação Segura:
   • Bloqueio de scripts maliciosos
   • Proteção contra rastreadores
   • Modo de navegação anônima
   • DNS sobre HTTPS (DoH)

2. Ferramentas Red Team:
   • WHOIS - Consulta informações de domínios
   • Enumeração DNS - Busca registros DNS
   • Scanner de Portas - Varredura de portas TCP
   • Busca de Subdomínios
   • Crawler Web
   • Detecção de WAF
   • Análise de Headers de Segurança
   • Verificação de CORS

3. Análise de Tráfego:
   • Captura de pacotes em tempo real
   • Inspeção de conexões
   • Estatísticas de tráfego
   • Detecção de anomalias

4. Privacidade:
   • Bloqueio de fingerprinting
   • Sem histórico persistente
   • Proteção contra vazamento de DNS
   • Cookies temporários

5. Interface:
   • Design moderno e intuitivo
   • Suporte a múltiplas abas
   • Barra de ferramentas personalizável
   • Atalhos de teclado

Desenvolvido com PyQt6 e tecnologias modernas de segurança.

Criado por Lucas MCI.
@https://github.com/LucasMCI"""
        
        QMessageBox.about(self, "Sobre o CyberSparrow", about_text)

    def navigate_to_url(self):
        """Navega para a URL digitada ou realiza uma pesquisa"""
        url = self.url_bar.text()
        
        # Verifica se é uma URL válida
        if not url.startswith(('http://', 'https://')):
            # Verifica se tem extensão de domínio
            if not re.search(r'\.[a-zA-Z]{2,}$', url):
                # Se não tiver extensão, faz uma pesquisa
                url = f"https://duckduckgo.com/?q={url}"
            else:
                # Adiciona https:// se for um domínio
                url = f"https://{url}"
        
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.setUrl(QUrl(url))
            
    def tab_changed(self, index):
        """Atualiza a barra de URL quando a aba é alterada"""
        if index >= 0:
            current_tab = self.tabs.widget(index)
            if current_tab:
                url = current_tab.url().toString()
                self.url_bar.setText(url)

    def update_url_bar(self, url):
        """Atualiza a barra de URL"""
        if self.tabs.currentWidget() == self.sender():
            self.url_bar.setText(url.toString())
            self.url_bar.setCursorPosition(0)

    def on_load_finished(self):
        """Chamado quando uma página termina de carregar"""
        self.status_bar.showMessage("Pronto")
        current_tab = self.tabs.currentWidget()
        if current_tab:
            url = current_tab.url().toString()
            title = current_tab.title()
            self.history_manager.add_visit(url, title)

    def show_history(self):
        """Exibe o diálogo de histórico"""
        dialog = HistoryDialog(self)
        dialog.exec()

    def show_extensions(self):
        """Exibe o diálogo de extensões"""
        dialog = ExtensionsDialog(self)
        dialog.exec()

    def show_redteam_tools(self):
        """Exibe o diálogo de ferramentas Red Team"""
        dialog = RedTeamDialog(self)
        dialog.exec()

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    browser = SecureBrowser()
    browser.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()