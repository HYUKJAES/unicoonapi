FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

# 버전 고정 & UTF-8 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# 기본 패키지 + Python 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl git vim locales tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN locale-gen ko_KR.UTF-8

ENV LANG=ko_KR.UTF-8
ENV LANGUAGE=ko_KR:ko
ENV LC_ALL=ko_KR.UTF-8

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app

# Railway는 반드시 PORT 환경변수를 사용해야 함!
EXPOSE 8080

# CMD에서 포트를 환경변수로 받도록!
CMD ["sh", "-c", "uvicorn app.unicoonapi:app --host 0.0.0.0 --port ${PORT:-8080} --reload"]