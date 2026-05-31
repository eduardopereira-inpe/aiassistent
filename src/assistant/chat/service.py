from assistant.display.display_callback import (
    DisplayCallback
)


class ChatService:

    def __init__(
        self,
        ollama,
        ui,
        player,
        display
    ):

        self.ollama = ollama
        self.ui = ui
        self.player = player

        self.callback = (
            DisplayCallback(
                display
            )
        )

    async def ask(self, question):

        self.callback.buffer = ""
        self.callback.started_response = False

        self.ui.thinking()

        prompt = (
            "Voce e um mini assistente para um display OLED 128x64. "
            "Sua resposta sera exibida em uma unica linha com texto corrido. "
            "Responda de forma curta, clara e natural. "
            "Nao use acentuacao. "
            "Nao use markdown. "
            "Nao use emojis. "
            "Nao use listas. "
            "Use no maximo uma frase curta. "
            f"Pergunta do usuario: {question}"
        )

        self.ollama.chat(
            prompt,
            stream=True,
            callback=self.callback.on_token,
            keep_full_response=False
        )

        try:

            await self.player.play_async(
                [
                    'Star Trek intro',
                    80,
                    'NOTE_D4',
                    '-8',
                    'NOTE_G4',
                    '16',
                    'NOTE_C5',
                    '-4',
                    'NOTE_B4',
                    '8',
                    'NOTE_G4',
                    '-16',
                    'NOTE_E4',
                    '-16',
                    'NOTE_A4',
                    '-16',
                    'NOTE_D5',
                    '2'
                ]
            )

        except:
            pass

        self.ui.idle()
