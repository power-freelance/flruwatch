FROM python:3.6

RUN apt-get update && apt-get install -y \
    jq \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /robot
ADD requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt
ADD . .

CMD ["./wait-for-grid.sh", "python", "main.py"]
