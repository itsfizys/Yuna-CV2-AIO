"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .ext import commands 
import aiosqlite 
from utils .Tools import *
from discord import ui


class Unwhitelist (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .bot .loop .create_task (self .setup_database ())


    async def setup_database (self ):
        async with aiosqlite .connect ('db/anti.db')as db :
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS antinuke (
                    guild_id INTEGER PRIMARY KEY,
                    status BOOLEAN
                )
            ''')
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS limit_settings (
                    guild_id INTEGER,
                    action_type TEXT,
                    action_limit INTEGER,
                    time_window INTEGER,
                    PRIMARY KEY (guild_id, action_type)
                )
            ''')
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS extraowners (
                    guild_id INTEGER,
                    owner_id INTEGER,
                    PRIMARY KEY (guild_id, owner_id)
                )
            ''')
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS whitelisted_users (
                    guild_id INTEGER,
                    user_id INTEGER,
                    ban BOOLEAN DEFAULT 0,
                    kick BOOLEAN DEFAULT 0,
                    chdl BOOLEAN DEFAULT 0,
                    chcr BOOLEAN DEFAULT 0,
                    chup BOOLEAN DEFAULT 0,
                    meneve BOOLEAN DEFAULT 0,
                    rlcr BOOLEAN DEFAULT 0,
                    rldl BOOLEAN DEFAULT 0,
                    rlup BOOLEAN DEFAULT 0,
                    mngweb BOOLEAN DEFAULT 0,
                    prune BOOLEAN DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            await db .commit ()


    async def initialize_db (self ):
        self .db =await aiosqlite .connect ('db/anti.db')

    @commands .hybrid_command (name ='unwhitelist',aliases =['unwl'],help ="Unwhitelist a user from antinuke")
    @commands .has_permissions (administrator =True )
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,10 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    async def unwhitelist (self ,ctx ,member :discord .Member =None ):
        if ctx .guild .member_count <2 :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# Error"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("<:icon_cross:1372375094336425986> | Your Server Doesn't Meet My 30 Member Criteria"))
            view.add_item(container)
            return await ctx .send (view=view)

        async with self .db .execute (
        "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
        (ctx .guild .id ,ctx .author .id )
        )as cursor :
            check =await cursor .fetchone ()

        async with self .db .execute (
        "SELECT status FROM antinuke WHERE guild_id = ?",
        (ctx .guild .id ,)
        )as cursor :
            antinuke =await cursor .fetchone ()

        is_owner =ctx .author .id ==ctx .guild .owner_id 
        if not is_owner and not check :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# <:icon_cross:1372375094336425986> | Access Denied"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("Only Server Owner or Extra Owner can Run this Command!"))
            view.add_item(container)
            return await ctx .send (view=view)

        if not antinuke or not antinuke [0 ]:
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay(f"# {ctx.guild.name} Security Settings <:icon_stagemoderator:1337295812102721577>"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("Ohh NO! looks like your server doesn't enabled security\n\nCurrent Status : <:disable_no:1372374999310274600><:enable_yes:1372375008441143417>\n\nTo enable use `antinuke enable`"))
            view.add_item(container)
            return await ctx .send (view=view)

        if not member :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# Unwhitelist Commands"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("**Removes user from whitelisted users which means that the antinuke module will now take actions on them if they trigger it.**"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("**Usage**\n<:red_dot:1372500011669258281> `unwhitelist @user/id`\n<:red_dot:1372500011669258281> `unwl @user`"))
            view.add_item(container)
            return await ctx .send (view=view)

        async with self .db .execute (
        "SELECT * FROM whitelisted_users WHERE guild_id = ? AND user_id = ?",
        (ctx .guild .id ,member .id )
        )as cursor :
            data =await cursor .fetchone ()

        if not data :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# Not Whitelisted"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f"<@{member.id}> is not a whitelisted member."))
            view.add_item(container)
            return await ctx .send (view=view)

        await self .db .execute (
        "DELETE FROM whitelisted_users WHERE guild_id = ? AND user_id = ?",
        (ctx .guild .id ,member .id )
        )
        await self .db .commit ()

        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        container.add_item(ui.TextDisplay("# <:icon_tick:1372375089668161597> Success"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(f"User <@!{member.id}> has been removed from the whitelist."))
        view.add_item(container)
        await ctx .send (view=view)



"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
