"""
Módulo para coletar notícias de sites HTML genéricos.
"""
from typing import List, Dict
import asyncio
import yaml
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup
import datetime
import re
from urllib.parse import urljoin

async def fetch_page(url: str) -> str:
    """Fetch HTML content from a URL."""
    print(f"Fetching URL: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    print(f"Successfully fetched {url}")
                    return content
                else:
                    print(f"Failed to fetch {url}, status code: {response.status}")
                    return ""
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return ""

def extract_text(soup: BeautifulSoup, selector: str) -> str:
    """Extract text from HTML using CSS selectors."""
    print(f"Extracting text with selector: {selector}")
    try:
        if "::" in selector:  # Handle attribute selectors
            base_selector, attr = selector.split("::")
            elements = soup.select(base_selector)
            if elements:
                if attr.startswith("attr(") and attr.endswith(")"):
                    attr_name = attr[5:-1]
                    return elements[0].get(attr_name, "")
        else:
            elements = soup.select(selector)
            if elements:
                # Para seletores de conteúdo, pega todos os parágrafos
                if selector.endswith('content-text'):
                    paragraphs = []
                    for element in elements:
                        paragraphs.extend([p.get_text(strip=True) for p in element.find_all('p')])
                    return '\n'.join(filter(None, paragraphs))
                return elements[0].get_text(strip=True)
    except Exception as e:
        print(f"Error extracting text with selector {selector}: {str(e)}")
    return ""

def clean_date(date_text: str) -> str:
    """Clean and standardize date text."""
    try:
        # Remove texto extra comum em datas
        date_text = re.sub(r'Publicado em:|Atualizado em:', '', date_text, flags=re.IGNORECASE).strip()
        # Tenta converter para datetime e voltar para string em formato padrão
        date_obj = datetime.datetime.strptime(date_text, '%d/%m/%Y %H:%M')
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return date_text

async def collect_source(source_config: Dict) -> List[Dict]:
    """Collect news articles from a specific source."""
    print(f"Collecting from source: {source_config['name']}")
    
    # Fetch main page
    content = await fetch_page(source_config['landing_url'])
    if not content:
        return []
    
    soup = BeautifulSoup(content, 'html.parser')
    articles = []
    
    # Extract article links
    links = soup.select(source_config['article_link_selector'])
    print(f"Found {len(links)} article links")
    
    for link in links[:10]:  # Aumentado para 10 artigos
        try:
            article_url = link.get('href')
            if not article_url:
                continue
                
            # Usa urljoin para resolver URLs relativas corretamente
            article_url = urljoin(source_config['base_url'], article_url)
            
            print(f"Processing article: {article_url}")
            article_content = await fetch_page(article_url)
            if not article_content:
                continue
            
            article_soup = BeautifulSoup(article_content, 'html.parser')
            
            # Extract article details
            title = extract_text(article_soup, source_config['title_selector'])
            content = extract_text(article_soup, source_config['content_selector'])
            date_text = extract_text(article_soup, source_config['date_selector'])
            
            # Clean and validate date
            date_text = clean_date(date_text)
            
            # Basic article validation
            if title and content:
                articles.append({
                    'title': title,
                    'content': content,
                    'url': article_url,
                    'published_at': date_text,
                    'source': source_config['name']
                })
                print(f"Successfully processed article: {title}")
            else:
                print(f"Skipping article due to missing title or content: {article_url}")
                
        except Exception as e:
            print(f"Error processing article: {str(e)}")
            continue
    
    return articles

async def collect(sources: List[str] = None, limit: int = 30) -> List[Dict]:
    """Collect news from configured HTML sources."""
    print("Starting HTML collection")
    
    # Load configuration
    config_path = Path('src/config/html_sources.yaml')
    if not config_path.exists():
        print(f"Configuration file not found at {config_path}")
        return []
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Filter sources if specified
    if sources and not any(source.lower() in [s['name'].lower() for s in config['sources']] for source in sources):
        return []
    
    all_articles = []
    
    # Process each configured source
    for source_config in config['sources']:
        if not sources or source_config['name'].lower() in [s.lower() for s in sources]:
            try:
                articles = await collect_source(source_config)
                all_articles.extend(articles)
                print(f"Collected {len(articles)} articles from {source_config['name']}")
            except Exception as e:
                print(f"Error collecting from source {source_config['name']}: {str(e)}")
                continue
    
    # Sort by date and limit results
    all_articles = all_articles[:limit]
    print(f"Total articles collected: {len(all_articles)}")
    
    return all_articles
