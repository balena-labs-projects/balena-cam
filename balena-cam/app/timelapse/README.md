```
docker build -t timelapse .
docker run --workdir /app -v `pwd`:/app -it timelapse bash
```

Then:

```
python3 -m unittest discover
```