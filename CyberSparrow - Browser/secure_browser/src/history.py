#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
import os

class HistoryManager:
    def __init__(self, db_path="history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa o banco de dados do histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Criar tabela de histórico se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visit_count INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_visit(self, url, title=None):
        """Adiciona uma nova visita ao histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se a URL já existe
        cursor.execute('SELECT id, visit_count FROM history WHERE url = ?', (url,))
        result = cursor.fetchone()
        
        if result:
            # Atualizar contagem de visitas e timestamp
            cursor.execute('''
                UPDATE history 
                SET visit_count = ?, visit_time = ?, title = ?
                WHERE id = ?
            ''', (result[1] + 1, datetime.now(), title, result[0]))
        else:
            # Inserir nova entrada
            cursor.execute('''
                INSERT INTO history (url, title, visit_time)
                VALUES (?, ?, ?)
            ''', (url, title, datetime.now()))
        
        conn.commit()
        conn.close()

    def get_history(self, limit=100):
        """Retorna o histórico de navegação"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, title, visit_time, visit_count 
            FROM history 
            ORDER BY visit_time DESC 
            LIMIT ?
        ''', (limit,))
        
        history = cursor.fetchall()
        conn.close()
        return history

    def search_history(self, query):
        """Pesquisa no histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, title, visit_time, visit_count 
            FROM history 
            WHERE url LIKE ? OR title LIKE ?
            ORDER BY visit_time DESC
        ''', (f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        conn.close()
        return results

    def clear_history(self):
        """Limpa todo o histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history')
        conn.commit()
        conn.close()

    def delete_entry(self, url):
        """Deleta uma entrada específica do histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history WHERE url = ?', (url,))
        conn.commit()
        conn.close() 