"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
from __future__ import annotations
from discord.ext import commands
from discord import ui
import discord
from core import Cog, LightCore, Context
from utils.Tools import *


class GuildProfile(Cog):
    """Commands to customize the bot's guild-specific profile"""
    
    def __init__(self, bot: LightCore):
        self.bot = bot

    @commands.command(
        name="setguildavatar",
        help="Set the bot's avatar for this server only",
        aliases=["setguildpfp"]
    )
    @commands.has_permissions(administrator=True)
    async def setguildavatar(self, ctx: Context):
        """Set bot's guild-specific avatar"""
        
        if not ctx.message.attachments:
            return await ctx.send("Please attach an image while using this command.")
        
        attachment = ctx.message.attachments[0]
        
        if not attachment.content_type or not attachment.content_type.startswith('image/'):
            return await ctx.send("Please attach a valid image file.")
        
        try:
            avatar_bytes = await attachment.read()
            
            await ctx.guild.me.edit(avatar=avatar_bytes)
            
            container = ui.Container(accent_color=None)
            container.add_item(
                ui.TextDisplay("Bot's guild avatar has been updated successfully.")
            )
            
            await ctx.send(view=ui.LayoutView().add_item(container))
            
        except discord.HTTPException as e:
            await ctx.send(f"Failed to update avatar: {str(e)}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(
        name="setguildbanner",
        help="Set the bot's banner for this server only"
    )
    @commands.has_permissions(administrator=True)
    async def setguildbanner(self, ctx: Context):
        """Set bot's guild-specific banner"""
        
        if not ctx.message.attachments:
            return await ctx.send("Please attach an image while using this command.")
        
        attachment = ctx.message.attachments[0]
        
        if not attachment.content_type or not attachment.content_type.startswith('image/'):
            return await ctx.send("Please attach a valid image file.")
        
        try:
            banner_bytes = await attachment.read()
            
            await ctx.guild.me.edit(banner=banner_bytes)
            
            container = ui.Container(accent_color=None)
            container.add_item(
                ui.TextDisplay("Bot's guild banner has been updated successfully.")
            )
            
            await ctx.send(view=ui.LayoutView().add_item(container))
            
        except discord.HTTPException as e:
            await ctx.send(f"Failed to update banner: {str(e)}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(
        name="setguildbio",
        help="Set the bot's bio for this server only"
    )
    @commands.has_permissions(administrator=True)
    async def setguildbio(self, ctx: Context, *, bio: str):
        """Set bot's guild-specific bio"""
        
        if len(bio) > 190:
            return await ctx.send("Bio must be 190 characters or less.")
        
        try:
            await ctx.guild.me.edit(bio=bio)
            
            container = ui.Container(accent_color=None)
            container.add_item(
                ui.TextDisplay("Bot's guild bio has been updated successfully.")
            )
            
            await ctx.send(view=ui.LayoutView().add_item(container))
            
        except discord.HTTPException as e:
            await ctx.send(f"Failed to update bio: {str(e)}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(
        name="setguildname",
        help="Set the bot's nickname for this server only",
        aliases=["setguildnick", "setguildnickname"]
    )
    @commands.has_permissions(administrator=True)
    async def setguildname(self, ctx: Context, *, nickname: str):
        """Set bot's guild-specific nickname"""
        
        if len(nickname) > 32:
            return await ctx.send("Nickname must be 32 characters or less.")
        
        try:
            await ctx.guild.me.edit(nick=nickname)
            
            container = ui.Container(accent_color=None)
            container.add_item(
                ui.TextDisplay(f"Bot's guild nickname has been set to: {nickname}")
            )
            
            await ctx.send(view=ui.LayoutView().add_item(container))
            
        except discord.HTTPException as e:
            await ctx.send(f"Failed to update nickname: {str(e)}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command(
        name="setguildclear",
        help="Reset the bot's guild profile to default (avatar, banner, bio, nickname)",
        aliases=["clearguildprofile", "resetguildprofile"]
    )
    @commands.has_permissions(administrator=True)
    async def setguildclear(self, ctx: Context):
        """Reset bot's guild-specific profile to default"""
        
        try:
            await ctx.guild.me.edit(avatar=None, banner=None, bio=None, nick=None)
            
            container = ui.Container(accent_color=None)
            container.add_item(
                ui.TextDisplay("Bot's guild profile has been reset to default successfully.")
            )
            
            await ctx.send(view=ui.LayoutView().add_item(container))
            
        except discord.HTTPException as e:
            await ctx.send(f"Failed to reset profile: {str(e)}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
