"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .ext import commands 
import aiosqlite 
import os 
import time 
from typing import Optional 
from utils .Tools import *

black1 =0 
black2 =0 
black3 =0 

DB_PATH ="db/afk.db"


class afk (commands .Cog ):

    def __init__ (self ,client ,*args ,**kwargs ):
        self .client =client 
        self .client .loop .create_task (self .initialize_db ())

    async def initialize_db (self ):
        os .makedirs (os .path .dirname (DB_PATH ),exist_ok =True )
        async with aiosqlite .connect (DB_PATH )as db :
            await db .execute ("""
                CREATE TABLE IF NOT EXISTS afk (
                    user_id INTEGER PRIMARY KEY,
                    AFK TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    time INTEGER NOT NULL,
                    mentions INTEGER NOT NULL,
                    dm TEXT NOT NULL
                )
            """)
            await db .execute ("""
                CREATE TABLE IF NOT EXISTS afk_guild (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            await db .commit ()

    async def cog_after_invoke (self ,ctx ):
        ctx .command .reset_cooldown (ctx )

    async def update_data (self ,user ,guild_id ):
        async with aiosqlite .connect (DB_PATH )as db :
            await db .execute ("INSERT OR IGNORE INTO afk (user_id, AFK, reason, time, mentions, dm) VALUES (?, 'False', 'None', 0, 0, 'False')",(user .id ,))
            await db .execute ("INSERT OR IGNORE INTO afk_guild (user_id, guild_id) VALUES (?, ?)",(user .id ,guild_id ))
            await db .commit ()

    async def time_formatter (self ,seconds :float ):
        minutes ,seconds =divmod (int (seconds ),60 )
        hours ,minutes =divmod (minutes ,60 )
        days ,hours =divmod (hours ,24 )
        tmp =((str (days )+" days, ")if days else "")+((str (hours )+" hours, ")if hours else "")+((str (minutes )+" minutes, ")if minutes else "")+((str (seconds )+" seconds, ")if seconds else "")
        return tmp [:-2 ]

    @commands .Cog .listener ()
    async def on_message (self ,message ):
        try :
            if message .author .bot :
                return 

            async with aiosqlite .connect (DB_PATH )as db :
                cursor =await db .execute ("SELECT AFK, time, mentions, reason FROM afk WHERE user_id = ?",(message .author .id ,))
                afk_data =await cursor .fetchone ()
                await cursor .close ()

                if afk_data and afk_data [0 ]=='True':
                    cursor =await db .execute ("SELECT guild_id FROM afk_guild WHERE user_id = ?",(message .author .id ,))
                    guild_ids =[row [0 ]for row in await cursor .fetchall ()]
                    await cursor .close ()

                    if message .guild .id in guild_ids :
                        meth =int (time .time ())-int (afk_data [1 ])
                        been_afk_for =await self .time_formatter (meth )
                        mentionz =afk_data [2 ]
                        await db .execute ("UPDATE afk SET AFK = 'False', reason = 'None' WHERE user_id = ?",(message .author .id ,))
                        await db .execute ("DELETE FROM afk_guild WHERE user_id = ? AND guild_id = ?",(message .author .id ,message .guild .id ))
                        await db .commit ()
                        # Create welcome back view
                        welcome_view = discord.ui.LayoutView()
                        welcome_container = discord.ui.Container(accent_color=None)
                        
                        welcome_message = f"👋 **{message.author.display_name} Welcome Back!**\nI removed your AFK\n**Total Mentions:** {mentionz}\n**AFK Duration:** {been_afk_for}"
                        welcome_container.add_item(discord.ui.TextDisplay(welcome_message))
                        
                        welcome_view.add_item(welcome_container)
                        try :
                            await message .reply (view=welcome_view)
                        except discord .Forbidden :
                            print (f"(AFK module) Missing permissions to send messages in channel: {message.channel.id}")

            if message .mentions :
                async with aiosqlite .connect (DB_PATH )as db :
                    for user_mention in message .mentions :
                        cursor =await db .execute ("SELECT AFK, reason, time, mentions, dm FROM afk WHERE user_id = ?",(user_mention .id ,))
                        afk_data =await cursor .fetchone ()
                        await cursor .close ()

                        if afk_data and afk_data [0 ]=='True':
                            cursor =await db .execute ("SELECT guild_id FROM afk_guild WHERE user_id = ?",(user_mention .id ,))
                            guild_ids =[row [0 ]for row in await cursor .fetchall ()]
                            await cursor .close ()

                            if message .guild .id in guild_ids :
                                reason =afk_data [1 ]
                                ok =afk_data [2 ]
                                # Create AFK mention notification view
                                mention_view = discord.ui.LayoutView()
                                mention_container = discord.ui.Container(accent_color=None)
                                
                                mention_message = f"💤 **<@{user_mention.id}>** went AFK <t:{ok}:R>\n**Reason:** {reason}"
                                mention_container.add_item(discord.ui.TextDisplay(mention_message))
                                
                                mention_view.add_item(mention_container)
                                try :
                                    await message .reply (view=mention_view)
                                except discord .Forbidden :
                                    print (f"(AFK module) Missing permissions to send messages to user: {user_mention.id}")

                                new_mentions =afk_data [3 ]+1 
                                await db .execute ("UPDATE afk SET mentions = ? WHERE user_id = ?",(new_mentions ,user_mention .id ))
                                await db .commit ()

                                embed =discord .Embed (description =f'You were mentioned in **{message.guild.name}** by **{message.author}**',color =discord .Color .from_rgb (black1 ,black2 ,black3 ))
                                embed .add_field (name ="Total mentions:",value =new_mentions ,inline =False )
                                embed .add_field (name ="Message:",value =message .content ,inline =False )
                                embed .add_field (name ="Jump Message:",value =f"[Jump to message]({message.jump_url})",inline =False )

                                if afk_data [4 ]=='True':
                                    try :
                                        await user_mention .send (embed =embed )
                                    except discord .Forbidden :
                                        print (f"(AFK module) Missing permissions to send DMs to user: {user_mention.id}")

            if not message .author .bot :
                await self .update_data (message .author ,message .guild .id )
        except Exception as e :
            print (f"Ignoring exception in on_message: {e}")

    @commands .hybrid_command (description ="Shows an AFK status when you're mentioned")
    @blacklist_check ()
    @ignore_check ()
    @commands .guild_only ()
    @commands .cooldown (1 ,2 ,commands .BucketType .user )
    async def afk (self ,ctx ,*,reason =None ):
        if not reason :
            reason ="I am afk :)"

        if any (invite in reason .lower ()for invite in ['discord.gg','gg/']):
            emd =discord .Embed (description ="<:icon_danger:1373170993236803688> | You can't advertise Serve Invite in the AFK reason",color =0x0c0606 )
            return await ctx .send (embed =emd )

        # Create Components v2 layout for DM preference
        view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)
        
        # Title and question
        container.add_item(discord.ui.TextDisplay(f"💤 **AFK Settings**\n**User:** {ctx.author.mention}\n**Reason:** {reason}\n**Should I DM you when mentioned?**"))
        
        # Action buttons
        button_row = discord.ui.ActionRow()
        
        yes_button = discord.ui.Button(
            label="Yes",
            style=discord.ButtonStyle.success,
            custom_id="afk_dm_yes"
        )
        
        no_button = discord.ui.Button(
            label="No",
            style=discord.ButtonStyle.secondary,
            custom_id="afk_dm_no"
        )
        
        button_row.add_item(yes_button)
        button_row.add_item(no_button)
        
        # Button callbacks
        async def button_callback(interaction: discord.Interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("You can't use these buttons.", ephemeral=True)
            
            dm_status = 'True' if interaction.data['custom_id'] == 'afk_dm_yes' else 'False'
            
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("INSERT OR REPLACE INTO afk (user_id, AFK, reason, time, mentions, dm) VALUES (?, 'True', ?, ?, 0, ?)",
                (ctx.author.id, reason, int(time.time()), dm_status))
                await db.commit()
                await db.execute("INSERT OR IGNORE INTO afk_guild (user_id, guild_id) VALUES (?, ?)", (ctx.author.id, ctx.guild.id))
                await db.commit()
            
            # Create success view
            success_view = discord.ui.LayoutView()
            success_container = discord.ui.Container(accent_color=None)
            
            success_message = f"<:icon_tick:1372375089668161597> **AFK Activated**\n**Reason:** {reason}\n**DM on mentions:** {'Yes' if dm_status == 'True' else 'No'}\n**Time set:** <t:{int(time.time())}:R>"
            success_container.add_item(discord.ui.TextDisplay(success_message))
            
            success_view.add_item(success_container)
            await interaction.response.edit_message(view=success_view)
        
        yes_button.callback = button_callback
        no_button.callback = button_callback
        
        container.add_item(button_row)
        view.add_item(container)
        
        await ctx.reply(view=view)



"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
