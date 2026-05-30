# =========================================================
# Display Callback
# =========================================================

class DisplayCallback:

    def __init__(self, display):

        self.display = display
        self.buffer = ""
        self.started_response = False

    def normalize_text(self, text):

        replacements = {
            'á': 'a',
            'à': 'a',
            'ã': 'a',
            'â': 'a',
            'é': 'e',
            'ê': 'e',
            'í': 'i',
            'ó': 'o',
            'ô': 'o',
            'õ': 'o',
            'ú': 'u',
            'ç': 'c',
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        clean = ""

        for c in text:

            if 32 <= ord(c) <= 126:
                clean += c
            else:
                clean += '?'

        return clean

    def on_token(self, token):

        if not self.started_response:

            self.display.talk()

            self.started_response = True

        self.buffer += token

        clean = self.normalize_text(self.buffer)

        self.display.set_message(clean)