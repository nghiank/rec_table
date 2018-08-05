"""
WSGI config for turk project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

#sys.path.insert(0, '/opt/python/current/app/web/turk') --> This is for elastic beanstalk
sys.path.insert(0, '/home/ubuntu/rec_table/web/turk') 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turk.settings_prod")

application = get_wsgi_application()
