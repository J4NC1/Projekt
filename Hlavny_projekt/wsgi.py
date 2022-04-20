"""
WSGI config for Hlavny_projekt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hlavny_projekt.settings')

path = os.path.abspath(os.path.join(__file__, '..', '..'))

if path not in sys.path:
    sys.path.append(path)

application = get_wsgi_application()


