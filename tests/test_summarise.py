import asyncio
import os
from dotenv import load_dotenv
from src.processor.summarise import summarise

async def test_env():
    """Testa se a variável OPENAI_API_KEY está configurada"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    print("Status da configuração:")
    if api_key:
        print("✅ OPENAI_API_KEY encontrada no .env")
        if api_key == "sua-chave-aqui":
            print("❌ ERRO: Por favor, substitua 'sua-chave-aqui' pela chave real da API")
        else:
            print("✅ OPENAI_API_KEY parece estar configurada corretamente")
    else:
        print("❌ ERRO: OPENAI_API_KEY não encontrada no .env")

if __name__ == "__main__":
    asyncio.run(test_env()) 