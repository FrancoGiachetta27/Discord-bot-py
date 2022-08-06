import asyncio

import discord

import utils
from song import Song
from youtube import YouTube


class Queue:
    def __init__(self):
        self.queues = {}

    async def enqueue_track(self, ctx, id, source):
        if id in self.queues:
            self.queues[id].append(source)

            await utils.send_message_single(
                ctx,
                source.title,
                f"🎙️ Se ha añadido una cancion a la lista de reproduccion",
                "Atencion!",
            )

            print(self.queues[id])
        else:
            self.queues[id] = [source]

            await utils.send_message_single(
                ctx,
                source.title,
                f"🎙️ Se ha añadido una cancion a la lista de reproduccion",
                "Atencion!",
            )

            print(self.queues[id])

    async def enqueue_playlist(self, ctx, id, search):
        loop = asyncio.get_event_loop()
        playlist = search

        for track in playlist["items"]:
            name = track["track"]["name"]
            source = await YouTube.from_url(name, loop=loop, stream=True)

            if id in self.queues:
                self.queues[id].append(source)
            else:
                self.queues[id] = [source]

            print(source.title)

    # checks if the queue is finished or plays the next song
    async def check_queue(self, ctx, id):
        if len(self.queues[id]) != 0:
            voice_client = ctx.voice_client
            source = self.queues[id].pop(0)
            song = Song(ctx, source)

            await song.send_source_data(ctx)

            voice_client.play(
                source,
                after=lambda e: self.check_queue(ctx, id)
                if e
                else print(f"Player error: {e}"),
            )
        else:
            await utils.send_message_single(
                ctx, f"🛑 No hay mas canciones para reproducir", "❌ Error:", "Atencion!"
            )

    async def get_queue(self, ctx, id):
        if id in self.queues:
            queue = []

            if len(self.queues[id]) != 0:
                for i, song in enumerate(self.queues[id]):
                    queue.append([i, song.title])

                return queue

            await utils.send_message_single(
                ctx, f"🛑 No hay canciones en la lista", "❌ Error:", "Atencion!"
            )
        else:
            await utils.send_message_single(
                ctx,
                f"🛑 La lista aun no ha sido creada, reproduce una cancion primero",
                "❌ Error:",
                "Atencion!",
            )

    async def skip_song(self, ctx, voice_client, id):
        voice_client.stop()

        if len(self.queues[id]) != 0:
            next_song = self.queues[id].pop(0)

            return next_song
        else:
            await utils.send_message_single(
                ctx, f"🛑 No hay mas canciones para reproducir", "❌ Error:", "Atencion!"
            )
