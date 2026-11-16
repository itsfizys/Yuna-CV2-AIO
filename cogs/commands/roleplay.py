"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""

import discord 
from discord .ext import commands 
from discord import app_commands
from discord import ui
import aiohttp 
import random 
from core import Context 
from core .Cog import Cog 
from core .LightCore import LightCore 
from utils .Tools import *

class Roleplay (Cog ,name ="roleplay"):
    def __init__ (self ,client :LightCore ):
        self .client =client 

    def help_custom (self ):
        emoji ='🎭'
        label ="Roleplay"
        description ="Interactive roleplay commands"
        return emoji ,label ,description 

    async def get_roleplay_gif (self ,action ):
        """Fetch animated GIF from nekos.best and Tenor APIs with fallback"""

        try :
            async with aiohttp .ClientSession ()as session :
                url =f"https://nekos.best/api/v2/{action}"
                async with session .get (url )as response :
                    if response .status ==200 :
                        data =await response .json ()
                        if data .get ("results")and len (data ["results"])>0 :
                            return data ["results"][0 ].get ("url")
        except Exception as e :
            print (f"Nekos.best API error: {e}")


        try :
            async with aiohttp .ClientSession ()as session :
                url =f"https://tenor.googleapis.com/v2/search"
                params ={
                "q":f"anime {action}",
                "key":"AIzaSyAyimkuYQYF_FXVALexPuGQctUWRURdCYQ",
                "limit":25 ,
                "contentfilter":"medium",
                "media_filter":"gif"
                }

                async with session .get (url ,params =params )as response :
                    if response .status ==200 :
                        data =await response .json ()
                        if data .get ("results"):

                            all_gifs =[result .get ("media_formats",{}).get ("gif",{}).get ("url")
                            for result in data ["results"]
                            if result .get ("media_formats",{}).get ("gif",{}).get ("url")]

                            if all_gifs :
                                return random .choice (all_gifs )

        except Exception as e :
            print (f"Tenor API error: {e}")


        action_fallbacks ={
        "hug":[
        "https://media.tenor.com/VBXfHaXXK8UAAAAC/anime-hug.gif",
        "https://media.tenor.com/KAplWFVgZcMAAAAC/anime-hug-cute.gif",
        "https://media.tenor.com/x6xj9CyH_TYAAAAC/wholesome-hug.gif"
        ],
        "kiss":[
        "https://media.tenor.com/X2n2sz4wNYMAAAAC/anime-kiss.gif",
        "https://media.tenor.com/pK3lBkhH4EIAAAAC/anime-kiss-cute.gif"
        ],
        "cuddle":[
        "https://media.tenor.com/7vy_3CQrN8IAAAAC/anime-cuddle.gif",
        "https://media.tenor.com/YCEuJQT6_qsAAAAC/cuddle-anime.gif"
        ],
        "pat":[
        "https://media.tenor.com/efzrKPH-xeYAAAAC/anime-pat.gif",
        "https://media.tenor.com/d2bhHySVT9QAAAAC/anime-pat-head.gif"
        ],
        "slap":[
        "https://media.tenor.com/R_rjwlEH7zMAAAAC/anime-slap.gif",
        "https://media.tenor.com/HJZp5MrYHmMAAAAC/anime-slap-funny.gif"
        ],
        "tickle":[
        "https://media.tenor.com/rggT2ROoFpYAAAAC/anime-tickle.gif"
        ],
        "poke":[
        "https://media.tenor.com/1MoLS3INZuEAAAAC/anime-poke.gif"
        ],
        "wave":[
        "https://media.tenor.com/E3b2EAFV_pIAAAAC/anime-wave.gif"
        ],
        "dance":[
        "https://media.tenor.com/EAK-sPw8aRMAAAAC/anime-dance.gif"
        ],
        "cry":[
        "https://media.tenor.com/WZ8P6_LQQ2AAAAAC/anime-cry.gif"
        ],
        "laugh":[
        "https://media.tenor.com/84fgtyXgqTUAAAAC/anime-laugh.gif"
        ],
        "smile":[
        "https://media.tenor.com/Wn9X2FKr3PEAAAAC/anime-smile.gif"
        ],
        "blush":[
        "https://media.tenor.com/Mc8KFXbSJXUAAAAC/anime-blush.gif"
        ],
        "wink":[
        "https://media.tenor.com/YzWbgGF2sIEAAAAC/anime-wink.gif"
        ],
        "thumbsup":[
        "https://media.tenor.com/7hKJhE2gzGEAAAAC/anime-thumbs-up.gif"
        ],
        "clap":[
        "https://media.tenor.com/cxeBKKIqz8oAAAAC/anime-clap.gif"
        ],
        "bow":[
        "https://media.tenor.com/8KYAj3b2JO4AAAAC/anime-bow.gif"
        ],
        "salute":[
        "https://media.tenor.com/7w8WaOVY5T8AAAAC/anime-salute.gif"
        ],
        "facepalm":[
        "https://media.tenor.com/wQ0jLkfWgDYAAAAC/anime-facepalm.gif"
        ],
        "shrug":[
        "https://media.tenor.com/QIFq7g4r79EAAAAC/anime-shrug.gif"
        ],
        "sleep":[
        "https://media.tenor.com/W45_Xl9-enoAAAAC/anime-sleep.gif"
        ],
        "eat":[
        "https://media.tenor.com/qA7wC6Z3oAQAAAAC/anime-eating.gif"
        ],
        "drink":[
        "https://media.tenor.com/BHJqPnXiZdEAAAAC/anime-drink.gif"
        ],
        "run":[
        "https://media.tenor.com/Vq8MbpQlhWEAAAAC/anime-running.gif"
        ]
        }

        fallback_gifs =action_fallbacks .get (action ,action_fallbacks ["hug"])
        return random .choice (fallback_gifs )

    async def create_action_embed (self ,ctx ,action ,target =None ):
        if target and target .id ==ctx .author .id :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            
            container.add_item(ui.TextDisplay("# <:icon_danger:1372375135604047902> Invalid Action"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("You can't perform this action on yourself! Try targeting someone else."))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f"**Requested by:** {ctx.author.mention}"))
            
            view.add_item(container)
            return await ctx .reply (view=view ,mention_author =False )


        gif_url =await self .get_roleplay_gif (action )


        action_emojis ={
        "hug":"🤗","kiss":"💋","cuddle":"🫂","pat":"👋","slap":"✋",
        "tickle":"🤭","poke":"👉","wave":"👋","dance":"💃","cry":"😢",
        "laugh":"😂","smile":"😊","blush":"😊","wink":"😉","thumbsup":"👍",
        "clap":"👏","bow":"🙇","salute":"🫡","facepalm":"🤦","shrug":"🤷",
        "sleep":"😴","eat":"🍽️","drink":"🥤","run":"🏃"
        }

        emoji =action_emojis .get (action ,"✨")


        action_colors ={
        "hug":0xff9ff3 ,"kiss":0xff69b4 ,"cuddle":0xffa07a ,"pat":0x98fb98 ,
        "slap":0xff6347 ,"tickle":0xffd700 ,"poke":0x87ceeb ,"wave":0x90ee90 ,
        "dance":0xda70d6 ,"cry":0x4169e1 ,"laugh":0xffd700 ,"smile":0xffb6c1 ,
        "blush":0xffb6c1 ,"wink":0xdda0dd ,"thumbsup":0x32cd32 ,"clap":0xffa500 ,
        "bow":0xd2691e ,"salute":0x4682b4 ,"facepalm":0xf0e68c ,"shrug":0xc0c0c0 ,
        "sleep":0x9370db ,"eat":0xff8c00 ,"drink":0x20b2aa ,"run":0xff4500 
        }

        color =action_colors .get (action ,0x7289da )


        action_descriptions ={
        "hug":[
        f"{ctx.author.display_name} hugs {target.display_name if target else 'everyone'}! 🤗",
        f"{ctx.author.display_name} gives {target.display_name if target else 'everyone'} a warm hug~",
        f"{ctx.author.display_name} wraps {target.display_name if target else 'everyone'} in a loving embrace!"
        ],
        "kiss":[
        f"{ctx.author.display_name} kisses {target.display_name if target else 'the air'}'s lips~"if target else f"{ctx.author.display_name} kisses the air",
        f"{ctx.author.display_name} kissed {target.display_name if target else 'someone'}! Cute!",
        f"{ctx.author.display_name} gives {target.display_name if target else 'everyone'} a sweet kiss 💋"
        ],
        "cuddle":[
        f"{ctx.author.display_name} cuddles {target.display_name if target else 'a pillow'} warmly~",
        f"{ctx.author.display_name} snuggles up to {target.display_name if target else 'someone'}!",
        f"{ctx.author.display_name} gives {target.display_name if target else 'everyone'} cozy cuddles!"
        ],
        "pat":[
        f"{ctx.author.display_name} pats {target.display_name if target else 'someone'} gently",
        f"{ctx.author.display_name} gives {target.display_name if target else 'someone'} headpats~",
        f"{ctx.author.display_name} softly pats {target.display_name if target else 'someone'}"
        ],
        "slap":[
        f"{ctx.author.display_name} slaps {target.display_name if target else 'the air'} playfully!",
        f"{ctx.author.display_name} gives {target.display_name if target else 'someone'} a light slap",
        f"{ctx.author.display_name} playfully slaps {target.display_name if target else 'around'}!"
        ]
        }


        descriptions =action_descriptions .get (action ,[f"{ctx.author.display_name} {action}s {target.display_name if target else ''}!"])
        author_text =random .choice (descriptions )

        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        
        container.add_item(ui.TextDisplay(f"**{emoji} {author_text}**"))
        gallery = ui.MediaGallery()
        gallery.add_item(media=gif_url)
        container.add_item(gallery)
        
        view.add_item(container)
        await ctx .reply (view=view ,mention_author =False )

    async def create_action_embed_interaction (self ,interaction :discord .Interaction ,action ,target =None ):
        if target and target .id ==interaction .user .id :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            
            container.add_item(ui.TextDisplay("# <:icon_danger:1372375135604047902> Invalid Action"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("You can't perform this action on yourself! Try targeting someone else."))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f"**Requested by:** {interaction.user.mention}"))
            
            view.add_item(container)
            return await interaction .response .send_message (view=view )


        gif_url =await self .get_roleplay_gif (action )


        action_emojis ={
        "hug":"🤗","kiss":"💋","cuddle":"🫂","pat":"👋","slap":"✋",
        "tickle":"🤭","poke":"👉","wave":"👋","dance":"💃","cry":"😢",
        "laugh":"😂","smile":"😊","blush":"😊","wink":"😉","thumbsup":"👍",
        "clap":"👏","bow":"🙇","salute":"🫡","facepalm":"🤦","shrug":"🤷",
        "sleep":"😴","eat":"🍽️","drink":"🥤","run":"🏃"
        }

        emoji =action_emojis .get (action ,"✨")


        action_colors ={
        "hug":0xff9ff3 ,"kiss":0xff69b4 ,"cuddle":0xffa07a ,"pat":0x98fb98 ,
        "slap":0xff6347 ,"tickle":0xffd700 ,"poke":0x87ceeb ,"wave":0x90ee90 ,
        "dance":0xda70d6 ,"cry":0x4169e1 ,"laugh":0xffd700 ,"smile":0xffb6c1 ,
        "blush":0xffb6c1 ,"wink":0xdda0dd ,"thumbsup":0x32cd32 ,"clap":0xffa500 ,
        "bow":0xd2691e ,"salute":0x4682b4 ,"facepalm":0xf0e68c ,"shrug":0xc0c0c0 ,
        "sleep":0x9370db ,"eat":0xff8c00 ,"drink":0x20b2aa ,"run":0xff4500 
        }

        color =action_colors .get (action ,0x7289da )


        action_descriptions ={
        "hug":[
        f"{interaction.user.display_name} hugs {target.display_name if target else 'everyone'}! 🤗",
        f"{interaction.user.display_name} gives {target.display_name if target else 'everyone'} a warm hug~",
        f"{interaction.user.display_name} wraps {target.display_name if target else 'everyone'} in a loving embrace!"
        ],
        "kiss":[
        f"{interaction.user.display_name} kisses {target.display_name if target else 'the air'}'s lips~"if target else f"{interaction.user.display_name} kisses the air",
        f"{interaction.user.display_name} kissed {target.display_name if target else 'someone'}! Cute!",
        f"{interaction.user.display_name} gives {target.display_name if target else 'everyone'} a sweet kiss 💋"
        ],
        "cuddle":[
        f"{interaction.user.display_name} cuddles {target.display_name if target else 'a pillow'} warmly~",
        f"{interaction.user.display_name} snuggles up to {target.display_name if target else 'someone'}!",
        f"{interaction.user.display_name} gives {target.display_name if target else 'everyone'} cozy cuddles!"
        ],
        "pat":[
        f"{interaction.user.display_name} pats {target.display_name if target else 'someone'} gently",
        f"{interaction.user.display_name} gives {target.display_name if target else 'someone'} headpats~",
        f"{interaction.user.display_name} softly pats {target.display_name if target else 'someone'}"
        ],
        "slap":[
        f"{interaction.user.display_name} slaps {target.display_name if target else 'the air'} playfully!",
        f"{interaction.user.display_name} gives {target.display_name if target else 'someone'} a light slap",
        f"{interaction.user.display_name} playfully slaps {target.display_name if target else 'around'}!"
        ]
        }


        descriptions =action_descriptions .get (action ,[f"{interaction.user.display_name} {action}s {target.display_name if target else ''}!"])
        author_text =random .choice (descriptions )

        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        
        container.add_item(ui.TextDisplay(f"**{emoji} {author_text}**"))
        gallery = ui.MediaGallery()
        gallery.add_item(media=gif_url)
        container.add_item(gallery)
        
        view.add_item(container)
        await interaction .response .send_message (view=view )

    @commands .command (name="hug")
    async def hug (self ,ctx :Context ,target :discord .Member =None ):
        """Hug someone sweetly"""
        await self .create_action_embed (ctx ,"hug",target )

    @commands .command (name="kiss")
    async def kiss (self ,ctx :Context ,target :discord .Member =None ):
        """Kiss someone lovingly"""
        await self .create_action_embed (ctx ,"kiss",target )

    @commands .command (name="cuddle")
    async def cuddle (self ,ctx :Context ,target :discord .Member =None ):
        """Cuddle someone warmly"""
        await self .create_action_embed (ctx ,"cuddle",target )

    @commands .command (name="pat")
    async def pat (self ,ctx :Context ,target :discord .Member =None ):
        """Pat someone gently"""
        await self .create_action_embed (ctx ,"pat",target )

    @commands .command (name="slap")
    async def slap (self ,ctx :Context ,target :discord .Member =None ):
        """Slap someone playfully"""
        await self .create_action_embed (ctx ,"slap",target )

    @commands .command (name="tickle")
    async def tickle (self ,ctx :Context ,target :discord .Member =None ):
        """Tickle someone playfully"""
        await self .create_action_embed (ctx ,"tickle",target )

    @commands .command (name="poke")
    async def poke (self ,ctx :Context ,target :discord .Member =None ):
        """Poke someone gently"""
        await self .create_action_embed (ctx ,"poke",target )

    @commands .command (name="wave")
    async def wave (self ,ctx :Context ,target :discord .Member =None ):
        """Wave at someone"""
        await self .create_action_embed (ctx ,"wave",target )

    @commands .command (name="dance")
    async def dance (self ,ctx :Context ):
        """Dance with joy"""
        await self .create_action_embed (ctx ,"dance")

    @commands .command (name="cry")
    async def cry (self ,ctx :Context ):
        """Cry sadly"""
        await self .create_action_embed (ctx ,"cry")

    @commands .command (name="laugh")
    async def laugh (self ,ctx :Context ):
        """Laugh heartily"""
        await self .create_action_embed (ctx ,"laugh")

    @commands .command (name="smile")
    async def smile (self ,ctx :Context ):
        """Smile happily"""
        await self .create_action_embed (ctx ,"smile")

    @commands .command (name="blush")
    async def blush (self ,ctx :Context ):
        """Blush shyly"""
        await self .create_action_embed (ctx ,"blush")

    @commands .command (name="wink")
    async def wink (self ,ctx :Context ,target :discord .Member =None ):
        """Wink at someone"""
        await self .create_action_embed (ctx ,"wink",target )

    @commands .command (name="thumbsup")
    async def thumbsup (self ,ctx :Context ):
        """Give thumbs up"""
        await self .create_action_embed (ctx ,"thumbsup")

    @commands .command (name="clap")
    async def clap (self ,ctx :Context ):
        """Clap enthusiastically"""
        await self .create_action_embed (ctx ,"clap")

    @commands .command (name="bow")
    async def bow (self ,ctx :Context ,target :discord .Member =None ):
        """Bow respectfully"""
        await self .create_action_embed (ctx ,"bow",target )

    @commands .command (name="salute")
    async def salute (self ,ctx :Context ,target :discord .Member =None ):
        """Salute formally"""
        await self .create_action_embed (ctx ,"salute",target )

    @commands .command (name="facepalm")
    async def facepalm (self ,ctx :Context ):
        """Facepalm in frustration"""
        await self .create_action_embed (ctx ,"facepalm")

    @commands .command (name="shrug")
    async def shrug (self ,ctx :Context ):
        """Shrug casually"""
        await self .create_action_embed (ctx ,"shrug")

    @commands .command (name="sleep")
    async def sleep (self ,ctx :Context ):
        """Sleep peacefully"""
        await self .create_action_embed (ctx ,"sleep")

    @commands .command (name="eat")
    async def eat (self ,ctx :Context ):
        """Eat something delicious"""
        await self .create_action_embed (ctx ,"eat")

    @commands .command (name="drink")
    async def drink (self ,ctx :Context ):
        """Drink something refreshing"""
        await self .create_action_embed (ctx ,"drink")

    @commands .command (name="run")
    async def run_command (self ,ctx :Context ):
        """Run quickly"""
        await self .create_action_embed (ctx ,"run")

    roleplay_group = app_commands .Group (name="roleplay",description="Interactive roleplay slash commands")

    @roleplay_group .command (name="hug")
    async def roleplay_hug (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Hug someone sweetly"""
        await self .create_action_embed_interaction (interaction ,"hug",target )

    @roleplay_group .command (name="kiss")
    async def roleplay_kiss (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Kiss someone lovingly"""
        await self .create_action_embed_interaction (interaction ,"kiss",target )

    @roleplay_group .command (name="cuddle")
    async def roleplay_cuddle (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Cuddle someone warmly"""
        await self .create_action_embed_interaction (interaction ,"cuddle",target )

    @roleplay_group .command (name="pat")
    async def roleplay_pat (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Pat someone gently"""
        await self .create_action_embed_interaction (interaction ,"pat",target )

    @roleplay_group .command (name="slap")
    async def roleplay_slap (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Slap someone playfully"""
        await self .create_action_embed_interaction (interaction ,"slap",target )

    @roleplay_group .command (name="tickle")
    async def roleplay_tickle (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Tickle someone playfully"""
        await self .create_action_embed_interaction (interaction ,"tickle",target )

    @roleplay_group .command (name="poke")
    async def roleplay_poke (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Poke someone gently"""
        await self .create_action_embed_interaction (interaction ,"poke",target )

    @roleplay_group .command (name="wave")
    async def roleplay_wave (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Wave at someone"""
        await self .create_action_embed_interaction (interaction ,"wave",target )

    @roleplay_group .command (name="dance")
    async def roleplay_dance (self ,interaction :discord .Interaction ):
        """Dance with joy"""
        await self .create_action_embed_interaction (interaction ,"dance")

    @roleplay_group .command (name="cry")
    async def roleplay_cry (self ,interaction :discord .Interaction ):
        """Cry sadly"""
        await self .create_action_embed_interaction (interaction ,"cry")

    @roleplay_group .command (name="laugh")
    async def roleplay_laugh (self ,interaction :discord .Interaction ):
        """Laugh heartily"""
        await self .create_action_embed_interaction (interaction ,"laugh")

    @roleplay_group .command (name="smile")
    async def roleplay_smile (self ,interaction :discord .Interaction ):
        """Smile happily"""
        await self .create_action_embed_interaction (interaction ,"smile")

    @roleplay_group .command (name="blush")
    async def roleplay_blush (self ,interaction :discord .Interaction ):
        """Blush shyly"""
        await self .create_action_embed_interaction (interaction ,"blush")

    @roleplay_group .command (name="wink")
    async def roleplay_wink (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Wink at someone"""
        await self .create_action_embed_interaction (interaction ,"wink",target )

    @roleplay_group .command (name="thumbsup")
    async def roleplay_thumbsup (self ,interaction :discord .Interaction ):
        """Give thumbs up"""
        await self .create_action_embed_interaction (interaction ,"thumbsup")

    @roleplay_group .command (name="clap")
    async def roleplay_clap (self ,interaction :discord .Interaction ):
        """Clap enthusiastically"""
        await self .create_action_embed_interaction (interaction ,"clap")

    @roleplay_group .command (name="bow")
    async def roleplay_bow (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Bow respectfully"""
        await self .create_action_embed_interaction (interaction ,"bow",target )

    @roleplay_group .command (name="salute")
    async def roleplay_salute (self ,interaction :discord .Interaction ,target :discord .Member =None ):
        """Salute formally"""
        await self .create_action_embed_interaction (interaction ,"salute",target )

    @roleplay_group .command (name="facepalm")
    async def roleplay_facepalm (self ,interaction :discord .Interaction ):
        """Facepalm in frustration"""
        await self .create_action_embed_interaction (interaction ,"facepalm")

    @roleplay_group .command (name="shrug")
    async def roleplay_shrug (self ,interaction :discord .Interaction ):
        """Shrug casually"""
        await self .create_action_embed_interaction (interaction ,"shrug")

    @roleplay_group .command (name="sleep")
    async def roleplay_sleep (self ,interaction :discord .Interaction ):
        """Sleep peacefully"""
        await self .create_action_embed_interaction (interaction ,"sleep")

    @roleplay_group .command (name="eat")
    async def roleplay_eat (self ,interaction :discord .Interaction ):
        """Eat something delicious"""
        await self .create_action_embed_interaction (interaction ,"eat")

    @roleplay_group .command (name="drink")
    async def roleplay_drink (self ,interaction :discord .Interaction ):
        """Drink something refreshing"""
        await self .create_action_embed_interaction (interaction ,"drink")

    @roleplay_group .command (name="run")
    async def roleplay_run (self ,interaction :discord .Interaction ):
        """Run quickly"""
        await self .create_action_embed_interaction (interaction ,"run")

async def setup (client :LightCore ):
    cog =Roleplay (client )
    await client .add_cog (cog )
    client .tree .add_command (cog .roleplay_group )
"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
