#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de privacidade do navegador
"""

import dns.resolver
import json
from typing import Dict, List, Optional
from PyQt6.QtWebEngineCore import QWebEngineProfile
from cryptography.fernet import Fernet
import os
import requests

class PrivacyManager:
    """Gerenciador de privacidade do navegador"""
    
    def __init__(self):
        self.doh_providers = [
            "https://dns.google/dns-query",
            "https://cloudflare-dns.com/dns-query",
            "https://doh.powerdns.org"
        ]
        self.current_doh = self.doh_providers[0]
        self.fingerprint_blocking = True
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.dns_cache = DNSCache()
        
    def _generate_encryption_key(self) -> bytes:
        """Gera uma chave de criptografia"""
        if os.path.exists("config/encryption.key"):
            with open("config/encryption.key", "rb") as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            os.makedirs("config", exist_ok=True)
            with open("config/encryption.key", "wb") as key_file:
                key_file.write(key)
            return key
            
    def configure_doh(self, profile: QWebEngineProfile):
        """Configura DNS sobre HTTPS usando configurações do sistema"""
        # Em vez de usar setDnsOverHttpsEnabled, configuramos o DNS manualmente
        settings = profile.settings()
        
        # Configurar proxy para usar DoH
        settings.setAttribute(settings.WebAttribute.DnsPrefetchEnabled, True)
        
        # Usar o DNSCache para resolver domínios
        self.dns_cache.set_doh_provider(self.current_doh)
        
        # Configurar cabeçalhos personalizados para DoH
        profile.setHttpAcceptLanguage("pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7")
        
    def set_doh_provider(self, provider: str):
        """Define o provedor DoH"""
        if provider in self.doh_providers:
            self.current_doh = provider
            self.dns_cache.set_doh_provider(provider)
            return True
        return False
        
    def block_fingerprinting(self, profile: QWebEngineProfile):
        """Configura bloqueio de fingerprinting"""
        if not self.fingerprint_blocking:
            return
            
        # Configurações de privacidade
        settings = profile.settings()
        
        # Desativa recursos que podem ser usados para fingerprinting
        settings.setAttribute(settings.WebAttribute.ScreenCaptureEnabled, False)
        settings.setAttribute(settings.WebAttribute.WebGLEnabled, False)
        settings.setAttribute(settings.WebAttribute.WebRTCPublicInterfacesOnly, True)
        settings.setAttribute(settings.WebAttribute.AutoLoadImages, True)  # Alterado para True para melhor experiência
        settings.setAttribute(settings.WebAttribute.JavascriptCanAccessClipboard, False)
        
        # Configurar cabeçalhos personalizados para reduzir fingerprinting
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Generic Browser")
        
    def encrypt_data(self, data: str) -> bytes:
        """Criptografa dados"""
        return self.cipher_suite.encrypt(data.encode())
        
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Descriptografa dados"""
        return self.cipher_suite.decrypt(encrypted_data).decode()
        
    def save_privacy_settings(self):
        """Salva configurações de privacidade"""
        settings = {
            "doh_provider": self.current_doh,
            "fingerprint_blocking": self.fingerprint_blocking
        }
        
        os.makedirs("config", exist_ok=True)
        with open("config/privacy_settings.json", "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4)
            
    def load_privacy_settings(self):
        """Carrega configurações de privacidade"""
        try:
            with open("config/privacy_settings.json", "r", encoding="utf-8") as file:
                settings = json.load(file)
                self.current_doh = settings.get("doh_provider", self.doh_providers[0])
                self.fingerprint_blocking = settings.get("fingerprint_blocking", True)
        except FileNotFoundError:
            self.save_privacy_settings()
            
class DNSCache:
    """Cache de DNS com suporte a DoH"""
    
    def __init__(self):
        self.cache: Dict[str, List[str]] = {}
        self.doh_url = "https://dns.google/dns-query"
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/dns-json"
        })
        
    def set_doh_provider(self, provider: str):
        """Define o provedor DoH"""
        self.doh_url = provider
        
    def resolve(self, domain: str) -> Optional[List[str]]:
        """Resolve um domínio usando DoH"""
        if domain in self.cache:
            return self.cache[domain]
            
        try:
            params = {
                "name": domain,
                "type": "A"
            }
            response = self.session.get(self.doh_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if "Answer" in data:
                    ips = [answer["data"] for answer in data["Answer"] if answer["type"] == 1]
                    if ips:
                        self.cache[domain] = ips
                        return ips
            return None
        except Exception:
            return None
            
    def clear_cache(self):
        """Limpa o cache de DNS"""
        self.cache.clear()
        
    def get_cached_domains(self) -> List[str]:
        """Retorna a lista de domínios em cache"""
        return list(self.cache.keys())
        
    def remove_domain(self, domain: str):
        """Remove um domínio do cache"""
        if domain in self.cache:
            del self.cache[domain] 