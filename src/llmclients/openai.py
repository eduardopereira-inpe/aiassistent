import urequests
import ujson


# =========================================================
# OpenAI Client
# =========================================================

class OpenAI:

    def __init__(
        self,
        api_key,
        model="gpt-4o-mini",
        timeout=20,
        base_url="https://api.openai.com/v1/chat/completions"
    ):

        self.api_key = api_key
        self.model = model
        self.timeout = timeout

        self.base_url = base_url

    def chat(
        self,
        prompt,
        system_prompt="You are a helpful assistant.",
        max_tokens=100,
        temperature=0.7,
        stream=True,
        callback=None
    ):



        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        
        json_bytes = ujson.dumps(data).encode("utf-8")
        
        # 2. Configure os cabeçalhos manualmente, incluindo o Content-Length exato
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
            "Content-Length": str(len(json_bytes)) # <--- Essencial para o MicroPython
        }

        response = None

        try:

            response = urequests.post(
                self.base_url,
                headers=headers,
                data=json_bytes,
                stream=stream
            )



            if response.status_code != 200:

                raise Exception(
                    f"HTTP {response.status_code}: {response.text}"
                )

            # =================================================
            # STREAM MODE
            # =================================================

            if stream:

                full_response = ""

                while True:

                    line = response.raw.readline()

                    if not line:
                        break

                    try:

                        line = line.decode("utf-8").strip()

                        # SSE lines start with:
                        # data: {...}

                        if not line.startswith("data: "):
                            continue

                        payload = line[6:]

                        if payload == "[DONE]":
                            break

                        json_line = ujson.loads(payload)

                        delta = (
                            json_line["choices"][0]
                            ["delta"]
                        )

                        token = delta.get("content", "")

                        if token:

                            full_response += token

                            if callback:
                                callback(token)
                            else:
                                print(token, end="")

                    except:
                        pass

                print()

                return {
                    "response": full_response
                }

            # =================================================
            # NORMAL MODE
            # =================================================

            result = response.json()

            message = (
                result["choices"][0]
                ["message"]
                ["content"]
            )

            if callback:
                callback(message)
            else:
                print(message)

            return {
                "response": message,
                "raw": result
            }

        except Exception as error:

            raise Exception(
                f"OpenAI Error: {error}"
            )

        finally:

            if response:
                response.close()