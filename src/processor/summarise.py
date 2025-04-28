import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import Optional
from bs4 import BeautifulSoup
import re

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def extract_first_paragraph(text: str, max_chars: int = 300) -> str:
    """
    Extrai o primeiro parágrafo relevante do texto.
    Remove tags HTML e limita o tamanho.
    
    Args:
        text: Texto a ser processado
        max_chars: Número máximo de caracteres
        
    Returns:
        Primeiro parágrafo do texto, limitado a max_chars
    """
    # Remove tags HTML
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    
    # Remove espaços extras e quebras de linha
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Pega o primeiro parágrafo não vazio
    paragraphs = [p.strip() for p in text.split('.') if p.strip()]
    if not paragraphs:
        return text[:max_chars] + '...' if len(text) > max_chars else text
        
    first_par = paragraphs[0] + '.'
    return first_par[:max_chars] + '...' if len(first_par) > max_chars else first_par

async def summarise(text: str, url: str) -> str:
    """
    Gera um resumo conciso de 2-3 linhas em português do texto fornecido.
    Se a chave da API OpenAI não estiver disponível, extrai o primeiro parágrafo.
    
    Args:
        text (str): Texto a ser resumido
        url (str): URL da fonte do texto
        
    Returns:
        str: Resumo em português brasileiro com 2-3 linhas
        
    Note:
        Se o texto exceder 4000 caracteres, será truncado do início para caber.
    """
    # Se não houver chave da API, usa o método alternativo
    if not os.getenv("OPENAI_API_KEY"):
        return extract_first_paragraph(text)
    
    try:
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
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Erro ao gerar resumo via OpenAI: {e}")
        # Em caso de erro, usa o método alternativo
        return extract_first_paragraph(text)

async def process_item(item: dict) -> str:
    """
    Processa um item de notícia e retorna um resumo.
    
    Args:
        item: Dicionário contendo informações da notícia
        
    Returns:
        str: Resumo da notícia
    """
    # Combina título e conteúdo para o resumo
    content = f"{item.get('title', '')} {item.get('content', '')}"
    url = item.get('url', '')
    
    # Gera o resumo
    return await summarise(content, url) 