import asyncio
from src.processor.classify import rank_relevance

async def main():
    # Exemplos de itens para classificação
    items = [
        {
            'title': 'Petrobras anuncia novo plano de investimentos de R$ 100 bilhões',
            'summary': 'A Petrobras anunciou hoje seu novo plano estratégico quinquenal, com investimentos previstos de R$ 100 bilhões focados em exploração do pré-sal e transição energética. A empresa espera aumentar sua produção de petróleo em 30% até 2028.',
            'source': 'InfoMoney'
        },
        {
            'title': 'Inflação americana surpreende e dólar dispara',
            'summary': 'O índice de preços ao consumidor (CPI) dos EUA subiu mais que o esperado em janeiro, reduzindo as expectativas de cortes de juros pelo Federal Reserve no curto prazo. O dólar se fortaleceu globalmente após o dado.',
            'source': 'Valor Econômico'
        },
        {
            'title': 'Novo filme da Marvel quebra recordes de bilheteria',
            'summary': 'O mais recente lançamento do universo cinematográfico da Marvel arrecadou US$ 200 milhões em seu fim de semana de estreia, superando todas as expectativas dos analistas de mercado.',
            'source': 'G1'
        }
    ]
    
    try:
        print("=== Testando Classificação de Relevância ===\n")
        
        for item in items:
            score = await rank_relevance(item)
            print(f"Título: {item['title']}")
            print(f"Fonte: {item['source']}")
            print(f"Score de Relevância: {score}/5")
            print("-" * 50 + "\n")
            
    except Exception as e:
        print(f"Erro ao classificar: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 