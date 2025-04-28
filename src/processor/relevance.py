from typing import Dict, Any
import openai
from datetime import datetime, timezone

def process_item(item: Dict[str, Any]) -> float:
    """
    Processa um item de notícia e retorna uma pontuação de relevância.
    
    Args:
        item: Dicionário contendo informações da notícia (título, descrição, etc.)
    
    Returns:
        float: Pontuação de relevância entre 0 e 5
    """
    # Combina título e descrição para análise
    content = f"{item.get('title', '')} {item.get('description', '')}"
    
    # Critérios de relevância
    relevance_score = 3.0  # Pontuação base
    
    # Verifica a data de publicação (notícias mais recentes são mais relevantes)
    pub_date = item.get('published')
    if pub_date:
        try:
            pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            days_old = (now - pub_date).days
            
            if days_old <= 1:
                relevance_score += 1.0
            elif days_old <= 3:
                relevance_score += 0.5
            elif days_old >= 7:
                relevance_score -= 1.0
        except (ValueError, TypeError):
            pass
    
    # Palavras-chave que aumentam a relevância
    keywords = [
        'mercado', 'investimento', 'economia', 'bolsa',
        'ações', 'dólar', 'ibovespa', 'análise',
        'tendência', 'oportunidade', 'risco'
    ]
    
    content_lower = content.lower()
    keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
    relevance_score += min(keyword_matches * 0.2, 1.0)
    
    # Garante que a pontuação está entre 0 e 5
    return max(0.0, min(5.0, relevance_score)) 