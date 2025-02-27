#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   __init__.py
@Time    :   2024/11/02 14:37:00
@Author  :   huihuidehui 
@Desc    :   None
"""
import abc
from typing import Any, Generator, List, Optional

import requests

from config.config import HeaderParam
from model import Torrent


class BaseSiteSpider:

    def __init__(self, cookie: str, headers: List[HeaderParam] = []):
        self.cookie = cookie
        # self.headers = headers
        self.headers = {
            "accept": "*/*",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        }
        for i in headers:
            self.headers[i.key] = i.value

    def fetch(self, url: str, method: str = "GET", data: Any = "", *args, **kwargs) -> requests.Response:
        for i in range(3):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=self.headers,
                    cookies=self.cookie,
                    data=data,
                    timeout=(30,30),
                    *args,
                    **kwargs
                )
                return response
            except:
                pass
        raise Exception("fetch failed")

    @abc.abstractmethod
    def free_torrents(self):
        pass

    @abc.abstractmethod
    def parse_torrent_link(self, torrent_id: str) -> str:
        pass

    @abc.abstractmethod
    def download_torrent_content(self, torrent_link:str)->Optional[bytes]:
        pass

class TorrentFetch:
    from ptsite.mteam import MTeamSpider

    SITE_SPIDER_MAP = {"M-Team": MTeamSpider}

    def __init__(self, site: str, cookie: str, headers: List[HeaderParam] = []):
        self.site = site
        self.cookie = cookie
        self.headers = headers
        spider_class = self.SITE_SPIDER_MAP.get(self.site)
        if not spider_class:
            raise ValueError(f"Unknown site: {self.site}")

        self._spider_class: BaseSiteSpider = spider_class(
            self.cookie, self.headers)

    @property
    def free_torrents(self) -> Generator[Torrent, Torrent, Torrent]:

        for torrent in self._spider_class.free_torrents():
            yield torrent

    def parse_torrent_link(self, torrent_id: str) -> str:
        return self._spider_class.parse_torrent_link(torrent_id)

    def download_torrent_content(self, torrent_link:str)->Optional[bytes]:
        return self._spider_class.download_torrent_content(torrent_link)
