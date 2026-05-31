from machine import Pin
import time
import gc

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

from assistant.network.wifi import conectar_wifi

from assistant.config import (
    API_KEY,
    SSID,
    PASSWORD
)

# =========================================================
# CONFIG
# =========================================================

RECORD_SECONDS = 5

OUTPUT_FILE = "test.wav"

BUTTON_PIN = 4



print(f"Conectando na rede: {SSID}")

conectar_wifi(
    SSID,
    PASSWORD
)
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
# RECORD FUNCTION
# =========================================================

def record_wav():

    print("Recording...")

    total_pcm_bytes = 0

    with open(OUTPUT_FILE, "wb") as f:

        # reserve WAV header
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

        # write WAV header
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
# TRANSCRIBE FUNCTION
# =========================================================

def transcribe_wav():

    gc.collect()

    client = OpenAIStreamClient(
        api_key=API_KEY
    )

    print("Connecting...")

    client.connect()

    print("Uploading WAV...")

    client.send_wav_file(
        OUTPUT_FILE
    )

    print("Reading response...")

    response = client.read_response()

    print(response)

    client.close()


# =========================================================
# MAIN LOOP
# =========================================================

print("Ready.")
print("Press button to record.")

while True:

    # button pressed
    if button.value() == 0:

        print("Button pressed.")

        # debounce
        time.sleep_ms(200)

        record_wav()

        transcribe_wav()

        print("Ready again.")

        # wait release
        while button.value() == 0:
            time.sleep_ms(10)

    time.sleep_ms(50)