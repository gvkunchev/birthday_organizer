"""
WSGI config for birthday_organizer project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Include Django's project root in pythonpath to ensure working imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'birthday_organizer.settings')

application = get_wsgi_application()
