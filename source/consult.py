import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI

API_KEY = "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"
NEO4J_URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")

SYSTEM_PROMPT = """
You are a Neo4j Cypher expert for the PrimeKG (Precision Medicine Knowledge Graph).
Your task is to translate natural language questions into Cypher queries.

SCHEMA CONTEXT:
- Nodes: disease, drug, gene__protein, effect__phenotype, exposure.
- Relationships: disease_disease, indication, disease_phenotype_positive, disease_protein, exposure_disease.
- Properties: node_name, node_id, node_source, node_index.

CONSTRAINTS:
- Return ONLY the Cypher query.
- No markdown code blocks (```).
- No explanations.
- Ensure relationship directions are correct according to PrimeKG standards.
"""

print("A conectar ao Grafo no Neo4j...")
graph = Neo4jGraph(
    url=NEO4J_URI, username=AUTH[0], password=AUTH[1], database="primekg"
)

graph.refresh_schema()
print("Conexão estabelecida com sucesso!")

llm = ChatOpenAI(
    openai_api_key=API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="nvidia/nemotron-3-super-120b-a12b:free",
    temperature=0,
    max_tokens=500,
)


def get_cypher_from_llm(question):
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("user", "{question}")]
    )

    # Chain: Template -> LLM -> Parser de String
    chain = prompt | llm | StrOutputParser()

    try:
        raw_response = chain.invoke({"question": question})
        # print(f"DEBUG - Resposta Bruta: {raw_response}")

        if "</think>" in raw_response:
            query = raw_response.split("</think>")[-1].strip()
        else:
            query = raw_response.replace("<think>", "").strip()

        clean_query = query.replace("```cypher", "").replace("```", "").strip()

        return clean_query
    except Exception as e:
        return f"Error: {str(e)}"
