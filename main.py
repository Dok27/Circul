#!/usr/bin/env python3
"""
Автоматизация входа на WowCircle и перехода к голосованию
"""

import logging
import os
import time
from typing import Optional
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import click
from rich.console import Console
from rich.panel import Panel
from selenium.webdriver.common.action_chains import ActionChains

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования: теперь и в файл, и в консоль
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Лог в файл
file_handler = logging.FileHandler('wowcircle.log', mode='a', encoding='utf-8')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Лог в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

console = Console()


@dataclass
class WowCircleConfig:
    """Конфигурация для работы с WowCircle."""
    base_url: str = "https://cp.wowcircle.net"
    login_url: str = "https://cp.wowcircle.net/login"
    username: Optional[str] = None
    password: Optional[str] = None
    headless: bool = False
    timeout: int = 10


class WowCircleBot:
    """Бот для автоматизации работы с сайтом WowCircle."""
    
    def __init__(self, config: WowCircleConfig):
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        
        # Получаем учетные данные из переменных окружения
        if not self.config.username:
            self.config.username = os.getenv("WOWCIRCLE_USERNAME")
        if not self.config.password:
            self.config.password = os.getenv("WOWCIRCLE_PASSWORD")
    
    def setup_driver(self) -> None:
        """Настройка веб-драйвера."""
        chrome_options = Options()
        
        if self.config.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        
        # Автоматическая установка ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        # Указываем путь к Google Chrome
        chrome_options.binary_location = "/usr/bin/google-chrome-stable"
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, self.config.timeout)
        
        logger.info("Веб-драйвер успешно настроен")
    
    def login(self) -> bool:
        """Вход в систему."""
        if not self.config.username or not self.config.password:
            logger.error("Не указаны учетные данные для входа")
            console.print(Panel(
                "[red]❌ Ошибка: Не указаны учетные данные![/red]\n"
                "Создайте файл .env с вашими данными:\n"
                "WOWCIRCLE_USERNAME=ваш_логин\n"
                "WOWCIRCLE_PASSWORD=ваш_пароль\n\n"
                "Или укажите в командной строке:\n"
                "python3 main.py login -u логин -p пароль --headless",
                title="Настройка учетных данных"
            ))
            return False
        
        try:
            logger.info(f"Переходим на страницу входа: {self.config.login_url}")
            self.driver.get(self.config.login_url)
            time.sleep(3)
            logger.info(f"Текущий URL: {self.driver.current_url}")
            logger.info(f"Заголовок страницы: {self.driver.title}")
            logger.info("Ищем поле для ввода логина...")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "accountName"))
            )
            logger.info("Поле для логина найдено")
            logger.info("Ищем поле для ввода пароля...")
            password_field = self.driver.find_element(By.NAME, "password")
            logger.info("Поле для пароля найдено")
            logger.info("Вводим учетные данные...")
            username_field.clear()
            username_field.send_keys(self.config.username)
            password_field.clear()
            password_field.send_keys(self.config.password)
            logger.info("Ищем кнопку входа...")
            login_button = self.driver.find_element(By.CLASS_NAME, "cp-login-button")
            logger.info("Кнопка входа найдена")
            login_button.click()
            logger.info("Кнопка входа нажата")
            time.sleep(5)
            logger.info(f"URL после входа: {self.driver.current_url}")
            if "dashboard" in self.driver.current_url or "cp.wowcircle.net" in self.driver.current_url:
                logger.info("Успешный вход в систему")
                return True
            else:
                logger.error("Не удалось войти в систему: не перенаправлено на главную страницу. URL: %s", self.driver.current_url)
                self.driver.save_screenshot("login_failed.png")
                logger.info("Скриншот ошибки входа сохранен: login_failed.png")
                return False
        except Exception as e:
            logger.error(f"Ошибка при входе: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            try:
                self.driver.save_screenshot("error_screenshot.png")
                logger.info("Скриншот ошибки сохранен: error_screenshot.png")
            except Exception as se:
                logger.error(f"Ошибка при создании скриншота: {type(se).__name__}: {se}")
            return False
    
    def navigate_to_voting(self) -> bool:
        try:
            logger.info("Ищем раздел голосования...")
            time.sleep(3)
            # Перебираем все div с классом 'button flex-sc', ищем внутри fa-flag
            button_divs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'button') and contains(@class, 'flex-sc')]")
            # Проверяем только первые 15 div
            max_idx = min(len(button_divs), 15)
            for idx in range(max_idx):
                button_div = button_divs[idx]
                try:
                    flag_icon = button_div.find_element(By.XPATH, ".//i[contains(@class, 'fa fa-flag')]")
                    logger.info(f"В {idx+1}-м div найден fa fa-flag, пробуем кликнуть по div через ActionChains")
                    actions = ActionChains(self.driver)
                    actions.move_to_element(button_div).click().perform()
                    time.sleep(1)
                    logger.info(f"Клик по {idx+1}-му div 'button flex-sc' с fa fa-flag выполнен")
                    # Принудительно переходим на страницу голосования, если не произошло редиректа
                    if not self.driver.current_url.endswith("/vote"):
                        self.driver.get("https://cp.wowcircle.net/vote")
                        time.sleep(2)
                        logger.info(f"Принудительный переход на страницу голосования: {self.driver.current_url}")
                    time.sleep(3)
                    logger.info(f"URL страницы голосования: {self.driver.current_url}")
                    logger.info(f"Заголовок страницы: {self.driver.title}")
                    # Новый шаг: ищем table с классом 'table', затем td с классом 'mid pt05' и нужным текстом
                    try:
                        table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'table')]")
                        tds = table.find_elements(By.XPATH, ".//td[contains(@class, 'mid') and contains(@class, 'pt05')]")
                        found = False
                        vote_targets = ["mmovote", "top100arena", "xtremetop100"]
                        for td in tds:
                            td_text = td.text.strip().lower()
                            if td_text in vote_targets:
                                logger.info(f"Найден td с классом 'mid pt05' и текстом '{td_text}', кликаем по нему")
                                td.click()
                                logger.info(f"Клик по td '{td_text}' выполнен")
                                time.sleep(2)
                                found = True
                                break
                        if not found:
                            logger.error("Не найден td с классом 'mid pt05' и нужным текстом (mmovote, top100arena, xtremetop100)")
                            # Переход по пунктам (fallback)
                            voting_selectors = [
                                "//a[contains(text(), 'Голосование')]",
                                "//a[contains(text(), 'Vote')]",
                                "//a[contains(text(), 'Голосовать')]",
                                "//a[contains(@href, 'vote')]",
                                "//a[contains(@href, 'voting')]",
                                "//li/a[contains(text(), 'Голосование')]",
                                "//nav//a[contains(text(), 'Голосование')]"
                            ]
                            for selector in voting_selectors:
                                try:
                                    voting_link = self.driver.find_element(By.XPATH, selector)
                                    logger.info(f"Переход по fallback-ссылке: {selector}")
                                    voting_link.click()
                                    time.sleep(2)
                                    break
                                except Exception as e:
                                    logger.warning(f"Fallback-селектор не сработал: {selector}. Ошибка: {type(e).__name__}: {e}")
                    except Exception as e:
                        logger.error(f"Не удалось найти или кликнуть по td (mmovote, top100arena, xtremetop100): {type(e).__name__}: {e}")
                    return True
                except Exception:
                    pass
            # Если не найдено ни в одном из первых 15 div
            logger.warning("Не найден ни один div с fa fa-flag среди первых 15 button flex-sc")
            # fallback на обычные селекторы по тексту (если нужно)
            voting_selectors = [
                "//a[contains(text(), 'Голосование')]",
                "//a[contains(text(), 'Vote')]",
                "//a[contains(text(), 'Голосовать')]",
                "//a[contains(@href, 'vote')]",
                "//a[contains(@href, 'voting')]",
                "//li/a[contains(text(), 'Голосование')]",
                "//nav//a[contains(text(), 'Голосование')]"
            ]
            voting_link = None
            for selector in voting_selectors:
                try:
                    voting_link = self.driver.find_element(By.XPATH, selector)
                    logger.info(f"Ссылка на голосование найдена: {selector}")
                    break
                except Exception as e:
                    logger.warning(f"Селектор не сработал: {selector}. Ошибка: {type(e).__name__}: {e}")
            if not voting_link:
                logger.error("Ссылка на голосование не найдена ни по одному из селекторов!")
                self.driver.save_screenshot("voting_not_found.png")
                logger.info("Скриншот сохранен: voting_not_found.png")
                return False
            voting_link.click()
            logger.info("Переход к голосованию выполнен")
            time.sleep(3)
            logger.info(f"URL страницы голосования: {self.driver.current_url}")
            logger.info(f"Заголовок страницы: {self.driver.title}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при переходе к голосованию: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            try:
                self.driver.save_screenshot("voting_error.png")
                logger.info("Скриншот ошибки голосования сохранен: voting_error.png")
            except Exception as se:
                logger.error(f"Ошибка при создании скриншота: {type(se).__name__}: {se}")
            return False
    
    def take_screenshot(self, filename: str = "screenshot.png") -> bool:
        """Создание скриншота текущей страницы."""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Скриншот сохранен: {filename}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании скриншота: {e}")
            return False
    
    def close(self) -> None:
        """Закрытие браузера."""
        if self.driver:
            self.driver.quit()
            logger.info("Браузер закрыт")


@click.group()
def cli():
    """CLI для работы с WowCircle."""
    pass


@cli.command()
@click.option("--username", "-u", help="Имя пользователя")
@click.option("--password", "-p", help="Пароль")
@click.option("--headless", is_flag=True, help="Запуск в фоновом режиме")
@click.option("--screenshot", is_flag=True, help="Создать скриншот")
def login(username: str, password: str, headless: bool, screenshot: bool):
    """Вход в систему WowCircle."""
    config = WowCircleConfig(
        username=username,
        password=password,
        headless=headless
    )
    
    bot = WowCircleBot(config)
    
    try:
        bot.setup_driver()
        
        if bot.login():
            console.print(Panel("✅ Успешный вход в систему", style="green"))
            
            if screenshot:
                bot.take_screenshot("after_login.png")
        else:
            console.print(Panel("❌ Ошибка входа в систему", style="red"))
    
    except Exception as e:
        console.print(Panel(f"❌ Ошибка: {e}", style="red"))
        logger.error(f"Ошибка: {e}")
    
    finally:
        bot.close()


@cli.command()
@click.option("--username", "-u", help="Имя пользователя")
@click.option("--password", "-p", help="Пароль")
@click.option("--headless", is_flag=True, help="Запуск в фоновом режиме")
@click.option("--screenshot", is_flag=True, help="Создать скриншот")
def vote(username: str, password: str, headless: bool, screenshot: bool):
    """Вход в систему и переход к голосованию."""
    config = WowCircleConfig(
        username=username,
        password=password,
        headless=headless
    )
    
    bot = WowCircleBot(config)
    
    try:
        bot.setup_driver()
        
        if bot.login():
            console.print(Panel("✅ Успешный вход в систему", style="green"))
            
            if bot.navigate_to_voting():
                console.print(Panel("✅ Успешный переход к голосованию", style="green"))
                
                if screenshot:
                    bot.take_screenshot("voting_page.png")
            else:
                console.print(Panel("❌ Ошибка перехода к голосованию", style="red"))
        else:
            console.print(Panel("❌ Ошибка входа в систему", style="red"))
    
    except Exception as e:
        console.print(Panel(f"❌ Ошибка: {e}", style="red"))
        logger.error(f"Ошибка: {e}")
    
    finally:
        bot.close()


@cli.command()
@click.option("--headless", is_flag=True, help="Запуск в фоновом режиме")
def test_connection(headless: bool):
    """Тест подключения к сайту."""
    config = WowCircleConfig(headless=headless)
    bot = WowCircleBot(config)
    
    try:
        bot.setup_driver()
        bot.driver.get(config.base_url)
        
        console.print(Panel("✅ Подключение к сайту успешно", style="green"))
        console.print(f"URL: {bot.driver.current_url}")
        console.print(f"Заголовок: {bot.driver.title}")
        
    except Exception as e:
        console.print(Panel(f"❌ Ошибка подключения: {e}", style="red"))
        logger.error(f"Ошибка: {e}")
    
    finally:
        bot.close()


def main():
    """Основная функция приложения."""
    console.print(Panel.fit(
        "[bold blue]WowCircle Bot[/bold blue]\n"
        "Автоматизация входа и голосования на cp.wowcircle.net",
        border_style="blue"
    ))
    
    # Если нет аргументов командной строки, показываем справку
    import sys
    if len(sys.argv) == 1:
        cli.main(['--help'])
    else:
        cli()


if __name__ == "__main__":
    main()
