import json

from neo4j import GraphDatabase

# Configurações de conexão (ajuste para o seu caso)
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")


def validar_benchmark(arquivo_entrada, arquivo_saida):
    driver = GraphDatabase.driver(URI, auth=AUTH, database="primekg")
    dataset_validado = []

    with open(arquivo_entrada, "r") as f:
        perguntas = json.load(f)

    with driver.session() as session:
        for item in perguntas:
            try:
                # Tenta executar a query no seu PrimeKG
                result = session.run(item["cypher"])
                records = list(result)

                # Só salvamos se a query retornar dados reais
                if len(records) > 0:
                    item["expected_count"] = len(
                        records
                    )  # Opcional: guarda quantos resultados deu
                    dataset_validado.append(item)
                else:
                    print(f"⚠️ ID {item['id']} ignorado: Sem dados no banco.")

            except Exception as e:
                print(f"❌ ID {item['id']} erro de sintaxe: {e}")

    # Salva apenas o que funciona de verdade
    with open(arquivo_saida, "w") as f:
        json.dump(dataset_validado, f, indent=4)

    driver.close()


# Execução
validar_benchmark("hard.json", "dataset_final2.json")
