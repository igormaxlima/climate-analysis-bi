
# Data Pipeline para Análise Climática

Este projeto implementa uma pipeline de dados para processamento e análise de informações climáticas utilizando `MongoDB`, `MinIO`, `Jupyter Notebooks` e um dashboard em `Streamlit`.

## Pré-requisitos

Certifique-se de que você tenha as seguintes ferramentas instaladas no seu ambiente:
- [Docker](https://www.docker.com/)
- Conta no [Kaggle](https://www.kaggle.com/)

## Passo a Passo de Configuração

### 1. Clone o Repositório
Clone este repositório no seu ambiente local:
```bash
git clone https://github.com/igormaxlima/climate-analysis-bi.git
cd climate-analysis-bi
```

### 2. Obtenha o Arquivo CSV
1. Acesse esse [dataset do Kaggle](https://www.kaggle.com/datasets/PROPPG-PPG/hourly-weather-surface-brazil-southeast-region?select=central_west.csv).
2. Baixe o arquivo **`central_west.csv`**.
3. Crie uma pasta chamada `data` dentro da pasta `jupyter` do repositório:
   ```bash
   mkdir jupyter/data
   ```
4. Coloque o arquivo `central_west.csv` dentro da pasta `data`.

### 3. Suba o Projeto no Docker
1. No terminal, execute o comando:
   ```bash
   docker compose up -d
   ```
   Isso irá iniciar todos os serviços necessários.

2. Confirme que os containers estão rodando:
   ```bash
   docker ps
   ```

### 4. Obtenha os IPs dos Containers
1. Para acessar o `MinIO` e o `MongoDB`, você precisa dos IPs de seus containers.
2. Execute o comando abaixo para inspecionar os containers:
   ```bash
   docker inspect climate-analysis-bi_climate
   ```
3. Procure pelo campo `Networks > IPAddress` para encontrar o IP dos serviços:
   - **MongoDB**: Pegue o IP do container `mongo_service`.
   - **MinIO**: Pegue o IP do container `minio`.

### 5. Configure os Notebooks e a Aplicação
1. Abra os notebooks na pasta `jupyter` e substitua as URLs `localhost` pelos respectivos IPs dos serviços:
   - **MongoDB**: Substitua `localhost` pelo IP do `mongo_service`.
   - **MinIO**: Substitua `localhost` pelo IP do `minio`.

2. Faça o mesmo no arquivo `app.py` para garantir que a aplicação conecte corretamente aos serviços.

### 6. Acesse o Dashboard
1. Abra o navegador e acesse o dashboard no endereço:
   ```text
   http://localhost:8501/
   ```
2. Agora você pode visualizar e analisar os dados tratados.

---

## Observações
- Caso precise derrubar os serviços, use o comando:
  ```bash
  docker compose down
  ```
- Certifique-se de que todas as dependências do projeto estão devidamente configuradas antes de executar.

---

**Autores**: [Igor Max](https://github.com/igormaxlima) e [Pedro Nasser](https://github.com/pedronassero)
