import urequests
import ujson

# =========================================================
# Ollama Client
# =========================================================

class Ollama:

    def __init__(
        self,
        url="http://192.168.137.1",
        port="11434",
        model="gemma4:e2b",
        timeout=10,
    ):

        self.model = model
        self.timeout = timeout

        self._generate_url = f"{url}:{port}/api/generate"

    def chat(
        self,
        prompt,
        stream=True,
        callback=None
    ):

        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }

        response = None

        try:

            response = urequests.post(
                self._generate_url,
                json=data
            )

            response.raw.settimeout(self.timeout)

            if stream:

                full_response = ""

                while True:

                    line = response.raw.readline()

                    if not line:
                        break

                    try:

                        json_line = ujson.loads(line)

                        if "response" in json_line:

                            token = json_line["response"]

                            full_response += token

                            if callback:
                                callback(token)
                            else:
                                print(token, end="")

                        if json_line.get("done", False):
                            break

                    except:
                        pass

                print()

                response.close()

                return {
                    "response": full_response
                }

            result = response.json()

            response.close()

            return result

        except Exception as error:

            raise Exception(f"Ollama Error: {error}")

        finally:

            if response:
                response.close()