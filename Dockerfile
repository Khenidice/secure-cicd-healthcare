# ---- Stage 1: builder ----
FROM python:3.13-alpine AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Build-time dependencies needed to compile some Python packages
RUN apk add --no-cache --virtual .build-deps \
    gcc musl-dev libffi-dev jpeg-dev zlib-dev cairo-dev pango-dev \
    && python -m pip install --upgrade pip

COPY requirements.txt ./
RUN python -m pip wheel --wheel-dir /wheels -r requirements.txt

# ---- Stage 2: runtime (thin) ----
FROM python:3.13-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user for security (principle of least privilege)
RUN addgroup -S app && adduser -S app -G app

# Runtime system libraries required by the installed packages
RUN apk add --no-cache libpq libffi zlib libc6-compat cairo pango

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

COPY . .

# Non-root runtime user
USER app

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", \
     "--access-logfile", "-", "hospitalmanagement.wsgi:application"]
