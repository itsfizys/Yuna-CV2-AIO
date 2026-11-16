"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
import aiosqlite 
from discord .ext import commands 
from discord import ui
from utils .Tools import blacklist_check ,ignore_check 
from collections import defaultdict 
import time 

class Media (commands .Cog ):
    def __init__ (self ,client ):
        self .client =client 
        self .infractions =defaultdict (list )
        self .client .loop .create_task (self .set_db ())


    async def set_db (self ):
        async with aiosqlite .connect ('db/media.db')as db :
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS media_channels (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER NOT NULL
                )
            ''')
            await db .execute ('''
                CREATE TABLE IF NOT EXISTS media_bypass (
                    guild_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            await db .commit ()


    @commands .hybrid_group (name ="media",help ="Setup Media channel, Media channel will not allow users to send messages other than media files.",invoke_without_command =True )
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    async def media (self ,ctx ):
        if ctx .subcommand_passed is None :
            await ctx .send_help (ctx .command )
            ctx .command .reset_cooldown (ctx )

    @media .command (name ="setup",aliases =["set","add"],help ="Sets up a media-only channel for the server")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def setup (self ,ctx ,*,channel :discord .TextChannel ):
        async with aiosqlite .connect ('db/media.db')as db :
            async with db .execute ('SELECT channel_id FROM media_channels WHERE guild_id = ?',(ctx .guild .id ,))as cursor :
                result =await cursor .fetchone ()
                if result :
                    # Create error view using Components v2
                    error_view = ui.LayoutView()
                    error_container = ui.Container(
                        ui.TextDisplay("❌ **Media Channel Setup**\n\nA media channel is already set. Please remove it before setting a new one."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await ctx .reply (view=error_view)
                    return 

            await db .execute ('INSERT INTO media_channels (guild_id, channel_id) VALUES (?, ?)',(ctx .guild .id ,channel .id ))
            await db .commit ()

        # Create success view using Components v2
        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        
        # Title
        container.add_item(ui.TextDisplay("# <:icon_tick:1372375089668161597> Media Channel Setup"))
        container.add_item(ui.Separator())
        
        # Success message
        success_msg = f"Successfully set {channel.mention} as the media-only channel."
        container.add_item(ui.TextDisplay(success_msg))
        
        container.add_item(ui.Separator())
        
        # Important note
        note_msg = "⚠️ **Important:** Make sure to grant me \"Manage Messages\" permission for functioning of media channel."
        container.add_item(ui.TextDisplay(note_msg))
        
        view.add_item(container)
        await ctx .reply (view=view)

    @media .command (name ="remove",aliases =["reset","delete"],help ="Removes the current media-only channel")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def remove (self ,ctx ):
        async with aiosqlite .connect ('db/media.db')as db :
            async with db .execute ('SELECT channel_id FROM media_channels WHERE guild_id = ?',(ctx .guild .id ,))as cursor :
                result =await cursor .fetchone ()
                if not result :
                    # Create error view using Components v2
                    error_view = ui.LayoutView()
                    error_container = ui.Container(
                        ui.TextDisplay("❌ **Media Channel Remove**\n\nThere is no media-only channel set for this server."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await ctx .reply (view=error_view)
                    return 

            await db .execute ('DELETE FROM media_channels WHERE guild_id = ?',(ctx .guild .id ,))
            await db .commit ()

        # Create success view using Components v2
        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        
        # Title
        container.add_item(ui.TextDisplay("# <:icon_tick:1372375089668161597> Media Channel Removed"))
        container.add_item(ui.Separator())
        
        # Success message
        container.add_item(ui.TextDisplay("Successfully removed the media-only channel."))
        
        view.add_item(container)
        await ctx .reply (view=view)

    @media .command (name ="config",aliases =["settings","show"],help ="Shows the configured media-only channel")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def config (self ,ctx ):
        async with aiosqlite .connect ('db/media.db')as db :
            async with db .execute ('SELECT channel_id FROM media_channels WHERE guild_id = ?',(ctx .guild .id ,))as cursor :
                result =await cursor .fetchone ()
                if not result :
                    # Create error view using Components v2
                    error_view = ui.LayoutView()
                    error_container = ui.Container(
                        ui.TextDisplay("❌ **Media Channel Configuration**\n\nThere is no media-only channel set for this server."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await ctx .reply (view=error_view)
                    return 

        channel =self .client .get_channel (result [0 ])
        if not channel:
            # Create error view if channel was deleted
            error_view = ui.LayoutView()
            error_container = ui.Container(
                ui.TextDisplay("❌ **Channel Not Found**\n\nThe configured media channel has been deleted. Please set up a new one."),
                accent_color=None
            )
            error_view.add_item(error_container)
            await ctx .reply (view=error_view)
            return
            
        # Create config view using Components v2
        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        
        # Title
        container.add_item(ui.TextDisplay("# 📺 Media Channel Configuration"))
        container.add_item(ui.Separator())
        
        # Channel info
        channel_info = f"**Configured Channel:** {channel.mention}\n**Channel ID:** `{channel.id}`"
        container.add_item(ui.TextDisplay(channel_info))
        
        view.add_item(container)
        await ctx .reply (view=view)

    @media .group (name ="bypass",help ="Add/Remove user to bypass in Media only channel, Bypassed users can send messages in Media channel.",invoke_without_command =True )
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def bypass (self ,ctx ):
        if ctx .subcommand_passed is None :
            await ctx .send_help (ctx .command )
            ctx .command .reset_cooldown (ctx )

    @bypass .command (name ="add",help ="Adds a user to the bypass list")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def bypass_add (self ,ctx ,user :discord .Member ):
        async with aiosqlite .connect ('db/media.db')as db :
            async with db .execute ('SELECT COUNT(*) FROM media_bypass WHERE guild_id = ?',(ctx .guild .id ,))as cursor :
                count =await cursor .fetchone ()
                if count [0 ]>=25 :
                    # Create error view using Components v2
                    error_view = ui.LayoutView()
                    error_container = ui.Container(
                        ui.TextDisplay("❌ **Bypass List Full**\n\nThe bypass list can only hold up to 25 users."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await ctx .reply (view=error_view)
                    return 

            async with db .execute ('SELECT 1 FROM media_bypass WHERE guild_id = ? AND user_id = ?',(ctx .guild .id ,user .id ))as cursor :
                result =await cursor .fetchone ()
                if result :
                    # Create error view using Components v2
                    error_view = ui.LayoutView()
                    error_container = ui.Container(
                        ui.TextDisplay(f"❌ **User Already Bypassed**\n\n{user.mention} is already in the bypass list."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await ctx .reply (view=error_view)
                    return 

            await db .execute ('INSERT INTO media_bypass (guild_id, user_id) VALUES (?, ?)',(ctx .guild .id ,user .id ))
            await db .commit ()

        # Create success view using Components v2
        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        
        # Title
        container.add_item(ui.TextDisplay("# <:icon_tick:1372375089668161597> User Added to Bypass"))
        container.add_item(ui.Separator())
        
        # Success message with user avatar as thumbnail if available
        success_msg = f"**User:** {user.mention}\n**Status:** Added to bypass list\n**Can now:** Send messages in media channel"
        if user.avatar:
            container.add_item(
                ui.Section(
                    ui.TextDisplay(success_msg),
                    accessory=ui.Thumbnail(user.avatar.url)
                )
            )
        else:
            container.add_item(ui.TextDisplay(success_msg))
        
        view.add_item(container)
        await ctx .reply (view=view)

    @bypass .command (name ="remove",help ="Removes a user from the bypass list")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def bypass_remove (self ,ctx ,user :discord .Member ):
        async with aiosqlite .connect ('db/media.db')as db :
            async with db .execute ('SELECT 1 FROM media_bypass WHERE guild_id = ? AND user_id = ?',(ctx .guild .id ,user .id ))as cursor :
                result =await cursor .fetchone ()
                if not result :
                    # Create error view using Components v2
                    error_view = ui.LayoutView()
                    error_container = ui.Container(
                        ui.TextDisplay(f"❌ **User Not in Bypass List**\n\n{user.mention} is not in the bypass list."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await ctx .reply (view=error_view)
                    return 

            await db .execute ('DELETE FROM media_bypass WHERE guild_id = ? AND user_id = ?',(ctx .guild .id ,user .id ))
            await db .commit ()

        # Create success view using Components v2
        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        
        # Title
        container.add_item(ui.TextDisplay("# <:icon_tick:1372375089668161597> User Removed from Bypass"))
        container.add_item(ui.Separator())
        
        # Success message with user avatar as thumbnail if available
        success_msg = f"**User:** {user.mention}\n**Status:** Removed from bypass list\n**Restriction:** Can no longer send messages in media channel"
        if user.avatar:
            container.add_item(
                ui.Section(
                    ui.TextDisplay(success_msg),
                    accessory=ui.Thumbnail(user.avatar.url)
                )
            )
        else:
            container.add_item(ui.TextDisplay(success_msg))
        
        view.add_item(container)
        await ctx .reply (view=view)

    @bypass .command (name ="show",aliases =["list","view"],help ="Shows the bypass list")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    @commands .has_permissions (administrator =True )
    async def bypass_show (self ,ctx ):
        async with aiosqlite .connect ('db/media.db')as db :
            async with db .execute ('SELECT user_id FROM media_bypass WHERE guild_id = ?',(ctx .guild .id ,))as cursor :
                result =await cursor .fetchall ()
                if not result :
                    # Create empty list view using Components v2
                    view = ui.LayoutView()
                    container = ui.Container(accent_color=None)
                    
                    # Title
                    container.add_item(ui.TextDisplay("# 📋 Media Bypass List"))
                    container.add_item(ui.Separator())
                    
                    # Empty message
                    container.add_item(ui.TextDisplay("❌ **No Users Found**\n\nThere are no users in the bypass list."))
                    
                    view.add_item(container)
                    await ctx .reply (view=view)
                    return 

        users =[self .client .get_user (user_id ).mention for user_id ,in result ]
        user_mentions ="\n".join (users )

        # Create bypass list view using Components v2
        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        
        # Title
        container.add_item(ui.TextDisplay("# 📋 Media Bypass List"))
        container.add_item(ui.Separator())
        
        # User count info
        count_info = f"**Total Users:** {len(result)}/25"
        container.add_item(ui.TextDisplay(count_info))
        
        container.add_item(ui.Separator())
        
        # User list
        container.add_item(ui.TextDisplay(f"**Bypassed Users:**\n{user_mentions}"))
        
        container.add_item(ui.Separator())
        
        # Footer info
        footer_info = "*These users can send messages in the media-only channel.*"
        container.add_item(ui.TextDisplay(footer_info))
        
        view.add_item(container)
        await ctx .reply (view=view)

    @commands .Cog .listener ()
    async def on_message (self ,message ):
        if message .author .bot or not message .guild :
            return 

        async with aiosqlite .connect ('db/media.db')as db :
            async with db .execute ('SELECT channel_id FROM media_channels WHERE guild_id = ?',(message .guild .id ,))as cursor :
                media_channel =await cursor .fetchone ()

        if media_channel and message .channel .id ==media_channel [0 ]:
            async with aiosqlite .connect ('db/block.db')as block_db :
                async with block_db .execute ('SELECT 1 FROM user_blacklist WHERE user_id = ?',(message .author .id ,))as cursor :
                    blacklisted =await cursor .fetchone ()

            async with aiosqlite .connect ('db/media.db')as db :
                async with db .execute ('SELECT 1 FROM media_bypass WHERE guild_id = ? AND user_id = ?',(message .guild .id ,message .author .id ))as cursor :
                    bypassed =await cursor .fetchone ()

            if blacklisted or bypassed :
                return 

            if not message .attachments :
                try :
                    await message .delete ()
                    await message .channel .send (f"{message.author.mention} This channel is configured for Media only. Please send only media files.",
                    delete_after =5 
                    )
                except discord .Forbidden :
                    pass 
                except discord .HTTPException :
                    pass 
                except Exception as e :
                    pass 

                current_time =time .time ()
                self .infractions [message .author .id ].append (current_time )


                self .infractions [message .author .id ]=[
                infraction for infraction in self .infractions [message .author .id ]
                if current_time -infraction <=5 
                ]

                if len (self .infractions [message .author .id ])>=5 :
                    async with aiosqlite .connect ('db/block.db')as block_db :
                        await block_db .execute ('INSERT OR IGNORE INTO user_blacklist (user_id) VALUES (?)',(message .author .id ,))

                        await block_db .commit ()

                    embed =discord .Embed (
                    title ="You Have Been Blacklisted",
                    description =(
                    "<:icon_danger:1373170993236803688> You are blacklisted from using my commands due to spamming in the media channel. "
                    "If you believe this is a mistake, please reach out to the support server with proof."
                    ),
                    color =0x000000 
                    )
                    await message .channel .send (f"{message.author.mention}",embed =embed )
                    del self .infractions [message .author .id ]


"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
