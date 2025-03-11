#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de análise de tráfego
"""

import time
import socket
import struct
from typing import Dict, List, Optional
import threading
import queue
import psutil
import requests
from urllib.parse import urlparse

class PacketInspector:
    """Inspetor de pacotes"""
    
    def __init__(self):
        self.packets: List[Dict] = []
        
    def inspect_connection(self, connection) -> Optional[Dict]:
        """Inspeciona uma conexão"""
        try:
            packet_info = {
                'timestamp': time.time(),
                'src': connection.laddr.ip,
                'dst': connection.raddr.ip if connection.raddr else 'N/A',
                'sport': connection.laddr.port,
                'dport': connection.raddr.port if connection.raddr else 0,
                'type': connection.type,
                'status': connection.status,
                'size': 0  # Não é possível obter o tamanho real do pacote
            }
            
            self.packets.append(packet_info)
            return packet_info
        except Exception:
            return None

class TrafficAnalyzer:
    """Analisador de tráfego"""
    
    def __init__(self):
        self.packet_inspector = PacketInspector()
        self.is_capturing = False
        self.packet_queue = queue.Queue()
        self.capture_thread = None
        self.callback = None
        self.previous_connections = set()
        
    def get_connection_hash(self, conn):
        """Gera um hash único para uma conexão"""
        raddr = conn.raddr if conn.raddr else ('0.0.0.0', 0)
        return f"{conn.laddr.ip}:{conn.laddr.port}-{raddr[0]}:{raddr[1]}-{conn.type}-{conn.status}"
        
    def capture_connections(self):
        """Captura conexões ativas"""
        while self.is_capturing:
            try:
                # Obtém todas as conexões ativas
                connections = psutil.net_connections(kind='inet')
                current_connections = set()
                
                for conn in connections:
                    conn_hash = self.get_connection_hash(conn)
                    current_connections.add(conn_hash)
                    
                    # Se é uma nova conexão
                    if conn_hash not in self.previous_connections:
                        packet_info = self.packet_inspector.inspect_connection(conn)
                        if packet_info and self.callback:
                            self.packet_queue.put(packet_info)
                
                self.previous_connections = current_connections
                time.sleep(1)  # Atualiza a cada segundo
                
            except Exception as e:
                print(f"Erro ao capturar conexões: {e}")
                time.sleep(1)
                
    def process_queue(self):
        """Processa a fila de pacotes"""
        while self.is_capturing:
            try:
                while not self.packet_queue.empty():
                    packet_info = self.packet_queue.get_nowait()
                    if self.callback:
                        self.callback(packet_info)
            except queue.Empty:
                time.sleep(0.1)
                
    def start_capture(self, callback=None):
        """Inicia a captura de conexões"""
        if not self.is_capturing:
            self.is_capturing = True
            self.callback = callback
            self.previous_connections = set()
            
            # Inicia thread de captura
            self.capture_thread = threading.Thread(target=self.capture_connections)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            # Inicia thread de processamento
            self.process_thread = threading.Thread(target=self.process_queue)
            self.process_thread.daemon = True
            self.process_thread.start()
            
    def stop_capture(self):
        """Para a captura de conexões"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=1.0)
            
    def get_interfaces(self) -> List[str]:
        """Retorna lista de interfaces de rede"""
        interfaces = []
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interfaces.append(f"{iface} ({addr.address})")
        return interfaces
        
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do tráfego"""
        stats = {
            'total_packets': len(self.packet_inspector.packets),
            'tcp_packets': sum(1 for p in self.packet_inspector.packets if p['type'] == 'tcp'),
            'udp_packets': sum(1 for p in self.packet_inspector.packets if p['type'] == 'udp'),
            'total_bytes': sum(p.get('size', 0) for p in self.packet_inspector.packets)
        }
        return stats 