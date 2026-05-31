
from tools.load_dotenv import load_dotenv
from tools.wifi_connector import conectar_wifi



config = load_dotenv("env.txt")

API_KEY = config.get("API_KEY")
SSID = config.get("WIFI_SSID")
PASSWORD = config.get("WIFI_PASS")


conectar_wifi(
    SSID,
    PASSWORD
)

print(f"WIFI-SSID {SSID}")