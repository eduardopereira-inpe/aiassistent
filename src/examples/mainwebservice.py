try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from connectivity import connect_to_wifi

from udotenv.dotenv import load_dotenv

from assistant.app.webapp import (
    AssistantWebApp
)


async def main():

    config = load_dotenv(
        "env.txt"
    )

    api_key = config.get(
        "API_KEY"
    )

    ssid = config.get(
        "WIFI_SSID"
    )

    password = config.get(
        "WIFI_PASS"
    )

    print(
        "Conectando na rede:",
        ssid
    )

    connect_to_wifi(
        ssid,
        password
    )

    app = AssistantWebApp()

    await app.run(
        api_key
    )


if __name__ == "__main__":
    asyncio.run(main())