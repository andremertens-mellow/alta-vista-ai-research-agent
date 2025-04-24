import hashlib
from typing import List, Dict

def remove_dupes(items: List[Dict]) -> List[Dict]:
    """
    Remove itens duplicados de uma lista de dicionários usando um hash SHA256 como identificador único.
    O hash é gerado a partir da concatenação do título (em minúsculas) e fonte do item.
    
    Args:
        items (List[Dict]): Lista de dicionários contendo pelo menos as chaves 'title' e 'source'
        
    Returns:
        List[Dict]: Lista sem duplicatas, mantendo a ordem original dos itens
        
    Example:
        >>> items = [
        ...     {"title": "Notícia 1", "source": "site1"},
        ...     {"title": "Notícia 1", "source": "site1"},
        ...     {"title": "Notícia 2", "source": "site2"}
        ... ]
        >>> remove_dupes(items)
        [{"title": "Notícia 1", "source": "site1"}, {"title": "Notícia 2", "source": "site2"}]
    """
    seen = set()
    result = []
    
    for item in items:
        # Gera o identificador único usando title + source
        content = (item['title'].lower() + item['source']).encode('utf-8')
        uid = hashlib.sha256(content).hexdigest()
        
        # Adiciona o item apenas se ainda não foi visto
        if uid not in seen:
            seen.add(uid)
            result.append(item)
            
    return result 