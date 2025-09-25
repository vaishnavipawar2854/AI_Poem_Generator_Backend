FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
       ca-certificates \
       git \
       gcc \
       libssl-dev \
       pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (required by maturin / pyo3 / pydantic-core builds)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

# Install Python dependencies first (cacheable)
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel
RUN pip install --prefer-binary --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
