import discord


async def send_message_single(ctx, content, name):
    embed = discord.Embed(title="Atencion!", color=discord.Colour.random())

    embed.add_field(name=name, value=content, inline=True)

    await ctx.send(embed=embed)


async def send_message_multiple(ctx, contents: list):
    embed = discord.Embed(title="Atencion!", color=discord.Colour.random())

    for field in contents:
        embed.add_field(name=field[0], value=field[1], inline=True)

    await ctx.send(embed=embed)
