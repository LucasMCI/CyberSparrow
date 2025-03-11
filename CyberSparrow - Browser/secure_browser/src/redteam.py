#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import socket
import whois
import dns.resolver
import subprocess
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

class RedTeamTools:
    def __init__(self):
        self.has_nmap = False
        try:
            import nmap
            self.nmap_scanner = nmap.PortScanner()
            self.has_nmap = True
        except (ImportError, Exception):
            pass
        
    def scan_ports(self, target, ports="1-1000"):
        """Realiza um scan de portas no alvo"""
        if self.has_nmap:
            try:
                result = self.nmap_scanner.scan(target, ports)
                return result
            except Exception as e:
                return {"error": str(e)}
        else:
            # Método alternativo usando sockets
            results = {}
            try:
                ip = socket.gethostbyname(target)
                port_list = []
                
                # Converte a string de portas em uma lista
                if "-" in ports:
                    start, end = map(int, ports.split("-"))
                    port_list = range(start, end + 1)
                else:
                    port_list = [int(p.strip()) for p in ports.split(",")]
                
                open_ports = []
                for port in port_list:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((ip, port))
                    if result == 0:
                        try:
                            service = socket.getservbyport(port)
                        except:
                            service = "unknown"
                        open_ports.append({
                            "port": port,
                            "state": "open",
                            "service": service
                        })
                    sock.close()
                
                results = {
                    "scan": {
                        ip: {
                            "ports": open_ports
                        }
                    }
                }
                return results
            except Exception as e:
                return {"error": str(e)}
            
    def get_whois(self, domain):
        """Obtém informações WHOIS do domínio"""
        try:
            info = whois.whois(domain)
            return info
        except Exception as e:
            return {"error": str(e)}
            
    def dns_enumeration(self, domain):
        """Realiza enumeração DNS"""
        results = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']
        
        try:
            for record in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record)
                    results[record] = [str(rdata) for rdata in answers]
                except:
                    results[record] = []
            return results
        except Exception as e:
            return {"error": str(e)}
            
    def find_subdomains(self, domain):
        """Procura subdomínios usando wordlist comum"""
        common_subdomains = ['www', 'mail', 'ftp', 'admin', 'blog', 'dev', 
                           'test', 'staging', 'api', 'portal', 'vpn']
        found = []
        
        for sub in common_subdomains:
            try:
                subdomain = f"{sub}.{domain}"
                ip = socket.gethostbyname(subdomain)
                found.append({"subdomain": subdomain, "ip": ip})
            except:
                continue
                
        return found
        
    def crawl_site(self, url, max_pages=10):
        """Realiza crawling básico do site"""
        visited = set()
        to_visit = {url}
        found_urls = []
        
        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop()
            if current_url in visited:
                continue
                
            try:
                response = requests.get(current_url, timeout=5)
                visited.add(current_url)
                
                soup = BeautifulSoup(response.text, 'html.parser')
                base_url = urlparse(current_url).scheme + "://" + urlparse(current_url).netloc
                
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if urlparse(full_url).netloc == urlparse(base_url).netloc:
                            to_visit.add(full_url)
                            found_urls.append(full_url)
                            
            except Exception as e:
                continue
                
        return list(set(found_urls))
        
    def check_waf(self, url):
        """Verifica se o site usa WAF e tenta identificá-lo"""
        try:
            response = requests.get(url)
            headers = response.headers
            
            wafs = {
                'cloudflare': ['cf-ray', 'cloudflare'],
                'akamai': ['akamai'],
                'imperva': ['incap_ses', 'visid_incap'],
                'f5': ['big-ip', 'f5'],
                'sucuri': ['sucuri'],
                'aws': ['x-amz', 'aws']
            }
            
            detected = []
            for waf, signatures in wafs.items():
                for header in headers:
                    if any(sig in header.lower() for sig in signatures):
                        detected.append(waf)
                        
            return list(set(detected))
        except Exception as e:
            return {"error": str(e)}
            
    def ssl_info(self, domain):
        """Obtém informações do certificado SSL"""
        try:
            cmd = f"echo | openssl s_client -connect {domain}:443 2>/dev/null | openssl x509 -noout -text"
            result = subprocess.check_output(cmd, shell=True).decode()
            return result
        except Exception as e:
            return {"error": str(e)}
            
    def check_headers(self, url):
        """Analisa cabeçalhos de segurança"""
        try:
            response = requests.get(url)
            security_headers = {
                'Strict-Transport-Security': response.headers.get('Strict-Transport-Security'),
                'Content-Security-Policy': response.headers.get('Content-Security-Policy'),
                'X-Frame-Options': response.headers.get('X-Frame-Options'),
                'X-XSS-Protection': response.headers.get('X-XSS-Protection'),
                'X-Content-Type-Options': response.headers.get('X-Content-Type-Options')
            }
            return security_headers
        except Exception as e:
            return {"error": str(e)}
            
    def check_cors(self, url):
        """Verifica configuração CORS"""
        try:
            headers = {
                'Origin': 'https://evil.com'
            }
            response = requests.get(url, headers=headers)
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
                'Access-Control-Expose-Headers': response.headers.get('Access-Control-Expose-Headers'),
                'Access-Control-Max-Age': response.headers.get('Access-Control-Max-Age'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            return cors_headers
        except Exception as e:
            return {"error": str(e)} 