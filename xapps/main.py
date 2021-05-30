import asyncio
from typing import Dict, Optional

import aiohttp
import yaml

from xapps import ApkDL


async def write_links(apkdl: ApkDL) -> None:
    async def get_downloadlink(x: Dict[str, str]) -> Optional[str]:
        source = x["source"]
        if source == "github":
            return await apkdl.github(*x["args"])
        if source == "fdroid":
            return await apkdl.fdroid(x["package"])
        if source == "json":
            return await apkdl.json_api(x["link"], x["args"])
        if source == "direct":
            return x["link"]
        if source == "vlc":
            return await apkdl.vlc(x["link"])
        if source == "mix":
            return await apkdl.mixplorer(x["link"])

    with open("config.yaml", "r") as f:
        apk_data = yaml.load(f, Loader=yaml.FullLoader)
    urls = await asyncio.gather(*list(map(get_downloadlink, apk_data)))
    with open("apk_urls.txt", "w") as outfile:
        outfile.write("\n".join(list(filter(None, urls))))


async def main():
    session = aiohttp.ClientSession()
    apkdl = ApkDL(session)
    await apk_dl.start()
    try:
        await write_links(apkdl)
    finally:
        await session.close()
        await apkdl.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())