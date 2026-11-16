"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord import ui
from discord .ext import commands 
import aiosqlite 
import os 
from utils .Tools import *


DB_PATH ="db/autoresponder.db"

class AutoResponder (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .bot .loop .create_task (self .initialize_db ())

    async def initialize_db (self ):
        if not os .path .exists (os .path .dirname (DB_PATH )):
            os .makedirs (os .path .dirname (DB_PATH ))
        async with aiosqlite .connect (DB_PATH )as db :
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS autoresponses (
                    guild_id INTEGER,
                    name TEXT,
                    message TEXT,
                    PRIMARY KEY (guild_id, name)
                )
            ''')
            await db .commit ()

    async def send_message(self, ctx, title=None, description=None):
        view = ui.LayoutView(timeout=60.0)
        container = ui.Container(accent_color=None)
        
        if title:
            container.add_item(ui.TextDisplay(f"# {title}"))
            container.add_item(ui.Separator())
        
        if description:
            container.add_item(ui.TextDisplay(description))
        
        view.add_item(container)
        await ctx.reply(view=view)

    @commands .group (name ="autoresponder",invoke_without_command =True ,aliases =['ar'],help ="Manage autoresponders in the server.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    async def _ar (self ,ctx ):
        if ctx .subcommand_passed is None :
            await ctx .send_help (ctx .command )
            ctx .command .reset_cooldown (ctx )

    @_ar .command (name ="create",help ="Create a new autoresponder.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def _create (self ,ctx ,name ,*,message ):
        name_lower =name .lower ()
        async with aiosqlite .connect (DB_PATH )as db :
            async with db .execute ("SELECT COUNT(*) FROM autoresponses WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                count =(await cursor .fetchone ())[0 ]
                if count >=20 :
                    return 

            async with db .execute ("SELECT 1 FROM autoresponses WHERE guild_id = ? AND LOWER(name) = ?",(ctx .guild .id ,name_lower ))as cursor :
                if await cursor .fetchone ():
                    return 

            await db .execute ("INSERT INTO autoresponses (guild_id, name, message) VALUES (?, ?, ?)",(ctx .guild .id ,name_lower ,message ))
            await db .commit ()
            await self.send_message(ctx, title="<:icon_tick:1372375089668161597>| Success", description=f"Created autoresponder `{name}` in {ctx.guild.name}")

    @_ar .command (name ="delete",help ="Delete an existing autoresponder.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def _delete (self ,ctx ,name ):
        name_lower =name .lower ()
        async with aiosqlite .connect (DB_PATH )as db :
            async with db .execute ("SELECT 1 FROM autoresponses WHERE guild_id = ? AND LOWER(name) = ?",(ctx .guild .id ,name_lower ))as cursor :
                if not await cursor .fetchone ():
                    return 

            await db .execute ("DELETE FROM autoresponses WHERE guild_id = ? AND LOWER(name) = ?",(ctx .guild .id ,name_lower ))
            await db .commit ()
            await self.send_message(ctx, title="<:icon_tick:1372375089668161597>| Success", description=f"Deleted autoresponder `{name}` in {ctx.guild.name}")

    @_ar .command (name ="edit",help ="Edit an existing autoresponder.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def _edit (self ,ctx ,name ,*,message ):
        name_lower =name .lower ()
        async with aiosqlite .connect (DB_PATH )as db :
            async with db .execute ("SELECT 1 FROM autoresponses WHERE guild_id = ? AND LOWER(name) = ?",(ctx .guild .id ,name_lower ))as cursor :
                if not await cursor .fetchone ():
                    return 

            await db .execute ("UPDATE autoresponses SET message = ? WHERE guild_id = ? AND LOWER(name) = ?",(message ,ctx .guild .id ,name_lower ))
            await db .commit ()
            await self.send_message(ctx, title="<:icon_tick:1372375089668161597>| Success", description=f"Edited autoresponder `{name}` in {ctx.guild.name}")

    @_ar .command (name ="config",help ="List all autoresponders in the server.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def _config (self ,ctx ):
        async with aiosqlite .connect (DB_PATH )as db :
            async with db .execute ("SELECT name FROM autoresponders WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                autoresponses =await cursor .fetchall ()

        if not autoresponses :
            return await self.send_message(ctx, description=f"There are no autoresponders in {ctx.guild.name}")

        view = ui.LayoutView(timeout=60.0)
        container = ui.Container(accent_color=None)
        container.add_item(ui.TextDisplay(f"# Autoresponders in {ctx.guild.name}"))
        container.add_item(ui.Separator())
        
        for i ,(name ,)in enumerate (autoresponses ,start =1 ):
            container.add_item(ui.TextDisplay(f"**Autoresponder [{i}]**\n{name}"))
        
        view.add_item(container)
        await ctx .send (view=view)

    @commands .Cog .listener ()
    async def on_message (self ,message ):
        if message .author ==self .bot .user or not message .guild :
            return 

        async with aiosqlite .connect (DB_PATH )as db :
            async with db .execute ("SELECT message FROM autoresponses WHERE guild_id = ? AND LOWER(name) = ?",(message .guild .id ,message .content .lower ()))as cursor :
                row =await cursor .fetchone ()

        if row :
            await message .channel .send (row [0 ])

async def setup (bot ):
    await bot .add_cog (AutoResponder (bot ))
