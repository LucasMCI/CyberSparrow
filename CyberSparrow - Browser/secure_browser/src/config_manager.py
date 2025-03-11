#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de gerenciamento de configuração do navegador
"""

import os
import json
import yaml
from typing import Dict, Any, Optional

class ConfigManager:
    """Gerenciador de configuração do navegador"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config_data: Dict[str, Any] = {}
        self._ensure_config_dir()
        self.load_config()
        
    def _ensure_config_dir(self):
        """Garante que o diretório de configuração existe"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
    def load_config(self):
        """Carrega a configuração do arquivo"""
        config_path = os.path.join(self.config_dir, "browser_config.yaml")
        
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                self.config_data = yaml.safe_load(file) or {}
        except FileNotFoundError:
            self.create_default_config()
            
    def create_default_config(self):
        """Cria a configuração padrão"""
        default_config = {
            "general": {
                "home_page": "https://www.duckduckgo.com",
                "download_dir": "downloads",
                "theme": "dark"
            },
            "security": {
                "block_scripts": True,
                "block_ads": True,
                "block_trackers": True,
                "anonymous_mode": True
            },
            "privacy": {
                "doh_enabled": True,
                "doh_provider": "https://dns.google/dns-query",
                "block_fingerprinting": True
            },
            "proxy": {
                "enabled": False,
                "type": "socks5",
                "host": "127.0.0.1",
                "port": 9050
            }
        }
        
        self.config_data = default_config
        self.save_config()
        
    def save_config(self):
        """Salva a configuração no arquivo"""
        config_path = os.path.join(self.config_dir, "browser_config.yaml")
        
        with open(config_path, "w", encoding="utf-8") as file:
            yaml.dump(self.config_data, file, default_flow_style=False)
            
    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração"""
        if section in self.config_data and key in self.config_data[section]:
            return self.config_data[section][key]
        return default
        
    def set_config(self, section: str, key: str, value: Any) -> bool:
        """Define um valor de configuração"""
        if section not in self.config_data:
            self.config_data[section] = {}
            
        self.config_data[section][key] = value
        self.save_config()
        return True
        
    def get_section(self, section: str) -> Dict[str, Any]:
        """Obtém uma seção inteira da configuração"""
        return self.config_data.get(section, {})
        
    def export_config(self, filename: str) -> bool:
        """Exporta a configuração para um arquivo"""
        try:
            with open(filename, "w", encoding="utf-8") as file:
                yaml.dump(self.config_data, file, default_flow_style=False)
            return True
        except Exception:
            return False
            
    def import_config(self, filename: str) -> bool:
        """Importa a configuração de um arquivo"""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                if isinstance(config, dict):
                    self.config_data = config
                    self.save_config()
                    return True
            return False
        except Exception:
            return False