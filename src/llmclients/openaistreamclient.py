import socket
import ssl
import gc
import os

"""OpenAI audio transcription client for MicroPython.

This module provides :class:`OpenAIStreamClient`, a minimal HTTPS client that
uploads a local WAV file to the OpenAI ``/v1/audio/transcriptions`` endpoint
using ``multipart/form-data`` and returns the raw HTTP response text.

Requirements:
    - A valid OpenAI API key.
    - Network access to ``api.openai.com:443``.
    - A readable WAV file on the device filesystem.

Typical usage::

    API_KEY = "YOUR_OPENAI_API_KEY"
    client = OpenAIStreamClient(api_key=API_KEY)

    print("Connecting...")
    client.connect()

    print("Uploading WAV...")
    client.send_wav_file("test.wav")

    print("Reading response...")
    response = client.read_response()
    print(response)

    client.close()

Notes:
    - ``read_response()`` returns the full HTTP response as a decoded string.
    - The default transcription model is ``gpt-4o-mini-transcribe``.
"""

class OpenAIStreamClient:

    def __init__(
        self,
        api_key,
        model="gpt-4o-mini-transcribe"
    ):

        self.api_key = api_key
        self.model = model

        self.host = "api.openai.com"
        self.port = 443

        self.boundary = "----esp32mic"

        self.sock = None

    def connect(self):

        gc.collect()

        addr = socket.getaddrinfo(
            self.host,
            self.port
        )[0][-1]

        sock = socket.socket()

        sock.connect(addr)

        self.sock = ssl.wrap_socket(
            sock,
            server_hostname=self.host
        )

    def send_wav_file(
        self,
        filename
    ):

        wav_size = os.stat(filename)[6]

        print("WAV size:", wav_size)

        # multipart start
        part1 = (
            "--" + self.boundary + "\r\n"
            'Content-Disposition: form-data; '
            'name="file"; filename="audio.wav"\r\n'
            "Content-Type: audio/wav\r\n\r\n"
        ).encode()

        # multipart end
        part2 = (
            "\r\n--" + self.boundary + "\r\n"
            'Content-Disposition: form-data; name="model"\r\n\r\n'
            + self.model +
            "\r\n--" + self.boundary + "--\r\n"
        ).encode()

        # exact HTTP body size
        content_length = (
            len(part1) +
            wav_size +
            len(part2)
        )

        headers = (
            "POST /v1/audio/transcriptions HTTP/1.1\r\n"
            "Host: api.openai.com\r\n"
            "Authorization: Bearer {}\r\n"
            "Content-Type: multipart/form-data; boundary={}\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n\r\n"
        ).format(
            self.api_key,
            self.boundary,
            content_length
        )

        print("Sending headers...")

        self.sock.write(headers.encode())

        print("Sending multipart start...")

        self.sock.write(part1)

        print("Sending WAV file...")

        with open(filename, "rb") as f:

            while True:

                chunk = f.read(1024)

                if not chunk:
                    break

                self.sock.write(chunk)

        print("Sending multipart end...")

        self.sock.write(part2)

    def read_response(self):

        response = b""

        while True:

            try:

                data = self.sock.read(1024)

                if not data:
                    break

                response += data

            except OSError as e:

                print("Socket read error:", e)

                break

        return response.decode()

    def close(self):

        if self.sock:
            self.sock.close()