"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord
from discord.ext import commands
from discord import ui
import random
import json
from utils.logger import logger
from utils.Tools import *

class ProfilePictures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anime_pfps = []
        self.male_pfps = []
        self.female_pfps = []
        self.matching_pfps = []
        self.load_pfps()

    def load_pfps(self):
        """Load pfps from JSON files"""
        try:
            with open('pfps/anime.json', 'r') as f:
                self.anime_pfps = json.load(f)
        except Exception as e:
            logger.error("PFPS", f"Error loading anime.json: {e}")
            
        try:
            with open('pfps/males.json', 'r') as f:
                self.male_pfps = json.load(f)
        except Exception as e:
            logger.error("PFPS", f"Error loading males.json: {e}")
            
        try:
            with open('pfps/females.json', 'r') as f:
                self.female_pfps = json.load(f)
        except Exception as e:
            logger.error("PFPS", f"Error loading females.json: {e}")
            
        try:
            with open('pfps/matching.json', 'r') as f:
                raw_data = json.load(f)
                self.matching_pfps = [pair for pair in raw_data if isinstance(pair, list) and len(pair) >= 2]
                logger.success("PFPS", f"Loaded {len(self.matching_pfps)} valid matching pfp pairs (out of {len(raw_data)})")
        except Exception as e:
            logger.error("PFPS", f"Error loading matching.json: {e}")

    @commands.group(name="pfp", aliases=["pfps"])
    @blacklist_check()
    @ignore_check()
    async def pfp(self, ctx):
        """Profile picture commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @pfp.command(name="anime")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def anime(self, ctx):
        if not self.anime_pfps:
            await ctx.send("No anime pfps available.")
            return
            
        shuffled_pfps = random.sample(self.anime_pfps, len(self.anime_pfps))
        current_index = 0
        
        async def create_pfp_view(index: int):
            layout_view = ui.LayoutView(timeout=300.0)
            container = ui.Container(accent_color=None)
            
            container.add_item(ui.TextDisplay("# Anime Profile Pictures"))
            container.add_item(ui.Separator())
            
            gallery = ui.MediaGallery()
            gallery.add_item(media=shuffled_pfps[index])
            container.add_item(gallery)
            
            container.add_item(ui.Separator())
            
            button_row = ui.ActionRow(
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowLeft:1385846432535412758>",
                    custom_id="pfp_first",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_left:1385846548625363117>",
                    custom_id="pfp_prev",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_right:1385846525204103252>",
                    custom_id="pfp_next",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowRight:1385846409902948362>",
                    custom_id="pfp_last",
                    style=discord.ButtonStyle.secondary
                )
            )
            container.add_item(button_row)
            
            layout_view.add_item(container)
            return layout_view
        
        initial_view = await create_pfp_view(current_index)
        msg = await ctx.send(view=initial_view)
        
        def check(interaction: discord.Interaction):
            return interaction.user.id == ctx.author.id and interaction.message.id == msg.id
        
        while True:
            try:
                interaction = await self.bot.wait_for('interaction', timeout=300.0, check=check)
                
                custom_id = interaction.data.get('custom_id')
                
                if custom_id == 'pfp_first':
                    current_index = 0
                elif custom_id == 'pfp_prev':
                    current_index = (current_index - 1) % len(shuffled_pfps)
                elif custom_id == 'pfp_next':
                    current_index = (current_index + 1) % len(shuffled_pfps)
                elif custom_id == 'pfp_last':
                    current_index = len(shuffled_pfps) - 1
                
                updated_view = await create_pfp_view(current_index)
                await interaction.response.edit_message(view=updated_view)
                
            except:
                try:
                    expired_view = ui.LayoutView()
                    expired_container = ui.Container(accent_color=None)
                    expired_container.add_item(ui.TextDisplay("# Container Expired\nPlease use the command again"))
                    expired_view.add_item(expired_container)
                    await msg.edit(view=expired_view)
                except:
                    pass
                break

    @pfp.command(name="male")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def male(self, ctx):
        if not self.male_pfps:
            await ctx.send("No male pfps available.")
            return
            
        shuffled_pfps = random.sample(self.male_pfps, len(self.male_pfps))
        current_index = 0
        
        async def create_pfp_view(index: int):
            layout_view = ui.LayoutView(timeout=300.0)
            container = ui.Container(accent_color=None)
            
            container.add_item(ui.TextDisplay("# Male Profile Pictures"))
            container.add_item(ui.Separator())
            
            gallery = ui.MediaGallery()
            gallery.add_item(media=shuffled_pfps[index])
            container.add_item(gallery)
            
            container.add_item(ui.Separator())
            
            button_row = ui.ActionRow(
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowLeft:1385846432535412758>",
                    custom_id="pfp_first",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_left:1385846548625363117>",
                    custom_id="pfp_prev",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_right:1385846525204103252>",
                    custom_id="pfp_next",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowRight:1385846409902948362>",
                    custom_id="pfp_last",
                    style=discord.ButtonStyle.secondary
                )
            )
            container.add_item(button_row)
            
            layout_view.add_item(container)
            return layout_view
        
        initial_view = await create_pfp_view(current_index)
        msg = await ctx.send(view=initial_view)
        
        def check(interaction: discord.Interaction):
            return interaction.user.id == ctx.author.id and interaction.message.id == msg.id
        
        while True:
            try:
                interaction = await self.bot.wait_for('interaction', timeout=300.0, check=check)
                
                custom_id = interaction.data.get('custom_id')
                
                if custom_id == 'pfp_first':
                    current_index = 0
                elif custom_id == 'pfp_prev':
                    current_index = (current_index - 1) % len(shuffled_pfps)
                elif custom_id == 'pfp_next':
                    current_index = (current_index + 1) % len(shuffled_pfps)
                elif custom_id == 'pfp_last':
                    current_index = len(shuffled_pfps) - 1
                
                updated_view = await create_pfp_view(current_index)
                await interaction.response.edit_message(view=updated_view)
                
            except:
                try:
                    expired_view = ui.LayoutView()
                    expired_container = ui.Container(accent_color=None)
                    expired_container.add_item(ui.TextDisplay("# Container Expired\nPlease use the command again"))
                    expired_view.add_item(expired_container)
                    await msg.edit(view=expired_view)
                except:
                    pass
                break

    @pfp.command(name="female")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def female(self, ctx):
        if not self.female_pfps:
            await ctx.send("No female pfps available.")
            return
            
        shuffled_pfps = random.sample(self.female_pfps, len(self.female_pfps))
        current_index = 0
        
        async def create_pfp_view(index: int):
            layout_view = ui.LayoutView(timeout=300.0)
            container = ui.Container(accent_color=None)
            
            container.add_item(ui.TextDisplay("# Female Profile Pictures"))
            container.add_item(ui.Separator())
            
            gallery = ui.MediaGallery()
            gallery.add_item(media=shuffled_pfps[index])
            container.add_item(gallery)
            
            container.add_item(ui.Separator())
            
            button_row = ui.ActionRow(
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowLeft:1385846432535412758>",
                    custom_id="pfp_first",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_left:1385846548625363117>",
                    custom_id="pfp_prev",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_right:1385846525204103252>",
                    custom_id="pfp_next",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowRight:1385846409902948362>",
                    custom_id="pfp_last",
                    style=discord.ButtonStyle.secondary
                )
            )
            container.add_item(button_row)
            
            layout_view.add_item(container)
            return layout_view
        
        initial_view = await create_pfp_view(current_index)
        msg = await ctx.send(view=initial_view)
        
        def check(interaction: discord.Interaction):
            return interaction.user.id == ctx.author.id and interaction.message.id == msg.id
        
        while True:
            try:
                interaction = await self.bot.wait_for('interaction', timeout=300.0, check=check)
                
                custom_id = interaction.data.get('custom_id')
                
                if custom_id == 'pfp_first':
                    current_index = 0
                elif custom_id == 'pfp_prev':
                    current_index = (current_index - 1) % len(shuffled_pfps)
                elif custom_id == 'pfp_next':
                    current_index = (current_index + 1) % len(shuffled_pfps)
                elif custom_id == 'pfp_last':
                    current_index = len(shuffled_pfps) - 1
                
                updated_view = await create_pfp_view(current_index)
                await interaction.response.edit_message(view=updated_view)
                
            except:
                try:
                    expired_view = ui.LayoutView()
                    expired_container = ui.Container(accent_color=None)
                    expired_container.add_item(ui.TextDisplay("# Container Expired\nPlease use the command again"))
                    expired_view.add_item(expired_container)
                    await msg.edit(view=expired_view)
                except:
                    pass
                break

    @pfp.command(name="matching")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def matching(self, ctx):
        if not self.matching_pfps:
            await ctx.send("No matching pfps available.")
            return
            
        shuffled_pfps = random.sample(self.matching_pfps, len(self.matching_pfps))
        current_index = 0
        
        async def create_pfp_view(index: int):
            layout_view = ui.LayoutView(timeout=300.0)
            container = ui.Container(accent_color=None)
            
            container.add_item(ui.TextDisplay("# Matching Profile Pictures"))
            container.add_item(ui.Separator())
            
            pair = shuffled_pfps[index]
            
            gallery = ui.MediaGallery()
            if isinstance(pair, list) and len(pair) >= 2:
                gallery.add_item(media=pair[0])
                gallery.add_item(media=pair[1])
            
            if gallery.items:
                container.add_item(gallery)
            else:
                container.add_item(ui.TextDisplay("*Could not load this pair. Please try the next one.*"))
            
            container.add_item(ui.Separator())
            
            button_row = ui.ActionRow(
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowLeft:1385846432535412758>",
                    custom_id="pfp_matching_first",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_left:1385846548625363117>",
                    custom_id="pfp_matching_prev",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_right:1385846525204103252>",
                    custom_id="pfp_matching_next",
                    style=discord.ButtonStyle.secondary
                ),
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowRight:1385846409902948362>",
                    custom_id="pfp_matching_last",
                    style=discord.ButtonStyle.secondary
                )
            )
            container.add_item(button_row)
            
            layout_view.add_item(container)
            return layout_view
        
        initial_view = await create_pfp_view(current_index)
        msg = await ctx.send(view=initial_view)
        
        def check(interaction: discord.Interaction):
            return interaction.user.id == ctx.author.id and interaction.message.id == msg.id
        
        while True:
            try:
                interaction = await self.bot.wait_for('interaction', timeout=300.0, check=check)
                
                custom_id = interaction.data.get('custom_id')
                
                if custom_id == 'pfp_matching_first':
                    current_index = 0
                elif custom_id == 'pfp_matching_prev':
                    current_index = (current_index - 1) % len(shuffled_pfps)
                elif custom_id == 'pfp_matching_next':
                    current_index = (current_index + 1) % len(shuffled_pfps)
                elif custom_id == 'pfp_matching_last':
                    current_index = len(shuffled_pfps) - 1
                
                updated_view = await create_pfp_view(current_index)
                await interaction.response.edit_message(view=updated_view)
                
            except asyncio.TimeoutError:
                try:
                    expired_view = ui.LayoutView()
                    expired_container = ui.Container(accent_color=None)
                    expired_container.add_item(ui.TextDisplay("# Container Expired\nPlease use the command again"))
                    expired_view.add_item(expired_container)
                    await msg.edit(view=expired_view)
                except:
                    pass
                break
            except Exception as e:
                logger.error("PFPS", f"Error in matching pfp command: {e}")
                try:
                    error_view = ui.LayoutView()
                    error_container = ui.Container(accent_color=None)
                    error_container.add_item(ui.TextDisplay("# Error Occurred\nPlease use the command again"))
                    error_view.add_item(error_container)
                    await msg.edit(view=error_view)
                except:
                    pass
                break

async def setup(bot):
    await bot.add_cog(ProfilePictures(bot))
