# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://imgth.com/"""

from .common import Extractor, Message
from .. import text
import os.path

info = {
    "category": "imgth",
    "extractor": "ImgthExtractor",
    "directory": ["{category}", "{gallery-id} {title}"],
    "filename": "{category}_{gallery-id}_{num:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?imgth\.com/gallery/(\d+)",
    ],
}

class ImgthExtractor(Extractor):

    def __init__(self, match):
        Extractor.__init__(self)
        self.gid = match.group(1)
        self.url = "https://imgth.com/gallery/" + self.gid + "/g/page/"

    def items(self):
        page = self.request(self.url + "0").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, url in enumerate(self.get_images(page), 1):
            name, ext = os.path.splitext(text.filename_from_url(url))
            data["num"] = num
            data["name"] = name
            data["extension"] = ext[1:]
            yield Message.Url, url, data

    def get_images(self, page):
        pnum = 0
        while True:
            pos = 0
            while True:
                url, pos = text.extract(page, '<img src="', '"', pos)
                if not url:
                    break
                yield "https://imgth.com/images/" + url[24:]
            pos = page.find('<li class="next">', pos)
            if pos == -1:
                return
            pnum += 1
            page = self.request(self.url + str(pnum)).text

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        title, pos = text.extract(page, '<h1>', '</h1>')
        count, pos = text.extract(page, 'total of images in this gallery: ', ' ', pos)
        date , pos = text.extract(page, 'created on ', ' by <', pos)
        _    , pos = text.extract(page, 'href="/users/', '', pos)
        user , pos = text.extract(page, '>', '<', pos)
        return {
            "category": info["category"],
            "gallery-id": self.gid,
            "title": title,
            "user": user,
            "date": date,
            "count": count,
        }
