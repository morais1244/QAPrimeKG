# QAPrimeKG: Benchmark Text-to-Cypher para PrimeKG

Este projeto é um framework de benchmark de avaliação Text-to-Cypher focado no **PrimeKG (Precision Medicine Knowledge Graph)**. O objetivo principal é testar e validar a capacidade de Grandes Modelos de Linguagem (LLMs) em traduzir perguntas médicas e biológicas em linguagem natural para consultas Cypher executáveis no banco de dados de grafos Neo4j.

## 🚀 Sobre o Projeto

O QAPrimeKG avalia a precisão das consultas geradas comparando a quantidade de resultados reais (`observed_count`) retornados pela execução da consulta Cypher candidata no banco de dados com a quantidade esperada (`expected_count`) descrita no conjunto de dados de referência (gold standard).

### 🛠️ Tecnologias Utilizadas
- **Python 3**
- **Neo4j** (Graph Database)
- **LangChain** (Orquestração do LLM)
- **OpenRouter / OpenAI API** (Acesso ao LLM - configurado para utilizar modelos como `nvidia/nemotron-3-super-120b-a12b:free`)

## 📋 Pré-requisitos

1. **Neo4j Database**: É necessário ter uma instância do Neo4j rodando (local ou remotamente) contendo os dados do banco `primekg`.
   - As configurações de URI e credenciais (ex: `bolt://localhost:7687`) devem ser ajustadas nos arquivos `source/consult.py` e `source/run_benchmark.py`.

2. **Chave de API**: Uma chave de API válida do OpenRouter (ou OpenAI) configurada na variável `API_KEY` dentro do arquivo `source/consult.py`.

3. **Dependências Python**: Recomenda-se o uso de um ambiente virtual. Instale as dependências:
   ```bash
   pip install langchain langchain-neo4j langchain-openai langchain-core neo4j
   ```

## 🗂️ Estrutura do Projeto

- `source/consult.py`: Módulo responsável por conectar-se ao Neo4j e fazer a interface com o LLM via LangChain. Ele fornece o *System Prompt* contendo o contexto do schema do PrimeKG para que o LLM retorne apenas a query Cypher pertinente.
- `source/run_benchmark.py`: Script principal do benchmark. Lê os dados de teste em JSON, envia as perguntas para o modelo, roda a consulta retornada contra o banco de dados e verifica se a contagem das respostas está correta.
- `qa_cypher.json` *(Exemplo)*: Arquivo de entrada que deve conter os itens de benchmark, incluindo `id`, `question`, `expected_count` e o `cypher` correto (gold cypher).
- `benchmark_report.json`: Arquivo de saída contendo o relatório detalhado da execução.

## ⚙️ Como Executar

Para executar o benchmark completo, utilize:

```bash
python source/run_benchmark.py
```

O fluxo de execução segue estas etapas:
1. O arquivo `qa_cypher.json` é carregado.
2. Para cada questão, o `consult.py` é acionado para gerar a query Cypher com o LLM.
3. A query é executada diretamente na sessão do Neo4j.
4. O `observed_count` é comparado ao `expected_count`.
5. O resultado é consolidado e exportado com detalhes em `benchmark_report.json`.

## 📊 Status de Avaliação

O script classifica cada teste com um dos seguintes status:
- **Pass**: A query gerada foi executada com sucesso e retornou o número correto de resultados.
- **Count Mismatch**: A query executou, mas o número de resultados retornados foi diferente do gabarito (erros lógicos ou de relacionamento).
- **syntax error**: A query gerada apresentou erros de sintaxe ou alucinações e não pôde ser executada. A mensagem de erro é anexada ao relatório JSON.

## 🧠 Schema do PrimeKG

Para melhorar o desempenho da tradução, o LLM recebe as seguintes informações de contexto (schema constraints):
- **Nós (Nodes)**: `disease`, `drug`, `gene__protein`, `effect__phenotype`, `exposure`.
- **Relacionamentos (Relationships)**: `disease_disease`, `indication`, `disease_phenotype_positive`, `disease_protein`, `exposure_disease`.
- **Propriedades (Properties)**: `node_name`, `node_id`, `node_source`, `node_index`.