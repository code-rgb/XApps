import asyncio
from typing import Dict, Optional

import aiohttp
import yaml

from xapps import ApkDL


async def write_links(apk_dl: ApkDL) -> None:

    async def get_downloadlink(x: Dict[str, str]) -> Optional[str]:
        print("Fetching", x["app"])
        source = x["source"]
        if source == "github":
            return await apk_dl.github(*x["args"])
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
        if source == "playstore":
            return await apk_dl.playstore(x["package"])

    with open("config.yaml", "r") as f:
        apk_data = yaml.load(f, Loader=yaml.FullLoader)
    urls = await asyncio.gather(*list(map(get_downloadlink, apk_data)))
    with open("apk_urls.txt", "w") as outfile:
        outfile.write("\n".join(list(filter(None, urls))))


async def main() -> None:
    try:
        async with aiohttp.ClientSession() as session:
            apk_dl = ApkDL(session)
            await apk_dl.start()
            await write_links(apk_dl)
    finally:
        await apk_dl.stop()
