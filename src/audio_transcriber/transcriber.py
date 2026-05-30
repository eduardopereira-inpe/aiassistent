import time

from .wav import WavHeader


class AudioTranscriber:

    def __init__(
        self,
        microphone,
        client,
        duration_seconds=4,
        sample_rate=16000
    ):

        self.microphone = microphone

        self.client = client

        self.duration_seconds = duration_seconds

        self.sample_rate = sample_rate

    def transcribe(self):

        pcm_size = (
            self.sample_rate *
            self.duration_seconds *
            2
        )

        wav_size = pcm_size + 44

        print("Connecting...")

        self.client.connect()

        print("Starting request...")

        self.client.begin_request(wav_size)

        wav_header = WavHeader.generate(
            self.sample_rate,
            pcm_size
        )

        self.client.send_audio_chunk(wav_header)

        print("Recording...")

        start = time.time()

        while (
            time.time() - start <
            self.duration_seconds
        ):

            chunk = self.microphone.read_pcm16()

            if chunk:
                self.client.send_audio_chunk(chunk)

        print("Finishing request...")

        self.client.finish_request()

        print("Reading response...")

        response = self.client.read_response()

        self.client.close()

        return response