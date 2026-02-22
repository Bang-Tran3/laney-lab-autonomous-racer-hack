FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
RUN pip install --no-cache-dir onnx==1.17.0
RUN pip install --no-cache-dir onnxscript

COPY trainer ./trainer

ENV TRAINER_API_URL="" \
    TRAINER_POLL_SECONDS=30 \
    TRAINER_OUTPUT_ROOT=/tmp/trainer-data

CMD ["sh", "-c", "python -m trainer.worker --api-url \"$TRAINER_API_URL\" --poll-seconds \"$TRAINER_POLL_SECONDS\" --output-root \"$TRAINER_OUTPUT_ROOT\" --set-active"]
