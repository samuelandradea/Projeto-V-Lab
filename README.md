# V-Lab Abastecimentos API

API Gateway para Data Lake de abastecimentos da frota nacional.

## Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados

### Subindo a aplicação

```bash
docker compose up --build
```

A API estará disponível em `http://localhost:8000`.

Documentação interativa (Swagger): `http://localhost:8000/docs`

### Executando os testes

```bash
pip install -r requirements.txt
pip install aiosqlite
pytest -v
```

### Script de carga

Com a API rodando:

```bash
python load_data.py -n 100
```

## Endpoints

### Health Check

```
GET /health
```

### Ingestão de abastecimento

```
POST /api/v1/abastecimentos
Header: X-API-Key: vlab-secret-key-2024
```

```json
{
  "id_posto": 1,
  "data_hora": "2024-06-15T14:30:00",
  "tipo_combustivel": "GASOLINA",
  "preco_por_litro": 5.99,
  "volume_abastecido": 40.0,
  "cpf_motorista": "52998224725"
}
```

### Consulta com paginacao e filtros

```
GET /api/v1/abastecimentos?page=1&size=20&tipo_combustivel=GASOLINA&data_inicio=2024-01-01T00:00:00&data_fim=2024-12-31T23:59:59
```

### Historico do motorista

```
GET /api/v1/motoristas/{cpf}/historico
```

## Arquitetura

```
alembic/
├── env.py             # Config async do Alembic
└── versions/          # Migration files
app/
├── main.py            # Bootstrap FastAPI + lifespan (Alembic)
├── core/
│   ├── config.py      # Settings via pydantic-settings
│   ├── database.py    # Engine e session async
│   ├── auth.py        # Autenticacao por API Key
│   └── validators.py  # Validacao de CPF (digitos verificadores)
├── models/            # SQLAlchemy ORM
├── schemas/           # Pydantic (request/response)
├── services/          # Regras de negocio (flag de anomalia)
├── repositories/      # Acesso ao banco (queries)
└── routers/           # Endpoints HTTP
```

## O que foi feito

### Requisitos Minimos
- [x] POST /api/v1/abastecimentos com validacao completa (Pydantic)
- [x] Validacao de CPF com digitos verificadores (nao apenas formato)
- [x] Flag de anomalia (`improper_data`) quando preco > 25% acima da media de referencia
- [x] GET /api/v1/abastecimentos com paginacao e filtros
- [x] GET /api/v1/motoristas/{cpf}/historico (200 com lista vazia se sem registros)
- [x] Docker Compose (API + PostgreSQL) com `docker compose up`
- [x] Criacao automatica de tabelas via Alembic (com fallback para `Base.metadata.create_all`)

### Bonus implementados
- [x] Health Check: GET /health com teste real de conexao ao banco
- [x] Autenticacao: POST protegido com API Key via header X-API-Key
- [x] Script de carga: `load_data.py` com Faker e CPFs validos
- [x] Testes: validacao de CPF, flag de anomalia e testes de integracao da API

## Decisoes e Trade-offs

1. **Async por padrao**: Usei SQLAlchemy async + asyncpg para ter performance nao-bloqueante desde o inicio. Trade-off: um pouco mais de complexidade no setup de testes (precisei de aiosqlite).

2. **SQLite nos testes, PostgreSQL em producao**: Os testes rodam com SQLite em memoria (via aiosqlite) para serem rapidos e nao dependerem de Docker. Apesar de haver diferencas entre SQLite e PostgreSQL, para os cenarios testados isso nao impacta a fidelidade.

3. **Alembic com fallback**: A aplicacao tenta rodar `alembic upgrade head` na inicializacao. Se falhar (ex: nos testes com SQLite), cai no `Base.metadata.create_all` automaticamente.

4. **API Key simples**: A autenticacao e via header estatico. Em producao, usaria JWT ou OAuth2 com rotacao de chaves.

5. **Separacao em camadas**: Segui a arquitetura sugerida (routers -> services -> repositories -> models) para manter responsabilidades claras e facilitar testes unitarios.

6. **Medias de referencia mockadas**: Os precos de referencia estao em um dict constante no service. Em producao, viriam do banco ou de uma API externa.

## O que ficou pendente

- Rate limiting
- Logging estruturado
- CI/CD pipeline
- Testes de carga/stress
