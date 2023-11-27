FROM archlinux:base

WORKDIR /app

RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm python python-pip ffmpeg && \
        pip install --no-cache-dir python-telegram-bot==13.13 requests TikTokApi aiogram --break-system-packages

COPY . .
CMD ["python", "main.py"]
