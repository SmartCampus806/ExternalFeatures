FROM python:3.8-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV OAUTH_METRIKA='y0_AgAAAAA8R1a8AAu0wgAAAAEDaod4AACIItP8e8pPO7vBIASyMAHUr_jVCw'
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]