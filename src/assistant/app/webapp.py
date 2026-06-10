try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from ullmtools.core.apis.openaimtools import OpenAIMTools

from ullmtools.tools import (
    TurnOnOffLedTool,
    GetWeatherTool,
    Scheduler,
    ScheduleEventTool,
)




class AssistantWebApp:

    def __init__(self):

        self.webservice = WebService()

    async def setup_llm(self, api_key):

        system_prompt = (
            "Voce e um mini assistente para um display OLED 128x64. "
            "Sua resposta sera exibida em uma unica linha com texto corrido. "
            "Responda de forma curta, clara e natural. "
            "Nao use acentuacao. "
            "Nao use markdown. "
            "Nao use emojis. "
            "Nao use listas. "
            "Use no maximo uma frase curta. "
            "\nAo agendar uma ferramenta utilize exatamente"
            "o nome registrado na lista de tools."
            "Exemplo: turn_onoff_led\n"
            "Nao utilize prefixos como:"
            "\n functions."
            "\n tools."
            "\n assistant."
        )

        llm = OpenAIMTools(
            api_key=api_key,
            model="gpt-4o-mini",
            verbose=True
        )

        scheduler = Scheduler(
            tool_executor=llm.execute_tool
        )

        llm.set_scheduler(
            scheduler
        )

        schedule_tool = ScheduleEventTool(
            scheduler,
            verbose=True
        )

        weather_tool = GetWeatherTool()

        led_tool = TurnOnOffLedTool(
            pin=23
        )

        llm.register_tool(
            tool=schedule_tool
        )

        llm.register_tool(
            tool=weather_tool
        )

        llm.register_tool(
            tool=led_tool
        )

        self.webservice.llm = llm
        self.webservice.scheduler = scheduler
        self.webservice.system_prompt = system_prompt

        asyncio.create_task(
            scheduler.run()
        )

    async def run(self, api_key):

        await self.setup_llm(
            api_key
        )

        await self.webservice.run()