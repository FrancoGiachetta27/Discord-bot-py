import os
import os.path

from dotenv import load_dotenv

from music_bot import Bot, bot_setup

if __name__ == "__main__":
    path = os.path.abspath("../.env")

    load_dotenv(path)

    bot = bot_setup()
    bot.add_cog(Bot(bot))
    bot.run(os.getenv("TOKEN"))
