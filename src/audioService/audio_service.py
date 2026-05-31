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
        output_file="test.wav",
        mic_ibuf=32768
    ):

        self.api_key = api_key
        self.ui = ui

        self.record_seconds = record_seconds
        self.output_file = output_file
        self.mic_ibuf = mic_ibuf

        self.button = Pin(
            button_pin,
            Pin.IN,
            Pin.PULL_UP
        )

        self.mic = None

        self._ensure_mic()

    def _ensure_mic(self):

        if self.mic is not None:
            return

        self.mic = INMP441Microphone(
            sample_rate=SAMPLE_RATE,
            sck_pin=32,
            ws_pin=25,
            sd_pin=33,
            ibuf=self.mic_ibuf
        )

    def _release_mic(self):

        if self.mic is None:
            return

        try:
            self.mic.close()
        except Exception:
            pass

        self.mic = None
        gc.collect()

    def record_wav(self):

        gc.collect()

        self._ensure_mic()
        mic = self.mic

        if mic is None:
            raise Exception("Microphone unavailable")

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

                chunk = mic.read_pcm16()

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

        last_error = None

        for attempt in range(2):

            client = OpenAIStreamClient(
                api_key=self.api_key
            )

            try:

                print("[audio] transcribe_attempt=", attempt + 1)

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

            except Exception as error:

                last_error = error
                print(
                    "[audio] transcribe_error attempt=",
                    attempt + 1,
                    "error=",
                    error
                )

                gc.collect()

                if attempt == 0:
                    sleep_ms = getattr(
                        time,
                        "sleep_ms",
                        None
                    )
                    try:
                        if sleep_ms:
                            sleep_ms(250)
                        else:
                            time.sleep(0.25)
                    except Exception:
                        time.sleep(0.25)
                    continue

                raise

            finally:

                try:
                    client.close()
                except:
                    pass

                gc.collect()

        if last_error:
            raise last_error

        raise Exception(
            "Transcription failed"
        )

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

        # Free I2S buffers before TLS handshake to reduce ENOMEM risk.
        self._release_mic()

        try:
            text = self.transcribe_wav()
        finally:
            self._ensure_mic()

        while self.button.value() == 0:
            await asyncio.sleep_ms(10)

        self.ui.idle()

        return text
