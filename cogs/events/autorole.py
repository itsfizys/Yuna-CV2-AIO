"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
import aiohttp 
import aiosqlite 
import asyncio 
import logging 
from discord .ext import commands 
from core import LightCore ,Cog 

DATABASE_PATH ='db/autorole.db'
logger =logging .getLogger (__name__ )

class Autorole2 (Cog ):
    def __init__ (self ,bot :LightCore ):
        self .bot =bot 
        self .headers ={"Authorization":f"Bot {self.bot.http.token}"}
        self .bot .loop .create_task (self .setup_database ())

    async def setup_database (self ):
        async with aiosqlite .connect (DATABASE_PATH )as db :
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS autorole (
                    guild_id INTEGER PRIMARY KEY,
                    bots TEXT,
                    humans TEXT
                )
            ''')
            await db .commit ()

    async def get_autorole (self ,guild_id :int ):
        try:
            async with aiosqlite .connect (DATABASE_PATH )as db :
                async with db .execute ("SELECT bots, humans FROM autorole WHERE guild_id = ?",(guild_id ,))as cursor :
                    row =await cursor .fetchone ()
                    if row :
                        bots ,humans =row 
                        try:
                            bots =[int (role_id )for role_id in bots .replace ('[','').replace (']','').replace (' ','').split (',')if role_id .strip()]
                        except (ValueError, AttributeError):
                            bots = []
                        try:
                            humans =[int (role_id )for role_id in humans .replace ('[','').replace (']','').replace (' ','').split (',')if role_id .strip()]
                        except (ValueError, AttributeError):
                            humans = []
                        return {"bots":bots ,"humans":humans }
                    else :
                        return {"bots":[],"humans":[]}
        except Exception as e:
            logger.error(f"Error fetching autorole data for guild {guild_id}: {e}")
            return {"bots":[],"humans":[]}

    @commands .Cog .listener ()
    async def on_member_join (self ,member ):
        try:
            data =await self .get_autorole (member .guild .id )
            bot_roles =data ["bots"]
            human_roles =data ["humans"]

            if member .bot :
                roles_to_add =bot_roles 
            else :
                roles_to_add =human_roles 

            for role_id in roles_to_add :
                role =member .guild .get_role (role_id )
                if role :
                    try :
                        await member .add_roles (role ,reason ="LightCore Autoroles")
                    except discord .Forbidden :
                        logger.warn(f"Bot lacks permissions to add role {role.name} in {member.guild.name} during Autorole Event.")
                    except discord .errors .RateLimited as e :
                        logger.warn(f"Rate limit encountered: {e}. Retrying in {e.retry_after} seconds.")
                        await asyncio .sleep (e .retry_after )
                        try:
                            await member .add_roles (role ,reason ="LightCore Autoroles")
                        except Exception:
                            pass
                    except discord .HTTPException as e :
                        if e .status ==429 :
                            retry_after =e .response .headers .get ('Retry-After', 1)
                            retry_after =float (retry_after )
                            logger.warn(f"(Autorole) Rate limit encountered. Retrying after {retry_after} seconds.")
                            await asyncio .sleep (retry_after )
                            try:
                                await member .add_roles (role ,reason ="LightCore Autoroles")
                            except Exception:
                                pass
                        else:
                            logger.error(f"HTTP error in Autorole: {e}")
                    except Exception as e :
                        logger .error (f"Unexpected error in Autorole: {e}")
        except Exception as e:
            logger.error(f"Critical error in on_member_join autorole: {e}")


"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
