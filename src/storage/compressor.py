"""
Módulo para compressão de dados armazenados.
"""
import json
import gzip
import lzma
from pathlib import Path
from typing import List, Dict, Any, Union

class NewsCompressor:
    """Compressor de dados de notícias."""
    
    @staticmethod
    def compress_json(data: Union[List, Dict], output_path: str, method: str = 'gzip') -> None:
        """
        Comprime dados JSON usando o método especificado.
        
        Args:
            data: Dados a serem comprimidos (lista ou dicionário)
            output_path: Caminho do arquivo de saída
            method: Método de compressão ('gzip' ou 'lzma')
        """
        # Converte dados para JSON
        json_str = json.dumps(data, ensure_ascii=False)
        
        # Comprime usando o método especificado
        if method == 'gzip':
            with gzip.open(output_path, 'wt', encoding='utf-8') as f:
                f.write(json_str)
        elif method == 'lzma':
            with lzma.open(output_path, 'wt', encoding='utf-8') as f:
                f.write(json_str)
        else:
            raise ValueError(f"Método de compressão '{method}' não suportado")
    
    @staticmethod
    def decompress_json(input_path: str, method: str = None) -> Union[List, Dict]:
        """
        Descomprime dados JSON usando o método especificado.
        Se method=None, tenta detectar automaticamente o método.
        
        Args:
            input_path: Caminho do arquivo comprimido
            method: Método de compressão ('gzip', 'lzma' ou None)
            
        Returns:
            Dados descomprimidos
        """
        # Se método não especificado, tenta detectar pela extensão
        if method is None:
            ext = Path(input_path).suffix.lower()
            if ext == '.gz':
                method = 'gzip'
            elif ext in ('.xz', '.lzma'):
                method = 'lzma'
            else:
                raise ValueError(f"Não foi possível detectar método de compressão para extensão '{ext}'")
        
        # Descomprime usando o método apropriado
        try:
            if method == 'gzip':
                with gzip.open(input_path, 'rt', encoding='utf-8') as f:
                    return json.loads(f.read())
            elif method == 'lzma':
                with lzma.open(input_path, 'rt', encoding='utf-8') as f:
                    return json.loads(f.read())
            else:
                raise ValueError(f"Método de compressão '{method}' não suportado")
        except Exception as e:
            raise ValueError(f"Erro ao descomprimir arquivo: {e}")
    
    @staticmethod
    def compress_file(input_path: str, output_path: str = None, method: str = 'gzip') -> str:
        """
        Comprime um arquivo JSON existente.
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_path: Caminho do arquivo de saída (opcional)
            method: Método de compressão ('gzip' ou 'lzma')
            
        Returns:
            Caminho do arquivo comprimido
        """
        # Se output_path não especificado, usa input_path com extensão apropriada
        if output_path is None:
            ext = '.gz' if method == 'gzip' else '.xz'
            output_path = str(Path(input_path).with_suffix(ext))
        
        # Lê dados do arquivo original
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Comprime para novo arquivo
        NewsCompressor.compress_json(data, output_path, method)
        
        return output_path
    
    @staticmethod
    def get_compression_ratio(original_path: str, compressed_path: str) -> float:
        """
        Calcula a taxa de compressão entre dois arquivos.
        
        Args:
            original_path: Caminho do arquivo original
            compressed_path: Caminho do arquivo comprimido
            
        Returns:
            Taxa de compressão (tamanho_comprimido / tamanho_original)
        """
        original_size = Path(original_path).stat().st_size
        compressed_size = Path(compressed_path).stat().st_size
        
        return compressed_size / original_size 