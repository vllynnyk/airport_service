# ✈️ Airport Service API

A Django REST Framework backend for managing airports, routes, flights, crews, airplanes, and orders (tickets).  
Fully documented via **drf-spectacular** (OpenAPI v3), with Swagger UI and Redoc support.

## 🔗 Links

- 🌐 GitHub repository: https://github.com/vllynnyk/airport_service


---

## 🚀 Features

* **Airports**: CRUD + detailed view with departure and arrival routes
* **Routes**: Define and validate routes between airports
* **Airplanes & Airplane Types**: Categories and management of planes
* **Crew Management**: Assign crew members to flights
* **Flights**: Schedule flights with validation (crew, dates, airplane capacity)
* **Orders & Tickets**: Users can create orders with multiple tickets. Authenticated access only.
* **User Authentication**: Registration, login (token-based), and profile
* **OpenAPI**: Auto-generated documentation via drf-spectacular

  * JSON schema: `/api/schema/`
  * Swagger UI: `/api/schema/swagger-ui/`
  * Redoc UI: `/api/schema/redoc/`

---

## 🛠️ Installation

```bash
git clone https://github.com/vllynnyk/airport_service.git
cd airport_service
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

---
## 🐳 Docker Setup

To run the app using Docker:
```bash
docker compose up --build
```
To create a superuser inside the running container:
```bash
docker compose exec airport_service python manage.py createsuperuser
```
Access the app at http://localhost:8001/

---

## 📘 Usage

* **Register**: `POST /api/user/create/`
* **Login**: `POST /api/user/login/` → returns authentication token
* **Profile**: `GET/PUT/PATCH /api/user/me/`
* **Airports**: `GET /api/airports/`, `GET /api/airports/{id}/`, `POST`, `PUT`, `DELETE`
* **Routes**: same endpoints under `/api/routes/`, with validations
* **Airplanes & Types**, **Crew**, **Flights**, **Orders**: similar endpoints
* 
Explore the full API via:

* Swagger UI: `/api/schema/swagger-ui/`
* Redoc: `/api/schema/redoc/`

---

## 🧪 Running tests

```bash
pytest
```

---

## 🧑‍💻 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feat/YourFeature`
3. Commit your changes (`git commit -m "feat: ..."`)
4. Push and open a pull request

---

## 📝 Commit messages

Use **Conventional Commits** style. Examples:

* `feat: add drf-spectacular documentation for viewsets`
* `fix: correct validation logic in flight serializer`
* `docs: update README with API routes`
## 🔐 Default Superuser

A default superuser is already created:

* **Email**: admin@admin.com
* **Password**: 1234pass