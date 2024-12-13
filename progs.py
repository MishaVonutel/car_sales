import sys
import traceback
import shutil
import os
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QFormLayout, QTableWidget, QFileDialog, QTableWidgetItem, QTextEdit, QDesktopWidget, QLineEdit, QPushButton, QMessageBox, QComboBox, QGridLayout
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QFrame
from functools import partial
from PyQt5.QtWidgets import QMessageBox
# --- Создание базы данных ---
def create_database():
    conn = sqlite3.connect('car_sales.db')
    cursor = conn.cursor()

    # Таблицы
    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        login TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY,
    car_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY(car_id) REFERENCES cars(id),
    FOREIGN KEY(user_id) REFERENCES clients(id)
    )''')

    try:
        cursor.execute("ALTER TABLE reservations ADD COLUMN status TEXT DEFAULT 'Забронирован'")
    except sqlite3.OperationalError:
        # Если колонка уже существует, ошибка игнорируется
        pass
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY,
        login TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        price INTEGER NOT NULL,
        year INTEGER NOT NULL,
        body_type TEXT NOT NULL,
        color TEXT,
        image_path TEXT NOT NULL,
        description TEXT,
        horsepower INTEGER,
        mileage INTEGER,
        features TEXT
    )''')

    cursor.execute('''INSERT OR IGNORE INTO admins (id, login, password)
    VALUES (1, 'admin', 'admin123')''')

    cursor.execute('''INSERT OR IGNORE INTO cars (id, brand, model, price, year, body_type, image_path, horsepower, mileage, features)
    VALUES 
    (1, 'Toyota', 'Camry', 20000, 2020, 'Sedan', 'toyota_camry.jpg', 150, 30000, 'Leather seats, Sunroof'),
    (2, 'Toyota', 'Corolla', 18000, 2021, 'Sedan', 'toyota_corolla.jpg', 130, 25000, 'Bluetooth, Backup camera'),
    (3, 'Honda', 'Civic', 19000, 2020, 'Sedan', 'honda_civic.jpg', 140, 27000, 'Android Auto, Heated seats'),
    (4, 'Ford', 'Mustang', 35000, 2019, 'Coupe', 'ford_mustang.jpg', 300, 15000, 'V8 engine, Premium sound')''')



    conn.commit()
    conn.close()

# --- Функция для получения пути изображения ---
def get_image_path(image_name):
    image_path = os.path.join(os.getcwd(), 'images', image_name)
    if os.path.exists(image_path):
        return image_path
    else:
        return None

# --- Оформление ---
def apply_stylesheet(widget):
    widget.setStyleSheet("""
        QWidget {
            background-color: #f4f4f4;
        }
        QLabel {
            font-size: 14px;
            color: #333333;
        }
        QLineEdit {
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QComboBox {
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
    """)

# --- Окно авторизации ---
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 400, 250)
        self.setFixedSize(400, 250)

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

        self.layout = QVBoxLayout()

        self.title_label = QLabel("Добро пожаловать!")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.login_input = QLineEdit(self)
        self.login_input.setPlaceholderText("Логин")
        self.layout.addWidget(self.login_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login_user)
        self.layout.addWidget(self.login_button)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.open_register_window)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)
        apply_stylesheet(self)

    def login_user(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля!")
            return

        conn = sqlite3.connect('car_sales.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE login = ? AND password = ?", (login, password))
        admin = cursor.fetchone()

        cursor.execute("SELECT * FROM clients WHERE login = ? AND password = ?", (login, password))
        user = cursor.fetchone()

        conn.close()

        if admin:
            self.close()
            self.admin_window = AdminWindow()
            self.admin_window.show()
        elif user:
            self.close()
            self.user_window = UserWindow(user[0])
            self.user_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def open_register_window(self):
        self.close()
        self.register_window = RegisterWindow()
        self.register_window.show()


# --- Окно администратора ---
class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель администратора")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 400)

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

        self.layout = QVBoxLayout()

        self.title_label = QLabel("Добро пожаловать, Администратор!")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.manage_cars_button = QPushButton("Управление автомобилями")
        self.manage_cars_button.clicked.connect(self.open_manage_cars_window)
        self.layout.addWidget(self.manage_cars_button)

        self.add_car_button = QPushButton("Добавить автомобиль")
        self.add_car_button.clicked.connect(self.open_add_car_window)
        self.layout.addWidget(self.add_car_button)

        self.view_bookings_button = QPushButton("Просмотреть бронирования")
        self.view_bookings_button.clicked.connect(self.view_bookings)
        self.layout.addWidget(self.view_bookings_button)

        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        self.layout.addWidget(self.logout_button)

        self.setLayout(self.layout)
        apply_stylesheet(self)

    def open_manage_cars_window(self):
        """Открывает окно управления автомобилями."""
        self.manage_cars_window = ManageCarsWindow()  # Создаем окно для управления автомобилями
        self.manage_cars_window.show()  # Открываем его

    def open_add_car_window(self):
        self.add_car_window = AddCarWindow()
        self.add_car_window.show()

    def view_bookings(self):
        self.bookings_window = BookingsWindow()
        self.bookings_window.show()

    def logout(self):
        self.close()
        QMessageBox.information(self, "Выход", "Вы успешно вышли из панели администратора.")

    def load_reservations(self):
        # Очистить старые записи
        for i in range(self.reservations_table.count()):
            widget = self.reservations_table.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Подключение к базе данных и получение бронирований
        conn = sqlite3.connect('car_sales.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT clients.full_name, clients.phone, cars.brand, cars.model, cars.image_path, cars.id
            FROM reservations
            JOIN clients ON reservations.user_id = clients.id
            JOIN cars ON reservations.car_id = cars.id
        ''')
        reservations = cursor.fetchall()
        conn.close()

        # Заполнение таблицы
        row = 0
        for reservation in reservations:
            self.add_reservation_row(reservation, row)
            row += 1

    def add_reservation_row(self, reservation, row):
        # Разделяем данные
        full_name, phone, brand, model, image_path, car_id = reservation

        # Создаем виджеты для отображения информации
        full_name_label = QLabel(full_name)
        phone_label = QLabel(phone)
        car_label = QLabel(f"{brand} {model}")
        car_id_label = QLabel(f"ID: {car_id}")

        # Путь к изображению автомобиля
        image_path = get_image_path(image_path)  # Получаем полный путь к изображению
        car_image_label = QLabel()

        if image_path:
            pixmap = QPixmap(image_path)
            # Увеличиваем ширину и пропорционально уменьшаем высоту
            pixmap = pixmap.scaled(300, 200, aspectRatioMode=True)  # Устанавливаем ширину 300px, высота подстраивается
            car_image_label.setPixmap(pixmap)
            car_image_label.setScaledContents(True)

        # Добавляем их в таблицу
        self.reservations_table.addWidget(full_name_label, row, 0)
        self.reservations_table.addWidget(phone_label, row, 1)
        self.reservations_table.addWidget(car_label, row, 2)
        self.reservations_table.addWidget(car_id_label, row, 3)
        self.reservations_table.addWidget(car_image_label, row, 4)

class ManageCarsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Управление автомобилями")
        self.setGeometry(100, 100, 825, 470)  # Уменьшено по высоте и увеличено по ширине
        self.setFixedSize(825, 470)  # Устанавливаем фиксированный размер

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

        self.layout = QVBoxLayout()

        # Заголовок
        self.title_label = QLabel("Управление автомобилями")
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Таблица для отображения автомобилей
        self.cars_table = QTableWidget()
        self.cars_table.setColumnCount(6)
        self.cars_table.setHorizontalHeaderLabels(["Марка", "Модель", "Год", "Цена", "Цвет", "Удалить"])

        # Стиль для заголовков таблицы
        self.cars_table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #007BFF; color: white; font-weight: bold; }")
        self.cars_table.setAlternatingRowColors(True)
        self.cars_table.setStyleSheet("QTableWidget::item:selected { background-color: #d9eaf7; }")

        self.layout.addWidget(self.cars_table)

        # Кнопка "Назад"
        self.back_button = QPushButton("Назад")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;  /* Синяя кнопка */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.back_button.setFixedHeight(40)  # Устанавливаем фиксированную высоту кнопки
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        self.load_cars()

        self.setLayout(self.layout)

    def load_cars(self):
        """Загружает все автомобили из базы данных и отображает их в таблице."""
        try:
            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, brand, model, year, price, color FROM cars")
            cars = cursor.fetchall()
            conn.close()

            self.cars_table.setRowCount(len(cars))  # Устанавливаем количество строк

            for row, car in enumerate(cars):
                # Заполняем таблицу
                self.cars_table.setItem(row, 0, QTableWidgetItem(car[1]))  # Марка
                self.cars_table.setItem(row, 1, QTableWidgetItem(car[2]))  # Модель
                self.cars_table.setItem(row, 2, QTableWidgetItem(str(car[3])))  # Год
                self.cars_table.setItem(row, 3, QTableWidgetItem(str(car[4])))  # Цена

                # Проверка на существование цвета
                color = car[5] if len(car) > 5 else "Не указан"
                self.cars_table.setItem(row, 4, QTableWidgetItem(color))  # Цвет

                # Добавляем кнопку "Удалить" для каждого автомобиля
                delete_button = QPushButton("Удалить")
                delete_button.setStyleSheet(""" 
                    QPushButton {
                        background-color: #FF6347;  /* Красная кнопка */
                        color: white;
                        font-weight: bold;
                        border-radius: 5px;
                        padding: 10px 20px;
                        font-size: 12pt;
                    }
                    QPushButton:hover {
                        background-color: #e04e36;
                    }
                """)
                delete_button.clicked.connect(partial(self.delete_car, car[0]))  # Передаем id автомобиля
                self.cars_table.setCellWidget(row, 5, delete_button)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить автомобили: {e}")

    def delete_car(self, car_id):
        """Удаляет автомобиль из базы данных по ID."""
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы действительно хотите удалить этот автомобиль?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect('car_sales.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "Успех", "Автомобиль успешно удален!")
                self.load_cars()  # Перезагружаем список автомобилей

            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить автомобиль: {e}")

    def go_back(self):
        """Возвращает к родительскому окну"""
        if self.parent():
            self.parent().show()  # Показываем родительское окно
        self.close()  # Закрываем текущее окно


class AddCarWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить автомобиль")
        self.setGeometry(100, 100, 400, 600)  # Увеличим высоту, чтобы влезло больше полей
        self.setFixedSize(400, 600)

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

        self.layout = QVBoxLayout()

        # Заголовок
        self.title_label = QLabel("Добавить автомобиль")
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Используем QFormLayout для лучшего выравнивания
        self.form_layout = QFormLayout()

        # Поля ввода
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("Марка")
        self.form_layout.addRow("Марка:", self.brand_input)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Модель")
        self.form_layout.addRow("Модель:", self.model_input)

        self.body_type_input = QLineEdit()
        self.body_type_input.setPlaceholderText("Тип кузова")
        self.form_layout.addRow("Тип кузова:", self.body_type_input)

        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Год выпуска")
        self.form_layout.addRow("Год выпуска:", self.year_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Цена")
        self.form_layout.addRow("Цена:", self.price_input)

        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("Цвет")
        self.form_layout.addRow("Цвет:", self.color_input)

        self.mileage_input = QLineEdit()
        self.mileage_input.setPlaceholderText("Пробег")
        self.form_layout.addRow("Пробег:", self.mileage_input)

        # Поля для мощности и особенностей
        self.horsepower_input = QLineEdit()
        self.horsepower_input.setPlaceholderText("Мощность")
        self.form_layout.addRow("Мощность:", self.horsepower_input)

        self.features_input = QLineEdit()
        self.features_input.setPlaceholderText("Особенности")
        self.form_layout.addRow("Особенности:", self.features_input)

        # Добавляем поле для ввода описания автомобиля
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Описание")
        self.form_layout.addRow("Описание:", self.description_input)

        self.layout.addLayout(self.form_layout)

        # Загрузка изображения
        self.image_path = None
        self.upload_button = QPushButton("Загрузить изображение")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.upload_button.clicked.connect(self.upload_image)
        self.layout.addWidget(self.upload_button)

        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.save_button.clicked.connect(self.save_car)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def upload_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)", options=options)
        if file_path:
            self.image_path = file_path
            print(f"Загруженный путь к изображению: {self.image_path}")  # Логируем путь
            QMessageBox.information(self, "Загрузка изображения", f"Изображение загружено: {file_path}")

    def save_car(self):
        try:
            # Сохранение данных в базу
            brand = self.brand_input.text()
            model = self.model_input.text()
            body_type = self.body_type_input.text()
            year = self.year_input.text()
            price = self.price_input.text()
            color = self.color_input.text()  # Это цвет
            mileage = self.mileage_input.text()  # Пробег
            description = self.description_input.toPlainText()  # Описание
            features = self.features_input.text()  # Особенности
            horsepower = self.horsepower_input.text()  # Мощность

            # Проверьте, что все поля заполнены
            if not all([brand, model, body_type, year, price, color, mileage, description, features, horsepower, self.image_path]):
                QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
                return

            # Преобразуем типы данных
            price = float(price)  # Цена должна быть числом
            mileage = int(mileage)  # Пробег должен быть числом

            # Мощность и особенности должны быть строками, проверим, что мощность — это число
            if not horsepower.isdigit():  # Проверка, что мощность является числом
                raise ValueError("Мощность должна быть числом!")
            horsepower = int(horsepower)  # Преобразуем мощность в целое число

            # Логируем данные для отладки
            print(f"brand: {brand}, model: {model}, year: {year}, price: {price}, horsepower: {horsepower}, mileage: {mileage}, features: {features}, description: {description}")

            # Проверка пути к изображению
            if not self.image_path or not os.path.exists(self.image_path):
                raise ValueError("Ошибка: Путь к изображению не существует или пустой!")

            print(f"Путь к изображению: {self.image_path}")  # Логируем путь для отладки

            base_path = os.path.dirname(os.path.abspath(__file__))  # Путь к текущему скрипту
            images_dir = os.path.join(base_path, 'images')  # Папка для изображений

            # Убедимся, что папка `images` существует
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)

            # Формируем относительный путь
            image_filename = os.path.basename(self.image_path)  # Имя файла (например, "image.jpg")
            relative_image_path = os.path.join('images', image_filename)  # Путь относительно проекта
            absolute_image_path = os.path.join(images_dir, image_filename)  # Абсолютный путь для копирования

            # Если изображение не было скопировано, копируем его
            if os.path.abspath(self.image_path) != os.path.abspath(absolute_image_path):
                shutil.copyfile(self.image_path, absolute_image_path)

            # Сохраняем данные в базе
            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()

            # Модифицированный запрос с правильными данными
            cursor.execute(''' 
                INSERT INTO cars (brand, model, body_type, year, price, horsepower, mileage, features, description, image_path) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
            ''', (
                brand, model, body_type, year, price, horsepower, mileage, features, description, relative_image_path
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", "Автомобиль добавлен!")
            self.close()

        except Exception as e:
            print("Ошибка при добавлении автомобиля:", str(e))
            print(traceback.format_exc())  # Печать стека вызовов для отладки
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")


class BookingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Бронирования клиентов")
        self.setGeometry(150, 150, 600, 400)
        self.setFixedSize(600, 400)

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

        # Основной макет
        self.layout = QVBoxLayout()

        # Заголовок
        self.title_label = QLabel("Бронирования клиентов")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Прокручиваемая область
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Виджет внутри прокрутки
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout.addWidget(self.scroll_area)

        # Кнопка назад
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.close)
        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)

        # Применение общего стиля
        apply_stylesheet(self)

        # Загрузка данных о бронированиях
        self.load_reservations()

    def load_reservations(self):
        try:
            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()
            cursor.execute(''' 
                SELECT clients.full_name, clients.phone, cars.brand, cars.model, cars.image_path, cars.id
                FROM reservations
                JOIN clients ON reservations.user_id = clients.id
                JOIN cars ON reservations.car_id = cars.id
            ''')
            reservations = cursor.fetchall()
            conn.close()

            for reservation in reservations:
                try:
                    self.add_reservation_row(reservation)
                except Exception as e:
                    print(f"Ошибка при обработке записи: {reservation} - {e}")

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def add_reservation_row(self, reservation):
        full_name, phone, brand, model, image_filename, car_id = reservation

        # Макет для одной строки бронирования
        row_layout = QVBoxLayout()

        # Текстовая информация
        full_name_label = QLabel(f"ФИО: {full_name}")
        phone_label = QLabel(f"Телефон: {phone}")
        car_label = QLabel(f"Автомобиль: {brand} {model}")
        car_id_label = QLabel(f"ID автомобиля: {car_id}")  # Отображаем ID автомобиля

        # Изображение автомобиля
        car_image_label = QLabel()

        # Проверка на пустой или None путь к изображению
        if image_filename:
            # Получаем полный путь к изображению
            image_path = self.get_image_path(image_filename)

            # Проверяем существование файла изображения
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio)
                    car_image_label.setPixmap(pixmap)
                    car_image_label.setAlignment(Qt.AlignCenter)
                    car_image_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
                else:
                    car_image_label.setText("Не удалось загрузить изображение")
            else:
                car_image_label.setText("Изображение не найдено")
        else:
            car_image_label.setText("Изображение не указано")

        # Добавляем все элементы в строку
        row_layout.addWidget(full_name_label)
        row_layout.addWidget(phone_label)
        row_layout.addWidget(car_label)
        row_layout.addWidget(car_id_label)  # Добавляем отображение ID автомобиля
        row_layout.addWidget(car_image_label)

        # Разделитель между записями
        separator = QLabel("—" * 50)
        separator.setAlignment(Qt.AlignCenter)

        # Добавляем строку и разделитель в основной макет
        self.scroll_layout.addLayout(row_layout)
        self.scroll_layout.addWidget(separator)

    def get_image_path(self, image_filename):
        # Проверка на None или пустую строку
        if not image_filename:
            print("Ошибка: image_filename пустой или None")
            return None

        base_path = os.path.dirname(os.path.abspath(__file__))  # Получаем абсолютный путь к каталогу с проектом
        image_path = os.path.join(base_path, 'images', image_filename)  # Формируем полный путь к изображению
        print(f"Путь к изображению: {image_path}")
        return image_path


# --- Окно регистрации ---
class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setGeometry(100, 100, 400, 300)
        self.setFixedSize(400, 300)

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

        self.layout = QVBoxLayout()

        self.title_label = QLabel("Регистрация нового пользователя")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Полное имя")
        self.layout.addWidget(self.name_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setPlaceholderText("Телефон")
        self.layout.addWidget(self.phone_input)

        self.login_input = QLineEdit(self)
        self.login_input.setPlaceholderText("Логин")
        self.layout.addWidget(self.login_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.register_user)
        self.layout.addWidget(self.register_button)

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)
        apply_stylesheet(self)

    def register_user(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        if not all([name, phone, login, password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        conn = sqlite3.connect('car_sales.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO clients (full_name, phone, login, password) VALUES (?, ?, ?, ?)",
                           (name, phone, login, password))
            conn.commit()
            QMessageBox.information(self, "Успех", "Вы успешно зарегистрировались!")
            self.go_back()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Этот логин или телефон уже зарегистрирован!")
        finally:
            conn.close()

    def go_back(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

# --- Окно выбора автомобилей ---
class UserWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Личный кабинет")
        self.setGeometry(100, 100, 900, 700)
        self.setFixedSize(900, 700)

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

        self.layout = QVBoxLayout()

        self.title_label = QLabel("Добро пожаловать в личный кабинет!")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.setup_filter_ui()  # Добавляем фильтры

        self.my_reservations_button = QPushButton("Мои бронирования")
        self.my_reservations_button.clicked.connect(self.view_reservations)
        self.layout.addWidget(self.my_reservations_button)

        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        self.layout.addWidget(self.logout_button)

        self.setLayout(self.layout)
        apply_stylesheet(self)

        self.filter_cars()

    def setup_filter_ui(self):
        """Настраивает интерфейс для фильтрации автомобилей."""
        # Фильтр по марке
        self.brand_combo = QComboBox()
        self.brand_combo.addItem("Выберите марку")
        self.brand_combo.currentTextChanged.connect(self.load_models)
        self.layout.addWidget(self.brand_combo)

        # Фильтр по модели
        self.model_combo = QComboBox()
        self.model_combo.addItem("Выберите модель")
        self.layout.addWidget(self.model_combo)

        # Кнопка фильтрации
        self.filter_button = QPushButton("Фильтровать")
        self.filter_button.clicked.connect(self.filter_cars)
        self.layout.addWidget(self.filter_button)

        # Область прокрутки для карточек автомобилей
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_content = QWidget(self)
        self.scroll_area.setWidget(self.scroll_area_content)

        # Сетка для отображения автомобилей
        self.cars_layout = QGridLayout(self.scroll_area_content)
        self.layout.addWidget(self.scroll_area)

        self.load_brands()  # Загружаем марки автомобилей

    def load_brands(self):
        """Загружаем марки автомобилей из базы данных."""
        try:
            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT brand FROM cars")
            brands = cursor.fetchall()
            conn.close()

            self.brand_combo.addItems([brand[0] for brand in brands])

        except sqlite3.Error as e:
            print(f"Ошибка при загрузке марок: {e}")

    def load_models(self, brand):
        """Загружаем модели автомобилей для выбранной марки."""
        if brand == "Выберите марку":
            self.model_combo.clear()
            self.model_combo.addItem("Выберите модель")
            self.filter_cars()
            return

        try:
            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT model FROM cars WHERE brand = ?", (brand,))
            models = cursor.fetchall()
            conn.close()

            self.model_combo.clear()
            self.model_combo.addItem("Выберите модель")
            self.model_combo.addItems([model[0] for model in models])

        except sqlite3.Error as e:
            print(f"Ошибка при загрузке моделей: {e}")

    def filter_cars(self):
        """Фильтрует автомобили по марке и модели."""
        brand = self.brand_combo.currentText()
        model = self.model_combo.currentText()

        try:
            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()

            query = "SELECT * FROM cars WHERE 1=1"
            params = []

            if brand != "Выберите марку":
                query += " AND brand = ?"
                params.append(brand)

            if model != "Выберите модель":
                query += " AND model = ?"
                params.append(model)

            cursor.execute(query, tuple(params))
            cars = cursor.fetchall()
            conn.close()

            # Очищаем старые карточки
            for i in reversed(range(self.cars_layout.count())):
                widget = self.cars_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Отображаем карточки автомобилей
            row, col = 0, 0
            for car in cars:
                self.add_car_card(car, row, col)
                col += 1
                if col > 3:
                    col = 0
                    row += 1

        except sqlite3.Error as e:
            print(f"Ошибка при фильтрации автомобилей: {e}")

    def add_car_card(self, car, row, col):
        """Добавляет карточку автомобиля."""
        card = QWidget()
        card_layout = QVBoxLayout()

        # Название автомобиля
        car_name = QLabel(f"{car[1]} {car[2]} ({car[4]})")
        car_name.setFont(QFont("Arial", 12, QFont.Bold))
        car_name.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(car_name)

        # Изображение автомобиля
        brand = car[1].lower().replace(" ", "_")
        model = car[2].lower().replace(" ", "_")
        image_path = f"images/{brand}_{model}.jpg"

        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            print(f"Файл изображения не найден: {image_path}")
            pixmap = QPixmap("images/default.jpg").scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        car_image = QLabel()
        car_image.setPixmap(pixmap)
        car_image.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(car_image)

        # Кнопка "Подробнее"
        details_button = QPushButton("Подробнее")
        details_button.clicked.connect(partial(self.show_car_details, car))
        card_layout.addWidget(details_button)

        card.setLayout(card_layout)
        self.cars_layout.addWidget(card, row, col)

    def show_car_details(self, car):
        """Показывает информацию об автомобиле в новом окне."""
        try:
            # Логируем данные для диагностики
            print(f"Данные автомобиля: {car}")  # Выводим данные для проверки

            # Проверка на наличие данных автомобиля
            if not car or len(car) < 10:  # Убедитесь, что количество элементов не меньше 10
                QMessageBox.warning(self, "Ошибка", "Данные автомобиля неполные или отсутствуют.")
                return

            # Попытка преобразования цены в число
            try:
                price = float(car[3])  # Преобразуем строку в число, предполагаем что цена на 4-й позиции (индекс 3)
            except (ValueError, TypeError):
                price = 0.0  # Если преобразование невозможно, устанавливаем цену в 0

            # Форматирование данных для отображения
            car_info = f"""
                <b>Марка:</b> {car[1]}<br>  <!-- Марка автомобиля -->
                <b>Модель:</b> {car[2]}<br>  <!-- Модель автомобиля -->
                <b>Цена:</b> ${price}<br>  <!-- Используем price для корректного отображения -->
                <b>Год выпуска:</b> {car[4]}<br>  <!-- Год выпуска -->
                <b>Тип кузова:</b> {car[5]}<br>  <!-- Тип кузова -->
                <b>Цвет:</b> {car[10] if len(car) > 10 else 'Не указан'}<br>  <!-- Цвет, если есть -->
                <b>Пробег:</b> {car[8]} км<br>  <!-- Пробег -->
                <b>Описание:</b> {car[9]}<br>  <!-- Описание -->
                <b>Мощность:</b> {car[7]} л.с.  <!-- Мощность -->
            """

            # Создание окна с детальной информацией
            details_box = QMessageBox(self)
            details_box.setWindowTitle(f"Информация о {car[1]} {car[2]}")  # Используем марку и модель
            details_box.setTextFormat(Qt.RichText)  # Поддержка HTML форматирования
            details_box.setText(car_info.strip())
            details_box.setIcon(QMessageBox.Information)

            # Добавление кнопки бронирования
            reserve_button = QPushButton("Забронировать")
            details_box.addButton(reserve_button, QMessageBox.AcceptRole)

            reserve_button.clicked.connect(lambda: self.reserve_car(car))
            details_box.exec()

        except IndexError as e:
            QMessageBox.critical(self, "Ошибка", f"Некорректные данные автомобиля: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

    def reserve_car(self, car):
        """Добавляет бронирование в базу данных."""
        try:
            # Проверка наличия таблицы и данных
            if not self.user_id:
                QMessageBox.warning(self, "Ошибка", "Необходимо войти в систему для бронирования.")
                return

            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()

            # Добавление записи в таблицу бронирований
            cursor.execute(
                "INSERT INTO reservations (user_id, car_id, status) VALUES (?, ?, ?)",
                (self.user_id, car[0], "Забронирован")
            )
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", f"Машина {car[1]} {car[2]} успешно забронирована!")

            self.filter_cars()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось забронировать машину: {e}")

    def view_reservations(self):
        reservations_window = ReservationsWindow(self.user_id)
        reservations_window.show()

    def logout(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()

# --- Окно бронирований ---
class ReservationsWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Мои бронирования")
        self.setGeometry(150, 150, 600, 400)
        self.setFixedSize(600, 400)

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

        # Инициализация layout
        self.layout = QVBoxLayout(self)

        self.title_label = QLabel("Мои бронирования")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Область прокрутки для списка бронирований
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_content = QWidget(self)
        self.scroll_area.setWidget(self.scroll_area_content)

        # Сетка для отображения бронирований
        self.reservations_layout = QVBoxLayout(self.scroll_area_content)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

        # Загружаем бронирования
        self.load_reservations()

    def load_reservations(self):
        """Загружает бронирования текущего пользователя из базы данных."""
        try:
            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()

            # Получение бронирований пользователя
            cursor.execute("""
                SELECT r.id, c.brand, c.model, c.year, c.price, r.status
                FROM reservations r
                JOIN cars c ON r.car_id = c.id
                WHERE r.user_id = ?
                ORDER BY r.id DESC
            """, (self.user_id,))
            reservations = cursor.fetchall()

            # Закрываем соединение с базой данных
            conn.close()

            # Очистка старых записей
            for i in reversed(range(self.reservations_layout.count())):
                widget = self.reservations_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Отображение бронирований
            if not reservations:
                no_reservations_label = QLabel("У вас нет бронирований.")
                no_reservations_label.setAlignment(Qt.AlignCenter)
                self.reservations_layout.addWidget(no_reservations_label)
            else:
                for reservation in reservations:
                    self.add_reservation_card(reservation)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить бронирования: {e}")

    def add_reservation_card(self, reservation):
        """Добавляет карточку бронирования."""
        reservation_card = QWidget()
        card_layout = QVBoxLayout()

        # Информация о бронировании
        reservation_info = QLabel(
            f"<b>Бронирование #{reservation[0]}</b><br>"
            f"<b>Марка:</b> {reservation[1]}<br>"
            f"<b>Модель:</b> {reservation[2]}<br>"
            f"<b>Год выпуска:</b> {reservation[3]}<br>"
            f"<b>Цена:</b> ${reservation[4]:,.2f}<br>"
            f"<b>Статус:</b> {reservation[5]}"
        )
        reservation_info.setTextFormat(Qt.RichText)
        card_layout.addWidget(reservation_info)

        # Кнопка отмены бронирования
        cancel_button = QPushButton("Отменить бронирование")
        cancel_button.clicked.connect(lambda: self.cancel_reservation(reservation[0]))
        card_layout.addWidget(cancel_button)

        reservation_card.setLayout(card_layout)
        self.reservations_layout.addWidget(reservation_card)

    def cancel_reservation(self, reservation_id):
        """Отменяет бронирование."""
        try:
            reply = QMessageBox.question(
                self,
                "Подтверждение отмены",
                "Вы уверены, что хотите отменить это бронирование?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                conn = sqlite3.connect('car_sales.db')
                cursor = conn.cursor()

                # Удаление бронирования из базы данных
                cursor.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
                conn.commit()
                conn.close()

                QMessageBox.information(self, "Успех", "Бронирование успешно отменено.")

                # Перезагрузка списка бронирований
                self.load_reservations()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отменить бронирование: {e}")

class CarDetailsWindow(QWidget):
    def __init__(self, car, user_id):
        super().__init__()
        self.car = car
        self.user_id = user_id
        self.setWindowTitle(f"Детали автомобиля: {car[1]} {car[2]}")
        self.setGeometry(300, 200, 500, 600)
        self.setFixedSize(500, 600)

        screen_geometry = QDesktopWidget().availableGeometry()
        screen_center = screen_geometry.center()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_center)
        self.move(window_geometry.topLeft())

        layout = QVBoxLayout()

        # Название автомобиля
        title = QLabel(f"{car[1]} {car[2]} ({car[4]})")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Изображение автомобиля
        try:
            image_path = f"images/{car[6]}"
            pixmap = QPixmap(image_path).scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            layout.addWidget(image_label)
        except Exception as e:
            layout.addWidget(QLabel(f"Ошибка загрузки изображения: {e}"))

        # Подробное описание
        car_info = QLabel(self.format_car_info())
        car_info.setFont(QFont("Arial", 12))
        car_info.setWordWrap(True)
        layout.addWidget(car_info)

        # Кнопка "Забронировать"
        self.reserve_button = QPushButton("Забронировать")
        self.reserve_button.clicked.connect(self.reserve_car)
        layout.addWidget(self.reserve_button)

        self.setLayout(layout)

    def format_car_info(self):
        """Возвращает строку с подробной информацией о машине."""
        try:
            price = float(self.car[5]) if isinstance(self.car[5], (int, float)) else float(self.car[5] or 0)
            return f"""
            Марка: {self.car[1]}
            Модель: {self.car[2]}
            Тип кузова: {self.car[3]}
            Год выпуска: {self.car[4]}
            Цена: ${price:,.2f}
            Цвет: {self.car[8]}
            Пробег: {self.car[9]} км
            Описание: {self.car[7]}
            """
        except Exception as e:
            return f"Ошибка: {e}"

    def reserve_car(self):
        """Добавляет бронирование в базу данных и уведомляет администратора."""
        try:
            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reservations (user_id, car_id, status)
                VALUES (?, ?, ?)
            """, (self.user_id, self.car[0], "Забронирован"))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", "Машина успешно забронирована!")
            self.notify_admin()  # Уведомление администратора
            self.close()  # Закрыть окно после бронирования

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось забронировать машину: {e}")

    def notify_admin(self):
        """Уведомляет администратора о новой брони."""
        try:
            conn = sqlite3.connect('car_sales.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.name, c.brand, c.model, c.year
                FROM reservations r
                JOIN users u ON r.user_id = u.id
                JOIN cars c ON r.car_id = c.id
                WHERE r.car_id = ? AND r.user_id = ?
                ORDER BY r.id DESC LIMIT 1
            """, (self.car[0], self.user_id))
            reservation = cursor.fetchone()
            conn.close()

            if reservation:
                user_name, brand, model, year = reservation
                print(f"Уведомление для администратора: {user_name} забронировал {brand} {model} ({year})")
                QMessageBox.information(self, "Уведомление", f"Администратор уведомлён: {user_name} забронировал {brand} {model} ({year})")
            else:
                print("Не удалось найти детали бронирования для уведомления.")
        except sqlite3.Error as e:
            print(f"Ошибка при уведомлении администратора: {e}")

# --- Основная часть приложения ---
if __name__ == "__main__":
    create_database()  # Создаем базу данных, если она не существует

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
