"""
Testes para os componentes de armazenamento.
"""
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
import pytest

from src.storage.validator import NewsValidator
from src.storage.compressor import NewsCompressor
from src.storage.indexer import NewsIndex

# Dados de exemplo para testes
SAMPLE_ITEMS = [
    {
        "title": "Notícia 1",
        "link": "https://example.com/1",
        "source": "Site A",
        "published": "2025-04-24T18:49:50+00:00",
        "summary": "Resumo da notícia 1",
        "relevance": 3.4,
        "categories": {"economia": 0.8}
    },
    {
        "title": "Notícia 2",
        "link": "https://example.com/2",
        "source": "Site B",
        "published": "2025-04-24T18:30:00+00:00",
        "summary": "Resumo da notícia 2",
        "relevance": 2.8,
        "categories": {"política": 0.9}
    }
]

def test_validator_valid_item():
    """Testa validação de item válido."""
    validator = NewsValidator()
    errors = validator.validate_item(SAMPLE_ITEMS[0])
    assert len(errors) == 0

def test_validator_invalid_item():
    """Testa validação de item inválido."""
    validator = NewsValidator()
    invalid_item = {
        "title": "",  # título vazio
        "link": "not-a-url",  # URL inválida
        "source": 123,  # tipo inválido
        "relevance": 6.0  # valor fora do range
    }
    errors = validator.validate_item(invalid_item)
    assert len(errors) > 0
    assert any("title" in err for err in errors)
    assert any("link" in err for err in errors)
    assert any("source" in err for err in errors)
    assert any("relevance" in err for err in errors)

def test_validator_clean_item():
    """Testa limpeza e normalização de item."""
    validator = NewsValidator()
    item = {
        "title": "  Título com espaços  ",
        "source": " Fonte com espaços ",
        "relevance": 6.5,
        "published": "2025-04-24T18:49:50Z"
    }
    cleaned = validator.clean_item(item)
    assert cleaned["title"] == "Título com espaços"
    assert cleaned["source"] == "Fonte com espaços"
    assert cleaned["relevance"] == 5.0
    assert cleaned["published"] == "2025-04-24T18:49:50+00:00"

def test_compressor_compression():
    """Testa compressão e descompressão de dados."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Testa compressão gzip
        gz_path = os.path.join(tmpdir, "test.json.gz")
        NewsCompressor.compress_json(SAMPLE_ITEMS, gz_path, method='gzip')
        assert os.path.exists(gz_path)
        
        # Testa descompressão gzip
        decompressed = NewsCompressor.decompress_json(gz_path)
        assert decompressed == SAMPLE_ITEMS
        
        # Testa compressão lzma
        xz_path = os.path.join(tmpdir, "test.json.xz")
        NewsCompressor.compress_json(SAMPLE_ITEMS, xz_path, method='lzma')
        assert os.path.exists(xz_path)
        
        # Testa descompressão lzma
        decompressed = NewsCompressor.decompress_json(xz_path)
        assert decompressed == SAMPLE_ITEMS

def test_compressor_compression_ratio():
    """Testa cálculo da taxa de compressão."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Cria arquivo original
        orig_path = os.path.join(tmpdir, "test.json")
        with open(orig_path, 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_ITEMS, f)
        
        # Comprime arquivo
        comp_path = os.path.join(tmpdir, "test.json.gz")
        NewsCompressor.compress_file(orig_path, comp_path)
        
        # Calcula taxa de compressão
        ratio = NewsCompressor.get_compression_ratio(orig_path, comp_path)
        assert 0 < ratio < 1  # Arquivo comprimido deve ser menor

def test_indexer_operations():
    """Testa operações do indexador."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Cria arquivo de teste
        test_file = os.path.join(tmpdir, "test.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(SAMPLE_ITEMS, f)
        
        # Inicializa indexador com banco de dados temporário
        db_path = os.path.join(tmpdir, "test.db")
        indexer = NewsIndex(db_path)
        
        # Testa indexação
        indexer.index_file(test_file)
        
        # Testa busca por título
        results = indexer.search(query="Notícia")
        assert len(results) == 2
        
        # Testa busca por fonte
        results = indexer.search(source="Site A")
        assert len(results) == 1
        
        # Testa busca por relevância mínima
        results = indexer.search(min_relevance=3.0)
        assert len(results) == 1
        assert results[0]["relevance"] >= 3.0
        
        # Testa busca por data
        results = indexer.search(
            start_date=datetime(2025, 4, 24, 18, 0),
            end_date=datetime(2025, 4, 24, 19, 0)
        )
        assert len(results) == 2 