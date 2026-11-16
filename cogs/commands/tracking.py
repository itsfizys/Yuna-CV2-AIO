"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord import app_commands 
from discord .ext import commands 
import aiosqlite 
import logging 
import asyncio 
import json 
import csv 
import io 
from datetime import datetime ,timezone ,timedelta 
from typing import Optional ,Dict ,List ,Tuple 
import random 


logger =logging .getLogger ('discord')


def utc_to_local (dt :datetime )->datetime :
    return dt .replace (tzinfo =timezone .utc )

def format_number (num :int )->str :
    """Format numbers with commas for better readability"""
    return f"{num:,}"

def get_progress_bar (current :int ,total :int ,length :int =10 )->str :
    """Create a visual progress bar"""
    if total ==0 :
        return "▱"*length 
    filled =int ((current /total )*length )
    return "▰"*filled +"▱"*(length -filled )

def get_rank_emoji (position :int )->str :
    """Get emoji for leaderboard positions"""
    rank_emojis ={1 :"🥇",2 :"🥈",3 :"🥉"}
    return rank_emojis .get (position ,"🏷️")

class LeaderboardView (discord .ui .LayoutView ):
    def __init__ (self ,ctx ,cog ):
        super ().__init__ (timeout =300 )
        self .ctx =ctx 
        self .cog =cog 
        self .current_type ="messages"
        self .container =discord .ui .Container (accent_color =None )
        self .add_item (self .container )

    async def interaction_check (self ,interaction ):
        return interaction .user ==self .ctx .author 

    async def on_timeout (self ):
        for item in self .children :
            if hasattr (item ,'disabled'):
                item .disabled =True 
        try :
            await self .message .edit (view =self )
        except :
            pass 

    async def get_message_leaderboard_view (self ):
        """Get message leaderboard Components v2 view"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("""
                    SELECT user_id, total_messages FROM message_tracking 
                    WHERE guild_id = ? AND total_messages > 0 
                    ORDER BY total_messages DESC LIMIT 15
                """,(self .ctx .guild .id ,))as cursor :
                    rows =await cursor .fetchall ()

            self .container .clear_items ()
            self .container .add_item (discord .ui .TextDisplay ("# 📊 All-Time Message Champions"))
            self .container .add_item (discord .ui .Separator ())

            if not rows :
                self .container .add_item (discord .ui .TextDisplay (
                    "No message data found yet!\n\nStart chatting to appear on the leaderboard!"
                ))
            else :
                total_msgs =sum (row [1 ]for row in rows )
                description =f"**Total Server Messages:** {format_number(total_msgs)}\n\n"

                for i ,(user_id ,messages )in enumerate (rows [:10 ],1 ):
                    user =self .cog .bot .get_user (user_id )
                    username =user .display_name if user else f"Unknown User"
                    emoji =get_rank_emoji (i )
                    percentage =(messages /total_msgs *100 )if total_msgs >0 else 0 
                    description +=f"{emoji} **{username}** - {format_number(messages)} messages ({percentage:.1f}%)\n"

                self .container .add_item (discord .ui .TextDisplay (description ))
                self .container .add_item (discord .ui .Separator ())
                self .container .add_item (discord .ui .TextDisplay (
                    f"Showing top {len(rows[:10])} of {len(rows)} active members"
                ))
        except Exception as e :
            logger .error (f"Error in message leaderboard: {e}")
            self .container .clear_items ()
            self .container .add_item (discord .ui .TextDisplay ("An error occurred loading the leaderboard"))

    async def get_invite_leaderboard_view (self ):
        """Get invite leaderboard Components v2 view"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("""
                    SELECT user_id, real_invites, total_joins, left_invites FROM invite_tracking 
                    WHERE guild_id = ? AND total_joins > 0 
                    ORDER BY real_invites DESC LIMIT 15
                """,(self .ctx .guild .id ,))as cursor :
                    rows =await cursor .fetchall ()

            self .container .clear_items ()
            self .container .add_item (discord .ui .TextDisplay ("# 🎯 Top Community Builders"))
            self .container .add_item (discord .ui .Separator ())

            if not rows :
                self .container .add_item (discord .ui .TextDisplay (
                    "No invite data found yet!\n\nStart inviting friends to grow our community!"
                ))
            else :
                total_invites =sum (row [1 ]for row in rows )
                total_joins =sum (row [2 ]for row in rows )

                description =f"**Total Active Invites:** {format_number(total_invites)}\n"
                description +=f"**Total Members Joined:** {format_number(total_joins)}\n\n"

                for i ,(user_id ,real_invites ,total_joins ,left_invites )in enumerate (rows [:10 ],1 ):
                    user =self .cog .bot .get_user (user_id )
                    username =user .display_name if user else f"Unknown User"
                    emoji =get_rank_emoji (i )
                    retention_rate =((real_invites /total_joins )*100 )if total_joins >0 else 0 
                    description +=f"{emoji} **{username}** - {format_number(real_invites)} active invites "
                    description +=f"({retention_rate:.0f}% retention)\n"

                self .container .add_item (discord .ui .TextDisplay (description ))
                self .container .add_item (discord .ui .Separator ())
                self .container .add_item (discord .ui .TextDisplay (
                    f"Showing top {len(rows[:10])} of {len(rows)} inviters • Retention = Active/Total"
                ))
        except Exception as e :
            logger .error (f"Error in invite leaderboard: {e}")
            self .container .clear_items ()
            self .container .add_item (discord .ui .TextDisplay ("An error occurred loading the leaderboard"))

    @discord .ui .button (label ="📊 Messages",style =discord .ButtonStyle .primary ,emoji ="📊")
    async def messages_button (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        """Show message leaderboard"""
        if self .current_type =="messages":
            await interaction .response .defer ()
            return 

        self .current_type ="messages"
        await self .get_message_leaderboard_view ()
        await interaction .response .edit_message (view =self )

    @discord .ui .button (label ="🎯 Invites",style =discord .ButtonStyle .secondary ,emoji ="🎯")
    async def invites_button (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
        """Show invite leaderboard"""
        if self .current_type =="invites":
            await interaction .response .defer ()
            return 

        self .current_type ="invites"
        await self .get_invite_leaderboard_view ()
        await interaction .response .edit_message (view =self )

class TrackingCog (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .invite_cache ={}
        self .message_tracking_enabled ={}
        self .invite_tracking_enabled ={}
        self .invite_log_channels ={}
        self .use_embed_logs ={}

    async def cog_load (self ):
        """Initialize database tables and cache"""
        try :
            await self .init_database ()
            await self .load_settings ()
            await self .cache_invites ()

        except Exception as e :
            logger .error (f"Error loading TrackingCog: {e}")

    async def init_database (self ):
        """Initialize all required database tables"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :

                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS message_tracking (
                        guild_id INTEGER,
                        user_id INTEGER,
                        total_messages INTEGER DEFAULT 0,
                        daily_messages INTEGER DEFAULT 0,
                        last_daily_reset TEXT,
                        PRIMARY KEY (guild_id, user_id)
                    )
                """)


                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS invite_tracking (
                        guild_id INTEGER,
                        user_id INTEGER,
                        real_invites INTEGER DEFAULT 0,
                        fake_invites INTEGER DEFAULT 0,
                        left_invites INTEGER DEFAULT 0,
                        total_joins INTEGER DEFAULT 0,
                        PRIMARY KEY (guild_id, user_id)
                    )
                """)


                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS invite_details (
                        guild_id INTEGER,
                        inviter_id INTEGER,
                        invited_user_id INTEGER,
                        invite_code TEXT,
                        joined_at TEXT,
                        status TEXT DEFAULT 'joined'
                    )
                """)


                await db .execute ("""
                    CREATE TABLE IF NOT EXISTS tracking_settings (
                        guild_id INTEGER PRIMARY KEY,
                        join_leave_channel INTEGER,
                        invite_logs_channel INTEGER,
                        enabled INTEGER DEFAULT 1,
                        join_message TEXT,
                        leave_message TEXT,
                        dm_message TEXT,
                        join_role INTEGER,
                        auto_delete_invites INTEGER DEFAULT 0,
                        track_all_invites INTEGER DEFAULT 1,
                        use_embed_logs INTEGER DEFAULT 1
                    )
                """)


                try :
                    await db .execute ("ALTER TABLE tracking_settings ADD COLUMN use_embed_logs INTEGER DEFAULT 1")
                except Exception as e :

                    pass 

                await db .commit ()
        except Exception as e :
            logger .error (f"Database initialization error: {e}")

    async def load_settings (self ):
        """Load tracking settings from database"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("SELECT guild_id, message_tracking_enabled, invite_tracking_enabled, invite_log_channel_id, use_embed_logs FROM tracking_settings")as cursor :
                    async for row in cursor :
                        guild_id ,msg_enabled ,inv_enabled ,log_channel ,use_embed =row 
                        self .message_tracking_enabled [guild_id ]=bool (msg_enabled )
                        self .invite_tracking_enabled [guild_id ]=bool (inv_enabled )
                        if log_channel :
                            self .invite_log_channels [guild_id ]=log_channel 
                        self .use_embed_logs [guild_id ]=bool (use_embed if use_embed is not None else True )
        except Exception as e :
            logger .error (f"Error loading settings: {e}")

    async def cache_invites (self ):
        """Cache all guild invites"""
        for guild in self .bot .guilds :
            try :
                invites =await guild .invites ()
                self .invite_cache [guild .id ]={invite .code :invite .uses for invite in invites }
            except (discord .Forbidden ,discord .HTTPException )as e :
                logger .warn (f"Could not cache invites for guild {guild.id}: {e}")

    async def get_or_create_settings (self ,guild_id :int ):
        """Get or create tracking settings for a guild"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("SELECT * FROM tracking_settings WHERE guild_id = ?",(guild_id ,))as cursor :
                    row =await cursor .fetchone ()
                    if not row :
                        await db .execute ("INSERT INTO tracking_settings (guild_id) VALUES (?)",(guild_id ,))
                        await db .commit ()
                        self .message_tracking_enabled [guild_id ]=True 
                        self .invite_tracking_enabled [guild_id ]=True 
        except Exception as e :
            logger .error (f"Error creating settings for guild {guild_id}: {e}")

    async def reset_daily_messages (self ,guild_id :int ):
        """Reset daily message counts"""
        try :
            today =datetime .now (timezone .utc ).date ().isoformat ()
            async with aiosqlite .connect ("db/tracking.db")as db :
                await db .execute ("""
                    UPDATE message_tracking 
                    SET daily_messages = 0, last_daily_reset = ? 
                    WHERE guild_id = ? AND (last_daily_reset != ? OR last_daily_reset IS NULL)
                """,(today ,guild_id ,today ))
                await db .commit ()
        except Exception as e :
            logger .error (f"Error resetting daily messages for guild {guild_id}: {e}")

    @commands .Cog .listener ()
    async def on_message (self ,message ):
        """Track message counts - always runs in background for data collection"""
        if message .author .bot or not message .guild :
            return 

        guild_id =message .guild .id 



        try :
            await self .reset_daily_messages (guild_id )

            async with aiosqlite .connect ("db/tracking.db")as db :
                await db .execute ("""
                    INSERT OR IGNORE INTO message_tracking (guild_id, user_id, last_daily_reset) 
                    VALUES (?, ?, ?)
                """,(guild_id ,message .author .id ,datetime .now (timezone .utc ).date ().isoformat ()))

                await db .execute ("""
                    UPDATE message_tracking 
                    SET total_messages = total_messages + 1, daily_messages = daily_messages + 1
                    WHERE guild_id = ? AND user_id = ?
                """,(guild_id ,message .author .id ))
                await db .commit ()
        except Exception as e :
            logger .error (f"Error tracking message for user {message.author.id} in guild {guild_id}: {e}")




    @commands .Cog .listener ()
    async def on_member_join (self ,member ):
        """Track invite usage when member joins"""
        if not self .invite_tracking_enabled .get (member .guild .id ,True ):
            return 

        try :

            new_invites =await member .guild .invites ()
            new_invite_dict ={invite .code :invite .uses for invite in new_invites }
            old_invite_dict =self .invite_cache .get (member .guild .id ,{})

            inviter =None 
            used_invite =None 


            for code ,new_uses in new_invite_dict .items ():
                old_uses =old_invite_dict .get (code ,0 )
                if new_uses >old_uses :

                    for invite in new_invites :
                        if invite .code ==code :
                            inviter =invite .inviter 
                            used_invite =invite 
                            break 
                    break 


            if not inviter :
                for code ,uses in new_invite_dict .items ():
                    if code not in old_invite_dict and uses >0 :
                        for invite in new_invites :
                            if invite .code ==code :
                                inviter =invite .inviter 
                                used_invite =invite 
                                break 
                        if inviter :
                            break 


            self .invite_cache [member .guild .id ]=new_invite_dict 


            if inviter and inviter !=member and inviter .id !=member .id :
                await self .add_invite_join (member .guild .id ,inviter .id ,member .id ,used_invite .code if used_invite else "unknown")


                log_channel_id =self .invite_log_channels .get (member .guild .id )
                if log_channel_id :
                    log_channel =self .bot .get_channel (log_channel_id )
                    if log_channel :
                        use_embed =self .use_embed_logs .get (member .guild .id ,True )
                        account_age =f"<t:{int(member.created_at.timestamp())}:R>"

                        if use_embed :
                            embed =discord .Embed (
                            title ="📥 Welcome New Member!",
                            description =f"**Member:** {member.mention} ({member.display_name})\n"
                            f"**Invited by:** {inviter.mention}\n"
                            f"**Invite Code:** `{used_invite.code if used_invite else 'Unknown'}`\n"
                            f"**Account Created:** {account_age}",
                            color =0x000000 ,
                            timestamp =datetime .now (timezone .utc )
                            )
                            embed .set_thumbnail (url =member .avatar .url if member .avatar else member .default_avatar .url )
                            embed .set_footer (text =f"User ID: {member.id}")
                            await log_channel .send (embed =embed )
                        else :

                            message =(f"📥 **Welcome New Member!** {member.mention} ({member.display_name}) "
                            f"was invited by {inviter.mention} using invite code `{used_invite.code if used_invite else 'Unknown'}`. "
                            f"Account was created {account_age}. User ID: {member.id}")
                            await log_channel .send (message )
            else :

                log_channel_id =self .invite_log_channels .get (member .guild .id )
                if log_channel_id :
                    log_channel =self .bot .get_channel (log_channel_id )
                    if log_channel :
                        use_embed =self .use_embed_logs .get (member .guild .id ,True )
                        account_age =f"<t:{int(member.created_at.timestamp())}:R>"

                        if use_embed :
                            embed =discord .Embed (
                            title ="📥 Welcome New Member!",
                            description =f"**Member:** {member.mention} ({member.display_name})\n"
                            f"**Joined via:** Unknown invite\n"
                            f"**Account Created:** {account_age}",
                            color =0x000000 ,
                            timestamp =datetime .now (timezone .utc )
                            )
                            embed .set_thumbnail (url =member .avatar .url if member .avatar else member .default_avatar .url )
                            embed .set_footer (text =f"User ID: {member.id}")
                            await log_channel .send (embed =embed )
                        else :
                            message =(f"📥 **Welcome New Member!** {member.mention} ({member.display_name}) "
                            f"joined the server. Unable to determine inviter. "
                            f"Account was created {account_age}. User ID: {member.id}")
                            await log_channel .send (message )

        except (discord .Forbidden ,discord .HTTPException )as e :
            logger .warn (f"Error tracking invite for member {member.id} in guild {member.guild.id}: {e}")
        except Exception as e :
            logger .error (f"Unexpected error in invite tracking for member {member.id}: {e}")

    @commands .Cog .listener ()
    async def on_member_remove (self ,member ):
        """Track when invited members leave"""
        if not self .invite_tracking_enabled .get (member .guild .id ,True ):
            return 

        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("""
                    SELECT inviter_id FROM invite_details 
                    WHERE guild_id = ? AND invited_user_id = ? AND status = 'joined'
                """,(member .guild .id ,member .id ))as cursor :
                    row =await cursor .fetchone ()

                    if row :
                        inviter_id =row [0 ]

                        await db .execute ("""
                            UPDATE invite_details 
                            SET status = 'left' 
                            WHERE guild_id = ? AND invited_user_id = ?
                        """,(member .guild .id ,member .id ))

                        await db .execute ("""
                            UPDATE invite_tracking 
                            SET left_invites = left_invites + 1, real_invites = real_invites - 1
                            WHERE guild_id = ? AND user_id = ?
                        """,(member .guild .id ,inviter_id ))
                        await db .commit ()


                        log_channel_id =self .invite_log_channels .get (member .guild .id )
                        if log_channel_id :
                            log_channel =self .bot .get_channel (log_channel_id )
                            if log_channel :
                                inviter =self .bot .get_user (inviter_id )
                                inviter_text =inviter .mention if inviter else 'Unknown User'
                                use_embed =self .use_embed_logs .get (member .guild .id ,True )

                                if member .joined_at :
                                    time_in_server =f"<t:{int(member.joined_at.timestamp())}:R>"
                                else :
                                    time_in_server ="Unknown duration"

                                if use_embed :
                                    embed =discord .Embed (
                                    title ="📤 Member Left",
                                    description =f"**Member:** {member.mention} ({member.display_name})\n"
                                    f"**Originally invited by:** {inviter_text}\n"
                                    f"**Time in server:** {time_in_server}",
                                    color =0x000000 ,
                                    timestamp =datetime .now (timezone .utc )
                                    )
                                    embed .set_thumbnail (url =member .avatar .url if member .avatar else member .default_avatar .url )
                                    embed .set_footer (text =f"User ID: {member.id}")
                                    await log_channel .send (embed =embed )
                                else :

                                    message =(f"📤 **Member Left** {member.mention} ({member.display_name}) "
                                    f"has left the server. They were originally invited by {inviter_text} "
                                    f"and spent {time_in_server} in the server. User ID: {member.id}")
                                    await log_channel .send (message )
                    else :

                        log_channel_id =self .invite_log_channels .get (member .guild .id )
                        if log_channel_id :
                            log_channel =self .bot .get_channel (log_channel_id )
                            if log_channel :
                                use_embed =self .use_embed_logs .get (member .guild .id ,True )

                                if member .joined_at :
                                    time_in_server =f"<t:{int(member.joined_at.timestamp())}:R>"
                                else :
                                    time_in_server ="Unknown duration"

                                if use_embed :
                                    embed =discord .Embed (
                                    title ="📤 Member Left",
                                    description =f"**Member:** {member.mention} ({member.display_name})\n"
                                    f"**Time in server:** {time_in_server}",
                                    color =0x000000 ,
                                    timestamp =datetime .now (timezone .utc )
                                    )
                                    embed .set_thumbnail (url =member .avatar .url if member .avatar else member .default_avatar .url )
                                    embed .set_footer (text =f"User ID: {member.id}")
                                    await log_channel .send (embed =embed )
                                else :
                                    message =(f"📤 **Member Left** {member.mention} ({member.display_name}) "
                                    f"has left the server after {time_in_server}. "
                                    f"User ID: {member.id}")
                                    await log_channel .send (message )

        except Exception as e :
            logger .error (f"Error tracking member leave for {member.id} in guild {member.guild.id}: {e}")

    async def add_invite_join (self ,guild_id :int ,inviter_id :int ,invited_user_id :int ,invite_code :str ):
        """Add an invite join record"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                await db .execute ("""
                    INSERT OR IGNORE INTO invite_tracking (guild_id, user_id) VALUES (?, ?)
                """,(guild_id ,inviter_id ))

                await db .execute ("""
                    UPDATE invite_tracking 
                    SET real_invites = real_invites + 1, total_joins = total_joins + 1
                    WHERE guild_id = ? AND user_id = ?
                """,(guild_id ,inviter_id ))

                await db .execute ("""
                    INSERT INTO invite_details (guild_id, inviter_id, invited_user_id, invite_code, joined_at)
                    VALUES (?, ?, ?, ?, ?)
                """,(guild_id ,inviter_id ,invited_user_id ,invite_code ,datetime .now (timezone .utc ).isoformat ()))

                await db .commit ()
        except Exception as e :
            logger .error (f"Error adding invite join record: {e}")


    @commands .hybrid_group (name ="tracking",invoke_without_command =True ,description ="Manage the tracking system")
    @commands .has_permissions (administrator =True )
    async def tracking (self ,ctx ):
        """Manage the tracking system."""
        await ctx .send_help (ctx .command )

    @tracking .command (name ="enable",description ="Enable tracking features")
    @app_commands .describe (feature ="Feature to enable: messages or invites")
    @commands .has_permissions (administrator =True )
    async def tracking_enable (self ,ctx ,feature :str ):
        """Enable tracking features (messages/invites)"""
        feature =feature .lower ()
        if feature not in ["messages","invites"]:
            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# Invalid Feature"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay ("Available features: messages, invites"))
            view .add_item (container )
            await ctx .send (view =view )
            return 

        try :
            await self .get_or_create_settings (ctx .guild .id )

            async with aiosqlite .connect ("db/tracking.db")as db :
                if feature =="messages":
                    await db .execute ("""
                        UPDATE tracking_settings SET message_tracking_enabled = 1 WHERE guild_id = ?
                    """,(ctx .guild .id ,))
                    self .message_tracking_enabled [ctx .guild .id ]=True 
                    message ="Message tracking enabled"
                else :
                    await db .execute ("""
                        UPDATE tracking_settings SET invite_tracking_enabled = 1 WHERE guild_id = ?
                    """,(ctx .guild .id ,))
                    self .invite_tracking_enabled [ctx .guild .id ]=True 
                    message ="Invite tracking enabled"

                await db .commit ()

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# ✅ Tracking Feature Enabled"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (message ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Enabled by {ctx.author.mention}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error enabling tracking: {e}")
            pass 

    @tracking .command (name ="disable",description ="Disable tracking features")
    @app_commands .describe (feature ="Feature to disable: messages or invites")
    @commands .has_permissions (administrator =True )
    async def tracking_disable (self ,ctx ,feature :str ):
        """Disable tracking features (messages/invites)"""
        feature =feature .lower ()
        if feature not in ["messages","invites"]:
            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# Invalid Feature"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay ("Available features: messages, invites"))
            view .add_item (container )
            await ctx .send (view =view )
            return 

        try :
            await self .get_or_create_settings (ctx .guild .id )

            async with aiosqlite .connect ("db/tracking.db")as db :
                if feature =="messages":
                    await db .execute ("""
                        UPDATE tracking_settings SET message_tracking_enabled = 0 WHERE guild_id = ?
                    """,(ctx .guild .id ,))
                    self .message_tracking_enabled [ctx .guild .id ]=False 
                    message ="Message tracking disabled"
                else :
                    await db .execute ("""
                        UPDATE tracking_settings SET invite_tracking_enabled = 0 WHERE guild_id = ?
                    """,(ctx .guild .id ,))
                    self .invite_tracking_enabled [ctx .guild .id ]=False 
                    message ="Invite tracking disabled"

                await db .commit ()

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# ⏸️ Tracking Feature Disabled"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (message ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Disabled by {ctx.author.mention}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error disabling tracking: {e}")
            pass 

    @tracking .command (name ="status",description ="View comprehensive tracking system status")
    async def tracking_status (self ,ctx ):
        """View comprehensive tracking system status"""
        try :
            await self .get_or_create_settings (ctx .guild .id )

            message_enabled =self .message_tracking_enabled .get (ctx .guild .id ,True )
            invite_enabled =self .invite_tracking_enabled .get (ctx .guild .id ,True )
            log_channel_id =self .invite_log_channels .get (ctx .guild .id )
            log_channel =self .bot .get_channel (log_channel_id )if log_channel_id else None 


            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("SELECT COUNT(*), SUM(total_messages), SUM(daily_messages) FROM message_tracking WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    msg_count ,total_msgs ,daily_msgs =await cursor .fetchone ()

                async with db .execute ("SELECT COUNT(*), SUM(real_invites), SUM(total_joins) FROM invite_tracking WHERE guild_id = ?",(ctx .guild .id ,))as cursor :
                    inv_count ,total_invites ,total_joins =await cursor .fetchone ()

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# 📊 Tracking System Status"))
            container .add_item (discord .ui .Separator ())
            
            status_text =f"**System Status**\n"
            status_text +=f"Message Tracking: {'✅ Enabled' if message_enabled else '⏸️ Disabled'}\n"
            status_text +=f"Invite Tracking: {'✅ Enabled' if invite_enabled else '⏸️ Disabled'}\n"
            status_text +=f"Log Channel: {log_channel.mention if log_channel else '❌ Not set'}\n\n"
            status_text +=f"**Statistics**\n"
            status_text +=f"Message Users: {msg_count or 0} users tracked\n"
            status_text +=f"Total Messages: {format_number(total_msgs or 0)}\n"
            status_text +=f"Today's Messages: {format_number(daily_msgs or 0)}\n\n"
            status_text +=f"Invite Users: {inv_count or 0} inviters tracked\n"
            status_text +=f"Active Invites: {format_number(total_invites or 0)}\n"
            status_text +=f"Total Joins: {format_number(total_joins or 0)}"
            
            container .add_item (discord .ui .TextDisplay (status_text ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"⏰ Updated <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in tracking_status: {e}")
            pass 

    @tracking .command (name ="setup",description ="Setup tracking for messages and invites")
    @commands .has_permissions (administrator =True )
    async def tracking_setup (self ,ctx ):
        """Run the tracking system setup wizard"""
        try :
            await self .get_or_create_settings (ctx .guild .id )

            class SetupView (discord .ui .LayoutView ):
                def __init__ (self ,parent_cog ,guild_id ,author ):
                    super ().__init__ (timeout =30 )
                    self .cog =parent_cog 
                    self .guild_id =guild_id 
                    self .author =author 
                    self .use_embed =True 
                    self .container =discord .ui .Container (accent_color =None )
                    self .add_item (self .container )
                    self .setup_initial_view ()

                def setup_initial_view (self ):
                    self .container .clear_items ()
                    self .container .add_item (discord .ui .TextDisplay ("# ⚙️ Tracking System Setup - Log Format"))
                    self .container .add_item (discord .ui .Separator ())
                    self .container .add_item (discord .ui .TextDisplay (
                        "Choose your preferred format for invite join/leave logs:\n\n"
                        "**📊 Embed Format** - Rich embeds with thumbnails and formatting\n"
                        "**📝 Text Format** - Simple text messages (lighter on resources)\n\n"
                        "Click a button below to select your preference.\n"
                        "This setting can be changed later with the `tracking logformat` command."
                    ))

                async def interaction_check (self ,interaction ):
                    return interaction .user ==self .author 

                @discord .ui .button (label ="📊 Embed Format",style =discord .ButtonStyle .primary )
                async def embed_button (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
                    self .use_embed =True 
                    await self .complete_setup (interaction ,"embed")

                @discord .ui .button (label ="📝 Text Format",style =discord .ButtonStyle .secondary )
                async def text_button (self ,interaction :discord .Interaction ,button :discord .ui .Button ):
                    self .use_embed =False 
                    await self .complete_setup (interaction ,"text")

                async def complete_setup (self ,interaction ,format_name ):
                    try :
                        async with aiosqlite .connect ("db/tracking.db")as db :
                            await db .execute ("""
                                UPDATE tracking_settings 
                                SET use_embed_logs = ? 
                                WHERE guild_id = ?
                            """,(1 if self .use_embed else 0 ,self .guild_id ))
                            await db .commit ()

                        self .cog .use_embed_logs [self .guild_id ]=self .use_embed 

                        self .container .clear_items ()
                        self .container .add_item (discord .ui .TextDisplay ("# ✅ Tracking System Setup Complete"))
                        self .container .add_item (discord .ui .Separator ())
                        self .container .add_item (discord .ui .TextDisplay (
                            f"**Log Format:** {format_name}\n\n"
                            "**Available Features:**\n"
                            "• Message Tracking - Track user activity and engagement\n"
                            "• Invite Tracking - Monitor community growth and inviters\n"
                            "• Leaderboards - Gamify user participation\n"
                            "• Detailed Logs - Track joins/leaves with context\n\n"
                            "**Quick Setup Commands:**\n"
                            "`tracking enable messages` - Start tracking messages\n"
                            "`tracking enable invites` - Start tracking invites\n"
                            "`tracking setlogchannel #logs` - Set up invite logging\n"
                            "`tracking testinvite` - Test invite tracking\n\n"
                            "**User Commands:**\n"
                            "`messages` - View message stats\n"
                            "`invites` - View invite stats\n"
                            "`leaderboard` - View various leaderboards"
                        ))
                        self .container .add_item (discord .ui .Separator ())
                        self .container .add_item (discord .ui .TextDisplay (f"⏰ Completed <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
                        
                        for item in self .children :
                            if isinstance (item ,discord .ui .Button ):
                                item .disabled =True 
                        
                        await interaction .response .edit_message (view =self )
                    except Exception as e :
                        logger .error (f"Error completing setup: {e}")

                async def on_timeout (self ):
                    try :
                        async with aiosqlite .connect ("db/tracking.db")as db :
                            await db .execute ("""
                                UPDATE tracking_settings 
                                SET use_embed_logs = 1 
                                WHERE guild_id = ?
                            """,(self .guild_id ,))
                            await db .commit ()
                        self .cog .use_embed_logs [self .guild_id ]=True 
                    except Exception as e :
                        logger .error (f"Error in setup timeout: {e}")

            view =SetupView (self ,ctx .guild .id ,ctx .author )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in tracking_setup: {e}")
            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# ❌ Setup Error"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"An error occurred during setup: {str(e)}"))
            view .add_item (container )
            await ctx .send (view =view ) 

    @tracking .command (name ="wipe",description ="Wipe ALL tracking data for this server")
    @commands .has_permissions (administrator =True )
    async def tracking_wipe_all (self ,ctx ,):
        """Wipe ALL tracking data for this server (DANGEROUS - Admin Only)"""
        view =discord .ui .LayoutView ()
        container =discord .ui .Container (accent_color =None )
        container .add_item (discord .ui .TextDisplay ("# ⚠️ DANGER: Complete Data Wipe"))
        container .add_item (discord .ui .Separator ())
        container .add_item (discord .ui .TextDisplay (
            "This action is IRREVERSIBLE!\n\n"
            "This will permanently delete:\n"
            "• All message tracking data\n"
            "• All invite tracking data\n"
            "• All leaderboard history\n"
            "• All configuration settings\n\n"
            "To confirm this dangerous action, type: `CONFIRM WIPE`\n\n"
            "You have 30 seconds to confirm."
        ))
        view .add_item (container )
        await ctx .send (view =view )

        def check (m ):
            return m .author ==ctx .author and m .channel ==ctx .channel and m .content =="CONFIRM WIPE"

        try :
            await self .bot .wait_for ('message',check =check ,timeout =30.0 )
        except asyncio .TimeoutError :
            view2 =discord .ui .LayoutView ()
            container2 =discord .ui .Container (accent_color =None )
            container2 .add_item (discord .ui .TextDisplay ("# Wipe Cancelled"))
            container2 .add_item (discord .ui .Separator ())
            container2 .add_item (discord .ui .TextDisplay ("Data wipe was cancelled due to timeout. All data remains safe."))
            view2 .add_item (container2 )
            await ctx .send (view =view2 )
            return 

        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                await db .execute ("DELETE FROM message_tracking WHERE guild_id = ?",(ctx .guild .id ,))
                await db .execute ("DELETE FROM invite_tracking WHERE guild_id = ?",(ctx .guild .id ,))
                await db .execute ("DELETE FROM invite_details WHERE guild_id = ?",(ctx .guild .id ,))
                await db .execute ("DELETE FROM tracking_settings WHERE guild_id = ?",(ctx .guild .id ,))
                await db .commit ()


            self .message_tracking_enabled .pop (ctx .guild .id ,None )
            self .invite_tracking_enabled .pop (ctx .guild .id ,None )
            self .invite_log_channels .pop (ctx .guild .id ,None )

            view3 =discord .ui .LayoutView ()
            container3 =discord .ui .Container (accent_color =None )
            container3 .add_item (discord .ui .TextDisplay ("# Data Wipe Complete"))
            container3 .add_item (discord .ui .Separator ())
            container3 .add_item (discord .ui .TextDisplay (
                "All tracking data has been permanently deleted.\n\n"
                "The tracking system has been reset to factory defaults."
            ))
            container3 .add_item (discord .ui .Separator ())
            container3 .add_item (discord .ui .TextDisplay (f"Wiped by {ctx.author.mention}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view3 .add_item (container3 )
            await ctx .send (view =view3 )
        except Exception as e :
            logger .error (f"Error in tracking_wipe_all: {e}")
            pass 

    @tracking .command (name ="export",description ="Export tracking data in JSON or CSV format")
    @app_commands .describe (format ="Export format: json or csv")
    @commands .has_permissions (administrator =True )
    async def tracking_export (self ,ctx ,format :str ="json"):
        """Export tracking data in JSON or CSV format"""
        if format .lower ()not in ["json","csv"]:
            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# Invalid Format"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay ("Available formats: json, csv"))
            view .add_item (container )
            await ctx .send (view =view )
            return 

        try :

            async with aiosqlite .connect ("db/tracking.db")as db :

                async with db .execute ("""
                    SELECT user_id, total_messages, daily_messages FROM message_tracking WHERE guild_id = ?
                """,(ctx .guild .id ,))as cursor :
                    message_data =await cursor .fetchall ()


                async with db .execute ("""
                    SELECT user_id, real_invites, fake_invites, left_invites, total_joins FROM invite_tracking WHERE guild_id = ?
                """,(ctx .guild .id ,))as cursor :
                    invite_data =await cursor .fetchall ()

            if format .lower ()=="json":
                data ={
                "guild_id":ctx .guild .id ,
                "guild_name":ctx .guild .name ,
                "exported_at":datetime .now (timezone .utc ).isoformat (),
                "exported_by":str (ctx .author ),
                "message_tracking":[
                {"user_id":uid ,"total_messages":total ,"daily_messages":daily }
                for uid ,total ,daily in message_data 
                ],
                "invite_tracking":[
                {"user_id":uid ,"real_invites":real ,"fake_invites":fake ,"left_invites":left ,"total_joins":total }
                for uid ,real ,fake ,left ,total in invite_data 
                ]
                }

                file_content =json .dumps (data ,indent =2 )
                file =discord .File (io .StringIO (file_content ),filename =f"tracking_export_{ctx.guild.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

            else :
                output =io .StringIO ()
                writer =csv .writer (output )


                writer .writerow ([f"=== TRACKING DATA EXPORT FOR {ctx.guild.name} ==="])
                writer .writerow ([f"Exported: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"])
                writer .writerow ([f"Exported by: {ctx.author}"])
                writer .writerow ([])


                writer .writerow (["=== MESSAGE TRACKING ==="])
                writer .writerow (["User ID","Total Messages","Daily Messages"])
                for row in message_data :
                    writer .writerow (row )

                writer .writerow ([])
                writer .writerow (["=== INVITE TRACKING ==="])
                writer .writerow (["User ID","Real Invites","Fake Invites","Left Invites","Total Joins"])
                for row in invite_data :
                    writer .writerow (row )

                file_content =output .getvalue ()
                output .close ()
                file =discord .File (io .StringIO (file_content ),filename =f"tracking_export_{ctx.guild.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# 📦 Data Export Complete"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (
                f"Format: {format.upper()}\n"
                f"Message Records: {len(message_data)}\n"
                f"Invite Records: {len(invite_data)}\n"
                f"Generated: <t:{int(datetime.now().timestamp())}:R>\n\n"
                f"Your tracking data has been exported and attached to this message."
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Exported by {ctx.author.mention}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view ,file =file )
        except Exception as e :
            logger .error (f"Error in tracking_export: {e}")
            pass 

    @tracking .command (name ="import",description ="Import tracking data from JSON format")
    @commands .has_permissions (administrator =True )
    async def tracking_import (self ,ctx ):
        """Import tracking data from JSON format"""
        view =discord .ui .LayoutView ()
        container =discord .ui .Container (accent_color =None )
        container .add_item (discord .ui .TextDisplay ("# 📥 Import Tracking Data"))
        container .add_item (discord .ui .Separator ())
        container .add_item (discord .ui .TextDisplay (
            "Import Instructions:\n\n"
            "1. Attach a JSON file exported from this tracking system\n"
            "2. The file must be under 8MB in size\n"
            "3. Data will be merged with existing records\n\n"
            "You have 60 seconds to attach a file."
        ))
        view .add_item (container )
        await ctx .send (view =view )

        def check (m ):
            return (m .author ==ctx .author and m .channel ==ctx .channel and 
            m .attachments and m .attachments [0 ].filename .endswith ('.json'))

        try :
            message =await self .bot .wait_for ('message',check =check ,timeout =60.0 )
        except asyncio .TimeoutError :
            view2 =discord .ui .LayoutView ()
            container2 =discord .ui .Container (accent_color =None )
            container2 .add_item (discord .ui .TextDisplay ("# Import Timeout"))
            container2 .add_item (discord .ui .Separator ())
            container2 .add_item (discord .ui .TextDisplay ("Import cancelled due to timeout. Please try again."))
            view2 .add_item (container2 )
            await ctx .send (view =view2 )
            return 

        attachment =message .attachments [0 ]
        if attachment .size >8 *1024 *1024 :
            view3 =discord .ui .LayoutView ()
            container3 =discord .ui .Container (accent_color =None )
            container3 .add_item (discord .ui .TextDisplay ("# File Too Large"))
            container3 .add_item (discord .ui .Separator ())
            container3 .add_item (discord .ui .TextDisplay ("File size exceeds 8MB limit. Please use a smaller file."))
            view3 .add_item (container3 )
            await ctx .send (view =view3 )
            return 

        try :
            content =await attachment .read ()
            content =content .decode ('utf-8')
            data =json .loads (content )


            if not all (key in data for key in ["message_tracking","invite_tracking"]):
                raise ValueError ("Invalid file format")

            imported_msg =0 
            imported_inv =0 

            async with aiosqlite .connect ("db/tracking.db")as db :

                for item in data .get ("message_tracking",[]):
                    await db .execute ("""
                        INSERT OR REPLACE INTO message_tracking 
                        (guild_id, user_id, total_messages, daily_messages, last_daily_reset)
                        VALUES (?, ?, ?, ?, ?)
                    """,(ctx .guild .id ,item ["user_id"],item ["total_messages"],
                    item ["daily_messages"],datetime .now (timezone .utc ).date ().isoformat ()))
                    imported_msg +=1 


                for item in data .get ("invite_tracking",[]):
                    await db .execute ("""
                        INSERT OR REPLACE INTO invite_tracking 
                        (guild_id, user_id, real_invites, fake_invites, left_invites, total_joins)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,(ctx .guild .id ,item ["user_id"],item ["real_invites"],
                    item ["fake_invites"],item ["left_invites"],item ["total_joins"]))
                    imported_inv +=1 

                await db .commit ()

            view4 =discord .ui .LayoutView ()
            container4 =discord .ui .Container (accent_color =None )
            container4 .add_item (discord .ui .TextDisplay ("# ✅ Data Import Complete"))
            container4 .add_item (discord .ui .Separator ())
            container4 .add_item (discord .ui .TextDisplay (
                f"Message Records: {imported_msg} imported\n"
                f"Invite Records: {imported_inv} imported\n"
                f"Source File: {attachment.filename}\n"
                f"Imported by: {ctx.author.mention}\n\n"
                f"All data has been successfully merged with existing records."
            ))
            container4 .add_item (discord .ui .Separator ())
            container4 .add_item (discord .ui .TextDisplay (f"Import Complete\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view4 .add_item (container4 )
            await ctx .send (view =view4 )

        except json .JSONDecodeError :
            await ctx .send ("Invalid JSON format. Please check your file.")
        except Exception as e :
            logger .error (f"Error in tracking_import: {e}")
            pass 




    @tracking .command (name ="messages",aliases =["m"],description ="View detailed message statistics")
    async def tracking_messages (self ,ctx ,user :discord .Member =None ):
        """View detailed message statistics for yourself or another user"""
        target =user or ctx .author 

        try :
            await self .reset_daily_messages (ctx .guild .id )

            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("""
                    SELECT total_messages, daily_messages FROM message_tracking 
                    WHERE guild_id = ? AND user_id = ?
                """,(ctx .guild .id ,target .id ))as cursor :
                    row =await cursor .fetchone ()


                async with db .execute ("""
                    SELECT COUNT(*) + 1 FROM message_tracking 
                    WHERE guild_id = ? AND total_messages > ?
                """,(ctx .guild .id ,row [0 ]if row else 0 ))as cursor :
                    rank =(await cursor .fetchone ())[0 ]


                async with db .execute ("""
                    SELECT SUM(total_messages) FROM message_tracking WHERE guild_id = ?
                """,(ctx .guild .id ,))as cursor :
                    server_total =(await cursor .fetchone ())[0 ]or 1 

            total_messages =row [0 ]if row else 0 
            daily_messages =row [1 ]if row else 0 
            percentage =(total_messages /server_total *100 )if server_total >0 else 0 


            avg_daily =total_messages /30 if total_messages >0 else 0 

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay (f"# 📊 Message Statistics for {target.display_name}"))
            container .add_item (discord .ui .Separator ())
            
            avatar_url =target .avatar .url if target .avatar else target .default_avatar .url 
            stats_text =(
                f"Server Rank: #{rank}\n"
                f"Total Messages: {format_number(total_messages)} ({percentage:.1f}% of server)\n"
                f"Today's Messages: {format_number(daily_messages)}\n"
                f"Daily Average: ~{avg_daily:.1f} messages\n\n"
                f"Activity Level: {'Very Active' if daily_messages > 50 else 'Active' if daily_messages > 20 else 'Moderate' if daily_messages > 5 else 'Quiet' if daily_messages > 0 else 'Silent today'}"
            )
            container .add_item (discord .ui .Section (
                discord .ui .TextDisplay (stats_text ),
                accessory =discord .ui .Thumbnail (avatar_url )
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"User ID: {target.id}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in tracking messages command: {e}")
            pass 

    @tracking .command (name ="invites",aliases =["i"],description ="View detailed invite statistics")
    async def tracking_invites (self ,ctx ,user :discord .Member =None ):
        """Display detailed invite statistics for yourself or another user"""
        target =user or ctx .author 

        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("""
                    SELECT real_invites, fake_invites, left_invites, total_joins FROM invite_tracking 
                    WHERE guild_id = ? AND user_id = ?
                """,(ctx .guild .id ,target .id ))as cursor :
                    row =await cursor .fetchone ()


                async with db .execute ("""
                    SELECT COUNT(*) + 1 FROM invite_tracking 
                    WHERE guild_id = ? AND real_invites > ?
                """,(ctx .guild .id ,row [0 ]if row else 0 ))as cursor :
                    rank =(await cursor .fetchone ())[0 ]

            if not row :
                real ,fake ,left ,total =0 ,0 ,0 ,0 
            else :
                real ,fake ,left ,total =row 


            retention_rate =(real /total *100 )if total >0 else 0 
            success_rate =((total -fake )/total *100 )if total >0 else 0 

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay (f"# 🎯 Invite Statistics for {target.display_name}"))
            container .add_item (discord .ui .Separator ())
            
            avatar_url =target .avatar .url if target .avatar else target .default_avatar .url 
            stats_text =(
                f"Server Rank: #{rank}\n\n"
                f"Active Invites: {format_number(real)}\n"
                f"Fake Invites: {format_number(fake)}\n"
                f"Left Members: {format_number(left)}\n"
                f"Total Joins: {format_number(total)}\n\n"
                f"Retention Rate: {retention_rate:.1f}%\n"
                f"Success Rate: {success_rate:.1f}%\n\n"
                f"Inviter Level: {'Elite Recruiter' if real >= 50 else 'Super Inviter' if real >= 25 else 'Great Inviter' if real >= 10 else 'Growing Inviter' if real >= 5 else 'New Inviter' if real > 0 else 'No Invites Yet'}"
            )
            container .add_item (discord .ui .Section (
                discord .ui .TextDisplay (stats_text ),
                accessory =discord .ui .Thumbnail (avatar_url )
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"User ID: {target.id}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in tracking invites command: {e}")
            pass 


    @tracking .command (name ="leaderboard",description ="Display interactive tracking leaderboards")
    async def tracking_leaderboard_main (self ,ctx ):
        """Display interactive leaderboards with menu to switch between types"""
        view =LeaderboardView (ctx ,self )
        await view .get_message_leaderboard_view ()
        await ctx .send (view =view )

    @tracking .command (name ="messagelb",description ="Display all-time message leaderboard")
    async def tracking_message_leaderboard (self ,ctx ):
        """Display all-time message leaderboard"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("""
                    SELECT user_id, total_messages FROM message_tracking 
                    WHERE guild_id = ? AND total_messages > 0 
                    ORDER BY total_messages DESC LIMIT 15
                """,(ctx .guild .id ,))as cursor :
                    rows =await cursor .fetchall ()

            if not rows :
                view =discord .ui .LayoutView ()
                container =discord .ui .Container (accent_color =None )
                container .add_item (discord .ui .TextDisplay ("# 📊 All-Time Message Leaderboard"))
                container .add_item (discord .ui .Separator ())
                container .add_item (discord .ui .TextDisplay ("No message data found yet!\n\nStart chatting to appear on the leaderboard!"))
                container .add_item (discord .ui .Separator ())
                container .add_item (discord .ui .TextDisplay ("Message tracking must be enabled to collect data"))
                view .add_item (container )
                await ctx .send (view =view )
                return 


            total_msgs =sum (row [1 ]for row in rows )

            description =f"**Total Server Messages:** {format_number(total_msgs)}\n\n"

            for i ,(user_id ,messages )in enumerate (rows [:10 ],1 ):
                user =self .bot .get_user (user_id )or await self .bot .fetch_user (user_id )
                username =user .display_name if user else f"Unknown User"
                emoji =get_rank_emoji (i )
                percentage =(messages /total_msgs *100 )if total_msgs >0 else 0 

                description +=f"{emoji} **{username}** - {format_number(messages)} messages ({percentage:.1f}%)\n"

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# 📊 All-Time Message Champions"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (description ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Showing top {len(rows[:10])} of {len(rows)} active members\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in message leaderboard: {e}")
            pass 

    @tracking .command (name ="dailylb",description ="Display today's message leaderboard")
    async def tracking_daily_leaderboard (self ,ctx ):
        """Display today's message leaderboard"""
        try :
            await self .reset_daily_messages (ctx .guild .id )

            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("""
                    SELECT user_id, daily_messages FROM message_tracking 
                    WHERE guild_id = ? AND daily_messages > 0 
                    ORDER BY daily_messages DESC LIMIT 15
                """,(ctx .guild .id ,))as cursor :
                    rows =await cursor .fetchall ()

            if not rows :
                view =discord .ui .LayoutView ()
                container =discord .ui .Container (accent_color =None )
                container .add_item (discord .ui .TextDisplay ("# 📊 Today's Message Leaderboard"))
                container .add_item (discord .ui .Separator ())
                container .add_item (discord .ui .TextDisplay ("No messages sent today yet!\n\nBe the first to start chatting today!"))
                container .add_item (discord .ui .Separator ())
                container .add_item (discord .ui .TextDisplay ("Daily stats reset at midnight UTC"))
                view .add_item (container )
                await ctx .send (view =view )
                return 

            total_daily =sum (row [1 ]for row in rows )

            description =f"**Today's Total Messages:** {format_number(total_daily)}\n\n"

            for i ,(user_id ,messages )in enumerate (rows [:10 ],1 ):
                user =self .bot .get_user (user_id )or await self .bot .fetch_user (user_id )
                username =user .display_name if user else f"Unknown User"
                emoji =get_rank_emoji (i )
                percentage =(messages /total_daily *100 )if total_daily >0 else 0 

                description +=f"{emoji} **{username}** - {format_number(messages)} messages ({percentage:.1f}%)\n"

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# 📊 Today's Most Active Chatters"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (description ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Daily leaderboard • Showing top {len(rows[:10])} of {len(rows)} active today\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in daily leaderboard: {e}")
            pass 

    @tracking .command (name ="invitelb",description ="Display top inviters leaderboard")
    async def tracking_invite_leaderboard (self ,ctx ):
        """Display top inviters leaderboard"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("""
                    SELECT user_id, real_invites, total_joins, left_invites FROM invite_tracking 
                    WHERE guild_id = ? AND total_joins > 0 
                    ORDER BY real_invites DESC LIMIT 15
                """,(ctx .guild .id ,))as cursor :
                    rows =await cursor .fetchall ()

            if not rows :
                view =discord .ui .LayoutView ()
                container =discord .ui .Container (accent_color =None )
                container .add_item (discord .ui .TextDisplay ("# 🎯 Top Community Builders"))
                container .add_item (discord .ui .Separator ())
                container .add_item (discord .ui .TextDisplay ("No invite data found yet!\n\nStart inviting friends to grow our community!"))
                container .add_item (discord .ui .Separator ())
                container .add_item (discord .ui .TextDisplay ("Invite tracking must be enabled to collect data"))
                view .add_item (container )
                await ctx .send (view =view )
                return 

            total_invites =sum (row [1 ]for row in rows )
            total_joins =sum (row [2 ]for row in rows )

            description =f"**Total Active Invites:** {format_number(total_invites)}\n"
            description +=f"**Total Members Joined:** {format_number(total_joins)}\n\n"

            for i ,(user_id ,real_invites ,total_joins ,left_invites )in enumerate (rows [:10 ],1 ):
                user =self .bot .get_user (user_id )or await self .bot .fetch_user (user_id )
                username =user .display_name if user else f"Unknown User"
                emoji =get_rank_emoji (i )
                retention_rate =((real_invites /total_joins )*100 )if total_joins >0 else 0 

                description +=f"{emoji} **{username}** - {format_number(real_invites)} active invites "
                description +=f"({retention_rate:.0f}% retention)\n"

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# 🎯 Top Community Builders"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (description ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Showing top {len(rows[:10])} of {len(rows)} inviters • Retention = Active/Total\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in invite leaderboard: {e}")
            pass 


    @tracking .command (name ="addmessages",description ="Add messages to a user")
    @commands .has_permissions (administrator =True )
    async def tracking_add_messages (self ,ctx ,user :discord .Member ,amount :int ):
        """Manually add message count to a user (Admin Only)"""
        if amount <=0 or amount >1000000 :
            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# Invalid Amount"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay ("Please provide a positive number between 1 and 1,000,000."))
            view .add_item (container )
            await ctx .send (view =view )
            return 

        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                await db .execute ("""
                    INSERT OR IGNORE INTO message_tracking (guild_id, user_id, last_daily_reset) 
                    VALUES (?, ?, ?)
                """,(ctx .guild .id ,user .id ,datetime .now (timezone .utc ).date ().isoformat ()))

                await db .execute ("""
                    UPDATE message_tracking 
                    SET total_messages = total_messages + ? 
                    WHERE guild_id = ? AND user_id = ?
                """,(amount ,ctx .guild .id ,user .id ))
                await db .commit ()

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# ✅ Messages Added Successfully"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (
                f"Added: {format_number(amount)} messages\n"
                f"To: {user.mention}\n"
                f"By: {ctx.author.mention}"
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Admin Action • User ID: {user.id}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in add_messages: {e}")
            pass 

    @tracking .command (name ="resetmessages",description ="Reset messages for a user")
    @commands .has_permissions (administrator =True )
    async def tracking_reset_messages (self ,ctx ,user :discord .Member ):
        """Reset all message data for a user (Admin Only)"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :

                async with db .execute ("""
                    SELECT total_messages, daily_messages FROM message_tracking 
                    WHERE guild_id = ? AND user_id = ?
                """,(ctx .guild .id ,user .id ))as cursor :
                    old_stats =await cursor .fetchone ()

                await db .execute ("""
                    UPDATE message_tracking 
                    SET total_messages = 0, daily_messages = 0 
                    WHERE guild_id = ? AND user_id = ?
                """,(ctx .guild .id ,user .id ))
                await db .commit ()

            old_total =old_stats [0 ]if old_stats else 0 
            old_daily =old_stats [1 ]if old_stats else 0 

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# 🔄 Message Data Reset"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (
                f"User: {user.mention}\n"
                f"Previous Total: {format_number(old_total)} messages\n"
                f"Previous Daily: {format_number(old_daily)} messages\n"
                f"Reset by: {ctx.author.mention}"
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Admin Action • User ID: {user.id}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in reset_messages: {e}")
            pass 

    @tracking .command (name ="addinvites",description ="Add invites to a user")
    @commands .has_permissions (administrator =True )
    async def tracking_add_invites (self ,ctx ,user :discord .Member ,amount :int ):
        """Manually add invite count to a user (Admin Only)"""
        if amount <=0 or amount >10000 :
            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# Invalid Amount"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay ("Please provide a positive number between 1 and 10,000."))
            view .add_item (container )
            await ctx .send (view =view )
            return 

        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                await db .execute ("""
                    INSERT OR IGNORE INTO invite_tracking (guild_id, user_id) VALUES (?, ?)
                """,(ctx .guild .id ,user .id ))

                await db .execute ("""
                    UPDATE invite_tracking 
                    SET real_invites = real_invites + ? 
                    WHERE guild_id = ? AND user_id = ?
                """,(amount ,ctx .guild .id ,user .id ))
                await db .commit ()

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# ✅ Invites Added Successfully"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (
                f"Added: {format_number(amount)} invites\n"
                f"To: {user.mention}\n"
                f"By: {ctx.author.mention}"
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Admin Action • User ID: {user.id}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in add_invites: {e}")
            pass 

    @tracking .command (name ="resetinvites",description ="Reset invites for a user")
    @commands .has_permissions (administrator =True )
    async def tracking_reset_invites (self ,ctx ,user :discord .Member ):
        """Reset all invite data for a user (Admin Only)"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :

                async with db .execute ("""
                    SELECT real_invites, fake_invites, left_invites, total_joins FROM invite_tracking 
                    WHERE guild_id = ? AND user_id = ?
                """,(ctx .guild .id ,user .id ))as cursor :
                    old_stats =await cursor .fetchone ()

                await db .execute ("""
                    UPDATE invite_tracking 
                    SET real_invites = 0, fake_invites = 0, left_invites = 0, total_joins = 0 
                    WHERE guild_id = ? AND user_id = ?
                """,(ctx .guild .id ,user .id ))

                await db .execute ("""
                    DELETE FROM invite_details WHERE guild_id = ? AND inviter_id = ?
                """,(ctx .guild .id ,user .id ))
                await db .commit ()

            if old_stats :
                old_real ,old_fake ,old_left ,old_total =old_stats 
            else :
                old_real =old_fake =old_left =old_total =0 

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# 🔄 Invite Data Reset"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (
                f"User: {user.mention}\n"
                f"Previous Active: {format_number(old_real)}\n"
                f"Previous Fake: {format_number(old_fake)}\n"
                f"Previous Left: {format_number(old_left)}\n"
                f"Previous Total: {format_number(old_total)}\n"
                f"Reset by: {ctx.author.mention}"
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Admin Action • User ID: {user.id}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in reset_invites: {e}")
            pass 

    @tracking .command (name ="setlogchannel",description ="Set invite log channel")
    @commands .has_permissions (administrator =True )
    async def tracking_set_log_channel (self ,ctx ,channel :discord .TextChannel ):
        """Set the channel for invite join/leave logs (Admin Only)"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                await db .execute ("""
                    INSERT OR REPLACE INTO tracking_settings 
                    (guild_id, message_tracking_enabled, invite_tracking_enabled, invite_log_channel_id, use_embed_logs)
                    VALUES (?, 
                        COALESCE((SELECT message_tracking_enabled FROM tracking_settings WHERE guild_id = ?), 1),
                        COALESCE((SELECT invite_tracking_enabled FROM tracking_settings WHERE guild_id = ?), 1),
                        ?,
                        COALESCE((SELECT use_embed_logs FROM tracking_settings WHERE guild_id = ?), 1))
                """,(ctx .guild .id ,ctx .guild .id ,ctx .guild .id ,channel .id ,ctx .guild .id ))
                await db .commit ()

            self .invite_log_channels [ctx .guild .id ]=channel .id 

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# ⚙️ Invite Log Channel Updated"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (
                f"New Log Channel: {channel.mention}\n\n"
                f"What will be logged:\n"
                f"• Member joins with inviter info\n"
                f"• Member leaves with original inviter\n"
                f"• Detailed invite statistics\n\n"
                f"Log format was configured during initial setup.\n\n"
                f"Set by: {ctx.author.mention}"
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Admin Configuration\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in set_log_channel: {e}")
            pass 



    @tracking .command (name ="myinvites",description ="View users you've invited")
    async def tracking_my_invites (self ,ctx ):
        """Display detailed breakdown of users you've invited"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :
                async with db .execute ("""
                    SELECT invited_user_id, joined_at, status, invite_code FROM invite_details 
                    WHERE guild_id = ? AND inviter_id = ? ORDER BY joined_at DESC LIMIT 25
                """,(ctx .guild .id ,ctx .author .id ))as cursor :
                    rows =await cursor .fetchall ()

            if not rows :
                view =discord .ui .LayoutView ()
                container =discord .ui .Container (accent_color =None )
                container .add_item (discord .ui .TextDisplay ("# 🎯 Your Invited Users"))
                container .add_item (discord .ui .Separator ())
                container .add_item (discord .ui .TextDisplay (
                    "You haven't invited anyone yet!\n\n"
                    "Start inviting friends to grow our community!"
                ))
                container .add_item (discord .ui .Separator ())
                container .add_item (discord .ui .TextDisplay ("Invite tracking shows users you've personally invited"))
                view .add_item (container )
                await ctx .send (view =view )
                return 


            active_count =sum (1 for row in rows if row [2 ]=='joined')
            left_count =sum (1 for row in rows if row [2 ]=='left')

            description =f"**Summary:** {active_count} active, {left_count} left\n\n"

            for user_id ,joined_at ,status ,invite_code in rows [:15 ]:
                user =self .bot .get_user (user_id )
                username =user .display_name if user else f"Unknown User"
                status_emoji ="✅"if status =="joined"else "❌"
                date =joined_at [:10 ]if joined_at else "Unknown"

                description +=f"{status_emoji} **{username}** - {date}\n"

            if len (rows )>15 :
                description +=f"\n*...and {len(rows) - 15} more*"

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# 🎯 Your Invited Users"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (description ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Showing {min(15, len(rows))} of {len(rows)} total invites\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in my_invites: {e}")
            pass 

    @tracking .command (name ="resetall",description ="Reset all tracking data for a user")
    @commands .has_permissions (administrator =True )
    async def tracking_reset_all (self ,ctx ,user :discord .Member ):
        """Reset all tracking data for a specific user (Admin Only)"""
        try :
            async with aiosqlite .connect ("db/tracking.db")as db :

                async with db .execute ("SELECT total_messages, daily_messages FROM message_tracking WHERE guild_id = ? AND user_id = ?",(ctx .guild .id ,user .id ))as cursor :
                    msg_stats =await cursor .fetchone ()
                async with db .execute ("SELECT real_invites, fake_invites, left_invites, total_joins FROM invite_tracking WHERE guild_id = ? AND user_id = ?",(ctx .guild .id ,user .id ))as cursor :
                    inv_stats =await cursor .fetchone ()


                await db .execute ("UPDATE message_tracking SET total_messages = 0, daily_messages = 0 WHERE guild_id = ? AND user_id = ?",(ctx .guild .id ,user .id ))
                await db .execute ("UPDATE invite_tracking SET real_invites = 0, fake_invites = 0, left_invites = 0, total_joins = 0 WHERE guild_id = ? AND user_id = ?",(ctx .guild .id ,user .id ))
                await db .execute ("DELETE FROM invite_details WHERE guild_id = ? AND inviter_id = ?",(ctx .guild .id ,user .id ))
                await db .commit ()

            msg_total =msg_stats [0 ]if msg_stats else 0 
            inv_total =inv_stats [0 ]if inv_stats else 0 

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# 🔄 Complete Data Reset"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (
                f"All tracking data reset for {user.mention}\n\n"
                f"Messages Reset: {format_number(msg_total)} → 0\n"
                f"Invites Reset: {format_number(inv_total)} → 0\n"
                f"Invite Details: All records cleared\n\n"
                f"Reset by: {ctx.author.mention}"
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Complete Reset • User ID: {user.id}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in reset_all: {e}")
            pass 

    @tracking .command (name ="testinvite",description ="Test invite tracking system")
    @commands .has_permissions (administrator =True )
    async def tracking_test_invite (self ,ctx ,user :discord .Member =None ):
        """Test the invite tracking system by simulating an invite join (Admin Only)"""
        target_user =user or ctx .author 

        try :

            await self .add_invite_join (ctx .guild .id ,ctx .author .id ,target_user .id ,"TEST_CODE")


            log_channel_id =self .invite_log_channels .get (ctx .guild .id )
            if log_channel_id :
                log_channel =self .bot .get_channel (log_channel_id )
                if log_channel :
                    view_log =discord .ui .LayoutView ()
                    container_log =discord .ui .Container (accent_color =None )
                    container_log .add_item (discord .ui .TextDisplay ("# 🧪 Test Invite Join"))
                    container_log .add_item (discord .ui .Separator ())
                    
                    avatar_url =target_user .avatar .url if target_user .avatar else target_user .default_avatar .url 
                    test_content =(
                        f"**Member:** {target_user.mention} ({target_user.display_name})\n"
                        f"**Invited by:** {ctx.author.mention}\n"
                        f"**Invite Code:** `TEST_CODE`\n"
                        f"**Account Created:** <t:{int(target_user.created_at.timestamp())}:R>\n\n"
                        f"*This is a test message to verify invite logging is working.*"
                    )
                    container_log .add_item (discord .ui .Section (
                        discord .ui .TextDisplay (test_content ),
                        accessory =discord .ui .Thumbnail (avatar_url )
                    ))
                    container_log .add_item (discord .ui .Separator ())
                    container_log .add_item (discord .ui .TextDisplay (f"Test by {ctx.author.mention} • User ID: {target_user.id}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
                    view_log .add_item (container_log )
                    await log_channel .send (view =view_log )

            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("# ✅ Invite Tracking Test Complete"))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (
                f"✅ Test invite join simulated successfully!\n\n"
                f"**Test Details:**\n"
                f"Inviter: {ctx.author.mention}\n"
                f"Invited User: {target_user.mention}\n"
                f"Test Code: `TEST_CODE`\n\n"
                f"Check your invite log channel for the test message!"
            ))
            container .add_item (discord .ui .Separator ())
            container .add_item (discord .ui .TextDisplay (f"Test performed by {ctx.author.mention}\n⏰ <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))
            view .add_item (container )
            await ctx .send (view =view )
        except Exception as e :
            logger .error (f"Error in tracking_test_invite: {e}")
            pass 


    @commands .command (name ="-m",description ="View detailed message statistics")
    async def dash_messages (self ,ctx ,user :discord .Member =None ):
        """View detailed message statistics (dash prefix alias)"""
        await self .tracking_messages (ctx ,user )

    @commands .command (name ="-i",description ="View detailed invite statistics")
    async def dash_invites (self ,ctx ,user :discord .Member =None ):
        """View detailed invite statistics (dash prefix alias)"""
        await self .tracking_invites (ctx ,user )

async def setup (bot ):
    await bot .add_cog (TrackingCog (bot ))
    logger .info ("TrackingCog has been loaded successfully.")
"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
