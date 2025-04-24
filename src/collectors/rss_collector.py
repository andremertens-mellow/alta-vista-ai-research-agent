"""
Módulo responsável por coletar dados de feeds RSS definidos no arquivo de configuração.
"""
from typing import Dict, List
import asyncio
import yaml
import aiohttp
import feedparser
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup

def clean_html(text: str) -> str:
    """Remove tags HTML e formata o texto."""
    # Remove tags HTML
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    
    # Remove espaços extras e quebras de linha
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

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
                # Tenta obter o melhor conteúdo disponível
                content = ''
                if hasattr(entry, 'content'):
                    # Alguns feeds têm o conteúdo completo
                    content = entry.content[0].value
                elif hasattr(entry, 'description'):
                    content = entry.description
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                else:
                    content = entry.get('summary', '')
                
                # Limpa o conteúdo
                clean_content = clean_html(content)
                
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', datetime.now().isoformat()),
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

async def fetch_all() -> List[Dict]:
    """
    Busca todos os feeds RSS definidos no arquivo de configuração.
    
    Returns:
        Lista combinada de artigos de todos os feeds
    """
    config_path = Path(__file__).parent.parent / 'config' / 'sources.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    rss_urls = config.get('rss', [])
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