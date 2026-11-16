"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .ext import commands 
from discord .ui import View ,Select ,Button 
from discord import ui
from datetime import datetime 
import random 
import string 
import aiohttp 
import asyncio 
from utils .logger import logger
import json 
import io 
import aiosqlite

from utils.config import OWNER_IDS
GUILD_ID =1370623292142256188 

async def check_backup_id_exists(backup_id: str) -> bool:
    try:
        async with aiosqlite.connect("db/backups.db") as db:
            async with db.execute("SELECT 1 FROM server_backups WHERE backup_id = ?", (backup_id,)) as cursor:
                return await cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking backup_id: {e}")
        return False

async def generate_backup_id(length=8):
    while True:
        backup_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if not await check_backup_id_exists(backup_id):
            return backup_id

class Backup (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot
        self.bot.loop.create_task(self.setup_database())

    async def setup_database(self):
        try:
            async with aiosqlite.connect("db/backups.db") as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS server_backups (
                        backup_id TEXT PRIMARY KEY,
                        guild_id INTEGER,
                        guild_name TEXT,
                        creator_id INTEGER,
                        created_at TEXT,
                        data TEXT
                    )
                """)
                await db.commit()
                logger.success("DATABASE", "Backup database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize backup database: {e}")

    async def cog_unload (self ):
        # Only close session if we own it; here we just use the bot's session
        logger .info ("Backup cog unloaded.")

    def is_admin (self ,ctx ):
        return ctx .author .guild_permissions .administrator or ctx .author .id in OWNER_IDS 

    def is_owner (self ,user_id ):
        return user_id in OWNER_IDS 

    async def check_db_connection (self ):
        # Since SQLite is a local file, we just check if we can connect
        try:
            async with aiosqlite.connect("db/backups.db") as db:
                await db.execute("SELECT 1")
                return True
        except Exception:
            return False

    async def post_status (self ,dest ,msg ,color =0x000000 ):
        embed =discord .Embed (description =msg ,color =color )
        try :
            await dest .send (embed =embed )
        except discord .HTTPException as e :
            logger .warn (f"Failed to send status: {e}")

    async def safe_delete (self ,obj ,status_channel ):
        if isinstance (obj ,discord .Role ):
            bot_member =status_channel .guild .get_member (self .bot .user .id )
            if bot_member and obj ==bot_member .top_role :
                logger .debug (f"Skipping deletion of bot's own role: {obj.name}")
                return 
        try :
            await obj .delete ()
            await asyncio .sleep (0.5 )
        except discord .HTTPException as e :
            await self .post_status (status_channel ,f"<:icon_danger:1372375135604047902> Failed to delete {obj}: {e}",0x000000 )

    async def create_emoji_with_retry (self ,guild ,name ,image ,status ,retries =3 ):
        for attempt in range (retries ):
            try :
                await guild .create_custom_emoji (name =name ,image =image )
                await asyncio .sleep (0.5 )
                return True 
            except discord .HTTPException as e :
                if e .status ==429 and attempt <retries -1 :
                    retry_after =e .retry_after if hasattr (e ,"retry_after")else 5 
                    await self .post_status (status ,f"<:icon_danger:1372375135604047902> Rate limit on emoji {name}, retrying in {retry_after}s...",0x000000 )
                    await asyncio .sleep (retry_after )
                    continue 
                await self .post_status (status ,f"<:icon_danger:1372375135604047902> Failed to create emoji {name}: {e}",0x000000 )
                return False 

    @commands .hybrid_group (
    name ="backup",
    description ="Manage server backups with various subcommands",
    invoke_without_command =True 
    )
    async def backup (self ,ctx ):
        await ctx .send_help (ctx .command )

    @backup .command (name ="create",description ="Create a new server backup")
    @commands .cooldown (1 ,30 ,commands .BucketType .user )
    async def create (self ,ctx ):
        if not self .is_admin (ctx ):
            return await ctx .send ("<:icon_cross:1372375094336425986> Administrator permissions required.")
        if not await self .check_db_connection ():
            return await ctx .send ("<:icon_cross:1372375094336425986> Database unavailable.")
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT COUNT(*) as count FROM server_backups WHERE creator_id = ?", (ctx.author.id,)) as cursor:
                    row = await cursor.fetchone()
                    if row and row["count"] >= 2:
                        async with db.execute("SELECT backup_id, guild_name FROM server_backups WHERE creator_id = ?", (ctx.author.id,)) as c2:
                            user_backups = await c2.fetchall()
                            
                            container =ui .Container (accent_color =None )
                            container .add_item (ui .TextDisplay ("# 🚫 Backup Limit Reached"))
                            container .add_item (ui .Separator ())
                            container .add_item (ui .TextDisplay (
                                "**You've reached the maximum of 2 backups!**\n"
                                "*Delete one backup to create a new one.*"
                            ))
                            container .add_item (ui .Separator ())
                            backup_lines = "\n".join(f"🔹 `{b['backup_id']}` - *{b['guild_name']}*" for b in user_backups)
                            container .add_item (ui .TextDisplay (
                                f"**📦 Your Current Backups**\n"
                                f"{backup_lines}\n\n"
                                f"💡 Tip: Use 'backup delete <id>' to remove a backup"
                            ))
                            
                            view =ui .LayoutView ()
                            view .add_item (container )
                            return await ctx .send (view =view )
        except Exception as e:
            logger.error(f"Error checking backup limit: {e}")

        backup_id = await generate_backup_id ()
        guild =ctx .guild 

        roles =[{"id":r .id ,"name":r .name ,"permissions":r .permissions .value ,"color":r .color .value ,"hoist":r .hoist ,"mentionable":r .mentionable ,"position":r .position }for r in guild .roles if not r .is_default ()]
        categories =[{"name":c .name ,"position":c .position }for c in guild .categories ]
        channels =[]
        for cat in guild .categories :
            for ch in cat .channels :
                overwrites =[{"id":t .id ,"type":"role"if isinstance (t ,discord .Role )else "member","allow":p .pair ()[0 ].value ,"deny":p .pair ()[1 ].value }for t ,p in ch .overwrites .items ()]
                if isinstance (ch ,discord .TextChannel ):
                    channels .append ({"name":ch .name ,"type":"text","topic":ch .topic ,"slowmode":ch .slowmode_delay ,"nsfw":ch .nsfw ,"category":cat .name ,"overwrites":overwrites })
                elif isinstance (ch ,discord .VoiceChannel ):
                    channels .append ({"name":ch .name ,"type":"voice","bitrate":min (ch .bitrate ,96000 ),"user_limit":ch .user_limit ,"category":cat .name ,"overwrites":overwrites })
        emojis =[{"name":e .name ,"url":str (e .url )}for e in guild .emojis ]
        
        backup_data = {
            "roles": roles,
            "categories": categories,
            "channels": channels,
            "emojis": emojis
        }

        try :
            async with aiosqlite.connect("db/backups.db") as db:
                await db.execute(
                    "INSERT INTO server_backups (backup_id, guild_id, guild_name, creator_id, created_at, data) VALUES (?, ?, ?, ?, ?, ?)",
                    (backup_id, guild.id, guild.name, ctx.author.id, datetime.utcnow().isoformat(), json.dumps(backup_data))
                )
                await db.commit()

            container =ui .Container (accent_color =None )
            container .add_item (ui .TextDisplay ("# ✅ Backup Created Successfully!"))
            container .add_item (ui .Separator ())
            container .add_item (ui .TextDisplay (f"**Your server backup is ready!**\n🆔 **Backup ID:** `{backup_id}`"))
            container .add_item (ui .Separator ())
            container .add_item (ui .TextDisplay (
                f"**📊 Backup Contents**\n"
                f"🎭 **{len(roles)}** roles\n"
                f"📁 **{len(categories)}** categories\n"
                f"📺 **{len(channels)}** channels\n"
                f"😀 **{len(emojis)}** emojis\n\n"
                f"**🏠 Server**\n"
                f"**{guild.name}**\n"
                f"👑 Created by [{ctx.author.display_name}]({ctx.author.avatar.url if ctx.author.avatar else 'https://discord.com'})\n\n"
                f"💾 Use 'backup load {backup_id}' to restore this backup"
            ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e:
            logger.error(f"Error creating backup: {e}")

    @backup .command (name ="list",description ="List all your server backups")
    async def list (self ,ctx ):
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM server_backups WHERE creator_id = ?", (ctx.author.id,)) as cursor:
                    backups = await cursor.fetchall()

            if not backups :
                return await ctx .send ("<:icon_cross:1372375094336425986> No backups found.")
            
            container =ui .Container (accent_color =None )
            container .add_item (ui .TextDisplay ("# 📦 Your Server Backups"))
            container .add_item (ui .Separator ())
            container .add_item (ui .TextDisplay ("*Here are all your saved server backups:*"))
            container .add_item (ui .Separator ())

            backup_list =[]
            for b in backups :
                try:
                    created_date_obj = datetime.fromisoformat(b["created_at"])
                    created_date = created_date_obj.strftime("%m/%d/%Y")
                except:
                    created_date = "Unknown"
                backup_list .append (f"🔹 **`{b['backup_id']}`**\n   🏠 *{b['guild_name']}*\n   📅 *Created: {created_date}*")

            container .add_item (ui .TextDisplay (
                f"**💾 Available Backups**\n\n"
                f"{chr(10).join(backup_list) if backup_list else 'No backups found'}\n\n"
                f"💡 Use 'backup info <id>' for detailed information"
            ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e:
            logger.error(f"Error listing backups: {e}")

    @backup .command (name ="delete",description ="Delete a server backup by ID")
    async def delete (self ,ctx ,backup_id :str ):
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM server_backups WHERE backup_id = ?", (backup_id,)) as cursor:
                    backup = await cursor.fetchone()

            if not backup:
                return await ctx.send("<:icon_cross:1372375094336425986> Backup not found.")
            if not (self.is_admin(ctx) or backup["creator_id"] == ctx.author.id):
                return await ctx .send ("<:icon_cross:1372375094336425986> Must be creator, admin, or owner to delete.")
            
            logger .debug (f"Deleting backup {backup_id} for user {ctx.author.id}")
            async with aiosqlite.connect("db/backups.db") as db:
                await db.execute("DELETE FROM server_backups WHERE backup_id = ?", (backup_id,))
                await db.commit()
                deleted_count = db.total_changes
            
            container =ui .Container (accent_color =None )
            if deleted_count > 0:
                container .add_item (ui .TextDisplay ("# 🗑️ Backup Deleted Successfully"))
                container .add_item (ui .Separator ())
                container .add_item (ui .TextDisplay (
                    f"**Backup ID:** `{backup_id}`\n"
                    f"*The backup has been permanently removed from the system.*\n\n"
                    f"💡 You now have an available backup slot"
                ))
            else :
                container .add_item (ui .TextDisplay ("# ❌ Deletion Failed"))
                container .add_item (ui .Separator ())
                container .add_item (ui .TextDisplay (
                    f"**Backup ID:** `{backup_id}`\n"
                    f"*Backup not found or you don't have permission to delete it.*"
                ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e:
            logger.error(f"Error deleting backup: {e}")

    @backup .command (name ="info",description ="View details of a server backup by ID")
    async def info (self ,ctx ,backup_id :str ):
        if not self .is_admin (ctx ):
            return await ctx .send ("<:icon_cross:1372375094336425986> Administrator permissions required.")
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM server_backups WHERE backup_id = ?", (backup_id,)) as cursor:
                    backup = await cursor.fetchone()

            if not backup :
                return await ctx .send ("<:icon_cross:1372375094336425986> Backup not found.")
            
            backup_data = json.loads(backup["data"])

            container =ui .Container (accent_color =None )
            container .add_item (ui .TextDisplay ("# 📋 Backup Information"))
            container .add_item (ui .Separator ())
            container .add_item (ui .TextDisplay (f"**Backup ID:** `{backup_id}`"))
            container .add_item (ui .Separator ())
            
            creator_id =backup ['creator_id']
            creator_display =f"User ID: {creator_id}"
            try :
                creator_user =await self .bot .fetch_user (int (creator_id ))
                creator_display =f"[{creator_user.display_name}]({creator_user.avatar.url if creator_user.avatar else 'https://discord.com'})"
            except :
                pass 
            
            try:
                created_at = datetime.fromisoformat(backup['created_at']).strftime('%B %d, %Y at %H:%M UTC')
            except:
                created_at = backup['created_at']

            container .add_item (ui .TextDisplay (
                f"**🏠 Server Details**\n"
                f"**Name:** {backup['guild_name']}\n"
                f"**Creator:** {creator_display}\n"
                f"**Created:** {created_at}\n\n"
                f"🎭 **Roles:** {len(backup_data.get('roles', []))} roles\n"
                f"📁 **Categories:** {len(backup_data.get('categories', []))} categories\n"
                f"📺 **Channels:** {len(backup_data.get('channels', []))} channels\n"
                f"😀 **Emojis:** {len(backup_data.get('emojis', []))} emojis\n"
                f"💾 **Total Size:** Complete backup\n"
                f"🔒 **Status:** ✅ Ready to load\n\n"
                f"💡 Use 'backup load' to restore this backup to your server"
            ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e:
            logger.error(f"Error fetching backup info: {e}")

    @backup .command (name ="transfer",description ="Transfer a server backup to another user")
    async def transfer (self ,ctx ,backup_id :str ,user :discord .User ):
        if not self .is_admin (ctx ):
            return await ctx .send ("<:icon_cross:1372375094336425986> Administrator permissions required.")
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT creator_id FROM server_backups WHERE backup_id = ?", (backup_id,)) as cursor:
                    backup = await cursor.fetchone()

            if not backup:
                return await ctx .send ("<:icon_cross:1372375094336425986> Backup not found.")
            if backup["creator_id"] != ctx.author.id and not self.is_admin(ctx):
                 return await ctx .send ("<:icon_cross:1372375094336425986> Not owned by you.")
            
            async with aiosqlite.connect("db/backups.db") as db:
                await db.execute("UPDATE server_backups SET creator_id = ? WHERE backup_id = ?", (user.id, backup_id))
                await db.commit()
                modified_count = db.total_changes
            
            container =ui .Container (accent_color =None )
            if modified_count > 0:
                container .add_item (ui .TextDisplay ("# 🔄 Backup Transferred Successfully"))
                container .add_item (ui .Separator ())
                container .add_item (ui .TextDisplay (
                    f"**Backup ID:** `{backup_id}`\n"
                    f"*Ownership has been transferred to [{user.display_name}]({user.avatar.url if user.avatar else 'https://discord.com'})*\n\n"
                    f"**Transfer Details**\n"
                    f"**From:** [{ctx.author.display_name}]({ctx.author.avatar.url if ctx.author.avatar else 'https://discord.com'})\n"
                    f"**To:** [{user.display_name}]({user.avatar.url if user.avatar else 'https://discord.com'})\n"
                    f"**Status:** ✅ Complete\n\n"
                    f"The new owner can now manage this backup"
                ))
            else :
                container .add_item (ui .TextDisplay ("# ❌ Transfer Failed"))
                container .add_item (ui .Separator ())
                container .add_item (ui .TextDisplay (
                    f"**Backup ID:** `{backup_id}`\n"
                    f"*The transfer could not be completed.*"
                ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e:
            logger.error(f"Error transferring backup: {e}")

    @backup .command (name ="preview",description ="Preview the contents of a server backup")
    async def preview (self ,ctx ,backup_id :str ):
        if not self .is_admin (ctx ):
            return await ctx .send ("<:icon_cross:1372375094336425986> Administrator permissions required.")
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM server_backups WHERE backup_id = ?", (backup_id,)) as cursor:
                    backup = await cursor.fetchone()

            if not backup :
                return await ctx .send ("<:icon_cross:1372375094336425986> Backup not found.")
            
            backup_data = json.loads(backup["data"])

            def truncate_list (items ,key ,max_chars =1000 ):
                result =[]
                total_chars =0 
                for item in items :
                    line =f"- {item[key]} (Position: {item['position']})"if key =="name"and "position"in item else f"- {item[key]}"
                    if total_chars +len (line )+1 >max_chars :
                        break 
                    result .append (line )
                    total_chars +=len (line )+1 
                if len (items )>len (result ):
                    result .append (f"...and {len(items) - len(result)} more")
                return "\n".join (result )or "None"
            
            creator_id =backup ['creator_id']
            creator_display =f"User ID: {creator_id}"
            try :
                creator_user =await self .bot .fetch_user (int (creator_id ))
                creator_display =f"[{creator_user.display_name}]({creator_user.avatar.url if creator_user.avatar else 'https://discord.com'})"
            except :
                pass 

            try:
                created_at = datetime.fromisoformat(backup['created_at']).strftime('%B %d, %Y')
            except:
                created_at = backup['created_at']
            
            container =ui .Container (accent_color =None )
            container .add_item (ui .TextDisplay ("# 👀 Backup Preview"))
            container .add_item (ui .Separator ())
            container .add_item (ui .TextDisplay (
                f"**Backup ID:** `{backup_id}`\n"
                f"**Server:** {backup['guild_name']}\n"
                f"**Creator:** {creator_display}\n"
                f"**Created:** {created_at}"
            ))
            container .add_item (ui .Separator ())
            container .add_item (ui .TextDisplay (
                f"**Roles**\n{truncate_list(backup_data.get('roles', []), 'name')}\n\n"
                f"**Categories**\n{truncate_list(backup_data.get('categories', []), 'name')}\n\n"
                f"**Channels**\n{truncate_list(backup_data.get('channels', []), 'name')}\n\n"
                f"**Emojis**\n{truncate_list(backup_data.get('emojis', []), 'name')}"
            ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e:
            logger.error(f"Error previewing backup: {e}")

    @backup .command (name ="export",description ="Export a server backup as a JSON file")
    async def export (self ,ctx ,backup_id :str ):
        if not self .is_admin (ctx ):
            return await ctx .send ("<:icon_cross:1372375094336425986> Administrator permissions required.")
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM server_backups WHERE backup_id = ?", (backup_id,)) as cursor:
                    backup = await cursor.fetchone()

            if not backup:
                return await ctx .send ("<:icon_cross:1372375094336425986> Backup not found.")
            if backup["creator_id"] != ctx.author.id and not self.is_admin(ctx):
                return await ctx .send ("<:icon_cross:1372375094336425986> Not owned by you.")
            
            # Combine back into a full JSON
            full_backup = {
                "backup_id": backup["backup_id"],
                "guild_id": backup["guild_id"],
                "guild_name": backup["guild_name"],
                "creator_id": backup["creator_id"],
                "created_at": backup["created_at"]
            }
            parsed_data = json.loads(backup["data"])
            full_backup.update(parsed_data)

            backup_data =json .dumps (full_backup ,indent =2 ,default =str ).encode ()
            if len (backup_data )>8 *1024 *1024 :
                return await ctx .send ("<:icon_cross:1372375094336425986> Backup too large to export.")
            file =discord .File (io .BytesIO (backup_data ),filename =f"backup_{backup_id}.json")
            
            container =ui .Container (accent_color =None )
            container .add_item (ui .TextDisplay ("# 📤 Backup Exported Successfully"))
            container .add_item (ui .Separator ())
            container .add_item (ui .TextDisplay (
                f"**Backup ID:** `{backup_id}`\n"
                f"*Your backup has been exported as a JSON file.*\n\n"
                f"**📁 File Details**\n"
                f"**Filename:** `backup_{backup_id}.json`\n"
                f"**Format:** JSON\n"
                f"**Size:** {len(backup_data):,} bytes\n\n"
                f"💾 You can import this file on any server with the backup import command"
            ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view ,file =file )
        except Exception as e:
            logger.error(f"Error exporting backup: {e}")

    @backup .command (name ="import",description ="Import a server backup from a JSON file")
    @commands .cooldown (1 ,30 ,commands .BucketType .user )
    async def import_backup (self ,ctx ):
        if not self .is_admin (ctx ):
            return await ctx .send ("<:icon_cross:1372375094336425986> Administrator permissions required.")
        if not ctx .message .attachments :
            return await ctx .send ("<:icon_cross:1372375094336425986> Attach a JSON file.")
        attachment =ctx .message .attachments [0 ]
        if not attachment .filename .endswith (".json"):
            return await ctx .send ("<:icon_cross:1372375094336425986> Must be a JSON file.")
        try :
            backup_data =json .loads (await attachment .read ())
            required_fields =["guild_id","guild_name","roles","categories","channels","emojis"]
            for field in required_fields :
                if field not in backup_data or not isinstance (backup_data [field ],(list ,int ,str )):
                    return await ctx .send (f"<:icon_cross:1372375094336425986> Invalid backup: '{field}' missing or incorrect.")
            for role in backup_data ["roles"]:
                if not isinstance (role .get ("position",-1 ),int )or role ["position"]<1 :
                    role ["position"]=1 
            for channel in backup_data ["channels"]:
                if channel ["type"]=="voice":
                    channel ["bitrate"]=min (channel .get ("bitrate",64000 ),96000 )
            
            new_backup_id = await generate_backup_id ()
            guild_id = backup_data.get("guild_id", ctx.guild.id)
            guild_name = backup_data.get("guild_name", ctx.guild.name)

            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT COUNT(*) as count FROM server_backups WHERE creator_id = ?", (ctx.author.id,)) as cursor:
                    row = await cursor.fetchone()
                    if row and row["count"] >= 2:
                        return await ctx .send ("<:icon_cross:1372375094336425986> You have 2 backups. Delete one first.")
                
                data_to_store = {
                    "roles": backup_data["roles"],
                    "categories": backup_data["categories"],
                    "channels": backup_data["channels"],
                    "emojis": backup_data["emojis"]
                }
            
                await db.execute(
                    "INSERT INTO server_backups (backup_id, guild_id, guild_name, creator_id, created_at, data) VALUES (?, ?, ?, ?, ?, ?)",
                    (new_backup_id, guild_id, guild_name, ctx.author.id, datetime.utcnow().isoformat(), json.dumps(data_to_store))
                )
                await db.commit()
            
            container =ui .Container (accent_color =None )
            container .add_item (ui .TextDisplay ("# 📥 Backup Imported Successfully"))
            container .add_item (ui .Separator ())
            container .add_item (ui .TextDisplay (
                f"**New Backup ID:** `{new_backup_id}`\n"
                f"*Your backup file has been imported and is ready to use!*\n\n"
                f"**📋 Import Details**\n"
                f"**Server:** {guild_name}\n"
                f"**Roles:** {len(backup_data['roles'])}\n"
                f"**Channels:** {len(backup_data['channels'])}\n"
                f"**Emojis:** {len(backup_data['emojis'])}\n\n"
                f"🚀 Use 'backup load' to restore this backup to your server"
            ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view )
        except json .JSONDecodeError :
            await ctx .send ("<:icon_cross:1372375094336425986> Invalid JSON file.")
        except Exception as e:
            logger.error(f"Error importing backup: {e}")

    @backup .command (name ="verify",description ="Verify the integrity of a server backup")
    async def verify (self ,ctx ,backup_id :str ):
        if not self .is_admin (ctx ):
            return await ctx .send ("<:icon_cross:1372375094336425986> Administrator permissions required.")
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT data FROM server_backups WHERE backup_id = ?", (backup_id,)) as cursor:
                    backup_row = await cursor.fetchone()

            if not backup_row :
                return await ctx .send ("<:icon_cross:1372375094336425986> Backup not found.")
            
            backup_data = json.loads(backup_row["data"])

            issues =[]
            if not backup_data .get ("roles"):
                issues .append ("No roles found.")
            if not backup_data .get ("channels"):
                issues .append ("No channels found.")
            if not backup_data .get ("categories"):
                issues .append ("No categories found.")
            if not backup_data .get ("emojis"):
                issues .append ("No emojis found.")
            
            for role in backup_data.get("roles", []):
                if not isinstance (role .get ("position"),int )or role ["position"]<1 :
                    issues .append (f"Invalid position for role {role['name']}.")
            for channel in backup_data.get("channels", []):
                if channel .get("type")=="voice"and channel .get ("bitrate",64000 )>96000 :
                    issues .append (f"Invalid bitrate for channel {channel['name']}.")
            
            container =ui .Container (accent_color =None )
            if issues :
                container .add_item (ui .TextDisplay ("# ⚠️ Backup Verification Failed"))
                container .add_item (ui .Separator ())
                container .add_item (ui .TextDisplay (
                    f"**Backup ID:** `{backup_id}`\n"
                    f"*Found {len(issues)} issue(s) that need attention:*"
                ))
                container .add_item (ui .Separator ())
                container .add_item (ui .TextDisplay (
                    f"**🚨 Issues Found**\n"
                    f"{chr(10).join(f'• {issue}' for issue in issues)}\n\n"
                    f"🔧 These issues may cause problems during restoration"
                ))
            else :
                container .add_item (ui .TextDisplay ("# ✅ Backup Verification Passed"))
                container .add_item (ui .Separator ())
                container .add_item (ui .TextDisplay (
                    f"**Backup ID:** `{backup_id}`\n"
                    f"*This backup is valid and ready for restoration!*"
                ))
                container .add_item (ui .Separator ())
                container .add_item (ui .TextDisplay (
                    f"**🔍 Verification Results**\n"
                    f"• All roles have valid positions\n"
                    f"• All channels are properly configured\n"
                    f"• All data integrity checks passed\n\n"
                    f"✨ This backup can be safely loaded"
                ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e:
            logger.error(f"Error verifying backup: {e}")

    @backup .command (name ="stats",description ="View statistics about server backups")
    async def stats (self ,ctx ):
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT COUNT(*) as cnt FROM server_backups") as cursor:
                    total_backups = (await cursor.fetchone())["cnt"]
                async with db.execute("SELECT COUNT(*) as cnt FROM server_backups WHERE creator_id = ?", (ctx.author.id,)) as cursor:
                    user_backups = (await cursor.fetchone())["cnt"]
                async with db.execute("SELECT * FROM server_backups ORDER BY created_at DESC LIMIT 1") as cursor:
                    latest_backup = await cursor.fetchone()
            
            container =ui .Container (accent_color =None )
            container .add_item (ui .TextDisplay ("# 📊 Backup Statistics"))
            container .add_item (ui .Separator ())
            container .add_item (ui .TextDisplay ("*System-wide backup statistics and information*"))
            container .add_item (ui .Separator ())
            
            footer_text = ""
            if latest_backup:
                try:
                    created_at = datetime.fromisoformat(latest_backup['created_at']).strftime('%B %d, %Y')
                except:
                    created_at = latest_backup['created_at']
                footer_text = f"\n\nMost recent backup created: {created_at}"
            
            container .add_item (ui .TextDisplay (
                f"**🌐 Global Stats**\n"
                f"**Total Backups:** {total_backups:,}\n"
                f"**Latest Backup:** `{latest_backup['backup_id'] if latest_backup else 'None'}`\n\n"
                f"**👤 Your Stats**\n"
                f"**Your Backups:** {user_backups}/2\n"
                f"**Remaining Slots:** {2-user_backups}\n\n"
                f"**💡 System Info**\n"
                f"**Max per user:** 2\n"
                f"**Storage:** Unlimited"
                f"{footer_text}"
            ))
            
            view =ui .LayoutView ()
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")

    @commands .command (name ="backupdatabase",description ="Reset the entire backup database (bot owner only)")
    @commands .guild_only ()
    async def backupdatabase (self ,ctx ):
        if not self .is_owner (ctx .author .id ):
            return await ctx .send ("<:icon_cross:1372375094336425986> Bot owner only.")
        if ctx .guild .id !=GUILD_ID :
            return await ctx .send (f"<:icon_cross:1372375094336425986> Only usable in guild ID: {GUILD_ID}.")
        if not await self .check_db_connection ():
            return await ctx .send ("<:icon_cross:1372375094336425986> Database unavailable.")
        try :
            logger .debug (f"Bot owner {ctx.author.id} resetting database")
            async with aiosqlite.connect("db/backups.db") as db:
                await db.execute("DELETE FROM server_backups")
                await db.commit()
                deleted_count = db.total_changes
            await ctx .send (f"<:icon_tick:1372375089668161597> {deleted_count} backups deleted.")
        except Exception as e:
            logger.error(f"Error nuking database: {e}")

    @backup .command (name ="load",description ="Restore a server backup by ID")
    @commands .cooldown (1 ,30 ,commands .BucketType .user )
    async def load (self ,ctx ,backup_id :str ):
        if not self .is_admin (ctx ):
            return await ctx .send ("<:icon_cross:1372375094336425986> Administrator permissions needed.")
        try :
            async with aiosqlite.connect("db/backups.db") as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM server_backups WHERE backup_id = ?", (backup_id,)) as cursor:
                    backup_row = await cursor.fetchone()

            if not backup_row :
                return await ctx .send ("<:icon_cross:1372375094336425986> Backup not found.")
            
            backup_data = json.loads(backup_row["data"])
        except Exception as e:
            logger.error(f"Error finding load backup_id: {e}")
            return

        class ConfirmView (ui .LayoutView ):
            def __init__ (self ):
                super ().__init__ (timeout =180 )
                self .selection =None 
                self .timed_out =False 
                
                container =ui .Container (accent_color =None )
                container .add_item (ui .TextDisplay ("# 🔄 Backup Load Confirmation"))
                container .add_item (ui .Separator ())
                container .add_item (ui .TextDisplay (
                    f"**Backup ID:** `{backup_id}`\n"
                    f"Select what to delete before loading the backup:"
                ))
                container .add_item (ui .Separator ())
                
                select_menu =ui .ActionRow (
                    ui .Select (
                        placeholder ="Select what to delete before loading backup",
                        min_values =1 ,
                        max_values =5 ,
                        options =[
                            discord .SelectOption (label ="Roles",value ="roles",emoji ="🧷"),
                            discord .SelectOption (label ="Channels",value ="channels",emoji ="📺"),
                            discord .SelectOption (label ="Categories",value ="categories",emoji ="🗂️"),
                            discord .SelectOption (label ="Emojis",value ="emojis",emoji ="🙂"),
                            discord .SelectOption (label ="All",value ="all",emoji ="🗃️"),
                        ]
                    )
                )
                select_menu .children [0 ].callback =self .select_callback 
                container .add_item (select_menu )
                
                buttons =ui .ActionRow (
                    ui .Button (label ="Confirm",style =discord .ButtonStyle .green ),
                    ui .Button (label ="Cancel",style =discord .ButtonStyle .red )
                )
                buttons .children [0 ].callback =self .confirm_callback 
                buttons .children [1 ].callback =self .cancel_callback 
                container .add_item (buttons )
                
                self .add_item (container )

            async def select_callback (self ,interaction :discord .Interaction ):
                if interaction .user !=ctx .author :
                    await interaction .response .send_message ("<:icon_cross:1372375094336425986> Only the command author can choose.",ephemeral =True )
                    return 
                await interaction .response .defer (ephemeral =True )
                self .selection =interaction .data ["values"]
                await interaction .followup .send (f"<:icon_tick:1372375089668161597> Selected: {', '.join(self.selection)}. Click Confirm.",ephemeral =True )

            async def confirm_callback (self ,interaction :discord .Interaction ):
                if interaction .user !=ctx .author :
                    await interaction .response .send_message ("<:icon_cross:1372375094336425986> Only the command author can confirm.",ephemeral =True )
                    return 
                await interaction .response .defer (ephemeral =True )
                self .stop ()

            async def cancel_callback (self ,interaction :discord .Interaction ):
                if interaction .user !=ctx .author :
                    await interaction .response .send_message ("<:icon_cross:1372375094336425986> Only the command author can cancel.",ephemeral =True )
                    return 
                await interaction .response .send_message ("<:icon_cross:1372375094336425986> Backup loading cancelled.",ephemeral =True )
                self .selection =None 
                self .stop ()

            async def on_timeout (self ):
                self .timed_out =True 

        view =ConfirmView ()
        try :
            await ctx .send (view =view )
        except discord .HTTPException as e :
            logger .error (f"Failed to send view: {e}")
            return 

        await view .wait ()
        if view .selection is None :
            return await ctx .send ("<:icon_cross:1372375094336425986> Backup loading timed out."if view .timed_out else "<:icon_cross:1372375094336425986> Backup loading cancelled.")

        if not ctx .guild .me .guild_permissions .manage_channels :
            return await ctx .send ("<:icon_cross:1372375094336425986> Bot lacks manage channels permission.")

        status =discord .utils .get (ctx .guild .channels ,name ="backup-status")
        if not status :
            try :
                status =await ctx .guild .create_text_channel ("backup-status")
            except discord .HTTPException as e :
                logger .error (f"Failed to create status channel: {e}")
                return 

        await self .post_status (status ,"🧹 Deleting selected parts...")
        try :
            if "all"in view .selection or "channels"in view .selection :
                for ch in ctx .guild .channels :
                    if ch .name !="backup-status":
                        await self .safe_delete (ch ,status )
            if "all"in view .selection or "roles"in view .selection :
                for r in ctx .guild .roles :
                    if not r .is_default ():
                        await self .safe_delete (r ,status )
            if "all"in view .selection or "emojis"in view .selection :
                for e in ctx .guild .emojis :
                    await self .safe_delete (e ,status )
            if "all"in view .selection or "categories"in view .selection :
                for cat in ctx .guild .categories :
                    await self .safe_delete (cat ,status )
        except Exception as e :
            logger .error (f"Deletion error: {e}")
            await self .post_status (status ,f"<:icon_danger:1372375135604047902> Error deleting parts: {e}",0x000000 )
            return 

        await self .post_status (status ,"🎭 Restoring roles...")
        old_to_new_role ={}
        bot_member =ctx .guild .get_member (self .bot .user .id )
        if not bot_member :
            await self .post_status (status ,"<:icon_danger:1372375135604047902> Bot member not found.",0x000000 )
            return 

        bot_top_pos =bot_member .top_role .position 
        roles_data = backup_data.get("roles", [])
        if bot_top_pos <len (roles_data):
            await self .post_status (status ,"ℹ️ Adjusting role positions below bot's top role.",0x000000 )

        for r in sorted (roles_data,key =lambda x :x ["position"],reverse =True ):
            if not isinstance (r ["position"],int )or r ["position"]<1 :
                await self .post_status (status ,f"<:icon_danger:1372375135604047902> Invalid position for role {r['name']}. Setting to 1.",0x000000 )
                r ["position"]=1 
            try :
                logger .debug (f"Creating role: {r['name']} (Position: {r['position']})")
                new_role =await ctx .guild .create_role (name =r ["name"],colour =discord .Colour (r ["color"]),hoist =r ["hoist"],mentionable =r ["mentionable"])
                old_to_new_role [r ["id"]]=new_role 
                await asyncio .sleep (0.5 )
            except discord .HTTPException as e :
                await self .post_status (status ,f"<:icon_danger:1372375135604047902> Failed to create role {r['name']}: {e}",0x000000 )

        try :
            role_positions =[]
            max_available_pos =bot_top_pos -1 
            sorted_roles =sorted (roles_data,key =lambda x :x ["position"],reverse =True )
            for idx ,r_data in enumerate (sorted_roles ):
                new_role =old_to_new_role .get (r_data ["id"])
                if new_role :
                    orig_pos =max (r_data ["position"],1 )
                    new_pos =orig_pos if orig_pos <=max_available_pos else max_available_pos -idx 
                    if new_pos <1 :
                        new_pos =1 
                    role_positions .append ((new_role ,new_pos ,orig_pos ))

            for role ,pos ,orig_pos in sorted (role_positions ,key =lambda x :x [1 ],reverse =True ):
                try :
                    await role .edit (position =pos )
                    logger .debug (f"Set role {role.name} to position {pos} (original: {orig_pos})")
                    await asyncio .sleep (2 )
                    if role .position !=pos :
                        logger .warn (f"Role {role.name} position mismatch: set {pos}, got {role.position}")
                        await self .post_status (status ,f"<:icon_danger:1372375135604047902> Role {role.name} at {role.position}, expected {pos}",0x000000 )
                except discord .HTTPException as e :
                    logger .error (f"Failed to position role {role.name}: {e}")
                    await self .post_status (status ,f"<:icon_danger:1372375135604047902> Failed to position role {role.name}: {e}",0x000000 )
        except Exception as e :
            logger .error (f"Role positioning error: {e}")
            await self .post_status (status ,f"<:icon_danger:1372375135604047902> Failed to set role positions: {e}",0x000000 )

        await self .post_status (status ,"🗂️ Restoring categories...")
        category_map ={}
        categories_data = backup_data.get("categories", [])
        for cat_data in sorted (categories_data,key =lambda x :x ["position"]):
            try :
                category =await ctx .guild .create_category (cat_data ["name"])
                category_map [cat_data ["name"]]=category 
                await asyncio .sleep (0.5 )
            except discord .HTTPException as e :
                await self .post_status (status ,f"<:icon_danger:1372375135604047902> Failed to create category {cat_data['name']}: {e}",0x000000 )

        await self .post_status (status ,"📺 Restoring channels...")
        channels_data = backup_data.get("channels", [])
        for ch_data in channels_data:
            try :
                category =category_map .get (ch_data ["category"])
                overwrites ={}
                for perm in ch_data ["overwrites"]:
                    target_id =perm ["id"]
                    target =old_to_new_role .get (target_id )if perm ["type"]=="role"else ctx .guild .get_member (target_id )
                    if target :
                        overwrites [target ]=discord .PermissionOverwrite .from_pair (discord .Permissions (perm ["allow"]),discord .Permissions (perm ["deny"]))
                channel_name =ch_data ["name"][:100 ]
                if ch_data ["type"]=="text":
                    await ctx .guild .create_text_channel (name =channel_name ,topic =ch_data .get ("topic"),slowmode_delay =ch_data .get ("slowmode"),nsfw =ch_data .get ("nsfw",False ),category =category ,overwrites =overwrites )
                elif ch_data ["type"]=="voice":
                    bitrate =min (ch_data .get ("bitrate",64000 ),96000 )
                    await ctx .guild .create_voice_channel (name =channel_name ,bitrate =bitrate ,user_limit =ch_data .get ("user_limit"),category =category ,overwrites =overwrites )
                await asyncio .sleep (0.5 )
            except discord .HTTPException as e :
                await self .post_status (status ,f"<:icon_danger:1372375135604047902> Failed to create channel {ch_data['name']}: {e}",0x000000 )

        await self .post_status (status ,"🙂 Restoring emojis...")
        emojis_data = backup_data.get("emojis", [])
        for e_data in emojis_data:
            try :
                async with self.bot.session.get(e_data["url"]) as resp:
                    if resp .status ==200 :
                        image =await resp .read ()
                        await self .create_emoji_with_retry (ctx .guild ,e_data ["name"],image ,status )
                    else :
                        await self .post_status (status ,f"<:icon_danger:1372375135604047902> Failed to fetch emoji {e_data['name']} image: HTTP {resp.status}",0x000000 )
            except aiohttp .ClientError as e :
                await self .post_status (status ,f"<:icon_danger:1372375135604047902> Failed to fetch emoji {e_data['name']} image: {e}",0x000000 )

        await self .post_status (status ,"<:icon_tick:1372375089668161597> Backup restoration complete!",0x000000 )

async def setup (bot ):
    await bot .add_cog (Backup (bot ))
"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
