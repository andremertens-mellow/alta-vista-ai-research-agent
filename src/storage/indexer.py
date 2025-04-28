"""
Módulo para indexação de notícias armazenadas.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import sqlite3

class NewsIndex:
    def __init__(self, db_path: str = "data/news_index.db"):
        """
        Inicializa o indexador de notícias.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados SQLite
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Inicializa o banco de dados com as tabelas necessárias."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cria tabela principal de notícias
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            published TIMESTAMP,
            relevance FLOAT,
            file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Cria tabela de categorias
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id INTEGER,
            category TEXT NOT NULL,
            FOREIGN KEY (news_id) REFERENCES news(id)
        )
        """)
        
        # Cria índices para melhorar performance de busca
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_title ON news(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_source ON news(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_published ON news(published)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_relevance ON news(relevance)")
        
        conn.commit()
        conn.close()
    
    def index_file(self, file_path: str) -> None:
        """
        Indexa um arquivo de notícias.
        
        Args:
            file_path: Caminho para o arquivo JSON com as notícias
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                items = json.load(f)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in items:
                # Insere notícia
                cursor.execute("""
                INSERT INTO news (title, source, published, relevance, file_path)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    item['title'],
                    item['source'],
                    item.get('published'),
                    item.get('relevance', 0.0),
                    file_path
                ))
                
                news_id = cursor.lastrowid
                
                # Insere categorias
                for category in item.get('categories', {}).keys():
                    cursor.execute("""
                    INSERT INTO categories (news_id, category)
                    VALUES (?, ?)
                    """, (news_id, category))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Erro ao indexar arquivo {file_path}: {e}")
    
    def search(self, 
              query: Optional[str] = None,
              source: Optional[str] = None,
              category: Optional[str] = None,
              min_relevance: Optional[float] = None,
              start_date: Optional[datetime] = None,
              end_date: Optional[datetime] = None,
              limit: int = 100) -> List[Dict[str, Any]]:
        """
        Busca notícias no índice.
        
        Args:
            query: Texto para buscar no título
            source: Fonte específica para filtrar
            category: Categoria específica para filtrar
            min_relevance: Relevância mínima
            start_date: Data inicial
            end_date: Data final
            limit: Limite de resultados
            
        Returns:
            Lista de notícias encontradas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT DISTINCT n.* FROM news n"
        params = []
        where_clauses = []
        
        if category:
            sql += " LEFT JOIN categories c ON n.id = c.news_id"
            where_clauses.append("c.category = ?")
            params.append(category)
        
        if query:
            where_clauses.append("n.title LIKE ?")
            params.append(f"%{query}%")
            
        if source:
            where_clauses.append("n.source = ?")
            params.append(source)
            
        if min_relevance is not None:
            where_clauses.append("n.relevance >= ?")
            params.append(min_relevance)
            
        if start_date:
            where_clauses.append("n.published >= ?")
            params.append(start_date.isoformat())
            
        if end_date:
            where_clauses.append("n.published <= ?")
            params.append(end_date.isoformat())
        
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
            
        sql += " ORDER BY n.published DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        results = []
        
        for row in cursor.fetchall():
            with open(row[5], 'r', encoding='utf-8') as f:
                items = json.load(f)
                for item in items:
                    if item['title'] == row[1]:
                        results.append(item)
                        break
        
        conn.close()
        return results 