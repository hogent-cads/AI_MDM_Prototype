import logging
import logging.handlers


PATH = "./rule_finder.log"
logger = logging.getLogger("aimdm")
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(PATH, mode='a')
formatter = logging.Formatter(
    'RuleFinder | {funcName} | {asctime} | {levelname:8s} | {message}',
    datefmt='%Y-%m-%d %H:%M:%S', style='{')
handler.setFormatter(formatter)

logger.addHandler(handler)

configuration = {
    # Data profiling report will be stored in the following directory under "reports"
    "WWW_ROOT": "/usr/share/nginx/html",
    "HANDLER_TYPE": "Remote", # "Local" or "Remote
    "remote_url": '127.0.0.1',
    "remote_port": '8000',
    "WEBSOCKET_SERVER_URL": "wss://wsauthserver.supergroup.ai",
    "WEBSOCKET_SERVER_PORT": 80
}