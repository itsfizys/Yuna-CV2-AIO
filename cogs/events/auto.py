"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .utils import *
from core import LightCore ,Cog 
from utils .Tools import getConfig 
from utils .config import BotName ,serverLink 
from discord .ext import commands 
from discord import ui

class Autorole (Cog ):
    def __init__ (self ,bot :LightCore ):
        self .bot =bot

    @commands .Cog .listener (name ="on_guild_join")
    async def send_msg_to_adder (self ,guild :discord .Guild ):
        data =await getConfig (guild .id )
        prefix =data .get ("prefix","!")

        try:
            async for entry in guild .audit_logs (limit =3 ):
                if entry .action ==discord .AuditLogAction .bot_add :
                    view = ui.LayoutView()
                    container = ui.Container(accent_color=None)

                    container.add_item(ui.TextDisplay(f"<:icons_saturn:1372375229753593967> **Thanks for adding {BotName}!**"))
                    container.add_item(ui.Separator())

                    content_text = (
                        f"<a:GC_z_icon_rightarrow:1374279174751125534> My default prefix is `{prefix}`\n"
                        f"<a:GC_z_icon_rightarrow:1374279174751125534> Use `{prefix}help` to see a list of commands\n"
                        f"<a:GC_z_icon_rightarrow:1374279174751125534> For detailed guides, FAQ, and information, check out our help command!"
                    )
                    
                    bot_avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url
                    
                    container.add_item(
                        ui.Section(
                            ui.TextDisplay(content_text),
                            accessory=ui.Thumbnail(bot_avatar_url)
                        )
                    )

                    view.add_item(container)

                    try :
                        await entry .user .send (view=view)
                    except Exception as e :
                        print (f"Failed to send welcome message: {e}")
        except discord.Forbidden:
            print(f"Missing permissions to view audit logs in {guild.name}")
        except Exception as e:
            print(f"Error in on_guild_join: {e}")
"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
