import asyncio
import aiohttp
from bs4 import BeautifulSoup
import yaml
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_selectors():
    # Carregar configuração
    with open("src/config/html_sources.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Pegar configuração da Exame
    exame_config = next(s for s in config["sources"] if s["id"] == "exame")
    
    # URL de teste
    test_url = "https://exame.com/mundo/sobrinho-do-papa-francisco-viaja-da-argentina-para-roma-gracas-a-uma-doacao-privada/"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(test_url) as response:
            html = await response.text()
            
        soup = BeautifulSoup(html, "html.parser")
        article = exame_config["article"]
        
        # Testar cada seletor
        title = soup.select(article["title_selector"])
        content = soup.select(article["content_selector"])
        date = soup.select(article["date_selector"])
        
        print("\nResultados do teste:")
        print("-" * 50)
        print(f"Título encontrado: {bool(title)}")
        if title:
            print(f"Texto do título: {title[0].get_text().strip()}")
            
        print(f"\nConteúdo encontrado: {bool(content)}")
        if content:
            print(f"Primeiros 200 caracteres do conteúdo: {content[0].get_text().strip()[:200]}...")
            
        print(f"\nData encontrada: {bool(date)}")
        if date:
            print(f"Texto da data: {date[0].get_text().strip()}")

if __name__ == "__main__":
    asyncio.run(test_selectors()) 