import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import Dict

# Carrega as variáveis de ambiente
load_dotenv()

async def rank_relevance(item: Dict) -> int:
    """
    Avalia a relevância de um item para investidores brasileiros de renda variável.
    
    Args:
        item: Dicionário contendo title, summary e source do conteúdo
        
    Returns:
        int: Score de relevância de 0 a 5
    """
    # Verifica se a chave da API está configurada
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY não encontrada no arquivo .env. "
            "Por favor, configure a variável OPENAI_API_KEY=sua-chave-aqui"
        )
    
    # Inicializa o cliente OpenAI
    client = AsyncOpenAI()
    
    # Monta o prompt com as informações do item
    system_prompt = "Você é analista da Alta Vista Investimentos especializado em renda variável."
    user_prompt = f"""
    Título: {item['title']}
    Resumo: {item['summary']}
    Fonte: {item['source']}
    
    De 0 a 5, quão relevante é este conteúdo para investidores brasileiros de renda variável?
    """
    
    # Define o schema para extração do score
    function_schema = {
        "name": "extract_score",
        "description": "Extrai o score de relevância",
        "parameters": {
            "type": "object",
            "properties": {
                "score": {
                    "type": "integer",
                    "description": "Score de 0 a 5 indicando a relevância",
                    "minimum": 0,
                    "maximum": 5
                }
            },
            "required": ["score"]
        }
    }
    
    # Faz a chamada para a API com function calling
    response = await client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        functions=[function_schema],
        function_call={"name": "extract_score"},
        temperature=0.3
    )
    
    # Extrai o score do resultado
    try:
        function_args = json.loads(response.choices[0].message.function_call.arguments)
        return function_args["score"]
    except Exception as e:
        print(f"Erro ao extrair score: {e}")
        return 0  # Retorna 0 em caso de erro na extração 

async def process_item(item: Dict) -> Dict:
    """
    Processa um item de notícia e retorna suas categorias.
    
    Args:
        item: Dicionário contendo informações da notícia
        
    Returns:
        Dict: Dicionário com as categorias do item
    """
    # Por enquanto, vamos apenas retornar um dicionário vazio
    # TODO: Implementar classificação por categorias
    return {} 