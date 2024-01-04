FROM python:alpine3.17

# install python dependencies
RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# run
COPY main.py .
COPY postmarkcreds.py .
COPY wait-for-it.sh .
RUN chmod +x /wait-for-it.sh
CMD ["python3", "main.py"]