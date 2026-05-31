import uasyncio as asyncio


class AssistantUI:

    def __init__(self, display):

        self.display = display

    async def start(self):

        asyncio.create_task(
            self.display.run()
        )

    def startup(self):

        self.display.idle()
        self.display.set_message(
            "Assistente iniciado"
        )

    def connecting_wifi(self):

        self.display.think()
        self.display.set_message(
            "Conectando WiFi..."
        )

    def idle(self):

        self.display.idle()
        self.display.set_message(
            "Como posso ajudar?"
        )

    def listening(self):

        self.display.think()
        self.display.set_message(
            "Escutando..."
        )

    def recording(self):

        self.display.think()
        self.display.set_message(
            "Gravando..."
        )

    def transcribing(self):

        self.display.think()
        self.display.set_message(
            "Transcrevendo..."
        )

    def thinking(self):

        self.display.think()
        self.display.set_message(
            "Pensando..."
        )

    def error(self, message):

        self.display.error()
        self.display.set_message(
            message
        )

    def stop(self):

        self.display.stop()