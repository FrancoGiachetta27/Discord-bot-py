import discord


async def send_message_single(ctx, content, name, title):
    embed = discord.Embed(title=title, color=discord.Colour.random())

    embed.add_field(name=name, value=content, inline=True)

    await ctx.send(embed=embed)


async def send_message_multiple(ctx, contents: list, title):
    embed = discord.Embed(title=title, color=discord.Colour.random())

    for field in contents:
        embed.add_field(name=f"{field[0]}.", value=field[1], inline=False)

    await ctx.send(embed=embed)
