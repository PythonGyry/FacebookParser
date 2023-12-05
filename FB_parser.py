
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Primary
import re
from time import sleep

# add param
from config import cookies_fb
from config import BOT_TOKEN
from config import time_settings

import telebot
bot = telebot.TeleBot(BOT_TOKEN)

class FacebookParser:
    def __init__(self):
        self.should_continue_parsing = True

    def stop_parsing(self):
        self.should_continue_parsing = False

    def parse_fb(self, chat_id, url):
        edge_options = Options()

        # Вимкніть вивід спливаючих повідомлень
        edge_options.add_argument("--disable-notifications")
        
        # Створіть веб-драйвер і використайте опції Edge
        driver = webdriver.Chrome(options=edge_options)
        
        driver.get('https://www.facebook.com/profile.php?id=100095416489054')

        for cookie_name, cookie_value in cookies_fb.items():
            driver.add_cookie({'name': cookie_name, 'value': cookie_value})
        driver.refresh()
        driver.get(url)

        data = []
        last_seen_count = 0
        while self.should_continue_parsing:
            wait = WebDriverWait(driver, 5) # Число очікування елементів на сторінці

            # Використовуйте WebDriverWait для очікування елементів
            try:
                product_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'x3ct3a4')))
            except:
                bot.send_message(chat_id, 'Автомобілів не знайдено 😕\nНатисни старт та введи нові параметри')
                break
            current_count = len(product_cards)

            if current_count > last_seen_count:
                for card in product_cards:
                    if self.should_continue_parsing is False:
                        break
                    card_link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    match = re.search(r'/item/(\d+)/\?', card_link)

                    if match and match.group(1) not in data:
                        item_id = match.group(1)

                        price_elements = card.find_elements(By.CLASS_NAME, 'x193iq5w')
                        img_url = card.find_element(By.TAG_NAME, 'img').get_attribute('src')
                        url_product = card_link

                        # Отримуємо текст з кожного елемента
                        price_texts = [price.text for price in price_elements]
                        result_string = '\n'.join(price_texts)
                        text = f'Інформація:\n{result_string}\n<a href="{url_product}">Посилання на продукт</a>'

                        # Отправка сообщения с HTML-разметкой
                        bot.send_photo(chat_id, img_url, caption=text, parse_mode='HTML')
                        data.append(item_id)
                        sleep(time_settings['Message Delay'])

                # Прокрутити вниз за допомогою JavaScript (можливо, вам потрібно адаптувати це)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(3)

                last_seen_count = current_count
            else:
                bot.send_message(chat_id, 'Виконую перезевантаження сторінки Marketpace 🔄')
                driver.refresh()
                for _ in range(time_settings['Refresh Delay']):
                    if self.should_continue_parsing is False:
                        break
                    sleep(1)
        driver.quit()   