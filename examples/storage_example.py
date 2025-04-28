"""
Exemplo de uso dos componentes de armazenamento.
"""
from datetime import datetime, timedelta
from src.storage import NewsIndex, NewsValidator, NewsCompressor
from src.storage import save, search_news

def main():
    # Exemplo de notícias
    items = [
        {
            "title": "Ibovespa sobe 2% com otimismo global",
            "link": "https://example.com/ibov",
            "source": "InfoMoney",
            "published": "2025-04-24T18:49:50+00:00",
            "summary": "O Ibovespa subiu forte nesta quinta-feira, impulsionado pelo otimismo nos mercados globais.",
            "relevance": 4.2,
            "categories": {"mercado": 0.9, "economia": 0.8}
        },
        {
            "title": "Empresa XYZ anuncia expansão internacional",
            "link": "https://example.com/xyz",
            "source": "Valor Econômico",
            "published": "2025-04-24T18:30:00+00:00",
            "summary": "A Empresa XYZ anunciou planos de expansão para mercados internacionais.",
            "relevance": 3.8,
            "categories": {"negócios": 0.9, "internacional": 0.7}
        }
    ]
    
    print("=== Exemplo de Uso dos Componentes de Armazenamento ===\n")
    
    # Validação
    print("1. Validando dados...")
    validator = NewsValidator()
    errors = validator.validate_items(items)
    if errors:
        print("Erros encontrados:")
        for idx, item_errors in errors.items():
            print(f"Item {idx}:", item_errors)
    else:
        print("✓ Dados válidos")
    
    # Salvamento
    print("\n2. Salvando dados...")
    save(items)  # Salva como processado
    save(items, raw=True)  # Salva como raw
    
    # Compressão manual
    print("\n3. Testando compressão manual...")
    with open("data/test.json", "w", encoding="utf-8") as f:
        import json
        json.dump(items, f)
    
    compressed_path = NewsCompressor.compress_file("data/test.json")
    ratio = NewsCompressor.get_compression_ratio("data/test.json", compressed_path)
    print(f"✓ Taxa de compressão: {ratio:.2%}")
    
    # Busca
    print("\n4. Testando busca...")
    
    # Busca por título
    print("\nBusca por título 'Ibovespa':")
    results = search_news(query="Ibovespa")
    for item in results:
        print(f"- {item['title']} (relevância: {item['relevance']})")
    
    # Busca por fonte
    print("\nBusca por fonte 'InfoMoney':")
    results = search_news(source="InfoMoney")
    for item in results:
        print(f"- {item['title']} (fonte: {item['source']})")
    
    # Busca por relevância mínima
    print("\nBusca por relevância >= 4.0:")
    results = search_news(min_relevance=4.0)
    for item in results:
        print(f"- {item['title']} (relevância: {item['relevance']})")
    
    # Busca por período
    start = datetime.now() - timedelta(days=1)
    end = datetime.now()
    print(f"\nBusca por período ({start.date()} a {end.date()}):")
    results = search_news(start_date=start, end_date=end)
    for item in results:
        print(f"- {item['title']} (data: {item['published']})")

if __name__ == "__main__":
    main() 