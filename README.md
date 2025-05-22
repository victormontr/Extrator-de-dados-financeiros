# 📈 Extrator de Dados Financeiros

Aplicativo desktop para baixar dados históricos de ações do Yahoo Finance.

## 🚀 Como Rodar (Opção para Desenvolvedores/Contribuintes)

Se você deseja executar o código-fonte diretamente:

1.  **Ambiente Virtual (Recomendado)**:
    ```bash
    python -m venv StStr
    # Windows: .\StStr\Scripts\activate
    # macOS/Linux: source StStr/bin/activate
    ```

2.  **Instalar Dependências**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Arquivo de Tickers**:
    * Garanta que `Mapa Tickers B3.csv` (com colunas `Ação;Código`) esteja na pasta do projeto ou em `./Mapa/`.

4.  **Executar o Script**:
    ```bash
    python StockExtractor.py
    ```

## 📋 Funcionalidades Principais

* Interface gráfica para seleção de ticker, período, intervalo e formato (CSV/XLSX).
* Download de dados da B3 via Yahoo Finance.
* Salva arquivos em `Documentos/Dados financeiros Extraídos/`.

## 💾 Executável (.exe)

Uma versão executável (`.exe`) deste aplicativo é disponibilizada em `Extrator de Dados Financeiros/dist/`. Isso permite que usuários sem ambiente de desenvolvimento Python (ou até mesmo a linguagem instalada) possam utilizar o programa diretamente, sem necessidade de instalar dependências ou rodar o script via console/IDE.

Procure pelo arquivo `.exe` na seção de "releases" do projeto ou conforme distribuído.

## 📄 Saída

Os arquivos de dados extraídos são salvos automaticamente na pasta:
`Documentos/Dados financeiros Extraídos/`

## 📝 Nota

* Necessita de conexão com a internet para baixar os dados.

## 👨‍💻 Autor

Desenvolvido por **Victor Monteiro** em **22/05/2025**.

---