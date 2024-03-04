import requests
import dotenv, os
import psycopg2
import time
import requests
import base64
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


dotenv.load_dotenv()

RUCAPTCHA_KEY = os.getenv('RUCAPTCHA_KEY')

def parse_job():
    url = f"http://rucaptcha.com/res.php?key={RUCAPTCHA_KEY}&action=getbalance&json=1"
    response = requests.get(url)
    result = response.json()
    if result["status"] == 1:
        print(result["request"])
    else:
        print("Ошибка при получении баланса RuCaptcha")

    balance = result["request"]

    num_captchas = (float(balance) / 44) * 1000

    def get_captcha_image():
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "captcha_image")))
            captcha_element = driver.find_element(By.ID, "captcha_image")

            # Создаем снимок элемента капчи
            captcha_image = captcha_element.screenshot_as_png

            # Кодируем изображение в формате base64
            captcha_image_base64 = base64.b64encode(captcha_image).decode("utf-8")

            return captcha_image_base64
        except TimeoutException:
            raise Exception("Не удалось найти элемент капчи на странице")

    def solve_captcha(RUCAPTCHA_KEY, image_base64):
        url = "http://rucaptcha.com/in.php"
        data = {
            "key": RUCAPTCHA_KEY,
            "method": "base64",
            "body": image_base64,  # Убрал вызов метода decode
            "json": 1
        }
        response = requests.post(url, data=data)  # Используем параметр data вместо params
        if response.text.strip() == "":
            raise Exception("Пустой ответ от сервера RuCaptcha")
        try:
            request_result = response.json()
        except requests.exceptions.JSONDecodeError:
            raise Exception(f"Недопустимый JSON-ответ от сервера RuCaptcha: {response.text}")

        if request_result["status"] == 1:
            return request_result["request"]
        else:
            error_code = request_result["request"]
            if error_code == "ERROR_WRONG_USER_KEY":
                raise Exception("Неверный формат ключа")
            elif error_code == "ERROR_KEY_DOES_NOT_EXIST":
                raise Exception("Ключ не существует")
            elif error_code == "ERROR_ZERO_BALANCE":
                raise Exception("Баланс ключа нулевой")
            elif error_code == "ERROR_PAGEURL":
                raise Exception("Отсутствует URL страницы")
            elif error_code == "ERROR_NO_SLOT_AVAILABLE":
                raise Exception("Нет свободных работников")
            else:
                raise Exception("Неизвестная ошибка RuCaptcha")

    def get_captcha_result(captcha_id):
        url = f"http://rucaptcha.com/res.php?key={RUCAPTCHA_KEY}&action=get&id={captcha_id}&json=1"
        for _ in range(10):  # Пытаемся получить результат до 10 раз
            response = requests.get(url)
            result = response.json()
            if result["status"] == 1:
                return result["request"]
            time.sleep(5)
        raise Exception("Не удалось получить результат капчи")

    def report_bad_captcha(captcha_id):
        url = f"http://rucaptcha.com/res.php?key={RUCAPTCHA_KEY}&action=reportbad&id={captcha_id}&json=1"
        response = requests.get(url)
        result = response.json()
        if result["status"] != 1:
            print("Не удалось отправить жалобу на неверную капчу")

    # Параметры подключения
    params = {
        'user': os.getenv("DATABASE_USER"),
        'password': os.getenv("DATABASE_PASS"),
        'host': os.getenv("DATABASE_HOST"),
        'port': os.getenv("DATABASE_PORT"),
        'database': os.getenv("DATABASE_NAME")
    }

    EMAIL_REPORTER = os.getenv("EMAIL_HOST_USER")
    REPORTER_LAST_NAME = os.getenv("REPORTER_LAST_NAME")
    REPORTER_FIRST_NAME = os.getenv("REPORTER_FIRST_NAME")
    REPORTER_MIDDLE_NAME = os.getenv("REPORTER_MIDDLE_NAME")

    conn = None
    links = []
    try:
        conn = psycopg2.connect(**params)
        print("Подключение успешно.")

        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM main_userwork WHERE status = 'новое'
        ''')

        links = cursor.fetchall()
        # print("USER ID ", links[0])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Подключение закрыто.")

    # Запускаем браузер
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # Запускаем в режиме без головы
    options.add_argument('start-maximized')
    driver = webdriver.Chrome(options=options)

    index = 1

    # Цикл по ссылкам
    for link_object in links:
        link = link_object[1]
        print(f"---\nОбрабатывается ссылка {index} из {len(links)}: {link}")
        success = False
        for main_attempt in range(5):  # Основной внешний цикл
            message = None  # Инициализируем переменную здесь

            try:
                # Заходим на страницу
                driver.get("https://eais.rkn.gov.ru/feedback/")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Type")))

                # Выбираем тип обращения
                select = Select(driver.find_element(By.ID, "Type"))
                select.select_by_value("narcotics")

                # Ставим галочку
                checkbox = driver.find_element(By.CSS_SELECTOR,
                                                'input[type="checkbox"][name="MediaTypeU[]"][value="4"]')
                checkbox.click()
                # Вводим имя, фамилию, отчество
                driver.find_element(By.ID, "ReporterLastName").send_keys(REPORTER_LAST_NAME)
                driver.find_element(By.ID, "ReporterFirstName").send_keys(REPORTER_FIRST_NAME)
                driver.find_element(By.ID, "ReporterMiddleName").send_keys(REPORTER_MIDDLE_NAME)

                # Вводим email
                driver.find_element(By.ID, "ReporterEmail").send_keys(EMAIL_REPORTER)
                checkbox = driver.find_element(By.CSS_SELECTOR,
                                                'input[type="checkbox"][name="SendNotification"][value="true"]')
                checkbox.click()

                # Вводим ссылку
                input_field = driver.find_element(By.ID, "ResourceUrl")
                input_field.send_keys(link)

                captcha_result = None

                for captcha_attempt in range(5):  # Внутренний цикл для повторных попыток ввода капчи
                    if captcha_result is None:
                        captcha_image_base64 = get_captcha_image()  # Получаем изображение капчи в формате base64
                        captcha_id = solve_captcha(RUCAPTCHA_KEY,
                                                    captcha_image_base64)  # Передаем ключ и изображение капчи

                    captcha_result = get_captcha_result(captcha_id)

                captcha_field = driver.find_element(By.ID, "captcha")
                captcha_field.clear()
                captcha_field.send_keys(captcha_result)

                submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")

                submit_button.click()
                time.sleep(3)


                message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "divMsgModalText")))

                if message.text == "Ваше сообщение отправлено. Спасибо":
                    print(f"Сообщение отправлено для ссылки: {link}")
                    success = True
                    break  # Успешно отправлено, переходим к следующей ссылке

                if message.text == "Неверно указан защитный код":
                    report_bad_captcha(captcha_id)
                    captcha_result = None
                    close_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[@class="btn closeBtnBig"]')))
                    close_button.click()
                    # Сбрасываем результат капчи, чтобы получить новую
                    continue  # Повторяем попытку ввода капчи

                if message.text.startswith(
                        "Число обращений с одного адреса превысило допустимое. Повторите отправку позже."):
                    time.sleep(15)
                    close_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[@class="btn closeBtnBig"]')))
                    close_button.click()
                    continue
                if success:
                    try:
                        conn = psycopg2.connect(**params)
                        print("Подключение успешно.")

                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE main_userwork SET
                            status = '%s', 
                            WHERE link = '%s';
                        '''%('проверка', link))

                    except (Exception, psycopg2.DatabaseError) as error:
                        print(error)
                    finally:
                        if conn is not None:
                            conn.close()
                            print("Подключение закрыто.")
                    break
            except Exception as e:
                print(f"Ошибка при обработке ссылки {link}: {str(e)}. Повторяем попытку.")

        index += 1

    # Закрываем браузер
    driver.quit()
