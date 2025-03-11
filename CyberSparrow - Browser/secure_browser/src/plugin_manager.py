#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de gerenciamento de plugins do navegador
"""

import os
import sys
import importlib.util
import json
from typing import Dict, List, Any, Optional
import logging

class Plugin:
    """Classe base para plugins"""
    
    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description
        self.enabled = True
        
    def initialize(self) -> bool:
        """Inicializa o plugin"""
        return True
        
    def shutdown(self) -> bool:
        """Desativa o plugin"""
        return True
        
    def get_info(self) -> Dict[str, str]:
        """Retorna informações sobre o plugin"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled
        }

class PluginManager:
    """Gerenciador de plugins"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("PluginManager")
        
    def discover_plugins(self) -> List[str]:
        """Descobre plugins disponíveis"""
        plugin_files = []
        
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return plugin_files
            
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                plugin_files.append(os.path.join(self.plugin_dir, filename))
                
        return plugin_files
        
    def load_plugin(self, plugin_path: str) -> Optional[Plugin]:
        """Carrega um plugin a partir do caminho do arquivo"""
        try:
            plugin_name = os.path.basename(plugin_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            
            if spec is None or spec.loader is None:
                self.logger.error(f"Não foi possível carregar o plugin: {plugin_path}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            # Verifica se o módulo tem uma classe Plugin
            if hasattr(module, "Plugin"):
                plugin_class = getattr(module, "Plugin")
                plugin_instance = plugin_class()
                
                if isinstance(plugin_instance, Plugin):
                    self.plugins[plugin_name] = plugin_instance
                    return plugin_instance
                    
            self.logger.error(f"O arquivo {plugin_path} não contém uma classe Plugin válida")
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar plugin {plugin_path}: {str(e)}")
            return None
            
    def load_all_plugins(self) -> int:
        """Carrega todos os plugins disponíveis"""
        plugin_files = self.discover_plugins()
        loaded_count = 0
        
        for plugin_file in plugin_files:
            plugin = self.load_plugin(plugin_file)
            if plugin and plugin.initialize():
                loaded_count += 1
                self.logger.info(f"Plugin carregado: {plugin.name} v{plugin.version}")
                
        return loaded_count
        
    def enable_plugin(self, plugin_name: str) -> bool:
        """Ativa um plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            return True
        return False
        
    def disable_plugin(self, plugin_name: str) -> bool:
        """Desativa um plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            return True
        return False
            
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Retorna um plugin pelo nome"""
        return self.plugins.get(plugin_name)
        
    def get_all_plugins(self) -> List[Dict[str, str]]:
        """Retorna informações sobre todos os plugins"""
        return [plugin.get_info() for plugin in self.plugins.values()]
        
    def save_plugin_configs(self):
        """Salva as configurações dos plugins"""
        config_path = os.path.join("config", "plugins.json")
        
        with open(config_path, "w", encoding="utf-8") as file:
            json.dump(self.plugin_configs, file, indent=4)
            
    def load_plugin_configs(self):
        """Carrega as configurações dos plugins"""
        config_path = os.path.join("config", "plugins.json")
        
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                self.plugin_configs = json.load(file)
        except FileNotFoundError:
            self.plugin_configs = {}
            self.save_plugin_configs() 