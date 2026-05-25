import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breathe_esg.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'password123'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print('superuser created')
else:
    print('superuser already exists')
