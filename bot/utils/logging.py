import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from configreader import config


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger.opt(depth=6, exception=record.exc_info).log(record.levelname, record.getMessage())


file_log = logging.FileHandler("bot/utils/logs/Log.log", encoding="utf-8")
# console_out = logging.StreamHandler()
logger.add(
    "bot/utils/misc/logs/debug.log",
    format="{time} {level} {message}",
    level="INFO",
)
logging.basicConfig(
    handlers=(file_log, InterceptHandler()),
    format="%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    datefmt="%m.%d.%Y %H:%M:%S",
    level=logging.INFO,
)


def email_sender_error_logs(error_text):
    """Сервис по отправке логов ошибок на почту разраба"""
    text = f"Помилка в боті Poster Bot\n\n{error_text}"
    title = f"Помилка в боті Poster Bot"
    sender = config.log_sender_email
    receiver = config.log_receiver_email
    password = config.log_sender_email_pwd

    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = sender
    message["To"] = receiver

    part = MIMEText(text, "html")
    message.attach(part)
    log_file_path = os.path.join("utils", "misc", "Logs", "Log.log")
    if os.path.exists(log_file_path):
        with open(log_file_path, "rb") as file:
            part = MIMEApplication(file.read())
            part.add_header("Content-Disposition", "attachment", filename="Log.log")

            message.attach(part)

    server = smtplib.SMTP(config.log_email_service_ip, config.log_email_service_port)
    server.starttls()

    try:
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
        server.quit()
        logging.info("Succsess sended logs")
    except Exception as e:
        logging.error(e)
    except ConnectionRefusedError as e:
        logging.error("Ошибка подключения:", e)
