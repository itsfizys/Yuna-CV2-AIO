"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
from utils import getConfig 

import discord 

from discord .ext import commands 

from utils .Tools import get_ignore_data 

import aiosqlite 

class Mention (commands .Cog ):

    def __init__ (self ,bot ):

        self .bot =bot 

        self .color =0x000000 

        self .bot_name ="LightCore"
        self .bot .loop .create_task (self .setup_database ())

    async def setup_database (self ):
        async with aiosqlite .connect ("db/block.db")as db :
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS user_blacklist (
                    user_id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS guild_blacklist (
                    guild_id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db .commit ()

    async def is_blacklisted (self ,message ):

        async with aiosqlite .connect ("db/block.db")as db :

            cursor =await db .execute ("SELECT 1 FROM guild_blacklist WHERE guild_id = ?",(message .guild .id ,))

            if await cursor .fetchone ():

                return True 



            cursor =await db .execute ("SELECT 1 FROM user_blacklist WHERE user_id = ?",(message .author .id ,))

            if await cursor .fetchone ():

                return True 

        return False 

    @commands .Cog .listener ()

    async def on_message (self ,message ):

        if message .author .bot or not message .guild :

            return 

        if await self .is_blacklisted (message ):

            return 

        ignore_data =await get_ignore_data (message .guild .id )

        if str (message .author .id )in ignore_data ["user"]or str (message .channel .id )in ignore_data ["channel"]:

            return 

        if message .reference and message .reference .resolved :

            if isinstance (message .reference .resolved ,discord .Message ):

                if message .reference .resolved .author .id ==self .bot .user .id :

                    return 

        guild_id =message .guild .id 

        data =await getConfig (guild_id )

        prefix =data ["prefix"]

        if self .bot .user in message .mentions :
            if len (message .content .strip ().split ())==1 :

                from discord import ui

                view = ui.LayoutView()
                container = ui.Container(accent_color=None)

                content = (
                    f"### 👋 Hey [{message.author.display_name}](https://discord.com/users/{message.author.id})!\n"
                    f"I'm **LightCore**, your intelligent and friendly companion. <a:ButterflyWhite:1479361913812025386>\n"
                    f"> - **Server Prefix:** `{prefix}`\n"
                    f"> - **Total Commands:** `{self.bot.total_commands if hasattr(self.bot, 'total_commands') else '81'}`\n"
                    f"> - **Developer:** [lightcore](https://discord.com/users/1124248109472550993)"
                )
                container.add_item(ui.TextDisplay(content))
                view.add_item(container)
                await message .channel .send (view=view)
"""
: ! LightCore !
    + Discord: lightcore
"""