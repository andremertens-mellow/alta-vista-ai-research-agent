import asyncio
from src.collectors.html_generic import collect

def test_valorinv():
    """
    Testa a coleta de artigos do Valor Investe.
    Verifica se:
    - Pelo menos 1 artigo é coletado
    - Os artigos têm a fonte correta
    - Os artigos têm título e conteúdo
    """
    articles = asyncio.run(collect(sources=["Valor Investe"], limit=2))
    assert len(articles) >= 1, "Deveria coletar pelo menos 1 artigo"
    
    for art in articles:
        assert art["source"] == "Valor Investe", f"Fonte incorreta: {art['source']}"
        assert art["title"], f"Artigo sem título: {art}"
        assert art["content"], f"Artigo sem conteúdo: {art}"
        assert art["url"], f"Artigo sem URL: {art}"
        assert art["published_at"], f"Artigo sem data: {art}" 