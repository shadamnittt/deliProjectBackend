# import time
# import re
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium import webdriver
# from sqlalchemy.orm import Session

# from db.crud import (
#     get_film_by_title, add_film, get_or_create_genre,
#     get_or_create_actor, get_or_create_director, get_or_create_keyword
# )

# from selenium.webdriver.chrome.options import Options

# chrome_options = Options()
# chrome_options.add_argument("--dns-prefetch-disable")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-gpu")

# driver = webdriver.Chrome(options=chrome_options)

# from database import SessionLocal  # Файл с подключением к БД


# STOP_WORDS = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "with", "at", "by", "from", "about", "as", "for"} 


# def show_alert(driver, message):
#     """Функция для отображения уведомлений в браузере."""
#     driver.execute_script(f"alert('{message}');")
#     time.sleep(1)


# def get_film_links(driver):
#     url = "https://letterboxd.com/films/popular/"
#     driver.get(url)
#     time.sleep(5)
    
#     print("✅ Страница с популярными фильмами загружена")
#     show_alert(driver, "Страница с популярными фильмами загружена")

#     movies = driver.find_elements(By.CSS_SELECTOR, "li.poster-container")[:20]
#     films = []

#     for movie in movies:
#         title_elem = movie.find_element(By.CSS_SELECTOR, "img")
#         title = title_elem.get_attribute("alt")
#         poster = title_elem.get_attribute("src")

#         link_elem = movie.find_element(By.CSS_SELECTOR, "a.frame")
#         film_link = link_elem.get_attribute("href")
#         full_link = f"https://letterboxd.com{film_link}" if film_link.startswith("/film/") else film_link

#         year_elem = movie.find_element(By.CSS_SELECTOR, "span")
#         year = year_elem.text if year_elem else "Unknown"

#         films.append({"title": title, "year": year, "link": full_link, "poster": poster})

#     print(f"✅ Найдено {len(films)} фильмов")
#     show_alert(driver, f"Найдено {len(films)} фильмов")
#     return films


# def extract_keywords(description):
#     words = re.findall(r"\b[a-zA-Z']+\b", description.lower())
#     keywords = {word for word in words if word not in STOP_WORDS and len(word) > 2}
#     return list(keywords)


# def parse_film_page(driver, film_url, db: Session):
#     print(f"🌐 Загружаем страницу: {film_url}")
#     show_alert(driver, f"Загружаем страницу: {film_url}")

#     driver.get(film_url)
#     wait = WebDriverWait(driver, 10)
#     time.sleep(5)

#     try:
#         title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[property="og:title"]'))).get_attribute("content")

#         if get_film_by_title(db, title):
#             print(f"⚠️ Фильм '{title}' уже есть в базе. Пропускаем.")
#             show_alert(driver, f"Фильм '{title}' уже есть в базе. Пропускаем.")
#             return None

#         description = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]').get_attribute("content")
#         director_name = driver.find_element(By.CSS_SELECTOR, 'meta[name="twitter:data1"]').get_attribute("content")
#         rating_text = driver.find_element(By.CSS_SELECTOR, 'meta[name="twitter:data2"]').get_attribute("content")
#         poster = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']").get_attribute("content")
#         year = title.split("(")[-1].strip(")") if "(" in title else "Unknown"

#         rating = None
#         try:
#             rating = float(rating_text.split()[0])  
#         except ValueError:
#             print(f"⚠️ Не удалось преобразовать рейтинг: {rating_text}")

#         genres, actors, keywords = [], [], extract_keywords(description)

#         genres_link = driver.find_element(By.CSS_SELECTOR, "a[data-id='genres']").get_attribute("href")
#         driver.get(f"https://letterboxd.com{genres_link}")
#         time.sleep(3)

#         genre_elements = driver.find_elements(By.CSS_SELECTOR, "a.text-slug[href*='/films/genre/']")
#         genres = [g.text for g in genre_elements] if genre_elements else ["Unknown"]

#         driver.get(film_url)  
#         time.sleep(3)

#         try:
#             show_all_cast_button = driver.find_element(By.ID, "show-cast-overflow")
#             show_all_cast_button.click()
#             time.sleep(3)
#         except:
#             print("⚠️ Кнопка 'Show All' для актеров не найдена.")

#         actor_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/actor/']")
#         actors = [a.text for a in actor_elements] if actor_elements else ["Unknown"]

#         print(f"🎬 {title} ({year}) | 🎭 {', '.join(actors)} | 🎥 {', '.join(genres)} | 🏷 {', '.join(keywords)}")
#         show_alert(driver, f"Обработан фильм: {title}")

#         film = add_film(db, title, year, description, rating, poster)
#         db.add(film)  
#         db.commit()
#         db.refresh(film)  

#         director = get_or_create_director(db, director_name)
#         film.directors.append(director)

#         for genre_name in genres:
#             genre = get_or_create_genre(db, genre_name)
#             film.genres.append(genre)

#         for actor_name in actors:
#             actor = get_or_create_actor(db, actor_name)
#             film.actors.append(actor)

#         for keyword_name in keywords:
#             keyword = get_or_create_keyword(db, keyword_name)
#             film.keywords.append(keyword)

#         db.add(film)  
#         db.commit()
#         db.refresh(film)

#         return {
#             "title": title,
#             "year": year,
#             "description": description,
#             "director": director_name,
#             "rating": rating,
#             "poster": poster,
#             "genres": ", ".join(genres),
#             "actors": ", ".join(actors),
#             "keywords": ", ".join(keywords),
#             "link": film_url
#         }

#     except Exception as e:
#         print(f"❌ Ошибка при парсинге {film_url}: {e}")
#         show_alert(driver, f"Ошибка при парсинге: {e}")
#         return None


# def main():
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")  # Без GUI, но уведомления не работают в headless режиме!
#     driver = webdriver.Chrome(options=options)

#     db = SessionLocal()

#     try:
#         films_links = get_film_links(driver)
#         parsed_films = []

#         for film in films_links:
#             print(f"📥 Парсим: {film['title']}")
#             show_alert(driver, f"Парсим: {film['title']}")
#             film_info = parse_film_page(driver, film["link"], db)
#             if film_info:
#                 parsed_films.append(film_info)

#         print("✅ Парсинг завершён!")
#         show_alert(driver, "Парсинг завершён!")

#     finally:
#         driver.quit()
#         db.close()


# if __name__ == "__main__":
#     main()
