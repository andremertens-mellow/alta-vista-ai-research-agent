"""
Módulo para validação de dados antes do armazenamento.
"""
from typing import List, Dict, Any
from datetime import datetime
import re

class NewsValidator:
    """Validador de notícias antes do armazenamento."""
    
    @staticmethod
    def validate_item(item: Dict[str, Any]) -> List[str]:
        """
        Valida um item de notícia.
        
        Args:
            item: Dicionário contendo os dados da notícia
            
        Returns:
            Lista de erros encontrados. Lista vazia significa que o item é válido.
        """
        errors = []
        
        # Campos obrigatórios
        required_fields = ['title', 'link', 'source']
        for field in required_fields:
            if field not in item:
                errors.append(f"Campo obrigatório '{field}' não encontrado")
                
        # Validação do título
        if 'title' in item:
            if not isinstance(item['title'], str):
                errors.append("Campo 'title' deve ser uma string")
            elif len(item['title'].strip()) == 0:
                errors.append("Campo 'title' não pode estar vazio")
                
        # Validação do link
        if 'link' in item:
            if not isinstance(item['link'], str):
                errors.append("Campo 'link' deve ser uma string")
            elif not re.match(r'^https?://', item['link']):
                errors.append("Campo 'link' deve ser uma URL válida começando com http:// ou https://")
                
        # Validação da fonte
        if 'source' in item:
            if not isinstance(item['source'], str):
                errors.append("Campo 'source' deve ser uma string")
            elif len(item['source'].strip()) == 0:
                errors.append("Campo 'source' não pode estar vazio")
                
        # Validação da data de publicação
        if 'published' in item and item['published']:
            try:
                # Tenta converter para datetime
                if isinstance(item['published'], str):
                    datetime.fromisoformat(item['published'].replace('Z', '+00:00'))
            except ValueError:
                errors.append("Campo 'published' deve ser uma data ISO válida")
                
        # Validação da relevância
        if 'relevance' in item:
            if not isinstance(item['relevance'], (int, float)):
                errors.append("Campo 'relevance' deve ser um número")
            elif not 0 <= item['relevance'] <= 5:
                errors.append("Campo 'relevance' deve estar entre 0 e 5")
                
        # Validação das categorias
        if 'categories' in item:
            if not isinstance(item['categories'], dict):
                errors.append("Campo 'categories' deve ser um dicionário")
                
        # Validação do resumo
        if 'summary' in item:
            if not isinstance(item['summary'], str):
                errors.append("Campo 'summary' deve ser uma string")
            elif len(item['summary'].strip()) == 0:
                errors.append("Campo 'summary' não pode estar vazio")
                
        return errors
    
    @staticmethod
    def validate_items(items: List[Dict[str, Any]]) -> Dict[int, List[str]]:
        """
        Valida uma lista de itens de notícias.
        
        Args:
            items: Lista de dicionários contendo os dados das notícias
            
        Returns:
            Dicionário com índices dos itens com erro e suas respectivas mensagens
        """
        errors = {}
        
        for i, item in enumerate(items):
            item_errors = NewsValidator.validate_item(item)
            if item_errors:
                errors[i] = item_errors
                
        return errors
    
    @staticmethod
    def clean_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Limpa e normaliza os dados de um item.
        
        Args:
            item: Dicionário contendo os dados da notícia
            
        Returns:
            Dicionário com dados limpos e normalizados
        """
        cleaned = item.copy()
        
        # Remove espaços extras do título
        if 'title' in cleaned:
            cleaned['title'] = cleaned['title'].strip()
            
        # Remove espaços extras da fonte
        if 'source' in cleaned:
            cleaned['source'] = cleaned['source'].strip()
            
        # Normaliza a data de publicação
        if 'published' in cleaned and cleaned['published']:
            try:
                dt = datetime.fromisoformat(cleaned['published'].replace('Z', '+00:00'))
                cleaned['published'] = dt.isoformat()
            except ValueError:
                pass
            
        # Garante que relevância está entre 0 e 5
        if 'relevance' in cleaned:
            cleaned['relevance'] = max(0, min(5, float(cleaned['relevance'])))
            
        # Garante que categorias é um dicionário
        if 'categories' not in cleaned:
            cleaned['categories'] = {}
            
        # Remove espaços extras do resumo
        if 'summary' in cleaned:
            cleaned['summary'] = cleaned['summary'].strip()
            
        return cleaned 