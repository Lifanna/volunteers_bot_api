import schedule, time
import parser_sender

schedule.every(5).seconds.do(parser_sender.parse_job)

while True:
    schedule.run_pending()
    time.sleep(1)
