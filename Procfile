release: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py createsuperuser --noinput --username admin --email admin@finadvice.com || true
web: gunicorn config.wsgi --workers 2 --threads 2 --bind 0.0.0.0:$PORT
