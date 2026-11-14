[![CI](https://github.com/Bla-vk/simple-crud-api-django/actions/workflows/ci.yml/badge.svg)](https://github.com/Bla-vk/simple-crud-api-django/actions/workflows/ci.yml)

# Simple CRUD API (Django REST Framework)

A REST API for tracking **items** and the **locations** they are stored in.
Built with Django and Django REST Framework, packaged with Docker.

- Full Create / Read / Update / Delete for items and locations
- Versioned paths under `/api/v1/`
- Paginated lists (20 per page)
- Filter items by location: `/api/v1/items/?location=<id>`
- Location names are unique; deleting a location deletes its items
- A `/health/` endpoint for load balancer and container health checks
- 17 automated tests

## Endpoints

| Method                  | Path                      | Purpose                                                  |
| ----------------------- | ------------------------- | -------------------------------------------------------- |
| GET, POST               | `/api/v1/locations/`      | List / create locations                                  |
| GET, PUT, PATCH, DELETE | `/api/v1/locations/<id>/` | Read / update / delete a location                        |
| GET, POST               | `/api/v1/items/`          | List (supports `?location=` and `?page=`) / create items |
| GET, PUT, PATCH, DELETE | `/api/v1/items/<id>/`     | Read / update / delete an item                           |
| GET                     | `/health/`                | Returns `{"status": "ok"}`                               |

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export DJANGO_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")
export DJANGO_DEBUG=1

python manage.py migrate
python manage.py runserver
```

The app refuses to start if `DJANGO_SECRET_KEY` is not set.

## Try it

```bash
curl -X POST localhost:8000/api/v1/locations/ \
  -H 'Content-Type: application/json' -d '{"name":"Shelf A"}'

curl -X POST localhost:8000/api/v1/items/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Laptop","description":"14 inch","location":1}'

curl "localhost:8000/api/v1/items/?location=1&page=1"
curl -X PATCH localhost:8000/api/v1/items/1/ \
  -H 'Content-Type: application/json' -d '{"description":"updated"}'
curl -X DELETE localhost:8000/api/v1/items/1/
```

## Run the tests

```bash
export DJANGO_SECRET_KEY=test-key
python manage.py test
```

## Docker

```bash
docker build -t simple-crud-django .
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY=change-me \
  -e DJANGO_ALLOWED_HOSTS='*' \
  simple-crud-django
```

The image runs as a non-root user, applies migrations on start and serves with gunicorn on port 8000.

If you push the image to ECR with `docker buildx`, add `--provenance=false` so ECR can scan it.

## Configuration

| Variable               | Default               | Purpose                   |
| ---------------------- | --------------------- | ------------------------- |
| `DJANGO_SECRET_KEY`    | required              | Django secret key         |
| `DJANGO_DEBUG`         | `0`                   | Set to `1` for debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hostnames |

## Known limits

- Uses SQLite, so data is lost when a container or ECS task is replaced. Move to RDS (PostgreSQL) for persistence.
- No authentication yet.

## Project layout

```
config/       Django project settings and root URLs
inventory/    models, serializers, views, URLs, migrations, tests
Dockerfile
requirements.txt
```
