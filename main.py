import gc
import network
import re
import time
import uasyncio as asyncio
import ujson
import urequests

from buzzerplayer.melodies import melody
from buzzerplayer.buzzer_player import BuzzerPlayer
from tools.wifi_connector import conectar_wifi
from display.emotion_display import EmotionDisplay
from display.displaycallback import DisplayCallback
from llmclients.openai import OpenAI
from tools.asyncinput import async_input

from config import API_KEY, SSID, PASSWORD

gc.collect()





# =========================================================
# Async Chat Wrapper
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

        display.error()

        display.set_message(str(error))
        
    await player.play_async(melody[0])


# =========================================================
# Main
# =========================================================

# =========================================================
# Main
# =========================================================

async def main():    

    display = EmotionDisplay()

    asyncio.create_task(display.run())
    

    player = BuzzerPlayer(
        buzzer_pin=14,
        volume=600,
    )

    ollama = OpenAI(
        api_key=API_KEY
    )

    callback = DisplayCallback(display)
    
    display.set_message("Assistente iniciado")
    await asyncio.sleep(1)

    
    display.set_message(f"Conectando na rede: {SSID}")
    await asyncio.sleep(1)

    conectar_wifi(
        SSID,
        PASSWORD
    )

    display.set_message("Como posso ajudar?")
    await asyncio.sleep(1)
    
    while True:        

        try:

            user_question = await async_input("\nQual sua pergunta?\n> ")
            user_question = user_question.strip()

            if not user_question:
                continue
            
            # limpa estado anterior
            callback.buffer = ""
  
            prompt = (
                "Você é um mini assistente para um display OLED 128x64. "
                "Sua resposta será exibida em uma única linha com texto corrido. "
                "Responda de forma curta, clara e natural. "
                "Nao use acentuacao, pois o display nao suporta. "
                "Evite textos longos, listas, markdown, emojis e quebras de linha. "
                "Use no maximo 1 frase curta. "
                f"Pergunta do usuario: {user_question}"
            )

            await run_chat(
                ollama,
                prompt,
                callback,
                display,
                player
            )

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
            
        await asyncio.sleep(1)


    player.stop_song()

    display.stop()


# =========================================================
# Start
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())
    