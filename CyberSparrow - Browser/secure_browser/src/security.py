#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de segurança do navegador
"""

import re
from urllib.parse import urlparse
from typing import List, Set, Dict
import json
import yaml
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class SecurityInterceptor(QWebEngineUrlRequestInterceptor):
    """Interceptador de requisições para implementar medidas de segurança"""
    
    def __init__(self):
        super().__init__()
        self.blocked_domains: Set[str] = set()
        self.malicious_patterns: List[str] = []
        self.load_security_rules()
        
    def load_security_rules(self):
        """Carrega regras de segurança do arquivo de configuração"""
        try:
            with open("config/security_rules.yaml", "r", encoding="utf-8") as file:
                rules = yaml.safe_load(file)
                self.blocked_domains = set(rules.get("blocked_domains", []))
                self.malicious_patterns = rules.get("malicious_patterns", [])
        except FileNotFoundError:
            self.create_default_rules()
            
    def create_default_rules(self):
        """Cria regras padrão de segurança"""
        default_rules = {
            "blocked_domains": [
                "malware.com",
                "adtracker.net",
                "malicious-ads.com"
            ],
            "malicious_patterns": [
                r"<script>.*?alert\(.*?\).*?</script>",
                r"union\s+select",
                r"eval\s*\(",
                r"document\.cookie",
                r"<iframe.*?src=",
            ]
        }
        
        with open("config/security_rules.yaml", "w", encoding="utf-8") as file:
            yaml.dump(default_rules, file)
            
        self.blocked_domains = set(default_rules["blocked_domains"])
        self.malicious_patterns = default_rules["malicious_patterns"]
        
    def interceptRequest(self, info):
        """Intercepta e analisa requisições"""
        url = info.requestUrl().toString()
        domain = urlparse(url).netloc
        
        # Verifica domínios bloqueados
        if domain in self.blocked_domains:
            info.block(True)
            return
            
        # Verifica padrões maliciosos na URL
        for pattern in self.malicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                info.block(True)
                return
                
class FirewallManager:
    """Gerenciador do firewall interno"""
    
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.suspicious_ips: Dict[str, int] = {}
        self.load_blocked_ips()
        
    def load_blocked_ips(self):
        """Carrega IPs bloqueados do arquivo de configuração"""
        try:
            with open("config/blocked_ips.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                self.blocked_ips = set(data.get("blocked_ips", []))
        except FileNotFoundError:
            self.create_default_blocked_ips()
            
    def create_default_blocked_ips(self):
        """Cria lista padrão de IPs bloqueados"""
        default_ips = {
            "blocked_ips": [
                "192.168.1.100",
                "10.0.0.50"
            ]
        }
        
        with open("config/blocked_ips.json", "w", encoding="utf-8") as file:
            json.dump(default_ips, file, indent=4)
            
        self.blocked_ips = set(default_ips["blocked_ips"])
        
    def is_ip_blocked(self, ip: str) -> bool:
        """Verifica se um IP está bloqueado"""
        return ip in self.blocked_ips
        
    def block_ip(self, ip: str):
        """Bloqueia um IP"""
        self.blocked_ips.add(ip)
        self.save_blocked_ips()
        
    def save_blocked_ips(self):
        """Salva a lista de IPs bloqueados"""
        data = {"blocked_ips": list(self.blocked_ips)}
        with open("config/blocked_ips.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4) 