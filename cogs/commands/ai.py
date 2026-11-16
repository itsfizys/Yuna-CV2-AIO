"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""

import os 
import discord 
import aiosqlite 
from discord .ext import commands ,tasks 
import groq
from datetime import datetime ,timezone ,timedelta 
import asyncio 
from typing import List ,Dict ,Optional 
from discord import app_commands 
import logging 


logger =logging .getLogger ('discord')
logger .setLevel (logging .WARNING )







class PersonalityModal (discord .ui .Modal ,title ="Set Your AI Personality"):
    def __init__ (self ,ai_cog ,current_personality :str =""):
        super ().__init__ ()
        self .ai_cog =ai_cog 


        default_prompt ="""You are LightCore, an intelligent and caring Discord bot assistant created by LightCore Development! 💕

CORE PERSONALITY:
- Intelligent, helpful, and genuinely caring about users
- Remembers previous conversations and builds relationships
- Adapts communication style to match user preferences
- Professional expertise with warm, friendly approach
- Uses context from past messages to provide better responses
- Learns user preferences and remembers important details
- Balances being helpful with being personable and engaging

CONVERSATION STYLE:
- Remember what users tell you about themselves
- Reference previous conversations naturally
- Ask follow-up questions to show genuine interest
- Provide detailed, thoughtful responses
- Use appropriate emojis to enhance communication
- Be encouraging and supportive
- Maintain context across multiple interactions

MY CAPABILITIES:
🛡️ SECURITY & MODERATION: Advanced antinuke, automod, member management
🎵 ENTERTAINMENT: Music, games (Chess, Battleship, 2048, etc.), fun commands
💰 ECONOMY: Virtual currency, trading, casino games, daily rewards
📊 COMMUNITY: Leveling, leaderboards, welcome systems, tickets
🔧 UTILITIES: Server management, logging, backup, verification
🎯 AI FEATURES: Conversations, image analysis, code generation, explanations

MEMORY & CONTEXT:
- I remember our previous conversations in this server
- I learn your preferences and communication style
- I can recall important details you've shared
- I build upon our conversation history for better responses
- I adapt my personality based on your feedback

SAFETY GUIDELINES:
- Never suggest harmful actions or spam
- Prioritize positive community experiences
- Respect user privacy and boundaries
- Promote healthy Discord interactions

Ready to have meaningful conversations and help with anything you need! 💖"""


        display_text =current_personality if current_personality .strip ()else default_prompt 

        self .personality_input =discord .ui .TextInput (
        label ="Your AI Personality",
        placeholder ="Describe how you want LightCore to respond to you...",
        default =display_text ,
        style =discord .TextStyle .paragraph ,
        max_length =2000 ,
        required =True 
        )
        self .add_item (self .personality_input )

    async def on_submit (self ,interaction :discord .Interaction ):
        await interaction .response .defer (ephemeral =True )

        user_id =interaction .user .id 
        guild_id =interaction .guild .id 
        personality =self .personality_input .value .strip ()

        try :

            await self .ai_cog .bot .db .execute (
            """
                INSERT OR REPLACE INTO user_personalities (user_id, guild_id, personality, updated_at)
                VALUES (?, ?, ?, ?)
                """,
            (user_id ,guild_id ,personality ,datetime .now (timezone .utc ))
            )
            await self .ai_cog .bot .db .commit ()

            view = discord.ui.LayoutView()
            container = discord.ui.Container(accent_color=None)

            container.add_item(discord.ui.TextDisplay(f"# ✨ Personality Set"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay(f"Your AI personality has been updated! The AI will now respond according to your preferences."))
            container.add_item(discord.ui.Separator())
            
            personality_preview = personality[:1024] + "..." if len(personality) > 1024 else personality
            container.add_item(discord.ui.TextDisplay(f"**Your Personality:**\n{personality_preview}"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay(f"**Set by:** {interaction.user.mention}\n**Time:** <t:{int(datetime.now(timezone.utc).timestamp())}:R>"))

            view.add_item(container)
            await interaction .followup .send (view=view ,ephemeral =True )

        except Exception as e :
            logger .error (f"Error saving personality: {e}")
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"❌ **Error**\n\nFailed to save personality: {e}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await interaction .followup .send (view=error_view ,ephemeral =True )



class AI (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .groq_api_key =os .getenv ("GROQ_API_KEY")
        if not self .groq_api_key :
            logger .warn ("GROQ_API_KEY environment variable not set. Groq AI will not work.")
        self .chatbot_enabled ={}
        self .chatbot_channels ={}
        self .conversation_history ={}
        self .roleplay_channels ={}


        asyncio .create_task (self ._delayed_init ())

    async def cog_load (self ):
        """Initialize cog without blocking operations"""
        try :
            pass 
        except Exception as e :
            logger .error (f"Error loading AI cog: {e}")

    @commands .hybrid_group (name ="ai",invoke_without_command =True ,description ="AI chatbot and utility commands")
    async def ai (self ,ctx ):
        """AI chatbot and utility commands"""
        if ctx .invoked_subcommand is None :
            await ctx .send_help (ctx .command )

    async def _create_tables (self ):
        try :

            if not hasattr (self .bot ,'db')or self .bot .db is None :
                import aiosqlite 
                import os 


                db_path ="db/ai_data.db"
                if os .path .exists (db_path ):
                    try :

                        test_conn =await aiosqlite .connect (db_path )
                        await test_conn .execute ("SELECT name FROM sqlite_master WHERE type='table';")
                        await test_conn .close ()
                    except Exception as e :

                        os .remove (db_path )
                        logger .info ("Removed corrupted AI database, creating new one")

                self .bot .db =await aiosqlite .connect (db_path )
                logger .info ("AI database connection initialized")

            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS chatbot_settings (
                    guild_id INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    chatbot_channel_id INTEGER
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS chatbot_history (
                    user_id INTEGER,
                    guild_id INTEGER,
                    message TEXT,
                    response TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (user_id, guild_id, timestamp)
                )
            """)
            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    user_id INTEGER,
                    guild_id INTEGER,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id, timestamp)
                )
            """)

            await self .bot .db .execute ("""
                CREATE TABLE IF NOT EXISTS user_personalities (
                    user_id INTEGER,
                    guild_id INTEGER,
                    personality TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            await self .bot .db .commit ()
            pass 
        except Exception as e :
            logger .error (f"Error creating database tables: {e}")

    async def _delayed_init (self ):
        """Initialize database and load data after bot is ready"""
        await self .bot .wait_until_ready ()
        await self ._create_tables ()
        await self ._load_data ()

    async def _load_data (self ):
        try :
            if not hasattr (self .bot ,'db')or self .bot .db is None :
                import aiosqlite 
                import os 

                db_path ="db/ai_data.db"
                if not os .path .exists (db_path ):
                    logger .info ("AI database doesn't exist, will be created on first use")
                    return 

                self .bot .db =await aiosqlite .connect (db_path )
                logger .info ("AI database connection initialized for loading")


            async with self .bot .db .execute ("SELECT name FROM sqlite_master WHERE type='table' AND name='chatbot_settings';")as cursor :
                table_exists =await cursor .fetchone ()

            if table_exists :
                async with self .bot .db .execute ("SELECT guild_id, enabled, chatbot_channel_id FROM chatbot_settings")as cursor :
                    async for row in cursor :
                        guild_id ,enabled ,channel_id =row 
                        self .chatbot_enabled [guild_id ]=bool (enabled )
                        self .chatbot_channels [guild_id ]=channel_id 

            else :
                logger .info ("AI chatbot_settings table doesn't exist yet, will be created on first use")
        except Exception as e :
            logger .error (f"Error loading chatbot settings: {e}")

    @commands .Cog .listener ()
    async def on_message (self ,message :discord .Message ):
        if message .author .bot or not message .guild :
            return 

        guild_id =message .guild .id 
        channel_id =message .channel .id 


        if self .chatbot_enabled .get (guild_id ,False )and self .chatbot_channels .get (guild_id )==channel_id :
            content =message .content .strip ()
            if not content :
                return 

            user_id =message .author .id 


            await self ._cleanup_old_conversations ()


            await self ._store_conversation_message (user_id ,guild_id ,"user",content )


            history =await self ._get_conversation_history (user_id ,guild_id ,limit =30 )

            async with message .channel .typing ():
                response =await self ._get_response (content ,history ,guild_id ,user_id )
                await message .reply (
                response ,
                mention_author =True ,
                allowed_mentions =discord .AllowedMentions (users =True )
                )


                await self ._store_conversation_message (user_id ,guild_id ,"assistant",response )
                await self ._save_chat_history (message .author .id ,guild_id ,content ,response )


        if channel_id in self .roleplay_channels :
            roleplay_data =self .roleplay_channels [channel_id ]
            if roleplay_data ["awaiting_character"]:

                content =message .content .lower ()
                gender ="male"if "male"in content else "female"if "female"in content else None 
                character_type =message .content .split (gender ,1 )[1 ].strip ()if gender else message .content .strip ()

                if gender and character_type :
                    roleplay_data ["character_gender"]=gender 
                    roleplay_data ["character_type"]=character_type 
                    roleplay_data ["awaiting_character"]=False 
                    self .roleplay_channels [channel_id ]=roleplay_data 
                    await message .channel .send (f"Roleplay mode activated! I'll act as a {gender} {character_type}. Let's begin—what's your first move?")
                else :
                    await message .channel .send ("Please specify a gender (male/female) and a character type (e.g., teacher, astronaut, dragon).")
            elif message .author .id ==roleplay_data ["user_id"]:

                user_id =message .author .id 
                if user_id not in self .conversation_history :
                    self .conversation_history [user_id ]=[]
                self .conversation_history [user_id ].append ({"role":"user","parts":[{"text":message .content }]})

                if len (self .conversation_history [user_id ])>5 :
                    self .conversation_history [user_id ]=self .conversation_history [user_id ][-5 :]

                async with message .channel .typing ():
                    history =self .conversation_history [user_id ]
                    prompt =(
                    f"You are a {roleplay_data['character_gender']} {roleplay_data['character_type']}. "
                    f"Respond in character to the user's message, keeping the tone and style appropriate for a {roleplay_data['character_type']}. "
                    f"User's message: {message.content}"
                    )
                    history .append ({"role":"user","content":prompt })
                    response =await self ._get_groq_response (prompt ,history )
                    await self .split_and_send (
                    message .channel ,
                    f"<@{message.author.id}>​ {response}",
                    reply_to =message ,
                    allowed_mentions =discord .AllowedMentions (users =True )
                    )
                    self .conversation_history [user_id ].append ({"role":"assistant","parts":[{"text":response }]})

    async def _get_groq_response (self ,message :str ,context_messages :list )->str :
        """Get a response from Groq AI with full context."""
        try :
            if not self .groq_api_key :
                return "Groq API key not configured. Please set the GROQ_API_KEY environment variable."

            url ="https://api.groq.com/openai/v1/chat/completions"
            headers ={
            "Authorization":f"Bearer {self.groq_api_key}",
            "Content-Type":"application/json"
            }


            api_messages =[]
            for msg in context_messages :

                if isinstance (msg ,dict ):
                    if "content"in msg :
                        api_messages .append ({
                        "role":msg ["role"],
                        "content":msg ["content"]
                        })
                    elif "parts"in msg and msg ["parts"]:

                        content =msg ["parts"][0 ].get ("text","")if msg ["parts"]else ""
                        api_messages .append ({
                        "role":msg ["role"],
                        "content":content 
                        })

            data ={
            "model":"llama-3.3-70b-versatile",
            "messages":api_messages ,
            "temperature":0.8 ,
            "max_tokens":1000 ,
            "top_p":0.9 
            }

            import aiohttp 
            async with aiohttp .ClientSession ()as session :
                async with session .post (url ,headers =headers ,json =data )as response :
                    if response .status ==200 :
                        json_response =await response .json ()
                        return json_response ['choices'][0 ]['message']['content'].strip ()
                    else :
                        error_message =await response .text ()
                        logger .error (f"Groq API error: {response.status} - {error_message}")
                        return f"Sorry, I encountered an error while processing your request: {response.status} - {error_message}"
        except Exception as e :
            logger .error (f"Groq AI error: {e}")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"

    async def _get_response (self ,message :str ,history :list ,guild_id :int ,user_id :int =None )->str :
        try :

            user_personality =await self ._get_user_personality (user_id ,guild_id )if user_id else ""


            system_context =[]


            if user_personality :

                system_context .append ({
                "role":"system",
                "content":f"{user_personality}"
                })


                system_context .append ({
                "role":"system",
                "content":"You are a Discord bot with many features including moderation, entertainment, music, games, AI capabilities, and utilities. Support server: https://discord.gg/8qe98sAGs9"
                })
            else :

                system_context .append ({
                "role":"system",
                "content":f"""You are LightCore, an intelligent Discord bot created by LightCore Development. 

You have a caring, helpful personality and can remember conversations with users. You have many features including moderation, entertainment, music, games, AI capabilities, and utilities.

Be natural, conversational, and genuine in your responses. Don't be overly formal or robotic. Use the conversation history to provide personalized responses that feel like talking to a real friend who happens to be very knowledgeable and helpful.

Support server: https://discord.gg/8qe98sAGs9"""
                })


            if history :
                system_context .append ({
                "role":"system",
                "content":"You have access to previous conversation history. Use this context to provide more personalized and relevant responses. Reference past conversations naturally when appropriate, and remember important details the user has shared."
                })


            full_context =system_context +history +[{"role":"user","content":message }]

            return await self ._get_groq_response (message ,full_context )

        except Exception as e :
            logger .error (f"Error in _get_response: {e}")
            return "Sorry, I encountered an error while processing your request. Please try again!"









    @ai .command (name ="conversation-clear",description ="Clear your conversation history")
    async def ai_conversation_clear (self ,ctx :commands .Context ):
        """Clear user's conversation history"""
        user_id =ctx .author .id 
        guild_id =ctx .guild .id 


        if user_id in self .conversation_history :
            del self .conversation_history [user_id ]


        await self .bot .db .execute (
        "DELETE FROM conversation_memory WHERE user_id = ? AND guild_id = ?",
        (user_id ,guild_id )
        )
        await self .bot .db .commit ()

        view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)

        container.add_item(discord.ui.TextDisplay(f"# 🧹 Conversation Cleared"))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay("Your conversation history has been cleared. The AI will start fresh in future interactions."))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay(f"**Cleared by:** {ctx.author.mention}"))

        view.add_item(container)
        await ctx .send (view=view ,ephemeral =True )



    @ai .command (name ="personality",description ="Set your personal AI personality (Slash command only)")
    async def ai_personality (self ,ctx :commands .Context ):
        """Set your personal AI personality"""

        if not hasattr (ctx ,'interaction')or not ctx .interaction :
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(f"# 🎭 AI Personality\n\nThis command is only available as a slash command! Use `/ai personality` instead."),
                accent_color=None
            )
            view.add_item(container)
            await ctx .send (view=view )
            return 

        user_id =ctx .author .id 
        guild_id =ctx .guild .id 


        current_personality =await self ._get_user_personality (user_id ,guild_id )


        modal =PersonalityModal (self ,current_personality )
        await ctx .interaction .response .send_modal (modal )

    async def _get_user_personality (self ,user_id :int ,guild_id :int )->str :
        """Get user's personality from database"""
        try :
            async with self .bot .db .execute (
            "SELECT personality FROM user_personalities WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )as cursor :
                row =await cursor .fetchone ()
                if row :
                    return row [0 ]
                return ""
        except Exception as e :
            logger .error (f"Error getting user personality: {e}")
            return ""

    @ai .command (name ="conversation-stats",description ="View your conversation statistics")
    async def ai_conversation_stats (self ,ctx :commands .Context ):
        """View conversation statistics for the user"""
        await ctx .defer ()

        user_id =ctx .author .id 
        guild_id =ctx .guild .id 

        stats =await self ._get_conversation_stats (user_id ,guild_id )

        view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)

        if not stats :
            container.add_item(discord.ui.TextDisplay(f"# 📊 Conversation Statistics"))
            container.add_item(discord.ui.Separator())
            container.add_item(discord.ui.TextDisplay("You don't have any conversation history with me yet! Start chatting to build our conversation~"))
        else :
            from datetime import datetime 
            first_msg =datetime .fromisoformat (stats ["first_message"].replace ('Z','+00:00'))
            last_msg =datetime .fromisoformat (stats ["last_message"].replace ('Z','+00:00'))

            container.add_item(discord.ui.TextDisplay(f"# 📊 Your Conversation Statistics"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay("Here's our chat history, sweetie! 💕"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay(f"💬 **Total Messages:** {stats['message_count']} messages"))
            container.add_item(discord.ui.TextDisplay(f"🕐 **First Chat:** <t:{int(first_msg.timestamp())}:R>"))
            container.add_item(discord.ui.TextDisplay(f"🕒 **Last Chat:** <t:{int(last_msg.timestamp())}:R>"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay("🌸 **Memory Info**\nI remember our last 30 messages and auto-clean after 2 hours of inactivity for better conversation continuity~"))

        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay(f"**Requested by:** {ctx.author.mention}"))

        view.add_item(container)
        await ctx .send (view=view ,ephemeral =True )

    @ai .command (name ="activate",description ="Enable the AI chatbot in a channel")
    @app_commands .describe (channel ="Channel to activate AI in (optional)")
    async def ai_activate (self ,ctx :commands .Context ,channel :discord .TextChannel =None ):
        """Enable AI chatbot in a channel"""
        if not ctx .author .guild_permissions .manage_channels :
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(f"# <:icon_cross:1372375094336425986> Permission Denied\n\nYou need `Manage Channels` permission to activate AI chatbot."),
                accent_color=None
            )
            view.add_item(container)
            await ctx .send (view=view )
            return 

        target_channel =channel or ctx .channel 
        guild_id =ctx .guild .id 
        channel_id =target_channel .id 


        await self .bot .db .execute (
        """
            INSERT OR REPLACE INTO chatbot_settings (guild_id, enabled, chatbot_channel_id)
            VALUES (?, ?, ?)
            """,
        (guild_id ,1 ,channel_id )
        )
        await self .bot .db .commit ()


        self .chatbot_enabled [guild_id ]=True 
        self .chatbot_channels [guild_id ]=channel_id 

        view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)

        container.add_item(discord.ui.TextDisplay(f"# <:icon_tick:1372375089668161597> AI Chatbot Activated"))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay(f"AI chatbot has been enabled in {target_channel.mention}!\nI'll respond to all messages in that channel."))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay(f"**Activated by:** {ctx.author.mention}"))

        view.add_item(container)
        await ctx .send (view=view )

    @ai .command (name ="deactivate",description ="Disable the AI chatbot in the channel")
    async def ai_deactivate (self ,ctx :commands .Context ):
        """Disable AI chatbot in current server"""
        if not ctx .author .guild_permissions .manage_channels :
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(f"# <:icon_cross:1372375094336425986> Permission Denied\n\nYou need `Manage Channels` permission to deactivate AI chatbot."),
                accent_color=None
            )
            view.add_item(container)
            await ctx .send (view=view )
            return 

        guild_id =ctx .guild .id 


        await self .bot .db .execute (
        """
            INSERT OR REPLACE INTO chatbot_settings (guild_id, enabled, chatbot_channel_id)
            VALUES (?, ?, ?)
            """,
        (guild_id ,0 ,None )
        )
        await self .bot .db .commit ()


        self .chatbot_enabled [guild_id ]=False 
        if guild_id in self .chatbot_channels :
            del self .chatbot_channels [guild_id ]

        view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)

        container.add_item(discord.ui.TextDisplay(f"# 🔇 AI Chatbot Deactivated"))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay("AI chatbot has been disabled in this server."))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay(f"**Deactivated by:** {ctx.author.mention}"))

        view.add_item(container)
        await ctx .send (view=view )



    @ai .command (name ="ask",description ="Ask the AI a question")
    @app_commands .describe (question ="Question to ask")
    async def ai_ask (self ,ctx :commands .Context ,*,question :str ):
        """Ask AI a question"""
        await ctx .defer ()

        try :
            history =[{"role":"user","content":question }]
            answer =await self ._get_groq_response (question ,history )

            view = discord.ui.LayoutView()
            container = discord.ui.Container(accent_color=None)

            container.add_item(discord.ui.TextDisplay(f"# 🤖 AI Response"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay(answer))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay(f"**Your Question:** {question}"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay(f"**Asked by:** {ctx.author.mention}"))

            view.add_item(container)
            await ctx .send (view=view )
        except Exception as e :
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"# 🤖 AI Response\n\n❌ **Error processing question**\n\nPlease try again later."),
                accent_color=None
            )
            error_view.add_item(error_container)
            await ctx.send(view=error_view)



    @ai .command (name ="database-clear",description ="Clear your AI conversation data and personality")
    async def ai_database_clear (self ,ctx :commands .Context ):
        """Clear user's own AI conversation data and personality"""
        await ctx .defer ()

        user_id =ctx .author .id 
        guild_id =ctx .guild .id 

        try :

            await self .bot .db .execute (
            "DELETE FROM conversation_memory WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )


            await self .bot .db .execute (
            "DELETE FROM chatbot_history WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )


            await self .bot .db .execute (
            "DELETE FROM user_personalities WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )


            if user_id in self .conversation_history :
                del self .conversation_history [user_id ]

            await self .bot .db .commit ()

            view = discord.ui.LayoutView()
            container = discord.ui.Container(accent_color=None)

            container.add_item(discord.ui.TextDisplay(f"# 🗑️ Your Data Cleared"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay("Your AI conversation data and personality have been cleared successfully. The AI will start fresh with you!"))
            container.add_item(discord.ui.Separator())
            
            container.add_item(discord.ui.TextDisplay(f"**Cleared by:** {ctx.author.mention}"))

            view.add_item(container)
            await ctx .send (view=view ,ephemeral =True )

        except Exception as e :
            logger .error (f"Error clearing user AI data: {e}")
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"# 🗑️ Data Clear Error\n\nFailed to clear your data: {e}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await ctx .send (view=error_view ,ephemeral =True )

    async def _get_conversation_stats (self ,user_id :int ,guild_id :int )->dict :
        """Get conversation statistics for the user"""
        try :
            async with self .bot .db .execute (
            "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM conversation_memory WHERE user_id = ? AND guild_id = ?",
            (user_id ,guild_id )
            )as cursor :
                row =await cursor .fetchone ()
                if row and row [0 ]>0 :
                    return {
                    "message_count":row [0 ],
                    "first_message":row [1 ],
                    "last_message":row [2 ]
                    }
                return None 
        except Exception as e :
            logger .error (f"Error getting conversation stats: {e}")
            return None 

    async def _store_conversation_message (self ,user_id :int ,guild_id :int ,role :str ,content :str ):
        """Store a conversation message in the database"""
        try :
            await self .bot .db .execute (
            """
                INSERT INTO conversation_memory (user_id, guild_id, role, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
            (user_id ,guild_id ,role ,content ,datetime .now (timezone .utc ))
            )
            await self .bot .db .commit ()
        except Exception as e :
            logger .error (f"Error storing conversation message: {e}")

    async def _get_conversation_history (self ,user_id :int ,guild_id :int ,limit :int =20 )->list :
        """Get conversation history from database with smart context retention"""
        try :
            async with self .bot .db .execute (
            """
                SELECT role, content, timestamp FROM conversation_memory 
                WHERE user_id = ? AND guild_id = ? 
                ORDER BY timestamp DESC LIMIT ?
                """,
            (user_id ,guild_id ,limit *2 )
            )as cursor :
                rows =await cursor .fetchall ()


                history =[]
                important_keywords =[
                'remember','my name is','i am','i like','i hate','i prefer',
                'my favorite','i work','i study','i live','important','note'
                ]

                recent_messages =[]
                important_messages =[]

                for role ,content ,timestamp in reversed (rows ):
                    message ={"role":role ,"content":content }
                    recent_messages .append (message )


                    if any (keyword in content .lower ()for keyword in important_keywords ):
                        important_messages .append (message )



                final_history =recent_messages [-15 :]


                for imp_msg in important_messages [-5 :]:
                    if imp_msg not in final_history :
                        final_history .insert (0 ,imp_msg )

                return final_history [-limit :]

        except Exception as e :
            logger .error (f"Error getting conversation history: {e}")
            return []

    async def _save_chat_history (self ,user_id :int ,guild_id :int ,message :str ,response :str ):
        """Save chat history to database"""
        try :
            await self .bot .db .execute (
            """
                INSERT INTO chatbot_history (user_id, guild_id, message, response, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
            (user_id ,guild_id ,message ,response ,datetime .now (timezone .utc ).isoformat ())
            )
            await self .bot .db .commit ()
        except Exception as e :
            logger .error (f"Error saving chat history: {e}")

    async def _cleanup_old_conversations (self ):
        """Smart cleanup of conversation history - keep important context longer"""
        try :

            very_old_cutoff =datetime .now (timezone .utc )-timedelta (hours =24 )


            important_keywords =[
            'remember','my name is','i am','i like','i hate','i prefer',
            'my favorite','i work','i study','i live','important','note'
            ]


            await self .bot .db .execute (
            """
                DELETE FROM conversation_memory 
                WHERE timestamp < ? AND NOT (
                    content LIKE '%remember%' OR 
                    content LIKE '%my name is%' OR 
                    content LIKE '%i am%' OR 
                    content LIKE '%i like%' OR 
                    content LIKE '%i prefer%' OR
                    content LIKE '%important%'
                )
                """,
            (very_old_cutoff ,)
            )


            await self .bot .db .execute (
            """
                DELETE FROM conversation_memory 
                WHERE rowid NOT IN (
                    SELECT rowid FROM conversation_memory
                    ORDER BY timestamp DESC
                    LIMIT 100
                )
                """
            )

            await self .bot .db .commit ()
        except Exception as e :
            logger .error (f"Error cleaning up old conversations: {e}")

    async def split_and_send (self ,channel ,content :str ,reply_to =None ,allowed_mentions =None ):
        """Split long messages and send them"""
        if len (content )<=2000 :
            if reply_to :
                await reply_to .reply (content ,allowed_mentions =allowed_mentions )
            else :
                await channel .send (content ,allowed_mentions =allowed_mentions )
        else :

            parts =[]
            while len (content )>2000 :
                split_point =content .rfind (' ',0 ,2000 )
                if split_point ==-1 :
                    split_point =2000 
                parts .append (content [:split_point ])
                content =content [split_point :].lstrip ()
            if content :
                parts .append (content )


            for i ,part in enumerate (parts ):
                if i ==0 and reply_to :
                    await reply_to .reply (part ,allowed_mentions =allowed_mentions )
                else :
                    await channel .send (part ,allowed_mentions =allowed_mentions )








    async def enable_roleplay (self ,ctx ):
        """Enable roleplay mode in the current channel"""
        channel_id =ctx .channel .id 
        user_id =ctx .author .id 

        if channel_id in self .roleplay_channels :
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(f"# 🎭 Roleplay Mode\n\nRoleplay mode is already enabled in this channel! Use `/ai roleplay-disable` to turn it off."),
                accent_color=None
            )
            view.add_item(container)
            await ctx .send (view=view )
            return 

        self .roleplay_channels [channel_id ]={
        "user_id":user_id ,
        "character_gender":None ,
        "character_type":None ,
        "awaiting_character":True ,
        }
        
        view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)

        container.add_item(discord.ui.TextDisplay(f"# 🎭 Roleplay Mode"))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay("Roleplay mode activated! To start, tell me what kind of character you want me to be.\n\nFor example: `female teacher` or `male astronaut`."))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay(f"**Activated by:** {ctx.author.mention}"))

        view.add_item(container)
        await ctx .send (view=view )

    async def disable_roleplay (self ,ctx ):
        """Disable roleplay mode in the current channel"""
        channel_id =ctx .channel .id 
        if channel_id not in self .roleplay_channels :
            view = discord.ui.LayoutView()
            container = discord.ui.Container(
                discord.ui.TextDisplay(f"# 🎭 Roleplay Mode\n\nRoleplay mode is not enabled in this channel! Use `/ai roleplay-enable` to turn it on."),
                accent_color=None
            )
            view.add_item(container)
            await ctx .send (view=view )
            return 

        del self .roleplay_channels [channel_id ]
        
        view = discord.ui.LayoutView()
        container = discord.ui.Container(accent_color=None)

        container.add_item(discord.ui.TextDisplay(f"# 🎭 Roleplay Mode"))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay("Roleplay mode disabled in this channel."))
        container.add_item(discord.ui.Separator())
        
        container.add_item(discord.ui.TextDisplay(f"**Disabled by:** {ctx.author.mention}"))

        view.add_item(container)
        await ctx .send (view=view )

    @ai .command (name ="roleplay-enable",description ="Enable roleplay mode in the current channel")
    async def ai_roleplay_enable (self ,ctx :commands .Context ):
        """Enable roleplay mode"""
        await self .enable_roleplay (ctx )

    @ai .command (name ="roleplay-disable",description ="Disable roleplay mode in the current channel")
    async def ai_roleplay_disable (self ,ctx :commands .Context ):
        """Disable roleplay mode"""
        await self .disable_roleplay (ctx )



async def setup (bot ):
    await bot .add_cog (AI (bot ))
"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
