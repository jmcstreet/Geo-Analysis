import asyncio
from datetime import timedelta

from aiohttp import ClientSession

from aiowwlln import Client
from aiowwlln.errors import WWLLNError
#26.934200, -80.094200
TARGET_LATITUDE = 26.934200
TARGET_LONGITUDE = -80.094200
TARGET_RADIUS_KM = 50


async def main() -> None:
    """Create the aiohttp session and run the example."""
    async with ClientSession() as websession:
        try:
            # Create a client:
            client = Client(websession)

            # Get all strike data:
#            print(await client.dump())
            json_dump = await client.dump()

            for i in json_dump:
                lat = json_dump[i]["lat"]
                long = json_dump[i]["long"]
                if ((lat <= 29 and lat >= 24) and
                        (long <= -80 and long >= -90)):
                    print(json_dump[i])
                    print("\n")

            print("Test\n")

            # Get strike data within a 50km radius around a set of coordinates _and_
            # within the last hour:
            print(
                await client.within_radius(
                    TARGET_LATITUDE,
                    TARGET_LONGITUDE,
                    TARGET_RADIUS_KM,
#                    window=timedelta(hours=1),
                )
            )
        except WWLLNError as err:
            print(err)


asyncio.get_event_loop().run_until_complete(main())