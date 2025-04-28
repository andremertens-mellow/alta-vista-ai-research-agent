# src/create_post.py
from openai import AsyncClient
import os, textwrap
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

MODEL = "gpt-4"  # Corrigindo o nome do modelo
client = AsyncClient()

def validate_content(hook: str, text: str) -> tuple[bool, str]:
    """Valida o conteúdo gerado"""
    if len(hook.split()) > 20:
        return False, "Hook excede 20 palavras"
    if not 600 <= len(text) <= 800:
        return False, f"Texto tem {len(text)} caracteres (deve ter entre 600-800)"
    return True, ""

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def generate_content(prompt: str) -> str:
    """Gera conteúdo com retry em caso de falha"""
    try:
        rsp = await client.chat.completions.create(
            model=MODEL,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        return rsp.choices[0].message.content
    except Exception as e:
        print(f"Erro ao gerar conteúdo: {str(e)}")
        raise

async def draft_post(article: dict) -> dict:
    prompt = f"""
    Você é copywriter da Alta Vista Investimentos.
    Crie conteúdo para Instagram a partir do artigo abaixo.
    Use um tom profissional mas envolvente, adequado para investidores.

    Título: {article['title']}
    Resumo: {article['summary']}

    Regras importantes:
    - HOOK deve ter no máximo 20 palavras
    - TEXT deve ter entre 600-800 caracteres
    - Use 3-5 hashtags relevantes
    - Mantenha um tom inspirador e educativo
    - Inclua call-to-action sutil
    - Evite especulações sem fundamento

    Formato de saída (sem nada além disto):
    ---
    HOOK: <máx 20 palavras>
    TEXT: <600-800 caracteres, PT-BR>
    HASHTAGS: #Hashtag1 #Hashtag2 #Hashtag3
    ---
    """
    
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        raw = await generate_content(prompt)
        lines = [l.replace("HOOK:", "").replace("TEXT:", "").replace("HASHTAGS:", "").strip()
                for l in raw.split("\n") if l and not l.startswith("---")]
        
        if len(lines) != 3:
            attempt += 1
            continue
            
        hook, text, hashtags = lines
        is_valid, error = validate_content(hook, text)
        
        if is_valid:
            return {
                "title": article["title"],
                "hook": hook,
                "text": textwrap.fill(text, 90),
                "hashtags": hashtags,
                "link": article["link"],
                "source": article["source"],
                "score": article["relevance"],
            }
        
        attempt += 1
        
    raise ValueError("Não foi possível gerar conteúdo válido após várias tentativas") 