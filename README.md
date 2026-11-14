# Back Field Shift

Proyecto base con Django REST Framework.

## Puesta en marcha

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Admin: http://127.0.0.1:8000/admin/
- Login de la API navegable: http://127.0.0.1:8000/api-auth/login/

## Crear una app

```bash
python manage.py startapp nombre_app
```

Luego agrégala a `INSTALLED_APPS` en `config/settings.py` y registra sus rutas en `config/urls.py`.
