import asyncio
import os
import os.path
import time

import aiohttp
from discord.ext import commands
from dotenv import load_dotenv

import utils
from help_commands import HelpCommand
from song import Song
from songs_queue import Queue
from spotify import BotSpotify
from youtube import YouTube


class Bot(commands.Cog):
    def __init__(self, bot):
        path = os.path.abspath(".\.env")

        load_dotenv(path)

        self.bot = bot
        self.queue_ = Queue()
        self.sp = BotSpotify(
            os.getenv("CLIENT_ID"),
            os.getenv("CLIENT_SECRET"),
        )

    @commands.command(name="p")
    async def play(self, ctx, *, query):
        guild_id = ctx.message.guild.id
        voice_client = ctx.voice_client

        # get source from youtube
        async with ctx.typing():
            if query.startswith("https"):
                source = await YouTube.from_url(query, loop=self.bot.loop, stream=True)
            else:
                source = await YouTube.from_name(query, loop=self.bot.loop, stream=True)

        if not voice_client.is_playing():
            song = Song(ctx, source)

            await song.send_source_data(ctx)
            voice_client.play(
                source,
                after=lambda e: self.queue_.check_queue(ctx, guild_id)
                if e
                else print(f"Player error: {e}"),
            )

        else:
            await self.queue_.enqueue_track(ctx, guild_id, source)

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.voice_client

        await self.ensure_voice(ctx)

        if voice_client.is_playing():
            ctx.voice_client.stop()
        else:
            await utils.send_message_single(
                ctx, "Ninguna cancion se esta reproduciendo", "❌ Error:", "Atencion!"
            )

    @commands.command()
    async def pause(self, ctx):
        voice_client = ctx.voice_client

        await self.ensure_voice(ctx)

        if voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await utils.send_message_single(
                ctx, "Ninguna cancion se esta reproduciendo", "❌ Error:", "Atencion!"
            )

    @commands.command()
    async def resume(self, ctx):
        voice_client = ctx.voice_client

        await self.ensure_voice(ctx)

        if voice_client.is_paused():
            ctx.voice_client.resume()
        elif voice_client.is_playing():
            await utils.send_message_single(
                ctx, "La cancion ya esta en reproduccion", "❌ Error:", "Atencion!"
            )
        else:
            await utils.send_message_single(
                ctx, "Ninguna cancion se esta reproduciendo", "❌ Error:", "Atencion!"
            )

    @commands.command()
    async def skip(self, ctx, *, query=""):
        guild_id = ctx.message.guild.id
        voice_client = ctx.voice_client

        await self.ensure_voice(ctx)

        if query:
            await utils.send_message_single(
                ctx,
                "Ese comando no es correcto",
                "❌ Error:",
                "Atencion!",
            )
        elif voice_client.is_playing():
            try:
                source = await self.queue_.skip_song(ctx, voice_client, guild_id)

                time.sleep(1)

                song = Song(ctx, source)

                await song.send_source_data(ctx)

                voice_client.play(
                    source,
                    after=lambda e: self.queue_.check_queue(ctx, guild_id)
                    if e
                    else print(f"Player error: {e}"),
                )
            except Exception(commands.CommandError) as e:
                await utils.send_message_single(
                    ctx,
                    "Error al obtener la siguiente canción",
                    "❌ Error:",
                    "Atencion!",
                )

                print(e)
        else:
            await utils.send_message_single(
                ctx, "Ninguna cancion se esta reproduciendo", "❌ Error", "Atencion!"
            )

    @commands.command()
    async def playlist(self, ctx, *, query):
        guild_id = ctx.message.guild.id
        loop = asyncio.new_event_loop()
        voice_client = ctx.voice_client
        search = await self.sp.get_playlist(ctx, query)

        await self.queue_.enqueue_playlist(ctx, guild_id, search)

        if not voice_client.is_playing():
            source = self.queue_.queues[guild_id].pop()
            song = Song(ctx, source)

            await song.send_source_data(ctx)

            voice_client.play(
                source,
                after=lambda e: self.queue_.check_queue(ctx, guild_id)
                if e
                else print(f"Player error: {e}"),
            )

    @commands.command()
    async def queue(self, ctx):
        guild_id = ctx.message.guild.id
        queue = await self.queue_.get_queue(
            ctx,
            guild_id,
        )

        await utils.send_message_multiple(ctx, queue, "Atencion!")

    # @commands.command()
    # async def loop(self, ctx):
    #     pass

    # @commands.command()
    # async def endloop(self, ctx):
    #     pass

    # @commands.command()
    # async def lyrics(self, ctx):
    #     voice_client = ctx.voice_client
    #     song_name = voice_client.source.title

    #     async with ctx.typing():

    @play.before_invoke
    @playlist.before_invoke
    # @loop.before_invoke
    # @endloop.before_invoke
    @pause.before_invoke
    @stop.before_invoke
    @resume.before_invoke
    @skip.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await utils.send_message_single(
                    ctx, "No estas conectado a ningun canal", "❌ Error:", "Atencion!"
                )

                raise commands.CommandError("Author not connected to a voice channel.")


def bot_setup():
    bot = commands.Bot(command_prefix="-", description=None, help_command=HelpCommand())

    @bot.event
    async def on_ready():
        print(f"Bot ready. Logged in as {bot.user}")

    return bot
