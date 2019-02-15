FROM python:alpine3.7

COPY app.py /

RUN pip3 install flask

#set local time
RUN apk add tzdata
RUN ln -sf /usr/share/zoneinfo/Europe/Athens /etc/localtime

CMD ["python3", "app.py"]
