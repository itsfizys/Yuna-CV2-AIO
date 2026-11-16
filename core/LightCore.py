"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
from __future__ import annotations
from discord .ext import commands
import discord
import aiohttp
import json
import jishaku
import asyncio
import typing
from typing import List
import aiosqlite
from utils .config import OWNER_IDS
from utils import getConfig ,updateConfig
from .Context import Context
from discord .ext import commands ,tasks
from colorama import Fore ,Style ,init
import importlib
import inspect
from utils .Tools import get_ignore_data, adminlock_check
import random

init (autoreset =True )

extensions :List [str ]=[
"cogs"
]

class LightCore (commands .AutoShardedBot ):

    def __init__ (self ,*arg ,**kwargs ):
        intents =discord .Intents .all ()
        intents .presences =True
        intents .members =True
        super ().__init__ (command_prefix =self .get_prefix ,
        case_insensitive =True ,
        intents =intents ,
        status =discord .Status .idle ,
        strip_after_prefix =True ,
        owner_ids =OWNER_IDS ,
        allowed_mentions =discord .AllowedMentions (
        everyone =False ,replied_user =False ,roles =False ),
        sync_commands_debug =True ,
        sync_commands =True ,
        # Shard count is left to discord.py: 2 forced shards breaks self-hosting
        # for small bots, and Discord rejects more shards than ceil(guilds/1000).
        )


        self .add_check (self.global_adminlock_check)

    async def setup_hook (self ):
        await self .load_extensions ()

    async def load_extensions (self ):
        for extension in extensions :
            try :
                await self .load_extension (extension )
            except Exception as e :
                print (
                f"{Fore.RED}{Style.BRIGHT}Failed to load extension {extension}. {e}"
                )


    async def on_connect (self ):
        await self .set_streaming_status ()

    async def set_streaming_status (self ):
        activity =discord .Streaming (
            name ="&help | LightCore Development",
            url ="https://twitch.tv/LightCore"
        )
        await self .change_presence (status =discord .Status .idle ,activity =activity )

    async def send_raw (self ,channel_id :int ,content :str ,
    **kwargs )->typing .Optional [discord .Message ]:
        await self .http .send_message (channel_id ,content ,**kwargs )

    async def invoke_help_command (self ,ctx :Context )->None :
        """Invoke the help command or default help command if help extensions is not loaded."""
        return await ctx .send_help (ctx .command )

    async def fetch_message_by_channel (
    self ,channel :discord .TextChannel ,
    messageID :int )->typing .Optional [discord .Message ]:
        async for msg in channel .history (
        limit =1 ,
        before =discord .Object (messageID +1 ),
        after =discord .Object (messageID -1 ),
        ):
            return msg

    async def get_prefix (self ,message :discord .Message ):
        if message .guild :
            guild_id =message .guild .id
            async with aiosqlite .connect ('db/np.db')as db :
                async with db .execute ("SELECT id FROM np WHERE id = ?",(message .author .id ,))as cursor :
                    row =await cursor .fetchone ()
                    if row :
                        data =await getConfig (guild_id )
                        prefix =data ["prefix"]
                        prefixes = [prefix, '&', 'sys']
                        return commands .when_mentioned_or (*prefixes ,'')(self ,message )
                    else :
                        data =await getConfig (guild_id )
                        prefix =data ["prefix"]
                        prefixes = [prefix, '&', 'sys']
                        return commands .when_mentioned_or (*prefixes )(self ,message )
        else :
            async with aiosqlite .connect ('db/np.db')as db :
                async with db .execute ("SELECT id FROM np WHERE id = ?",(message .author .id ,))as cursor :
                    row =await cursor .fetchone ()
                    if row :
                        return commands .when_mentioned_or ('&', 'sys', '')(self ,message )
                    else :
                        return commands .when_mentioned_or ('&', 'sys')(self ,message )


    async def global_adminlock_check(self, ctx):
        """Global adminlock check that applies to all commands"""
        if ctx.command and ctx.command.name == "adminlock":
            return True

        if ctx.author.id in OWNER_IDS:
            return True

        from db.adminlock_db import adminlock_db
        is_locked = await adminlock_db.is_locked()

        if is_locked:
            from discord import ui

            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("sybau you're not allowed to use it! (Global Lock Active)"))

            view = ui.LayoutView()
            view.add_item(container)

            await ctx.send(view=view)
            return False

        return True

    async def on_message_edit (self ,before ,after ):
        ctx :Context =await self .get_context (after ,cls =Context )
        if before .content !=after .content :
            if after .guild is None or after .author .bot :
                return
            if ctx .command is None :
                return
            if type (ctx .channel )=="public_thread":
                return
            await self .invoke (ctx )
        else :
            return




def setup_bot ():
    intents =discord .Intents .all ()
    bot =LightCore (intents =intents )
    return bot

"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""