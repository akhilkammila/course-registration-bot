FROM python:alpine3.17

# install python dependencies
RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# run
COPY . .
ENTRYPOINT ["python3", "main.py"]