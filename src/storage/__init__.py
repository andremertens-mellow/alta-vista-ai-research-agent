"""
Pacote para armazenamento de dados do sistema de notícias.
"""
from .indexer import NewsIndex
from .validator import NewsValidator
from .compressor import NewsCompressor

__all__ = ['NewsIndex', 'NewsValidator', 'NewsCompressor'] 