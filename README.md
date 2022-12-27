**Running parking app**
1. `docker-compose -f docker-compose.yml up -d`

**Testing parking app**
1. `docker-compose -f docker-compose.test.yml up -d`
2. `docker exec -ti parking_app_1 bash`
3. In docker container console: `pytest -vv`

## alembic revision

```bash
alembic revision --autogenerate -m "<ur_revision_message>" --rev-id=<ur_revision_id (ex: 0001)>
```

## alembic migrate

```bash
alembic upgrade head
```