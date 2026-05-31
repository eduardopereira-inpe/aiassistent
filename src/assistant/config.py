
from assistant.utils.dotenv import load_dotenv
from assistant.network.wifi import conectar_wifi



config = load_dotenv("env.txt")

API_KEY = config.get("API_KEY")
SSID = config.get("WIFI_SSID")
PASSWORD = config.get("WIFI_PASS")


conectar_wifi(
    SSID,
    PASSWORD
)

print(f"WIFI-SSID {SSID}")