# 🤖 WowCircle Bot - Автоматизация входа и голосования

Бот для автоматизации входа на сайт [cp.wowcircle.net](https://cp.wowcircle.net) и перехода к разделу голосования.

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip3 install -r requirements.txt
```

### 2. Настройка учетных данных
Создайте файл `.env` на основе `env.example`:
```bash
cp env.example .env
nano .env
```

Добавьте ваши реальные данные:
```
WOWCIRCLE_USERNAME=ваш_логин
WOWCIRCLE_PASSWORD=ваш_пароль
```

### 3. Тест подключения
```bash
python3 main.py test-connection --headless
```

### 4. Вход в систему
```bash
python3 main.py login --headless
```

### 5. Вход и переход к голосованию
```bash
python3 main.py vote --headless
```

## 📋 Доступные команды

### Тест подключения
```bash
python3 main.py test-connection --headless
```

### Вход в систему
```bash
# С учетными данными из .env
python3 main.py login --headless

# С указанием данных в командной строке
python3 main.py login -u ваш_логин -p ваш_пароль --headless

# С созданием скриншота
python3 main.py login --headless --screenshot
```

### Вход и переход к голосованию
```bash
# С учетными данными из .env
python3 main.py vote --headless

# С указанием данных в командной строке
python3 main.py vote -u ваш_логин -p ваш_пароль --headless

# С созданием скриншота
python3 main.py vote --headless --screenshot
```

### Справка
```bash
python3 main.py --help
python3 main.py login --help
python3 main.py vote --help
```

## 🔧 Требования

- Python 3.7+
- Google Chrome
- Интернет-соединение

## 📁 Структура файлов

```
circle2/
├── main.py              # Основной файл бота
├── requirements.txt     # Зависимости Python
├── env.example         # Пример файла с переменными окружения
├── README.md           # Документация
└── .env                # Ваши учетные данные (создайте сами)
```

## 🎯 Возможности

- ✅ Автоматический вход в систему
- ✅ Переход к разделу голосования
- ✅ Создание скриншотов для диагностики
- ✅ Подробное логирование
- ✅ Работа в headless режиме
- ✅ Поддержка переменных окружения

## 🐛 Устранение неполадок

### Ошибка "Не указаны учетные данные"
Создайте файл `.env` с вашими данными или укажите их в командной строке.

### Ошибка "Chrome not found"
Убедитесь, что Google Chrome установлен в системе.

### Ошибка "Element not found"
Сайт может измениться. Проверьте скриншоты для диагностики.

## 📝 Примеры использования

### Автоматическое голосование каждый час
```bash
# Добавьте в crontab
0 * * * * cd /path/to/circle2 && python3 main.py vote --headless
```

### Создание скриншота после входа
```bash
python3 main.py login --headless --screenshot
```

## 🎉 Удачной автоматизации! 