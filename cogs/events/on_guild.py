"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
from discord .ext import commands 
from core import LightCore ,Cog 
from utils .Tools import getConfig 
import discord 
import logging 
from discord import ui 

logging .basicConfig (
level =logging .INFO ,
format ="\x1b[38;5;197m[\x1b[0m%(asctime)s\x1b[38;5;197m]\x1b[0m -> \x1b[38;5;197m%(message)s\x1b[0m",
datefmt ="%H:%M:%S",
)

client =LightCore ()

class Guild (Cog ):
    def __init__ (self ,client :LightCore ):
        self .client =client 

    @client .event 
    @commands .Cog .listener (name ="on_guild_join")
    async def on_guild_join (self ,guild :discord .Guild ):
        try :
            rope =[inv for inv in await guild .invites ()if inv .max_age ==0 and inv .max_uses ==0 ]
            ch =1324668336470102141 
            me =self .client .get_channel (ch )
            if me is None :
                logging .error (f"Channel with ID {ch} not found.")
                return 

            data =await getConfig (guild .id )
            prefix =data .get ("prefix","!")

            channels =len (set (self .client .get_all_channels ()))
            embed =discord .Embed (title =f"{guild.name}'s Information",color =0x000000 )
            embed .set_author (name ="Guild Joined")
            embed .set_footer (text =f"Added in {guild.name}")

            embed .add_field (
            name ="**__About__**",
            value =(
            f"**Name : ** {guild.name}\n**ID :** {guild.id}\n"
            f"**Owner <:owner_icon:1374273398204661800> :** {guild.owner} (<@{guild.owner_id}>)\n"
            f"<:icon_tick:1372375089668161597> **Created At : **{guild.created_at.month}/{guild.created_at.day}/{guild.created_at.year}\n"
            f"<:members_icons:1374275529674457150> **Members :** {len(guild.members)}"
            ),
            inline =False 
            )
            embed .add_field (name ="**__Description__**",value =guild .description or "No description",inline =False )
            embed .add_field (
            name ="**__Members__**",
            value =(
            f"<:members_icons:1374275529674457150> Members : {len(guild.members)}\n"
            f"<:icons_human:1374275042216509471> Humans : {len([m for m in guild.members if not m.bot])}\n"
            f"<:Automod:1374274713865687120> Bots : {len([m for m in guild.members if m.bot])}"
            ),
            inline =False 
            )
            embed .add_field (
            name ="**__Channels__**",
            value =(
            f"<:icon_categories:1373173618858659901> Categories : {len(guild.categories)}\n"
            f"<:icon_ignore:1373173575078379590> Text Channels : {len(guild.text_channels)}\n"
            f"<:icon_volume:1373928182314565693> Voice Channels : {len(guild.voice_channels)}\n"
            f"<:icons_home:1372374981203333140> Threads : {len(guild.threads)}"
            ),
            inline =False 
            )
            embed .add_field (
            name ="__Bot Stats:__",
            value =f"Servers: `{len(self.client.guilds)}`\nUsers: `{len(self.client.users)}`\nChannels: `{channels}`",
            inline =False 
            )

            if guild .icon :
                embed .set_thumbnail (url =guild .icon .url )
            embed .timestamp = discord .utils .utcnow ()

            await me .send (f"{rope[0]}"if rope else "No Pre-Made Invite Found",embed =embed )

            if not guild .chunked :
                await guild .chunk ()
        except Exception as e:
            logging .error (f"Error in on_guild_join: {e}")

    @client .event 
    @commands .Cog .listener (name ="on_guild_remove")
    async def on_guild_remove (self ,guild :discord .Guild ):
        try :
            ch =1324668336470102141 
            idk =self .client .get_channel (ch )
            if idk is None :
                logging .error (f"Channel with ID {ch} not found.")
                return 

            channels =len (set (self .client .get_all_channels ()))
            embed =discord .Embed (title =f"{guild.name}'s Information",color =0x000000 )
            embed .set_author (name ="Guild Removed")
            embed .set_footer (text =guild .name )

            embed .add_field (
            name ="**__About__**",
            value =(
            f"**Name : ** {guild.name}\n**ID :** {guild.id}\n"
            f"**Owner <:owner_icon:1374273398204661800> :** {guild.owner} (<@{guild.owner_id}>)\n"
            f"**Created At : ** {guild.created_at.month}/{guild.created_at.day}/{guild.created_at.year}\n"
            f"**Members :** {len(guild.members)}"
            ),
            inline =False 
            )
            embed .add_field (name ="**__Description__**",value =guild .description or "No description",inline =False )
            embed .add_field (
            name ="**__Members__**",
            value =(
            f"Members : {len(guild.members)}\n"
            f"Humans : {len([m for m in guild.members if not m.bot])}\n"
            f"Bots : {len([m for m in guild.members if m.bot])}"
            ),
            inline =False 
            )
            embed .add_field (
            name ="**__Channels__**",
            value =(
            f"Categories : {len(guild.categories)}\n"
            f"Text Channels : {len(guild.text_channels)}\n"
            f"Voice Channels : {len(guild.voice_channels)}\n"
            f"Threads : {len(guild.threads)}"
            ),
            inline =False 
            )
            embed .add_field (
            name ="__Bot Stats:__",
            value =f"Servers: `{len(self.client.guilds)}`\nUsers: `{len(self.client.users)}`\nChannels: `{channels}`",
            inline =False 
            )

            if guild .icon :
                embed .set_thumbnail (url =guild .icon .url )
            embed .timestamp = discord .utils .utcnow ()

            await idk .send (embed =embed )

        except Exception as e :
            logging .error (f"Error in on_guild_remove: {e}")




"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""