"""
WSGI config for parcial3Be project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from mangum import Mangum


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parcial3Be.settings')

application = get_wsgi_application()
handler = Mangum(django_app)
