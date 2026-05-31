# MicroPython AI Assistant

A modular, reusable MicroPython assistant library for ESP32-class boards.

This project captures audio from an INMP441 microphone, sends speech for transcription, generates an LLM response, and renders status/output on an OLED display with optional buzzer feedback.

The codebase is organized as a library-first package under `src/assistant`, with runnable scripts in `src/examples`.

## Features

- Domain-based package structure (`assistant.*`) designed for reuse.
- End-to-end voice assistant flow:
	- Button press -> record WAV -> transcribe -> chat completion -> OLED output.
- OLED expression/status UI with message internationalization support (`messages.json`).
- MicroPython-focused network/memory diagnostics in OpenAI clients.
- Retry/fallback logic for common ESP32 network/TLS instability scenarios.
- Initial `manifest.py` for future `mip`-based distribution.

## Project Layout

```text
src/
	assistant/
		__init__.py
		config.py
		app/
			__init__.py
			application.py
		ui/
			__init__.py
			ui.py
			messages.json
		audio/
			__init__.py
			service.py
			transcriber.py
			i2s_microphone.py
			wav.py
			interfaces.py
			config.py
		chat/
			__init__.py
			service.py
		display/
			__init__.py
			emotion_display.py
			display_callback.py
			ssd1306.py
		llm/
			__init__.py
			openai.py
			ollama.py
			stream_client.py
		buzzer/
			__init__.py
			player.py
			melodies.py
			notes.py
		network/
			__init__.py
			wifi.py
		utils/
			__init__.py
			dotenv.py
			asyncinput.py
	examples/
		main.py
		main_test.py
		main_old.py
		button_demo.py

manifest.py
```

## Requirements

### Hardware

- ESP32-compatible board running MicroPython.
- INMP441 I2S microphone.
- SSD1306 OLED display (I2C).
- Push button.
- Optional passive buzzer.

### Software

- MicroPython firmware compatible with:
	- `uasyncio`
	- `urequests`
	- `ujson`
	- `machine`, `network`, `ssl`, `socket`

## Configuration

Create an `env.txt` file on the device filesystem (same root where scripts run) with:

```text
API_KEY=your_openai_api_key
WIFI_SSID=your_wifi_name
WIFI_PASS=your_wifi_password
```

`assistant.config` reads this file and exposes:

- `API_KEY`
- `SSID`
- `PASSWORD`

## Running Examples

### Main assistant app

Run:

```python
import uasyncio as asyncio
from examples.main import main

asyncio.run(main())
```

Or set `src/examples/main.py` as your board entrypoint.

### Minimal button transcription demo

Run:

```python
import examples.button_demo
```

This script records audio when the button is pressed, uploads WAV to transcription, and prints the raw response.

## Library Entry Points

- Application orchestration: `assistant.app.application.AssistantApplication`
- UI controller: `assistant.ui.ui.AssistantUI`
- Audio flow: `assistant.audio.service.AudioService`
- Chat flow: `assistant.chat.service.ChatService`
- OpenAI chat client: `assistant.llm.openai.OpenAI`
- OpenAI transcription stream client: `assistant.llm.stream_client.OpenAIStreamClient`

## Import Style

All internal imports use absolute package paths:

```python
from assistant.audio.service import AudioService
from assistant.display.emotion_display import EmotionDisplay
from assistant.llm.openai import OpenAI
from assistant.network.wifi import conectar_wifi
```

This keeps the package layout stable and ready for packaging/distribution.

## Memory and Network Notes (ESP32)

The project includes targeted diagnostics and mitigations for constrained memory/network environments:

- TLS connection diagnostics in transcription and chat clients.
- Retry strategy for transient socket failures.
- Audio flow releases I2S buffers before TLS handshake to reduce ENOMEM risk.
- Optional streaming mode without accumulating full response payload in memory.

If you hit instability, check serial logs with prefixes:

- `[openaistream]`
- `[openai]`
- `[audio]`

## Packaging (mip)

`manifest.py` has an initial package declaration:

```python
metadata(
		version="0.1.0",
		description="MicroPython assistant library",
)

package("assistant", base_path="./src")
```

This is ready to evolve for full `mip` publication workflow.

## Current Status

This repository is actively evolving. The structure is now library-oriented, with examples separated from reusable code and imports standardized around `assistant.*`.
