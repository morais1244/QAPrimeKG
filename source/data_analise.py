import json

import pandas as pd


def analisar_resultados_benchmark(arquivo_json):
    """
    Lê o relatório do benchmark e gera estatísticas detalhadas.
    """
    try:
        # 1. Carregar os dados
        with open(arquivo_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        if df.empty:
            print("O arquivo de resultados está vazio.")
            return

        print("-" * 50)
        print(f"RELATÓRIO DE ANÁLISE: {arquivo_json}")
        print("-" * 50)

        # 2. Acurácia Global
        total = len(df)
        passes = len(df[df["status"] == "Pass"])
        acuracia_global = (passes / total) * 100
        print(f"Acurácia Global: {acuracia_global:.2f}% ({passes}/{total})")

        # 3. Performance por Dificuldade
        print("\n--- Acurácia por Nível de Dificuldade ---")
        # Criamos uma coluna binária para facilitar o cálculo da média (1 para Pass, 0 para o resto)
        df["is_pass"] = df["status"].apply(lambda x: 1 if x == "Pass" else 0)

        diff_stats = df.groupby("difficulty").agg(
            total=("id", "count"),
            sucessos=("is_pass", "sum"),
            acuracia=("is_pass", "mean"),
        )
        diff_stats["acuracia"] = (diff_stats["acuracia"] * 100).round(2).astype(
            str
        ) + "%"
        print(diff_stats)

        # 4. Estatísticas de Tempo
        print("\n--- Estatísticas de Tempo (Segundos) ---")
        print(f"Tempo Médio: {df['time'].mean():.2f}s")
        print(f"Tempo Máximo: {df['time'].max():.2f}s")

        # 5. Análise de Falhas (Por que não passou?)
        print("\n--- Distribuição de Status ---")
        status_counts = df["status"].value_counts()
        print(status_counts)

        # 6. Top Erros de Execução (Sintaxe/Conexão)
        erros_execucao = df[df["status"] == "Error"]
        if not erros_execucao.empty:
            print("\n--- Exemplos de Erros de Execução ---")
            for _, row in erros_execucao.head(3).iterrows():
                print(f"ID {row['id']}: {row['error'][:100]}...")

        # 7. Mismatch de Contagem (Lógica errada)
        mismatch = df[df["status"] == "Count Mismatch"]
        if not mismatch.empty:
            print("\n--- Exemplos de Mismatch de Contagem (Esperado vs Obtido) ---")
            for _, row in mismatch.head(3).iterrows():
                print(
                    f"ID {row['id']}: Esperava {row['expected']}, mas obteve {row['observed']}"
                )

    except Exception as e:
        print(f"Erro ao analisar o ficheiro: {e}")


if __name__ == "__main__":
    # Altere para o nome do ficheiro gerado pelo seu script de benchmark
    ARQUIVO_RELATORIO = "gpt_result.json"
    analisar_resultados_benchmark(ARQUIVO_RELATORIO)
