# https://www.geeksforgeeks.org/python-django-google-authentication-and-fetching-mails-from-scratch/

# Temp solution to fix library error.
# We are not going to use this

# path: venv3/lib/python3.8/site-packages/oauth2client/contrib/django_util/__init__.py
Line 233:
    replace from django.core import urlresolvers to
    from django.urls import reverse

Line 411:
    Change urlresolvers.reverse to
    reverse


## Create superuser
python manage.py createsuperuser