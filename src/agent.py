from typing import List, Dict, Any
import asyncio
from src.collectors.rss_collector import fetch_all as fetch_rss
from src.collectors.html_collector import fetch_all as fetch_html
from src.processor.summarise import process_item as summarise_item
from src.processor.classify import process_item as classify_item
from src.processor.deduplicate import process_items as deduplicate_items
from src.processor.relevance import process_item as calculate_relevance
from src.storage import save_raw_data, save_processed_data
from datetime import datetime

async def run_agent(sources: List[str] = None, limit: int = 30) -> None:
    """
    Run the agent to collect and process news articles.
    
    Args:
        sources (List[str], optional): List of news sources to collect from. Defaults to None.
        limit (int, optional): Maximum number of items to process. Defaults to 30.
    """
    print(f"\n🔍 Coletando notícias das fontes: {sources}")
    
    # Collect news from RSS feeds
    rss_items = await fetch_rss(sources)
    print(f"\nFeeds configurados: {len(rss_items)}")
    
    # Collect news from HTML sources
    html_items = await fetch_html(sources)
    
    # Combine items
    all_items = rss_items + html_items
    print(f"\n📊 Encontrados {len(all_items)} artigos no total:")
    print(f"   - {len(rss_items)} artigos via RSS")
    print(f"   - {len(html_items)} artigos via HTML")
    
    # Remove duplicates
    unique_items = deduplicate_items(all_items)
    print(f"\n🔄 {len(unique_items)} itens únicos após remoção de duplicatas")
    
    # Process items
    print("\n⚙️ Processando itens...")
    
    # Limit items if necessary
    if len(unique_items) > limit:
        print(f"\n⚠️ Limitando para {limit} itens dos {len(unique_items)} encontrados")
        unique_items = unique_items[:limit]
    
    processed_items = []
    for item in unique_items:
        # Calculate relevance
        relevance = calculate_relevance(item)
        item['relevance'] = relevance
        
        # Only process items with relevance > 0
        if relevance > 0:
            # Add summary
            summary = await summarise_item(item)
            item['summary'] = summary
            
            # Add categories
            categories = await classify_item(item)
            item['categories'] = categories
            
            processed_items.append(item)
    
    # Sort by relevance
    processed_items.sort(key=lambda x: x.get('relevance', 0), reverse=True)
    
    print(f"\n📰 {len(processed_items)} itens relevantes encontrados:\n")
    for item in processed_items:
        print(f"⭐ Relevância {item['relevance']}: {item['title']}")
        print(f"📝 Sumário: {item['summary']}")
        print(f"🔍 Fonte: {item['source']}\n")
    
    # Save data
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    raw_path = save_raw_data(unique_items, timestamp)
    processed_path = save_processed_data(processed_items, timestamp)
    
    print("💾 Dados salvos em:")
    print(f"   Raw: {raw_path}")
    print(f"   Processed: {processed_path}")

if __name__ == "__main__":
    asyncio.run(run_agent()) 