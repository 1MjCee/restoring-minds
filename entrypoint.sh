#!/bin/sh

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if needed
if [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(email='${DJANGO_SUPERUSER_EMAIL}').exists():
    user = User.objects.create_superuser(
        email='${DJANGO_SUPERUSER_EMAIL}',
        password='${DJANGO_SUPERUSER_PASSWORD}',
        first_name='${DJANGO_SUPERUSER_FIRSTNAME}',
        last_name='${DJANGO_SUPERUSER_LASTNAME}'
    )
    print(f'Superuser created with email: {user.email}')
else:
    print('Superuser already exists with this email.')
"
fi

# Execute the command passed to docker
exec "$@"