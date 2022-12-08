#!/bin/bash

# TODO: Once a server is present, the last line should not be here
#       Also, not sure about the migrations - there should be a better way to handle this

python3 /var/birthday_organizer/manage.py makemigrations
python3 /var/birthday_organizer/manage.py migrate

python3 /var/birthday_organizer/manage.py runserver 0.0.0.0:80