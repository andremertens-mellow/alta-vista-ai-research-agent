# alta-vista-ai-research-agent

## Sobre o Projeto

Alta Vista é um agente de pesquisa baseado em IA que coleta e analisa notícias de diversas fontes. O sistema utiliza web scraping inteligente e processamento de linguagem natural para extrair informações relevantes.

### Principais Funcionalidades

- Coleta automática de notícias de múltiplas fontes
- Processamento e análise de conteúdo
- Armazenamento estruturado de dados
- API para consulta de informações

## Requisitos

- Python 3.8+
- pip
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

## Estrutura do Projeto

```
alta-vista-ai-research-agent/
├── src/
│   ├── collectors/        # Módulos de coleta de dados
│   ├── config/           # Arquivos de configuração
│   ├── storage/          # Módulos de armazenamento
│   └── processors/       # Processadores de conteúdo
├── tests/               # Testes automatizados
├── docs/               # Documentação adicional
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

### Executando o Coletor

```python
from src.collectors.html_generic import collect
import asyncio

# Coleta de todas as fontes configuradas
articles = asyncio.run(collect())

# Coleta de fontes específicas
articles = asyncio.run(collect(sources=["Valor Investe", "Exame"]))
```

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

2. **Problemas de conexão**
   - Verifique sua conexão com a internet
   - Confirme se o site está acessível
   - Verifique configurações de proxy/firewall

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