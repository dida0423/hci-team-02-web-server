import requests as _requests
import bs4 as _bs4
from bs4.element import Tag
from typing import cast
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time

def get_dynamic_article_html(url: str) -> BeautifulSoup:
    options = Options()
    options.add_argument("--headless")  # run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="136.0.7103.114").install()), options=options)
    driver.get(url)

    try:
        # Wait for body/article to appear
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Scroll down to trigger lazy image load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # Now re-parse the rendered page
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        driver.quit()
        return soup

    except Exception as e:
        print("Error loading page:", e)
        driver.quit()
        raise 


def parse_html_from_link(url: str) -> _bs4.BeautifulSoup:
    """
    Parses the HTML content and returns a BeautifulSoup object.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    response = _requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    html = response.text
    soup = _bs4.BeautifulSoup(html, 'html.parser')
    return soup


def extract_data(soup: _bs4.BeautifulSoup) -> tuple[list, list]:
    # Find all press companies
    press_companies = soup.find_all('a', class_="rankingnews_box_head nclicks('RBP.rnkpname')")

    press_logo_dict = set()
    press_logo_dict.add(("000", "unknown", "https://static.vecteezy.com/system/resources/previews/022/059/000/non_2x/no-image-available-icon-vector.jpg"))
    count = 1

    for press in press_companies:
        print("Work in progress... (Press)", count)
        count += 1
        if isinstance(press, _bs4.element.Tag):
            press_link = str(press['href'])
            press_soup = parse_html_from_link(press_link)
            
            press_img_tag = press_soup.find('a', class_='press_hd_ci_image')
            # print(press_img_tag)
            if not press_img_tag or not isinstance(press_img_tag, _bs4.element.Tag):
                print(None)
                continue
            img_tag = press_img_tag.find('img')
            logo_img_src = None
            if img_tag and isinstance(img_tag, _bs4.element.Tag):
                if img_tag.has_attr('src'):
                    logo_img_src = img_tag['src']

            press_name_tag = press_soup.find('h3', class_='press_hd_name')
            if not press_name_tag or not isinstance(press_name_tag, _bs4.element.Tag):
                print(None)
                continue
            press_name = press_name_tag.get_text(strip=True)
            print(press_name)

            # print(logo_img_src)
            press_id = press_link[30:33]
 
            press_logo_dict.add((press_id, press_name, logo_img_src))

    list_items = soup.select("ul.rankingnews_list > li")

    news_items = []
    count = 0
    for item in list_items:
        count += 1
        if (count % 5) > 3 or (count % 5) == 0:
            continue
        print("Work in progress... (Article)", count)
        # Ranking number
        ranking_tag = item.select_one("em.list_ranking_num")
        ranking = ranking_tag.get_text(strip=True) if ranking_tag else "?"

        # Title and URL
        title_tag = item.select_one("div.list_content > a.list_title")
        if title_tag:
            title = title_tag.get_text(strip=True)
            url = title_tag.get("href")
        else:
            print("-------------")
            print("No title or URL found for item.")
            print(item)
            print("-------------")
            continue

        press_id = str(url)[33:36]

        article_soup = get_dynamic_article_html(str(url))
        content_tag = article_soup.find('article', id="dic_area")

        if not content_tag or not isinstance(content_tag, _bs4.element.Tag):
            print("-------------")
            print("No content found for article.")
            print(url)
            print("-------------")
            continue


        for tag in content_tag.select("em.img_desc, span.end_photo_org"):
            tag.decompose()  # remove the tag and its contents
        
        content = content_tag.get_text(separator="\n", strip=True)

        published_at_tag = article_soup.select_one("span._ARTICLE_DATE_TIME")

        if published_at_tag and published_at_tag.has_attr("data-date-time"):
            published_at = published_at_tag["data-date-time"]
        else:
            print("No published date found for article.")
            print(url)
            continue

        edited_at_tag = article_soup.select_one("span._ARTICLE_MODIFY_DATE_TIME")
        edited_at = edited_at_tag.get("data-modify-date-time") if edited_at_tag else None
        
        # image_tag = article_soup.find('img', id='img1')

        # print(url)
        # print(image_tag)
        # # print(article_soup)
        # if image_tag and isinstance(image_tag, _bs4.element.Tag):
        #     image_text = image_tag.get("alt")
        #     image_src = image_tag.get("src")
        #     print(image_text)
        #     print(image_src)
        # else:
        #     image_text = None
        #     image_src = None
        
        comment_count_tag = article_soup.select_one("span.u_cbox_count")
        comment_count = comment_count_tag.get_text(strip=True) if comment_count_tag else 0
        if comment_count:
            comment_count = int(comment_count.replace('"', "").replace(",", ""))

        like_count_tag = article_soup.select_one("span._count_num")
        like_count = like_count_tag.get_text(strip=True) if like_count_tag else 0
        if like_count:
            like_count = int(like_count.replace(",", ""))

        genre_tag_results = article_soup.find_all('a', class_="Nitem_link")
        genre = None

        for genre_tag in genre_tag_results:
            if genre_tag and isinstance(genre_tag, _bs4.element.Tag):
                if genre_tag['aria-selected'] == "true":
                    genre = genre_tag.get_text(strip=True)
                    break
                
        author_tag = article_soup.find('em', class_='media_journalistcard_summary_name_text')
        if not author_tag:
            print("-------------")
            print("No author found for article.")
            print(url)
            print("-------------")
            continue

        
        author_name = str(author_tag.get_text(strip=True)).split(" 기자")[0]
        a_tag = author_tag.find_parent('a')
        if a_tag and isinstance(a_tag, _bs4.element.Tag):
            author_url = a_tag.get("href")
            author_id = str(author_url)[39:]
            press_id = str(author_url)[35:38]
        else:
            print("-------------")
            print("No author URL found for article.")
            print(a_tag)
            print(url)
            print("-------------")
            continue

        if isinstance(like_count, int) and isinstance(comment_count, int):
            activity_score = like_count + comment_count * 2
            print(f"Activity Score: {activity_score}")
        else:
            print("Error: Like or comment count is not an integer.")
            activity_score = 0

        news_items.append({
            "ranking": ranking,
            "title": title,
            "url": url,
            "content": content,
            "published_at": published_at,
            "edited_at": edited_at,
            # "image_text": image_text,
            # "image_src": image_src,
            "genre": genre,
            "activity_score": activity_score,
            "author_name": author_name,
            "author_id": author_id,
            "press_id": press_id
        })

    
    # print(json.dumps(press_list, sort_keys=True, indent=4, ensure_ascii=False))
    # print(f"Total press companies: {len(press_list)}")

    # Remove duplicates based on URL
    unique_articles = {article['url']: article for article in news_items}.values()

    # Convert to a list
    news_list = list(unique_articles)
    
    return news_list, list(press_logo_dict)

def crawl():
    soup = parse_html_from_link('https://news.naver.com/main/ranking/popularDay.naver')
    data = extract_data(soup)
    return data

# ls = crawl()
# print(json.dumps(ls, sort_keys=True, indent=4, ensure_ascii=False))
# print(f"Total articles: {len(ls)}")