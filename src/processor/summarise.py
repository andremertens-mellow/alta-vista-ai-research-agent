import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import Optional

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

async def summarise(text: str, url: str) -> str:
    """
    Gera um resumo conciso de 2-3 linhas em português do texto fornecido usando GPT-4.
    
    Args:
        text (str): Texto a ser resumido
        url (str): URL da fonte do texto
        
    Returns:
        str: Resumo em português brasileiro com 2-3 linhas
        
    Note:
        Se o texto exceder 4000 caracteres, será truncado do início para caber.
    """
    # Verifica se a chave da API está configurada
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY não encontrada no arquivo .env. "
            "Por favor, configure a variável OPENAI_API_KEY=sua-chave-aqui"
        )
    
    # Inicializa o cliente OpenAI
    client = AsyncOpenAI()
    
    # Limita o texto a 4000 caracteres se necessário
    if len(text) > 4000:
        text = text[-4000:]
    
    # Define o prompt do sistema e do usuário
    system_prompt = "Você é analista da Alta Vista Investimentos."
    user_prompt = f"""
    Resuma o seguinte texto em 2-3 linhas em português brasileiro.
    Mantenha as informações mais relevantes para investidores.
    
    Fonte: {url}
    
    Texto: {text}
    """
    
    # Faz a chamada para a API
    response = await client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )
    
    # Retorna o resumo gerado
    return response.choices[0].message.content.strip() 