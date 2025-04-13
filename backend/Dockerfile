FROM python:3.10-alpine

WORKDIR /backend

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

ENV PYTHONPATH="$PYTHONPATH:/backend/hmtracker"

COPY ./hmtracker /backend/hmtracker

CMD ["fastapi", "run", "hmtracker/api/server.py", "--port", "1010"]
