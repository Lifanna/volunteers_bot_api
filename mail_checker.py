import imaplib
import email
from email.header import decode_header
import psycopg2
import re
import os, dotenv
import schedule, time
import mail_checker


dotenv.load_dotenv()


def mail_checker_job():
    # Параметры подключения
    params = {
        'user': os.getenv("DATABASE_USER"),
        'password': os.getenv("DATABASE_PASS"),
        'host': os.getenv("DATABASE_HOST"),
        'port': os.getenv("DATABASE_PORT"),
        'database': os.getenv("DATABASE_NAME")
    }

    # Подключение к базе данных
    conn = None
    user_links = []
    try:
        conn = psycopg2.connect(**params)
        print("Подключение успешно.")

        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM main_userwork WHERE status = 'проверка'
        ''')

        user_links = cursor.fetchall()

        print("USER ID ", user_links[0][3])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Подключение закрыто.")

    # Set up your IMAP server details
    imap_server = os.getenv("EMAIL_HOST")
    username = os.getenv("EMAIL_HOST_USER")
    password = os.getenv("EMAIL_HOST_PASSWORD")

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select("inbox")  # You can select other mailboxes like 'spam', 'sent', etc.

    # Search for unread emails
    result, data = mail.search(None, "UNSEEN")

    approved_links = []

    # Iterate through the list of unread emails
    for num in data[0].split():
        # Fetch the email using its unique identifier (UID)
        result, data = mail.fetch(num, "(RFC822)")
        raw_email = data[0][1]

        msg = email.message_from_bytes(raw_email)
        subject = msg["Subject"]

        # Extract the subject
        if subject:
            subject = decode_header(subject)[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
        else:
            subject = "No subject"

        # Extract the sender
        sender = decode_header(msg.get("From"))[0][0]
        if isinstance(sender, bytes):
            sender = sender.decode()

        print("Отправитель письма:", sender)

        # Iterate over the email parts
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                # Decode the text part of the email
                body = part.get_payload(decode=True).decode(part.get_content_charset())
                print("TEXT:", body)

                for link_object in user_links:
                    link = link_object[1]
                    user_id = link_object[3]
                    if link in body:
                        text = body
                        match = re.search(r'Вашему обращению присвоен номер: (\S+)', text)
                        if match:
                            number = match.group(1)

                            if 'подтверждено' in body.lower():
                                approved_links.append({
                                    'link': link,
                                    'status': "подтверждено",
                                    'user_id': user_id,
                                })
                                break
                            else:
                                approved_links.append({
                                    'link': link,
                                    'status': "не подтверждено",
                                    'user_id': user_id,
                                })
                                break

    # Close the connection
    mail.logout()

    try:
        conn = psycopg2.connect(**params)
        print("Подключение успешно.")

        cursor = conn.cursor()
        for approved in approved_links:
            # for link, status in approved.items():
            link = approved.get("link")
            status = approved.get("status")
            user_id = approved.get("user_id")
            print("FFFFF: ", approved.get("user_id"))
            print("Da: ", approved.get("link"), approved.get("status"))
            cursor.execute('''
                UPDATE main_userwork SET
                status = '%s', 
                WHERE link = '%s';
            '''%(status, link))

            if status == 'подтверждено':
                cursor.execute('''
                    IF EXISTS (SELECT * FROM main_userscore WHERE user_id=%s)
                        UPDATE main_userscore SET score = score + 100 WHERE user_id=%s;
                    ELSE
                        INSERT INTO main_userscore (user_id, score) VALUES (%s, 100);
                '''%(user_id, user_id, user_id))

        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Подключение закрыто.")


schedule.every(5).seconds.do(mail_checker.mail_checker_job)

while True:
    schedule.run_pending()
    time.sleep(1)
