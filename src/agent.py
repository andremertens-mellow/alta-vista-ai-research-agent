import asyncio
from collectors.rss_collector import fetch_all
from processor.deduplicate import remove_dupes
from processor.summarise import summarise
from processor.classify import rank_relevance

async def main():
    """
    Fluxo principal do agente:
    1. Coleta notícias dos feeds RSS
    2. Remove duplicatas
    3. Para cada item:
       - Gera resumo
       - Classifica relevância
    4. Filtra por score >= 3
    5. Ordena por relevância
    6. Exibe top 10
    """
    print("🤖 Alta Vista AI Research Agent\n")
    
    print("1. Coletando notícias...")
    raw = await fetch_all()
    print(f"   → {len(raw)} itens encontrados\n")
    
    print("2. Removendo duplicatas...")
    uniq = remove_dupes(raw)
    print(f"   → {len(uniq)} itens únicos\n")
    
    print("3. Processando itens...")
    curated = []
    for i, it in enumerate(uniq, 1):
        print(f"   → Processando item {i}/{len(uniq)}", end="\r")
        
        # Gera resumo e classifica
        it["summary"] = await summarise(it["summary"], it["link"])
        it["score"] = await rank_relevance(it)
        
        # Adiciona se relevante
        if it["score"] >= 3:
            curated.append(it)
    print("\n")
    
    print("4. Ordenando por relevância...")
    curated.sort(key=lambda x: x["score"], reverse=True)
    print(f"   → {len(curated)} itens relevantes encontrados\n")
    
    print("=== Top 10 Notícias Mais Relevantes ===\n")
    for it in curated[:10]:
        print(f"[{it['score']}/5] {it['title']}")
        print(f"→ {it['summary']}")
        print("-" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main()) 