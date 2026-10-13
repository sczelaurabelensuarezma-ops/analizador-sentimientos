FROM python:3.11-slim

# Hugging Face ejecuta los contenedores con un usuario normal (no root)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /home/user/app

# PyTorch versión CPU (mucho más liviana que la de GPU)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descarga el modelo durante la construcción, para que la app arranque rápido
RUN python -c "from pysentimiento import create_analyzer; create_analyzer(task='sentiment', lang='es')"

COPY --chown=user . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]