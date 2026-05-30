
from tools.load_dotenv import load_dotenv

config = load_dotenv()

API_KEY = config.get("API_KEY")
SSID = config.get("WIFI_SSID")
PASSWORD = config.get("WIFI_PASS")