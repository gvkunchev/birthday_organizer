# This is exact copy of django/Dockerfile,
# but it has its paths adjusted to look into the django subdirectory
# and also includes the CMD line at the end to start the tool directly.
# This Dockerfile will start the tool in a single container (useful for render.com)
# while the yaml setup and the README.md explain how to start this in GCP.

FROM ubuntu

# Install all generic software
RUN apt update
RUN apt install -y python3
RUN apt install -y python3-pip
RUN apt install -y apache2
RUN apt install -y apache2-utils
RUN apt install -y libapache2-mod-wsgi-py3
RUN apt install -y redis-server

# Install all python packages
COPY django/requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

# Copy the Django project
COPY django/birthday_organizer /var/birthday_organizer

# Prepare Apache
ADD django/apache.conf /etc/apache2/sites-available/000-default.conf
RUN a2enmod wsgi

# Expose the port and start Apache
EXPOSE 80

CMD ["bash", "/var/birthday_organizer/start", "include-celery"]
