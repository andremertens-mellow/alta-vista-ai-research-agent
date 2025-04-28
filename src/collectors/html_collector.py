import yaml
from typing import List, Dict, Optional
from datetime import datetime
import logging
from urllib.parse import urljoin
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from dateutil import parser
import re

# Configurar logging para mostrar mais informações
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_config() -> List[Dict]:
    with open("src/config/html_sources.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config["sources"]

def clean_date(date_str: str) -> str:
    """Clean and standardize date string."""
    logger.debug(f"Limpando data: {date_str}")
    # Remove common phrases
    date_str = re.sub(r'Atualizado em |Publicado em |às |em ', '', date_str)
    date_str = date_str.strip()
    
    try:
        # Parse date string to datetime
        dt = parser.parse(date_str, fuzzy=True)
        # Return ISO format
        return dt.isoformat()
    except:
        logger.warning(f"Could not parse date: {date_str}")
        return datetime.now().isoformat()

def extract_text(soup: BeautifulSoup, selector: str) -> str:
    """Extract text from HTML using selector."""
    logger.debug(f"Extraindo texto com seletor: {selector}")
    elements = soup.select(selector)
    logger.debug(f"Encontrados {len(elements)} elementos")
    
    if not elements:
        return ""
        
    # Handle special case for content selector
    if selector.endswith("p"):
        # Extract text from each paragraph
        texts = [p.get_text().strip() for p in elements]
        return "\n\n".join(filter(None, texts))
    
    return elements[0].get_text().strip()

async def fetch_article(session: aiohttp.ClientSession, url: str, source_config: Dict) -> Optional[Dict]:
    """Fetch and parse a single article."""
    try:
        logger.debug(f"Buscando artigo: {url}")
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            html = await response.text()
            logger.debug(f"HTML recebido: {html[:200]}...")
            
        soup = BeautifulSoup(html, "html.parser")
        article = source_config["article"]
        
        # Extract article data using selectors
        title = extract_text(soup, article["title_selector"])
        logger.debug(f"Título extraído: {title}")
        
        content = extract_text(soup, article["content_selector"])
        logger.debug(f"Conteúdo extraído: {content[:200]}...")
        
        date_str = extract_text(soup, article["date_selector"])
        logger.debug(f"Data extraída: {date_str}")
        
        author = extract_text(soup, article.get("author_selector", "")) or "Unknown"
        logger.debug(f"Autor extraído: {author}")
        
        if not (title and content):
            logger.warning(f"Missing title or content for {url}")
            return None
            
        return {
            "title": title,
            "content": content,
            "date": clean_date(date_str),
            "url": url,
            "source": source_config["name"],
            "author": author
        }
        
    except Exception as e:
        logger.error(f"Error fetching article {url}: {str(e)}")
        return None

async def fetch_source_articles(session: aiohttp.ClientSession, source_config: Dict, limit: int = 10) -> List[Dict]:
    """Fetch articles from a single source."""
    try:
        logger.info(f"Tentando buscar artigos de: {source_config['name']}")
        logger.info(f"URL da landing page: {source_config['landing_url']}")
        
        # Get landing page
        async with session.get(source_config["landing_url"], timeout=10) as response:
            response.raise_for_status()
            html = await response.text()
            logger.debug(f"HTML da landing page: {html[:200]}...")
            
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract article links
        selector = source_config["article"]["link_selector"]
        logger.debug(f"Usando seletor de links: {selector}")
        links = soup.select(selector)
        logger.info(f"Encontrados {len(links)} links usando seletor: {selector}")
        
        article_urls = []
        for link in links[:limit]:
            href = link.get("href")
            if href:
                # Handle relative URLs
                if not href.startswith(("http://", "https://")):
                    href = urljoin(source_config["base_url"], href)
                article_urls.append(href)
                logger.info(f"URL do artigo encontrada: {href}")
                
        # Fetch articles concurrently
        tasks = [fetch_article(session, url, source_config) for url in article_urls]
        articles = await asyncio.gather(*tasks)
        valid_articles = [a for a in articles if a is not None]
        logger.info(f"Coletados {len(valid_articles)} artigos válidos de {len(article_urls)} URLs")
        return valid_articles
        
    except Exception as e:
        logger.error(f"Erro ao buscar fonte {source_config['name']}: {str(e)}")
        return []

async def fetch_all(sources: Optional[List[str]] = None, limit: int = 10) -> List[Dict]:
    """Fetch articles from all configured sources or specified sources."""
    all_articles = []
    config = load_config()
    
    # Filter sources if specified
    if sources and "all" not in sources:
        sources = [s.lower() for s in sources]
        config = [s for s in config if s["id"].lower() in sources]
        logger.debug(f"Fontes filtradas: {[s['id'] for s in config]}")
        
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_source_articles(session, source_config, limit) for source_config in config]
        results = await asyncio.gather(*tasks)
        
        for articles in results:
            all_articles.extend(articles)
            
    return all_articles 