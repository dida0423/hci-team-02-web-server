# hci-team-02-web-server
2025 SNU HCI Spring Semester Team 2

## Contributors:
- <a href="">김다인</a>
- <a href="">오정윤</a>
    

## Project Set-up:

```
poetry install

uvicorn app.main:app --host 0.0.0.0 --port 80
```
with `--reload` for dev

## Preceding keywords for dev:

`CRAWL=true | false` -> If true, flag to crawl news portal. Additionally initializes (or updates) db

`ARTICLE_JSON_PATH=$path | None` -> If path defined, crawl data sourced from JSON (JSON is produced at first crawl). Requires `CRAWL`

`PRESS_ID_JSON_PATH=$path | None` -> Same as above

`DB=true | false` -> If true, initializes (or updates) db without crawling (Redundant if CRAWL set)

## Usage example
### Start Web Server
```
uvicorn app.main:app --host 0.0.0.0 --port 80
```

### Crawling
```
CRAWL=true uvicorn app.main:app --host 0.0.0.0 --port 80
```
### Using Pre-crawled Data (May 23)
Mac
```
ARTICLE_JSON_PATH=article_data.json PRESS_ID_JSON_PATH=press_logo_set.json CRAWL=true uvicorn app.main:app --host 0.0.0.0 --port 80
```
Windows
```
$env:ARTICLE_JSON_PATH="./article_data.json"; $env:PRESS_ID_JSON_PATH="./press_logo_set.json"; $env:CRAWL="true"; uvicorn app.main:app --host 0.0.0.0 --port 80
```