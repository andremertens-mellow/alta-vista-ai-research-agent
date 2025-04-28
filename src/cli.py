import typer
import asyncio
import csv
from pathlib import Path
import datetime as dt
from src.agent import run_agent

app = typer.Typer()

@app.command()
def run(
    sources: str = typer.Option("all", "--sources", "-s", help="Lista separada por vírgula de fontes (ex: valorinv,exame)"),
    limit: int = typer.Option(30, "--limit", "-l", help="Número máximo de itens por fonte"),
    draft: bool = typer.Option(False, "--draft", help="Gera drafts de posts para Instagram"),
):
    articles = asyncio.run(run_agent(sources.split(","), limit))

    if draft:
        if not articles:
            print("Nenhum artigo relevante encontrado para gerar drafts.")
            return
        from src.create_post import draft_post
        top5 = sorted(articles, key=lambda x: x.get("relevance", 0), reverse=True)[:5]
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        posts = loop.run_until_complete(asyncio.gather(*[draft_post(a) for a in top5]))

        out = Path("output")
        out.mkdir(exist_ok=True)
        fname = out / f"posts_{dt.date.today()}.csv"
        with fname.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)

        print(f"Drafts salvos em {fname}")

if __name__ == "__main__":
    app() 