release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn config.wsgi --workers 2 --threads 2 --bind 0.0.0.0:$PORT
