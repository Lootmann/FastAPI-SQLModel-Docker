# FastAPI + SQLModel + PostgresSQL Docker Compose Templates

## Envs

```
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── api/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   ├── main.py
│   │   ├── cruds/
│   │   ├── models/
│   │   ├── routers/
│   ├── pyproject.toml
│   └── requirements.txt
├── compose.yml
├── create_env.sh
└── db/
    └── Dockerfile
```

## run

1. `sh create_env.sh`
2. `make build` or `make buildup`
