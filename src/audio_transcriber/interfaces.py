class AudioSource:

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def read_chunk(self):
        raise NotImplementedError()