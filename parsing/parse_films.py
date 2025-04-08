import time
import re
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium import webdriver
from sqlalchemy.orm import Session

from app.db.crud import (
    get_film_by_title, add_film, get_or_create_genre,
    get_or_create_actor, get_or_create_director, get_or_create_keyword
)
from app.database import SessionLocal

def scroll_and_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(element)).click()

def get_film_links(driver):
    url = "https://letterboxd.com/films/popular/page/2/"
    driver.get(url)
    time.sleep(5)
    print("✅ Страница с популярными фильмами загружена")

    movies = driver.find_elements(By.CSS_SELECTOR, "li.poster-container")[:72]
    films = []

    for movie in movies:
        title_elem = movie.find_element(By.CSS_SELECTOR, "img")
        title_raw = title_elem.get_attribute("alt")

        # Извлекаем год из скобок
        match = re.search(r'\((\d{4})\)', title_raw)
        year = int(match.group(1)) if match else "Unknown"

        # Убираем год из названия фильма
        title = re.sub(r'\s*\(\d{4}\)', '', title_raw).strip()
        
        poster = title_elem.get_attribute("src")
        
        link_elem = movie.find_element(By.CSS_SELECTOR, "a.frame")
        film_link = link_elem.get_attribute("href")
        full_link = f"https://letterboxd.com{film_link}" if film_link.startswith("/film/") else film_link

        films.append({"title": title, "year": year, "link": full_link, "poster": poster})
    
    print(f"✅ Найдено {len(films)} фильмов")
    return films

def extract_keywords(description):
    stop_words = {"the", "a", "in", "on", "of", "and", "to", "is", "for", "with", "this", "that", "by", "as", "it", "at", "from"}
    words = re.findall(r'\b[a-zA-Z]{3,}\b', description.lower())  # Слова от 3 букв
    filtered_words = [word for word in words if word not in stop_words]
    return list(set(filtered_words))

def parse_film_page(driver, film_url, db: Session):
    print(f"🌐 Загружаем страницу: {film_url}")
    driver.get(film_url)
    wait = WebDriverWait(driver, 10)
    time.sleep(5)
    
    try:
        title_raw = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="og:title"]'))).get_attribute("content")

        # Извлекаем год из скобок
        match = re.search(r'\((\d{4})\)', title_raw)
        year = int(match.group(1)) if match else "Unknown"

        # Убираем год из названия фильма
        title = re.sub(r'\s*\(\d{4}\)', '', title_raw).strip()

        description = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]').get_attribute("content")
        director_name = driver.find_element(By.CSS_SELECTOR, 'meta[name="twitter:data1"]').get_attribute("content")
        rating_text = driver.find_element(By.CSS_SELECTOR, 'meta[name="twitter:data2"]').get_attribute("content")
        poster = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']").get_attribute("content")
        
        try:
            rating = float(rating_text.split()[0])
        except ValueError:
            rating = None
        
        try:
            genres_tab = driver.find_element(By.CSS_SELECTOR, "a[data-id='genres']")
            scroll_and_click(driver, genres_tab)
            time.sleep(3)
            genre_elements = driver.find_elements(By.CSS_SELECTOR, "#tab-genres .text-sluglist p a")
            genres = [g.text for g in genre_elements]
        except Exception as e:
            print(f"⚠️ Ошибка парсинга жанров: {e}")
            genres = []
        
        try:
            cast_tab = driver.find_element(By.CSS_SELECTOR, "a[data-id='cast']")
            scroll_and_click(driver, cast_tab)
            time.sleep(3)
            show_all_button = driver.find_element(By.CSS_SELECTOR, "#show-cast-overflow")
            scroll_and_click(driver, show_all_button)
            time.sleep(3)
            actor_elements = driver.find_elements(By.CSS_SELECTOR, "#tab-cast div p a")
            actors = [a.text for a in actor_elements]
        except Exception as e:
            print(f"⚠️ Ошибка парсинга актёров: {e}")
            actors = []
        
        description_keywords = extract_keywords(description)
        
        keyword_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/films/theme/'], a[href*='/films/mini-theme/']")
        page_keywords = [k.text for k in keyword_elements] if keyword_elements else []
        
        all_keywords = list(set(description_keywords + page_keywords))
        print(f"🏷 Все ключевые слова: {all_keywords}")
        
        film = get_film_by_title(db, title)
        if not film:
            film = add_film(db, title, year, description, rating, poster)
            db.add(film)
            db.commit()
            db.refresh(film)
        
        director = get_or_create_director(db, director_name)
        if director not in film.directors:
            film.directors.append(director)

        for genre_name in genres:
            genre = get_or_create_genre(db, genre_name)
            if genre not in film.genres:
                film.genres.append(genre)

        for actor_name in actors:
            actor = get_or_create_actor(db, actor_name)
            if actor not in film.actors:
                film.actors.append(actor)

        for keyword_name in all_keywords:
            keyword = get_or_create_keyword(db, keyword_name)
            if keyword not in film.keywords:
                film.keywords.append(keyword)

        db.add(film)
        db.commit()
        db.refresh(film)
        
        return {
            "title": title,
            "year": year,
            "description": description,
            "director": director_name,
            "rating": rating,
            "poster": poster,
            "genres": genres,
            "actors": actors,
            "keywords": all_keywords,
            "link": film_url
        }
    except Exception as e:
        print(f"❌ Ошибка при парсинге {film_url}: {e}")
        return None

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    db = SessionLocal()

    try:
        films_links = get_film_links(driver)
        parsed_films = []

        for film in films_links:
            print(f"📥 Парсим: {film['title']}")
            film_info = parse_film_page(driver, film["link"], db)
            if film_info:
                parsed_films.append(film_info)

        print("✅ Парсинг завершён!")
    finally:
        driver.quit()
        db.close()

if __name__ == "__main__":
    main()
