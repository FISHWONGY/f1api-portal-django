# f1api-portal-django

To initialize the wrapper, you need to provide the following parameters:

```bash
uv venv --python 3.11 
source .venv/bin/activate
uv pip install -r pyproject.toml 

# Optional: 
uv lock
```

To create a new django project, run the following command:
```commandline
django-admin startproject f1apiportal .
```

To create a client app, run the following command:
```commandline
python manage.py startapp apiportal
```

