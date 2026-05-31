import gc
import time
import uasyncio as asyncio
import ujson
from machine import Pin
import re
# from assistant.buzzer.melodies import melody
from assistant.buzzer.player import BuzzerPlayer

from assistant.network.wifi import conectar_wifi

from assistant.display.emotion_display import EmotionDisplay
from assistant.display.display_callback import DisplayCallback

from assistant.llm.openai import OpenAI

from assistant.audio.i2s_microphone import (
    INMP441Microphone,
    write_wav_header
)

from assistant.llm.stream_client import (
    OpenAIStreamClient
)

from assistant.audio.config import (
    SAMPLE_RATE
)

from assistant.config import (
    API_KEY,
    SSID,
    PASSWORD
)

melody = [
    ['Star Trek intro', 80, 'NOTE_D4', '-8', 'NOTE_G4', '16', 'NOTE_C5', '-4', 'NOTE_B4', '8', 'NOTE_G4', '-16', 'NOTE_E4', '-16', 'NOTE_A4', '-16', 'NOTE_D5', '2']
    ]

gc.collect()

# =========================================================
# CONFIG
# =========================================================

RECORD_SECONDS = 5
OUTPUT_FILE = "test.wav"
BUTTON_PIN = 4

# =========================================================
# BUTTON
# =========================================================

button = Pin(
    BUTTON_PIN,
    Pin.IN,
    Pin.PULL_UP
)

# =========================================================
# MICROPHONE
# =========================================================

mic = INMP441Microphone(
    sample_rate=SAMPLE_RATE,
    sck_pin=32,
    ws_pin=25,
    sd_pin=33
)

# =========================================================
# CHAT
# =========================================================

async def run_chat(
    ollama,
    prompt,
    callback,
    display,
    player
):

    callback.started_response = False

    display.think()
    display.set_message("Thinking...")

    await asyncio.sleep(1)

    try:

        response = ollama.chat(
            prompt,
            stream=True,
            callback=callback.on_token
        )

        print(response)

        display.idle()

    except Exception as error:

        print("Chat error:", error)

        display.error()
        display.set_message(str(error))

    try:

        await player.play_async(
            melody[0]
        )

    except Exception as error:

        print("Player error:", error)

# =========================================================
# RECORD
# =========================================================

def record_wav(display):

    gc.collect()

    print("Recording...")
    display.think()
    display.set_message("Gravando...")

    total_pcm_bytes = 0

    with open(OUTPUT_FILE, "wb") as f:

        f.seek(44)

        start = time.time()

        while (
            time.time() - start <
            RECORD_SECONDS
        ):

            chunk = mic.read_pcm16()

            if chunk:

                written = f.write(chunk)

                total_pcm_bytes += written

        f.seek(0)

        write_wav_header(
            file=f,
            sample_rate=SAMPLE_RATE,
            pcm_size=total_pcm_bytes
        )

    print("Done.")
    print("PCM bytes:", total_pcm_bytes)
    print("Saved:", OUTPUT_FILE)

# =========================================================
# TRANSCRIBE
# =========================================================

def transcribe_wav():

    gc.collect()

    client = OpenAIStreamClient(
        api_key=API_KEY
    )

    try:

        print("Connecting...")

        client.connect()

        print("Uploading WAV...")

        client.send_wav_file(
            OUTPUT_FILE
        )

        print("Reading response...")

        response = client.read_response()
        match = re.search(
            r'"text"\s*:\s*"([^"]*)"',
            response
        )

        if match:
            text = match.group(1)
        else:
            text = ""

        return text

    finally:

        try:
            client.close()
        except:
            pass

        gc.collect()

# =========================================================
# AUDIO
# =========================================================

async def get_audio(display):

    if button.value() != 0:
        return None

    print("Button pressed")
    display.think()
    display.set_message("Escutando...")
    await asyncio.sleep(1)

    time.sleep_ms(200)

    if button.value() != 0:
        display.idle()
        display.set_message("Como posso Ajudar?")
        return None

    gc.collect()

    record_wav(display)

    gc.collect()

    text = transcribe_wav()

    print("Transcribed:", text)

    while button.value() == 0:
        time.sleep_ms(10)

    gc.collect()
    display.idle()
    display.set_message("Como posso Ajudar?")

    return text

# =========================================================
# MAIN
# =========================================================

async def main():

    display = EmotionDisplay()

    asyncio.create_task(
        display.run()
    )

    player = BuzzerPlayer(
        buzzer_pin=14,
        volume=600
    )

    ollama = OpenAI(
        api_key=API_KEY
    )

    callback = DisplayCallback(
        display
    )

    display.set_message(
        "Assistente iniciado"
    )

    await asyncio.sleep(1)

    display.set_message(
        "Conectando WiFi..."
    )

    await asyncio.sleep(1)

    conectar_wifi(
        SSID,
        PASSWORD
    )

    display.set_message(
        "Como posso ajudar?"
    )

    await asyncio.sleep(1)

    print("Press button to record")

    while True:

        try:

            user_question = await get_audio(display)

            if not user_question:
                await asyncio.sleep_ms(50)
                continue

            callback.buffer = ""

            prompt = (
                "Voce e um mini assistente para um display OLED 128x64. "
                "Sua resposta sera exibida em uma unica linha com texto corrido. "
                "Responda de forma curta, clara e natural. "
                "Nao use acentuacao. "
                "Evite listas, markdown, emojis e quebras de linha. "
                "Use no maximo uma frase curta. "
                f"Pergunta do usuario: {user_question}"
            )

            await run_chat(
                ollama,
                prompt,
                callback,
                display,
                player
            )

            gc.collect()

        except KeyboardInterrupt:

            print("\nEncerrando...")

            display.sleep()

            break

        except Exception as error:

            print("Erro:", error)

            display.error()

            display.set_message(
                "Erro na requisicao"
            )

            await asyncio.sleep(2)

            gc.collect()

    player.stop_song()

    display.stop()

# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())
