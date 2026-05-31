import gc
import uasyncio as asyncio

from config import (
    API_KEY,
    SSID,
    PASSWORD
)

from tools.wifi_connector import (
    conectar_wifi
)

from display.emotion_display import (
    EmotionDisplay
)

from llmclients.openai import (
    OpenAI
)

from buzzerplayer.buzzer_player import (
    BuzzerPlayer
)

from assistant_ui import (
    AssistantUI
)

from audio_service import (
    AudioService
)

from chat_service import (
    ChatService
)


class AssistantApplication:

    def __init__(self):

        self.display = (
            EmotionDisplay()
        )

        self.ui = AssistantUI(
            self.display
        )

        self.player = (
            BuzzerPlayer(
                buzzer_pin=14,
                volume=600
            )
        )

        self.ollama = OpenAI(
            api_key=API_KEY
        )

        self.audio = AudioService(
            api_key=API_KEY,
            ui=self.ui
        )

        self.chat = ChatService(
            ollama=self.ollama,
            ui=self.ui,
            player=self.player,
            display=self.display
        )

    async def initialize(self):

        await self.ui.start()

        self.ui.startup()

        await asyncio.sleep(1)

        self.ui.connecting_wifi()

        await asyncio.sleep(1)

        conectar_wifi(
            SSID,
            PASSWORD
        )

        self.ui.idle()

    async def run(self):

        await self.initialize()

        while True:

            try:

                question = (
                    await self.audio.listen()
                )

                if not question:

                    await asyncio.sleep_ms(
                        50
                    )

                    continue

                await self.chat.ask(
                    question
                )

                gc.collect()

            except KeyboardInterrupt:

                break

            except Exception as error:

                print(error)

                self.ui.error(
                    "Erro na requisicao"
                )

                await asyncio.sleep(2)

                gc.collect()

        self.shutdown()

    def shutdown(self):

        try:
            self.player.stop_song()
        except:
            pass

        try:
            self.ui.stop()
        except:
            pass


async def main():

    app = AssistantApplication()

    await app.run()


if __name__ == "__main__":

    asyncio.run(main())