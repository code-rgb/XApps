__all__ = ["ApkDL"]

import asyncio
import json
import re
import sys
from typing import Dict, List, Optional, Pattern
from urllib.parse import urlencode

import aiohttp
import pyppeteer
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class PlayStoreDL(object):
    parameters: Dict[str, str]
    browser: pyppeteer.browser.Browser
    ua: UserAgent
    retry_after: int
    max_tries: int

    def __init__(self):
        self.parameters = {
            "device": "phone",
            "arches": "arm64-v8a",
            "sdkInt": "30",
            "expanded": "1",
            "format": "apk",
            "dpi": "480",
            "lang": "en",
        }
        self.ua = UserAgent()
        self.retry_after = 5
        self.max_tries = 8

    def __get_url(self, pkg: str) -> str:
        #  | -> merge operator (python 3.9 +)
        return f"https://apkcombo.com/en-in/apk-downloader?{urlencode({'package': pkg.strip()} | self.parameters)}"

    async def _playstore_fetch(self, package_name: str) -> Optional[str]:
        page = await self.browser.newPage()
        await page.setUserAgent(self.ua.random)
        await page.goto(self.__get_url(package_name))
        element = None
        try_count = 0
        while not element:
            if try_count >= self.max_tries:
                await page.screenshot(path="error.png", fullPage=True)
                return
            try_count += 1
            await asyncio.sleep(self.retry_after)
            element = await page.querySelector("ul.file-list a.variant")
            print(
                f"Waiting for {try_count * self.retry_after} s for page to load"
            )
        try:
            downlink = await page.evaluate("(element) => element.href", element)
        except pyppeteer.errors.ElementHandleError:
            await page.screenshot(path="error.png", fullPage=True)
        else:
            return downlink

    async def playstore(self, package_name: str) -> Optional[str]:
        try_count = 0
        dl_link = None
        while not dl_link:
            try_count += 1
            print("Trying to connect to server:", try_count)
            if try_count >= self.max_tries:
                break
            try:
                dl_link = await self._playstore_fetch(package_name)
            except Exception as e:
                print(e.__class__.__name__, e)
            # except pyppeteer.errors.PageError:
            #     pass
            else:
                # To avoid infinite loop
                break

        if dl_link:
            return dl_link
        print("Failed to fetch", package_name, "\nskipping ...")

    async def start(self) -> None:
        try:
            self.browser = await pyppeteer.launch(headless=True,
                                                  args=["--no-sandbox"])
        except BaseException:
            sys.exit("Cannot start the browser ;__;")

    async def stop(self) -> None:
        await self.browser.close()


class MiscDL(object):
    mixplorer_regex: Pattern
    _session: aiohttp.ClientSession

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session
        self.mixplorer_regex = re.compile(
            r"/attachments/mixplorer_v[\d-]+api\d{2}\w+-apk\.\d+/")

    async def _get_json(self, url: str) -> Optional[Dict]:
        async with self._session.get(url) as resp:
            if resp.status == 200:
                try:
                    return await resp.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    return json.loads(await resp.text())

    async def github(self, repo: str, name: str) -> Optional[str]:
        for apk in (await self._get_json(
                f"https://api.github.com/repos/{repo}/releases/latest")
                   ).get("assets"):
            if apk.get("name") == name:
                return apk.get("browser_download_url")

    async def fdroid(self, pkg_name: str) -> Optional[str]:
        version = (
            await
            self._get_json(f"https://f-droid.org/api/v1/packages/{pkg_name}")
        ).get("suggestedVersionCode")
        return f"https://f-droid.org/repo/{pkg_name}_{version}.apk"

    async def mixplorer(self, link: str) -> Optional[str]:
        async with self._session.get(link) as resp:
            if resp.status != 200:
                return
            text = await resp.text()
        if match := self.mixplorer_regex.search(text):
            return f"{link.rsplit('/', 1)[0]}{match.group(0)}"

    async def vlc(self, link: str) -> Optional[str]:
        async with self._session.get(link) as resp:
            if resp.status != 200:
                return
            page = await resp.text()
        soup = BeautifulSoup(page, "lxml")
        version = soup.find("span", {"id": "downloadVersion"}).text.strip()
        return f"https://get.videolan.org/vlc-android/{version}/VLC-Android-{version}-arm64-v8a.apk"

    async def json_api(self, link: str, args: List[str]) -> Optional[str]:
        if resp := await self._get_json(link):
            while len(args) != 0:
                resp = resp[args.pop(0)]
            return resp


class ApkDL(PlayStoreDL, MiscDL):

    def __init__(self, session: aiohttp.ClientSession):
        PlayStoreDL.__init__(self)
        MiscDL.__init__(self, session)
