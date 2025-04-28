# src/storage.py
"""
Módulo para persistência dos dados coletados e processados.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from src.storage.validator import NewsValidator
from src.storage.compressor import NewsCompressor
from src.storage.indexer import NewsIndex

def ensure_data_dirs():
    """Ensure data directories exist."""
    data_dir = Path(__file__).parent.parent / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    compressed_dir = data_dir / "compressed"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    compressed_dir.mkdir(parents=True, exist_ok=True)
    
    return raw_dir, processed_dir, compressed_dir

def save_raw_data(items: List[Dict[str, Any]], timestamp: str) -> str:
    """
    Save raw data to a JSON file.
    
    Args:
        items: List of items to save
        timestamp: Timestamp string for the filename
        
    Returns:
        str: Path to the saved file
    """
    raw_dir, _, _ = ensure_data_dirs()
    filepath = raw_dir / f"{timestamp}.json"
    
    # Valida os dados antes de salvar
    validator = NewsValidator()
    errors = validator.validate_items(items)
    if errors:
        raise ValueError(f"Erros de validação encontrados: {errors}")
    
    # Limpa e normaliza os dados
    cleaned_items = [validator.clean_item(item) for item in items]
    
    # Salva os dados
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cleaned_items, f, ensure_ascii=False, indent=2)
    
    return str(filepath.absolute())

def save_processed_data(items: List[Dict[str, Any]], timestamp: str) -> str:
    """
    Save processed data to a JSON file.
    
    Args:
        items: List of items to save
        timestamp: Timestamp string for the filename
        
    Returns:
        str: Path to the saved file
    """
    _, processed_dir, _ = ensure_data_dirs()
    filepath = processed_dir / f"{timestamp}.json"
    
    # Valida os dados antes de salvar
    validator = NewsValidator()
    errors = validator.validate_items(items)
    if errors:
        raise ValueError(f"Erros de validação encontrados: {errors}")
    
    # Limpa e normaliza os dados
    cleaned_items = [validator.clean_item(item) for item in items]
    
    # Salva os dados
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cleaned_items, f, ensure_ascii=False, indent=2)
    
    return str(filepath.absolute())

def save(items: List[Dict], raw: bool = False) -> None:
    """
    Salva os itens em um arquivo JSON com timestamp.
    
    Args:
        items: Lista de itens a serem salvos
        raw: Se True, salva na pasta raw/, senão na pasta processed/
        
    Example:
        >>> items = [{"title": "Notícia 1", "source": "Site A"}]
        >>> save(items, raw=True)  # Salva em data/raw/2024-03-21T14-30-00.json
        >>> save(items)  # Salva em data/processed/2024-03-21T14-30-00.json
    """
    # Gera timestamp
    timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    
    # Salva os dados
    if raw:
        filepath = save_raw_data(items, timestamp)
    else:
        filepath = save_processed_data(items, timestamp)
    
    # Comprime os dados
    _, _, compressed_dir = ensure_data_dirs()
    compressed_path = compressed_dir / f"{timestamp}.json.gz"
    NewsCompressor.compress_file(filepath, str(compressed_path))
    
    # Indexa os dados
    indexer = NewsIndex()
    indexer.index_file(filepath)
    
    print(f"✓ {len(items)} itens salvos em {filepath}")
    print(f"✓ Dados comprimidos em {compressed_path}")
    
    # Mostra taxa de compressão
    ratio = NewsCompressor.get_compression_ratio(filepath, str(compressed_path))
    print(f"✓ Taxa de compressão: {ratio:.2%}")

def search_news(
    query: str = None,
    source: str = None,
    category: str = None,
    min_relevance: float = None,
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
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
    indexer = NewsIndex()
    return indexer.search(
        query=query,
        source=source,
        category=category,
        min_relevance=min_relevance,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )