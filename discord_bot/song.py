import random

import discord


class Song:
    def __init__(self, ctx, source):
        self.requester = ctx.author
        self.source = source

    # sends the current song's info
    async def send_source_data(self, ctx):
        embed = (
            discord.Embed(
                title=f"🎶 Reproduciendo",
                description="```css\n{0.source.title}\n```".format(self),
                url=self.source.url,
                color=discord.Colour.random(),
            )
            .add_field(name="Solicitado por: ", value=f"{self.requester}", inline=True)
            .add_field(name="Duracion ", value=f"{self.source.duration}", inline=True)
            .set_thumbnail(url=self.source.thumbnail)
        )

        await ctx.send(embed=embed)
