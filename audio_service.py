import gc
import re
import time
import uasyncio as asyncio

from machine import Pin

from audio_transcriber.i2s_microphone import (
    INMP441Microphone,
    write_wav_header
)

from audio_transcriber.config import (
    SAMPLE_RATE
)

from llmclients.openaistreamclient import (
    OpenAIStreamClient
)


class AudioService:

    def __init__(
        self,
        api_key,
        ui,
        button_pin=4,
        record_seconds=5,
        output_file="test.wav"
    ):

        self.api_key = api_key
        self.ui = ui

        self.record_seconds = record_seconds
        self.output_file = output_file

        self.button = Pin(
            button_pin,
            Pin.IN,
            Pin.PULL_UP
        )

        self.mic = INMP441Microphone(
            sample_rate=SAMPLE_RATE,
            sck_pin=32,
            ws_pin=25,
            sd_pin=33
        )

    def record_wav(self):

        gc.collect()

        self.ui.recording()

        total_pcm_bytes = 0

        with open(
            self.output_file,
            "wb"
        ) as f:

            f.seek(44)

            start = time.time()

            while (
                time.time() - start <
                self.record_seconds
            ):

                chunk = self.mic.read_pcm16()

                if chunk:

                    total_pcm_bytes += (
                        f.write(chunk)
                    )

            f.seek(0)

            write_wav_header(
                file=f,
                sample_rate=SAMPLE_RATE,
                pcm_size=total_pcm_bytes
            )

    def transcribe_wav(self):

        gc.collect()

        self.ui.transcribing()

        client = OpenAIStreamClient(
            api_key=self.api_key
        )

        try:

            client.connect()

            client.send_wav_file(
                self.output_file
            )

            response = (
                client.read_response()
            )

            match = re.search(
                r'"text"\s*:\s*"([^"]*)"',
                response
            )

            if match:
                return match.group(1)

            return ""

        finally:

            try:
                client.close()
            except:
                pass

            gc.collect()

    async def listen(self):

        if self.button.value() != 0:
            return None

        self.ui.listening()

        await asyncio.sleep(1)

        await asyncio.sleep_ms(200)

        if self.button.value() != 0:

            self.ui.idle()

            return None

        self.record_wav()

        text = self.transcribe_wav()

        while self.button.value() == 0:
            await asyncio.sleep_ms(10)

        self.ui.idle()

        return text