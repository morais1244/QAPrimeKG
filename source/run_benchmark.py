import json

from consult import get_cypher_from_llm
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "12345678")


def run_benchmark(input_json, output_report):
    driver = GraphDatabase.driver(URI, auth=AUTH, database="primekg")
    report = []

    with open(input_json, "r") as f:
        bench_data = json.load(f)

    for item in bench_data:
        candidate_cypher = get_cypher_from_llm(item["question"])
        result_status = "Fail"
        observed_count = None
        error = None

        try:
            with driver.session() as session:
                result = session.run(candidate_cypher)
                observed_count = len(list(result))

                if observed_count == item["expected_count"]:
                    result_status = "Pass"
                else:
                    result_status = "Count Mismatch"
        except Exception as e:
            result_status = "syntax error"
            error = str(e)

        report_item = {
            "id": item["id"],
            "question": item["question"],
            "difficulty": item["difficulty"],
            "expected_count": item["expected_count"],
            "observed_count": observed_count,
            "gold_cypher": item["cypher"],
            "candidate_cypher": candidate_cypher,
            "status": result_status,
        }
        if error:
            report_item["error"] = error

        report.append(report_item)

        with open(output_report, "w") as f:
            json.dump(report, f, indent=2)


run_benchmark("qa_cypher.json", "benchmark_report.json")
