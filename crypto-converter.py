from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import requests
import os


# --- Функции ---

def update_crypto_label(event):
    """Обновляет название выбранной криптовалюты на русском языке"""
    code = crypto_combobox.get()
    name = crypto_cur.get(code, "")
    crypto_label.config(text=name)


def update_currency_label(event):
    """Обновляет название обычной валюты на русском языке"""
    code = currency_combobox.get()
    name = cur.get(code, "")
    currency_label.config(text=name)


def exchange():
    """Запрашивает курс с API и выполняет конвертацию"""
    crypto_currency = crypto_combobox.get()
    currency = currency_combobox.get()
    amount_str = amount_entry.get().strip()  # Берем введенное количество

    # Проверка на заполненность полей выбора
    if not crypto_currency or not currency:
        mb.showwarning('Внимание!', 'Выберите обе валюты из списков!')
        return

    # Валидация введенного количества (по умолчанию 1)
    if not amount_str:
        amount = 1.0
    else:
        try:
            amount = float(amount_str.replace(',', '.'))  # заменяем запятую на точку, если ввели дробь
            if amount <= 0:
                raise ValueError
        except ValueError:
            mb.showerror('Ошибка ввода', 'Введите корректное положительное число для количества!')
            return

    # Очищаем лейбл перед новым запросом (показываем статус загрузки)
    result_label.config(text='Загрузка курса...', fg='gray')
    window.update_idletasks()

    try:
        # Отправляем запрос к API CoinGecko
        response = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_currency}&vs_currencies={currency}',
            timeout=10  # ограничиваем время ожидания ответа, чтобы приложение не зависло намертво
        )
        response.raise_for_status()
        data = response.json()

        if crypto_currency in data and currency in data[crypto_currency]:
            exchange_rate = data[crypto_currency][currency]
            total_sum = exchange_rate * amount  # Считаем итоговую стоимость

            crypto_name = crypto_cur[crypto_currency]
            currency_name = cur[currency]

            # Форматируем вывод результата
            result_text = f'Курс: 1 {crypto_name} = {exchange_rate} {currency_name}\n'
            if amount != 1.0:
                result_text += f'Итого за {amount} {crypto_name}: {total_sum:.2f} {currency_name}'

            result_label.config(text=result_text, font=('Arial', 12, 'bold'), fg='green')
        else:
            mb.showerror('Ошибка', f'Валюта или курс не найдены в базе данных API.')
            result_label.config(text='')
    except requests.exceptions.RequestException as req_err:
        mb.showerror('Ошибка сети', f'Не удалось связаться с сервером:\n{req_err}')
        result_label.config(text='')
    except Exception as e:
        mb.showerror('Ошибка', f'Произошла непредвиденная ошибка: {e}')
        result_label.config(text='')


# --- Справочники данных ---

cur = {
    'eur': 'Евро',
    'rub': 'Российский рубль',
    'usd': 'Доллар США'
}

crypto_cur = {
    'bitcoin': 'Биткоин',
    'cardano': 'Кардано',
    'ethereum': 'Эфириум',
    'litecoin': 'Лайткоин',
    'ripple': 'Рипл'
}

# --- Инициализация окна интерфейса ---

window = Tk()
window.title('Курсы обмена криптовалюты')
window.geometry('380x420')  # Немного увеличили высоту под новое поле ввода

# Автоматическое определение пути к иконке, чтобы не было ошибок путей
current_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(current_dir, 'img.ico')
if os.path.exists(icon_path):
    window.iconbitmap(icon_path)

# --- Элементы UI ---

# 1. Выбор КРИПТОВАЛЮТЫ (Сначала выбираем её)
Label(text='Выберите криптовалюту:', font=('Arial', 10, 'bold')).pack(pady=(15, 2))
crypto_combobox = ttk.Combobox(values=list(crypto_cur.keys()),
                               state="readonly")  # state="readonly" запрещает ручной ввод левого текста
crypto_combobox.pack(pady=5)
crypto_combobox.bind('<<ComboboxSelected>>', update_crypto_label)

crypto_label = ttk.Label(font=('Arial', 9, 'italic'))
crypto_label.pack(pady=(0, 10))

# 2. Выбор ОБЫЧНОЙ ВАЛЮТЫ
Label(text='Выберите валюту:', font=('Arial', 10, 'bold')).pack(pady=2)
currency_combobox = ttk.Combobox(values=list(cur.keys()), state="readonly")
currency_combobox.pack(pady=5)
currency_combobox.bind('<<ComboboxSelected>>', update_currency_label)

currency_label = ttk.Label(font=('Arial', 9, 'italic'))
currency_label.pack(pady=(0, 10))

# 3. Поле ввода количества
Label(text='Количество криптовалюты (необязательно, дефолт 1):', font=('Arial', 9)).pack(pady=2)
amount_entry = ttk.Entry()
amount_entry.pack(pady=5)

# 4. Кнопка расчета
ttk.Button(text='Конвертировать', command=exchange).pack(pady=15)

# 5. Поле вывода результата
result_label = Label(text='', justify=CENTER)
result_label.pack(pady=10)

window.mainloop()
