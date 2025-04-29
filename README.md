# alta-vista-ai-research-agent

## Sobre o Projeto

Alta Vista é um agente de pesquisa baseado em IA que coleta, analisa notícias de diversas fontes e gera conteúdo para redes sociais. O sistema utiliza web scraping inteligente, processamento de linguagem natural e IA generativa para extrair informações relevantes e criar drafts de posts otimizados para engajamento.

### Principais Funcionalidades

- Coleta automática de notícias de múltiplas fontes (RSS e HTML)
- Processamento e análise de conteúdo com pontuação de relevância
- Armazenamento estruturado de dados com compressão
- Geração automática de drafts para redes sociais
- API para consulta de informações
- Workflow automatizado via GitHub Actions

## Requisitos

- Python 3.8+
- pip
- OpenAI API Key (para geração de drafts)
- Bibliotecas necessárias (listadas em `requirements.txt`)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/alta-vista-ai-research-agent.git
cd alta-vista-ai-research-agent
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
export OPENAI_API_KEY="sua-chave-aqui"  # Necessário para geração de drafts
```

## Estrutura do Projeto

```
alta-vista-ai-research-agent/
├── src/
│   ├── collectors/        # Módulos de coleta de dados
│   │   ├── html_collector.py  # Coleta via web scraping
│   │   └── rss_collector.py   # Coleta via RSS feeds
│   ├── config/           # Arquivos de configuração
│   │   ├── sources.yaml      # Configuração de fontes
│   │   └── html_sources.yaml # Configuração de fontes HTML
│   ├── storage/          # Módulos de armazenamento
│   │   ├── compressor.py     # Compressão de dados
│   │   └── indexer.py        # Indexação de artigos
│   ├── processor/        # Processadores de conteúdo
│   │   └── relevance.py      # Análise de relevância
│   ├── cli.py           # Interface de linha de comando
│   └── create_post.py   # Gerador de drafts para redes sociais
├── tests/               # Testes automatizados
├── output/             # Drafts gerados para redes sociais
├── data/               # Dados coletados e processados
└── requirements.txt    # Dependências do projeto
```

## Adicionando nova fonte HTML – Guia Rápido

Para adicionar uma nova fonte de notícias HTML ao sistema, siga estes passos:

1. Abra o arquivo `src/config/html_sources.yaml`

2. Adicione uma nova entrada na lista `sources` seguindo este modelo:

```yaml
- id: "nome_unico"              # Identificador único da fonte
  name: "Nome da Fonte"         # Nome de exibição da fonte
  base_url: "https://..."      # URL base do site
  landing_url: "https://..."   # URL da página principal de notícias
  link_selector: ".css-selector" # Seletor CSS para links dos artigos
  title_selector: ".titulo"     # Seletor CSS para título do artigo
  content_selector: ".conteudo" # Seletor CSS para conteúdo do artigo
  date_selector: ".data"        # Seletor CSS para data de publicação
  date_format: "%d/%m/%Y %H:%M" # Formato da data (strftime)
```

### Dicas para Seletores CSS

- Use ferramentas como DevTools do navegador para encontrar os seletores corretos
- Teste os seletores antes de adicionar ao YAML
- Exemplos comuns de seletores:
  - Classes: `.nome-da-classe`
  - IDs: `#id-do-elemento`
  - Tags: `article`, `div`, `p`
  - Combinados: `article .titulo h1`

### Formato de Data

O `date_format` deve seguir o padrão Python strftime:
- `%d`: dia (01-31)
- `%m`: mês (01-12)
- `%Y`: ano com 4 dígitos
- `%H`: hora (00-23)
- `%M`: minutos (00-59)

### Exemplo Completo

```yaml
- id: "valor_investe"
  name: "Valor Investe"
  base_url: "https://valorinveste.globo.com"
  landing_url: "https://valorinveste.globo.com/ultimas-noticias"
  link_selector: ".feed-post-link"
  title_selector: ".content-head__title"
  content_selector: ".content-text"
  date_selector: ".content-publication-data__updated"
  date_format: "%d/%m/%Y %H:%M"
```

### Testando a Nova Fonte

Após adicionar a configuração:

1. Execute os testes:
```bash
python -m pytest tests/test_html_collect.py
```

2. Teste a coleta específica da fonte:
```python
from src.collectors.html_generic import collect
import asyncio

articles = asyncio.run(collect(sources=["Nome da Fonte"]))
print(f"Artigos coletados: {len(articles)}")
```

## Uso

### Coletando Notícias e Gerando Drafts

O sistema oferece uma interface de linha de comando para suas principais funcionalidades:

```bash
# Coleta de notícias de todas as fontes
python -m src.cli

# Coleta de fontes específicas
python -m src.cli --sources valorinv infomoney

# Coleta e geração de drafts para redes sociais
python -m src.cli --sources valorinv --limit 30 --draft

# Apenas geração de drafts a partir de dados existentes
python -m src.cli --draft
```

### Formato dos Drafts

Os drafts gerados para redes sociais seguem um formato otimizado para Instagram:

- **Hook**: Título chamativo com máximo de 20 palavras
- **Text**: Corpo do post com 600-800 caracteres
- **Hashtags**: 3-5 hashtags relevantes

Os drafts são salvos em formato CSV em `output/posts_[DATA].csv` contendo:
- Título original
- Hook gerado
- Texto do post
- Hashtags
- Link da fonte
- Fonte original
- Score de relevância

### Configuração do Storage

O sistema suporta diferentes backends de armazenamento. Para configurar:

1. Edite `src/config/storage.yaml`:
```yaml
storage:
  type: "sqlite"  # ou "postgres", "mongodb"
  connection:
    database: "news.db"
    # outros parâmetros de conexão...
```

## Automação

### GitHub Actions

O projeto inclui workflows automatizados para:

1. Coleta periódica de notícias
2. Geração de drafts
3. Testes automatizados

Para configurar:

1. Adicione suas credenciais como secrets no GitHub:
   - `OPENAI_API_KEY`

2. Ajuste a frequência de execução em `.github/workflows/collect.yml`

## Desenvolvimento

### Executando Testes

```bash
# Todos os testes
python -m pytest

# Testes específicos
python -m pytest tests/test_html_collect.py
python -m pytest tests/test_storage.py
```

### Padrões de Código

- Siga PEP 8 para estilo de código Python
- Documente funções e classes usando docstrings
- Mantenha cobertura de testes acima de 80%

## Troubleshooting

### Problemas Comuns

1. **Erro na coleta de artigos**
   - Verifique os seletores CSS
   - Confirme se a estrutura do site não mudou
   - Verifique logs de erro em `logs/collector.log`

2. **Problemas com geração de drafts**
   - Verifique sua OPENAI_API_KEY
   - Confirme se há artigos coletados recentemente
   - Verifique a conectividade com a API da OpenAI

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-fonte`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova fonte'`)
4. Push para a branch (`git push origin feature/nova-fonte`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato

- Maintainer: [Seu Nome]
- Email: [seu.email@dominio.com]
- Issue Tracker: [Link para Issues do GitHub]