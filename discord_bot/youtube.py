import asyncio
import re
import urllib.parse
import urllib.request

import discord
import youtube_dl

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    "options": "-vn",
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YouTube(discord.PCMVolumeTransformer):
    def __init__(
        self, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5
    ):
        super().__init__(source, volume)

        self.data = data

        self.uploader = data.get("uploader")
        self.title = data.get("title")
        self.thumbnail = data.get("thumbnail")
        self.description = data.get("description")
        self.duration = self.parse_duration(int(data.get("duration")))
        self.url = data.get("webpage_url")
        self.tags = data.get("tags")
        self.views = data.get("view_count")
        self.likes = data.get("like_count")
        self.dislikes = data.get("dislike_count")

    @classmethod
    async def from_name(cls, search, *, loop=None, stream=False):
        query_string = urllib.parse.urlencode({"search_query": search})
        htm_content = urllib.request.urlopen(
            "http://youtube.com/results?" + query_string
        )
        search_results = re.findall(r"watch\?v=(\S{11})", htm_content.read().decode())
        url = "http://youtube.com/watch?v=" + search_results[0]

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @staticmethod
    def parse_duration(duration_: int):
        minutes, seconds = divmod(duration_, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration: list = []
        if days > 0:
            duration.append("{} dias".format(days))
        if hours > 0:
            duration.append("{} horas".format(hours))
        if minutes > 0:
            duration.append("{} minutos".format(minutes))
        if seconds > 0:
            duration.append("{} segundos".format(seconds))

        return ", ".join(duration)
