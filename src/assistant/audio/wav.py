import struct


class WavHeader:

    @staticmethod
    def generate(
        sample_rate,
        pcm_size
    ):

        byte_rate = sample_rate * 2
        block_align = 2

        header = b""

        header += b"RIFF"
        header += struct.pack("<I", pcm_size + 36)
        header += b"WAVE"

        header += b"fmt "
        header += struct.pack("<I", 16)
        header += struct.pack("<H", 1)
        header += struct.pack("<H", 1)

        header += struct.pack("<I", sample_rate)

        header += struct.pack("<I", byte_rate)

        header += struct.pack("<H", block_align)
        header += struct.pack("<H", 16)

        header += b"data"

        header += struct.pack("<I", pcm_size)

        return header