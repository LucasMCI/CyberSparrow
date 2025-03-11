#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de integração com ferramentas de segurança
"""

import subprocess
import json
import os
import tempfile
from typing import Dict, List, Optional, Tuple
import nmap
import logging

class SecurityToolsManager:
    """Gerenciador de ferramentas de segurança"""
    
    def __init__(self):
        self.logger = logging.getLogger("SecurityTools")
        self.tools_config = self._load_tools_config()
        
    def _load_tools_config(self) -> Dict:
        """Carrega a configuração das ferramentas"""
        config_path = os.path.join("config", "security_tools.json")
        
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            default_config = {
                "wireshark": {
                    "path": "",
                    "enabled": True
                },
                "nmap": {
                    "path": "",
                    "enabled": True
                },
                "burp": {
                    "path": "",
                    "enabled": False
                }
            }
            
            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(default_config, file, indent=4)
                
            return default_config
            
    def save_tools_config(self):
        """Salva a configuração das ferramentas"""
        config_path = os.path.join("config", "security_tools.json")
        
        with open(config_path, "w", encoding="utf-8") as file:
            json.dump(self.tools_config, file, indent=4)
            
    def set_tool_path(self, tool_name: str, path: str) -> bool:
        """Define o caminho de uma ferramenta"""
        if tool_name in self.tools_config:
            self.tools_config[tool_name]["path"] = path
            self.save_tools_config()
            return True
        return False
        
    def enable_tool(self, tool_name: str, enabled: bool = True) -> bool:
        """Ativa ou desativa uma ferramenta"""
        if tool_name in self.tools_config:
            self.tools_config[tool_name]["enabled"] = enabled
            self.save_tools_config()
            return True
        return False
        
class NmapScanner:
    """Integração com Nmap para escaneamento de rede"""
    
    def __init__(self):
        self.scanner = nmap.PortScanner()
        self.last_scan_results = {}
        
    def scan_host(self, host: str, ports: str = "1-1000") -> Dict:
        """Escaneia um host específico"""
        try:
            self.last_scan_results = self.scanner.scan(host, ports)
            return self.last_scan_results
        except Exception as e:
            logging.error(f"Erro ao escanear host {host}: {str(e)}")
            return {}
            
    def get_open_ports(self, host: str) -> List[int]:
        """Retorna as portas abertas de um host"""
        if host in self.scanner.all_hosts():
            open_ports = []
            for proto in self.scanner[host].all_protocols():
                ports = sorted(self.scanner[host][proto].keys())
                for port in ports:
                    if self.scanner[host][proto][port]["state"] == "open":
                        open_ports.append(port)
            return open_ports
        return []
        
    def save_scan_results(self, filename: str) -> bool:
        """Salva os resultados do escaneamento em um arquivo"""
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(self.last_scan_results, file, indent=4)
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar resultados: {str(e)}")
            return False
            
class WiresharkIntegration:
    """Integração com Wireshark para análise de pacotes"""
    
    def __init__(self, wireshark_path: str = ""):
        self.wireshark_path = wireshark_path or "wireshark"
        
    def capture_to_file(self, interface: str, output_file: str, 
                        filter_str: str = "", duration: int = 30) -> bool:
        """Captura pacotes para um arquivo pcap"""
        try:
            cmd = [
                self.wireshark_path, 
                "-i", interface, 
                "-w", output_file,
                "-a", f"duration:{duration}"
            ]
            
            if filter_str:
                cmd.extend(["-f", filter_str])
                
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            logging.error(f"Erro ao capturar pacotes: {str(e)}")
            return False
            
    def open_capture_file(self, file_path: str) -> bool:
        """Abre um arquivo de captura no Wireshark"""
        try:
            subprocess.Popen([self.wireshark_path, "-r", file_path])
            return True
        except Exception as e:
            logging.error(f"Erro ao abrir arquivo de captura: {str(e)}")
            return False
            
class SandboxManager:
    """Gerenciador de sandbox para carregamento seguro de páginas"""
    
    def __init__(self):
        self.sandbox_enabled = True
        self.isolation_level = "high"  # low, medium, high
        
    def configure_sandbox(self, profile):
        """Configura o sandbox para um perfil de navegador"""
        if not self.sandbox_enabled:
            return
            
        # Configurações de sandbox
        profile.settings().setAttribute(profile.settings().WebAttribute.JavascriptEnabled, 
                                       self.isolation_level != "high")
        profile.settings().setAttribute(profile.settings().WebAttribute.PluginsEnabled, False)
        profile.settings().setAttribute(profile.settings().WebAttribute.AutoLoadImages, 
                                       self.isolation_level == "low")
        
    def set_isolation_level(self, level: str):
        """Define o nível de isolamento do sandbox"""
        if level in ["low", "medium", "high"]:
            self.isolation_level = level
            return True
        return False