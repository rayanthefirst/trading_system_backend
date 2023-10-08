import logging
import os
from datetime import datetime
from logging import handlers

# Logging basic configurations
# Logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s:  %(message)s"
LOG_DIRECTORY_PATH = "logs"
LOG_FILE_PATH = f"{LOG_DIRECTORY_PATH}/{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.log"
# print(LOG_FILE_PATH)
LOG_DATEFTM = "Y-%m-%d %H:%M:%S"
# "%d-%b-%y %H:%M:%S"  ---> Month name (July)

# =====================================================================
# [CODE LINES] Keep the follwing code lines unchanged!

if not os.path.exists(LOG_FILE_PATH):                                  
    if not os.path.exists(LOG_DIRECTORY_PATH):
        os.mkdir(LOG_DIRECTORY_PATH)


log_format = logging.Formatter(LOG_FORMAT)

log_file_handler = logging.FileHandler(LOG_FILE_PATH)
log_file_handler.setFormatter(log_format)
log_file_handler.setLevel(logging.WARNING)

log_stream_handler = logging.StreamHandler()
log_stream_handler.setFormatter(log_format)
log_stream_handler.setLevel(logging.DEBUG)

email_handler = handlers.SMTPHandler(('smtp.gmail.com', 587), 'rayanthefirst.dev@gmail.com', 'rayanthefirst.dev@gmail.com', 'Trading Platform API Log', ('rayanthefirst.dev@gmail.com', 'nwhzuulhyxsybweu'), secure=())
email_handler.setFormatter(log_format)
email_handler.setLevel(logging.WARNING)

logging.basicConfig(
    datefmt=LOG_DATEFTM, 
    handlers=[log_file_handler, log_stream_handler, email_handler],
    level=logging.WARNING
)