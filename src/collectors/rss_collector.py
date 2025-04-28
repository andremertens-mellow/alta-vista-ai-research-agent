"""
Módulo responsável por coletar dados de feeds RSS definidos no arquivo de configuração.
"""
from typing import Dict, List, Optional
import asyncio
import yaml
import aiohttp
import feedparser
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

def clean_html(text: str) -> str:
    """Remove tags HTML e formata o texto."""
    # Remove tags HTML
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    
    # Remove espaços extras e quebras de linha
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_content(entry) -> str:
    """
    Extrai o melhor conteúdo disponível de uma entrada do feed.
    Tenta diferentes campos em ordem de preferência.
    
    Args:
        entry: Entrada do feed RSS
        
    Returns:
        str: Melhor conteúdo encontrado
    """
    # Tenta obter o conteúdo completo primeiro
    if hasattr(entry, 'content'):
        contents = entry.content
        if isinstance(contents, list) and contents:
            return contents[0].value
            
    # Tenta description ou summary
    for field in ['description', 'summary']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if content:
                return content
                
    # Se nenhum conteúdo for encontrado, usa o título
    return entry.get('title', '')

def match_source(url: str, source: str) -> bool:
    """
    Verifica se uma URL corresponde a uma fonte.
    Tenta diferentes partes do domínio para encontrar correspondência.
    
    Args:
        url: URL do feed
        source: Nome da fonte a procurar
        
    Returns:
        bool: True se a fonte corresponde à URL
    """
    domain = urlparse(url).netloc.lower()
    source = source.lower()
    
    # Remove subdomínios comuns
    parts = [p for p in domain.split('.') if p not in ('www', 'br', 'com')]
    
    # Tenta encontrar correspondência em qualquer parte do domínio
    return any(
        source in part or part in source
        for part in parts
    )

def to_iso8601(date_str):
    """Tenta converter uma string de data para ISO 8601. Se falhar, retorna a data/hora atual em ISO."""
    if not date_str:
        return datetime.now().isoformat()
    try:
        dt = date_parser.parse(date_str)
        return dt.isoformat()
    except Exception:
        return datetime.now().isoformat()

async def fetch_feed(session: aiohttp.ClientSession, url: str) -> List[Dict]:
    """
    Busca e processa um feed RSS específico.
    
    Args:
        session: Sessão HTTP assíncrona
        url: URL do feed RSS
        
    Returns:
        Lista de artigos processados do feed
    """
    try:
        print(f"\nTentando buscar feed: {url}")
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                print(f"Erro ao acessar {url}: Status {response.status}")
                return []
                
            content = await response.text()
            feed = feedparser.parse(content)
            
            if feed.bozo:  # Indica erro no parsing do feed
                print(f"Erro no parsing do feed {url}: {feed.bozo_exception}")
                return []
                
            if not feed.entries:
                print(f"Feed {url} não contém entradas")
                return []
            
            # Determina a fonte (source) do feed
            if feed.feed.get('title'):
                source = feed.feed.title
            else:
                # Usa o domínio da URL como fonte
                source = urlparse(url).netloc
                
            articles = []
            for entry in feed.entries:
                # Extrai o melhor conteúdo disponível
                content = extract_content(entry)
                
                # Limpa o conteúdo
                clean_content = clean_html(content)
                
                # Verifica se tem conteúdo mínimo
                if len(clean_content) < 10:  # Ignora conteúdo muito curto
                    continue
                
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': to_iso8601(entry.get('published', '')),
                    'summary': clean_content,
                    'source': source
                }
                articles.append(article)
            
            print(f"Sucesso! Encontrados {len(articles)} artigos em {url}")
            return articles
            
    except asyncio.TimeoutError:
        print(f"Timeout ao acessar {url}")
        return []
    except Exception as e:
        print(f"Erro ao processar feed {url}: {str(e)}")
        return []

async def fetch_all(sources: Optional[List[str]] = None) -> List[Dict]:
    """
    Busca todos os feeds RSS definidos no arquivo de configuração.
    
    Args:
        sources: Lista opcional de fontes a serem coletadas.
                Se None ou ["all"], coleta de todas as fontes.
                Ex: ["infomoney", "investing"]
    
    Returns:
        Lista combinada de artigos de todos os feeds
    """
    config_path = Path(__file__).parent.parent / 'config' / 'sources.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Filtra URLs baseado nas fontes solicitadas
    all_urls = config.get('rss', [])
    if sources and sources != ["all"]:
        rss_urls = []
        for url in all_urls:
            if any(match_source(url, s) for s in sources):
                rss_urls.append(url)
    else:
        rss_urls = all_urls
    
    print(f"\nFeeds configurados: {len(rss_urls)}")
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(session, url) for url in rss_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
    # Combina todos os resultados em uma única lista
    all_articles = []
    for result in results:
        if isinstance(result, list):  # Ignora exceções não tratadas
            all_articles.extend(result)
        else:
            print(f"Erro não tratado: {result}")
            
    return all_articles 