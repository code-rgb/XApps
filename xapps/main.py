import asyncio
from typing import Dict, Optional

import aiohttp
import yaml

from xapps import ApkDL


async def write_links(apk_dl: ApkDL) -> None:
    async def get_downloadlink(x: Dict[str, str]) -> Optional[str]:
        source = x["source"]
        if source == "github":
            m = await apk_dl.github(*x["args"])
            print(m)
            return m
        if source == "fdroid":
            return await apk_dl.fdroid(x["package"])
        if source == "json":
            return await apk_dl.json_api(x["link"], x["args"])
        if source == "direct":
            return x["link"]
        if source == "vlc":
            return await apk_dl.vlc(x["link"])
        if source == "mix":
            return await apk_dl.mixplorer(x["link"])

    with open("config.yaml", "r") as f:
        apk_data = yaml.load(f, Loader=yaml.FullLoader)
    urls = await asyncio.gather(*list(map(get_downloadlink, apk_data)))
    with open("apk_urls.txt", "w") as outfile:
        outfile.write("\n".join(list(filter(None, urls))))


async def main():
    session = aiohttp.ClientSession()
    apk_dl = ApkDL(session)
    await apk_dl.start()
    try:
        await write_links(apk_dl)
    finally:
        await session.close()
        await apk_dl.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())