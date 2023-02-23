FROM ubuntu

# Install all generic software
RUN apt update
RUN apt install -y python3.10
RUN apt install -y python3-pip
RUN apt install -y apache2
RUN apt install -y apache2-utils
RUN apt install -y libapache2-mod-wsgi-py3
RUN apt install -y redis-server

# Install all python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the Django project
COPY birthday_organizer /var/birthday_organizer

# Prepare Apache
ADD apache.conf /etc/apache2/sites-available/000-default.conf
RUN a2enmod wsgi

# Expose the port and start Apache
EXPOSE 80
