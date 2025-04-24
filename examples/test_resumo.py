import asyncio
from src.processor.summarise import summarise

async def main():
    # Texto de exemplo (notícia financeira)
    texto = """
    O Ibovespa, principal índice da bolsa brasileira, fechou em alta nesta sessão, 
    impulsionado principalmente pelo setor bancário e pela Vale. O movimento acompanhou 
    a tendência positiva das bolsas internacionais, especialmente após dados econômicos 
    dos Estados Unidos sugerirem que o Federal Reserve pode começar a reduzir as taxas 
    de juros ainda este ano. Os investidores também reagiram positivamente aos resultados 
    corporativos do primeiro trimestre e às declarações do presidente do Banco Central 
    sobre a condução da política monetária no Brasil.
    
    O volume financeiro da sessão foi superior à média das últimas semanas, indicando 
    maior participação dos investidores institucionais. O dólar, por sua vez, registrou 
    leve queda frente ao real, refletindo o ambiente mais favorável para moedas de 
    países emergentes.
    """
    
    url = "https://exemplo.com/noticia-mercado"
    
    try:
        # Gera o resumo
        resumo = await summarise(texto, url)
        
        print("=== Texto Original ===")
        print(texto.strip())
        print("\n=== Resumo Gerado ===")
        print(resumo)
        
    except Exception as e:
        print(f"Erro ao gerar resumo: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 