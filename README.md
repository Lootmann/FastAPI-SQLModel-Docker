# FastAPI + SQLAlchemy + Postgresql Docker compose templates

さくっと使えるようなやつ


## Envs

```
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── api/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   ├── main.py
│   │   ├── migrate_db.py
│   │   ├── cruds/
│   │   ├── models/
│   │   ├── routers/
│   │   └── schemas/
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
