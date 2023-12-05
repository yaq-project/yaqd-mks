__all__ = ["MksMultigas2030"]

import asyncio
from typing import Dict, Any, List
import aiohttp

from yaqd_core import IsDaemon


# TODO: url in config
# TODO: <V Name="EVID_10" Format="Integer" Description="number of gasses in analysis" Settable="False"/>
# TODO: <V Name="EVID_31" Format="ASCII" Description="Start Run trigger. Either set this value to non-zero or non-empty or read the value to activate" Settable="True"/>

# EVIDs https://gist.github.com/untzag/07939d7bfbfa43780614f9518b63abe6



class MksMultigas2030(IsDaemon):
    _kind = "mks-multigas-2030"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self._base_url = f"http://localhost/ToolWeb/Cmd"
        self._http_session = aiohttp.ClientSession()
        self._loop.create_task(self.poll_gas_names())
        self._loop.create_task(self._measure())  # TODO: this isn't how triggered sensors work
        self._ngasses = 26  # TODO: read from EVID 84

    async def _measure(self):
        while True:
            print("MEASURE")
            inner = [f"<V Name=\"EVID_{2000 + n}\"/>" for n in range(self._ngasses)]
            inner.append("<V Name=\"EVID_11\"/>")
            payload = f"<?xml version=\"1.0\" encoding=\"utf-8\"?> <PollRequest>{inner}</PollRequest>"
            response = await self._http_session.post(self._base_url, data=payload)
            await self.unpack_response(response)
            await asyncio.sleep(10)

    async def poll_gas_names(self):
        while True: 
            print("POLLING GAS NAMES")
            inner = [f"<V Name=\"EVID_{1000 + n}\"/>" for n in range(self._ngasses)]
            payload = f"<?xml version=\"1.0\" encoding=\"utf-8\"?> <PollRequest>{inner}</PollRequest>"
            response = await self._http_session.post(self._base_url, data=payload)
            await self.unpack_response(response)
            await asyncio.sleep(300)  # 5 minutes

    async def unpack_response(self, response):
        if response.status == 200:
            print(await response.text())
 
    async def update_state(self):
        """Continually monitor and update the current daemon state."""
        # If there is no state to monitor continuously, delete this function
        while True:
            async with self._http_session.get(self._base_url) as resp:
                await self.unpack_response(resp)

