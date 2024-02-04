class GmailThread(QThread):
    progress_signal = Signal(str)
    progress_bar_signal = Signal(int)

    def run(self):
        import imaplib
        import re
        from docx import Document

        success_count = 0
        mail = None
        max_attempts = 5
        attempt_count = 0
        while not mail and attempt_count < max_attempts:
            try:
                attempt_count += 1
                mail = imaplib.IMAP4_SSL('imap.mail.ru')
                mail.login('artem-rkn@mail.ru', 'EtxLZ26J5UGwyS1S4iHR')
                # mail = imaplib.IMAP4_SSL('imap.gmail.com')
                # mail.login('xdmaik.xdfox@gmail.com', 'rjxwyhubjhvkhmlo')
            except TimeoutError:
                pass
        if not mail:
            self.progress_signal.emit(f'Could not connect to Gmail after {max_attempts} attempts. Exiting...')
            return

        # mail.select('rkn1')
        mail.select('inbox ')

        with open('links.txt', 'r') as f:
            links = [line.strip() for line in f]

        result, data = mail.uid('search', None, "ALL")
        email_ids = data[0].split()

        total_count = len(email_ids)
        for i, email_id in enumerate(email_ids):
            progress_message = f'Обработка письма {i + 1} из {total_count}...'
            self.progress_signal.emit(progress_message)
            result, email_data = mail.uid('fetch', email_id, '(BODY[TEXT])')
            raw_email = email_data[0][1].decode('utf-8')

            for link in links:
                if link in raw_email:
                    text = raw_email
                    match = re.search(r'Вашему обращению присвоен номер: (\S+)', text)
                    if match:
                        number = match.group(1)
                        doc = Document('screenshots.docx')
                        table = doc.tables[0]

                        for row in table.rows:
                            if link in row.cells[1].text:
                                if 'Подтверждено' not in row.cells[3].text:
                                    row.cells[3].text = 'Подтверждено\n' + number
                                    success_count += 1
                                    doc.save('screenshots.docx')
                                break

            progress_percentage = int((i + 1) / total_count * 100)
            self.progress_bar_signal.emit(progress_percentage)

        mail.close()
        mail.logout()
        self.progress_signal.emit(f'Найдено {total_count} номеров. Из них успешно добавлено в таблицу: {success_count}')
