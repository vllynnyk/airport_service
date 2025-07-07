# ✈️ Airport Service API

A Django REST Framework backend for managing airports, routes, flights, crews, airplanes, and orders (tickets). Fully documented via **drf-spectacular** (OpenAPI v3), with Swagger UI and Redoc support.

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

## 🔧 Configuration

In your `settings.py`:

```python
INSTALLED_APPS += [
  'rest_framework',
  'drf_spectacular',
  'rest_framework.authtoken',
  'user',
  'airservice',
]

REST_FRAMEWORK = {
  'DEFAULT_AUTHENTICATION_CLASSES': [
    'rest_framework.authentication.TokenAuthentication',
  ],
  'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAuthenticatedOrReadOnly',
  ],
  'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
  'TITLE': 'Airport Service API',
  'VERSION': '1.0.0',
  'DESCRIPTION': 'API for airport and flight management',
}
```

Add URL patterns:

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns += [
  path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
  path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
  path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

---

## 📘 Usage

* **Register new user**: `POST /api/user/create/`
* **Login**: `POST /api/user/login/` → returns authentication token
* **Profile**: `GET/PUT/PATCH /api/user/me/`
* **Airports**: `GET /api/airports/`, `GET /api/airports/{id}/`, `POST`, `PUT`, `DELETE`
* **Routes**: same endpoints under `/api/routes/`, with validations
* **Airplanes & Types**, **Crew**, **Flights**, **Orders**: similar endpoints
* **Authenticated users only** may create orders.

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
