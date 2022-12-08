FROM ubuntu

RUN apt update
RUN apt install -y python3.10
RUN apt install -y python3-pip

COPY requirements.txt .
RUN pip3 install -r requirements.txt

EXPOSE 80
COPY birthday_organizer /var/birthday_organizer
RUN chmod +x /var/birthday_organizer/start.sh
ENTRYPOINT ["/var/birthday_organizer/start.sh"]
