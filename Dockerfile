FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

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
COPY ./app /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "unicoonapi:app", "--host", "0.0.0.0", "--port", "8090", "--reload"]