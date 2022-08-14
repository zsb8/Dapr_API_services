FROM python:3.8-slim-buster
WORKDIR /usr/src/app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
# CMD [ "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "80" ]
EXPOSE 80
CMD ["python", "main.py"]


