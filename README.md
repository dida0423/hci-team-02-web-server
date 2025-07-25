# hci-team-02-web-server
2025 SNU HCI Spring Semester Team 2
> [!NOTE]
> http://52.78.59.140 에서 최종 프로토타입을 확인할 수 있습니다.
> 해당 프로토타입은 iPhone 15 기준으로 제작되었습니다.

## Contributors:
- <a href="https://github.com/dida0423">김다인</a>
- <a href="https://github.com/nyunn2">오정윤</a>
    

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
### Using Pre-crawled Data (June 16)
```
ARTICLE_JSON_PATH=article_data.json PRESS_ID_JSON_PATH=press_logo_set.json CRAWL=true uvicorn app.main:app --host 0.0.0.0 --port 80
```
