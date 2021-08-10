FROM alanb128/video-streaming:pi-20210717

# Copy balenaCam html/UI elements into the container:
WORKDIR /app/html
COPY . .
WORKDIR /app

ENTRYPOINT ["/bin/bash", "/app/entry.sh"]
