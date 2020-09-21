FROM python:3.6-slim

RUN apt-get update && apt-get upgrade -y

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn==20.0.4
RUN pip install --no-cache-dir gunicorn
COPY . .

EXPOSE 8000
CMD ["gunicorn", "-b 0.0.0.0","-w 4", "auth_node:app"]