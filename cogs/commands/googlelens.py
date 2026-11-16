"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord
from discord.ext import commands
from discord import ui
import aiohttp
import asyncio
import os
import io
from typing import Optional, Dict
from utils.logger import logger

class GoogleLens(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_sessions: Dict[int, dict] = {}
        self.image_cache: Dict[int, discord.File] = {}
        
    @commands.command(name="googlelens", aliases=["glens", "reverseimage", "lens"])
    async def googlelens(self, ctx):
        """Perform reverse image search using Google Lens"""
        
        if not ctx.message.reference:
            error_view = ui.LayoutView()
            error_container = ui.Container(accent_color=None)
            error_container.add_item(ui.TextDisplay("# No Image Found"))
            error_container.add_item(ui.Separator())
            error_container.add_item(ui.TextDisplay(
                "Please reply to a message containing an image to use Google Lens search.\n\n"
                "**Usage:** Reply to an image with `googlelens` or `glens`"
            ))
            error_view.add_item(error_container)
            await ctx.send(view=error_view)
            return
            
        try:
            referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            
            if not referenced_message.attachments and not referenced_message.embeds:
                error_view = ui.LayoutView()
                error_container = ui.Container(accent_color=None)
                error_container.add_item(ui.TextDisplay("# No Image Found"))
                error_container.add_item(ui.Separator())
                error_container.add_item(ui.TextDisplay(
                    "The referenced message does not contain any images.\n\n"
                    "**Please reply to a message with:**\n• Image attachments\n• Embedded images"
                ))
                error_view.add_item(error_container)
                await ctx.send(view=error_view)
                return
                
            image_url = None
            
            if referenced_message.attachments:
                for attachment in referenced_message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        image_url = attachment.url
                        break
                        
            if not image_url and referenced_message.embeds:
                embed = referenced_message.embeds[0]
                if embed.image:
                    image_url = embed.image.url
                elif embed.thumbnail:
                    image_url = embed.thumbnail.url
                    
            if not image_url:
                error_view = ui.LayoutView()
                error_container = ui.Container(accent_color=None)
                error_container.add_item(ui.TextDisplay("# Invalid Image Format"))
                error_container.add_item(ui.Separator())
                error_container.add_item(ui.TextDisplay(
                    "No valid image found in the referenced message.\n\n"
                    "**Supported formats:** PNG, JPG, JPEG, GIF, WEBP"
                ))
                error_view.add_item(error_container)
                await ctx.send(view=error_view)
                return
                
            loading_view = ui.LayoutView()
            loading_container = ui.Container(accent_color=None)
            loading_container.add_item(ui.TextDisplay("# Processing Image"))
            loading_container.add_item(ui.Separator())
            loading_container.add_item(ui.TextDisplay("Performing Google Lens reverse image search..."))
            loading_view.add_item(loading_container)
            loading_msg = await ctx.send(view=loading_view)
            
            serp_api_key = os.getenv('SERPAPI_KEY')
            if not serp_api_key:
                error_view = ui.LayoutView()
                error_container = ui.Container(accent_color=None)
                error_container.add_item(ui.TextDisplay("# Configuration Required"))
                error_container.add_item(ui.Separator())
                error_container.add_item(ui.TextDisplay(
                    "SerpAPI key is not configured. Please contact the bot administrator to enable Google Lens functionality."
                ))
                error_view.add_item(error_container)
                await loading_msg.edit(view=error_view)
                return
                
            async with aiohttp.ClientSession() as session:
                params = {
                    'engine': 'google_lens',
                    'url': image_url,
                    'api_key': serp_api_key
                }
                async with session.get('https://serpapi.com/search', params=params) as resp:
                    if resp.status != 200:
                        raise Exception(f"API returned status {resp.status}")
                    results = await resp.json()
                    
            if not results.get('visual_matches') or len(results['visual_matches']) == 0:
                empty_view = ui.LayoutView()
                empty_container = ui.Container(accent_color=None)
                empty_container.add_item(ui.TextDisplay("# No Results Found"))
                empty_container.add_item(ui.Separator())
                empty_container.add_item(ui.TextDisplay(
                    "Google Lens could not find any matching images for this search."
                ))
                empty_view.add_item(empty_container)
                await loading_msg.edit(view=empty_view)
                return
                
            await self.display_search_results(loading_msg, results, image_url, ctx.author.id)
            
        except Exception as e:
            logger.error(f"Google Lens Error: {e}")
            error_view = ui.LayoutView()
            error_container = ui.Container(accent_color=None)
            error_container.add_item(ui.TextDisplay("# Search Failed"))
            error_container.add_item(ui.Separator())
            error_container.add_item(ui.TextDisplay(
                f"An error occurred while performing the reverse image search.\n\n**Error:** {str(e)}"
            ))
            error_view.add_item(error_container)
            await ctx.send(view=error_view)
            
    async def display_search_results(self, message, results, original_image_url: str, user_id: int):
        try:
            visual_matches = results.get('visual_matches', [])
            
            if not visual_matches:
                empty_view = ui.LayoutView()
                empty_container = ui.Container(accent_color=None)
                empty_container.add_item(ui.TextDisplay("# No Results Found"))
                empty_container.add_item(ui.Separator())
                empty_container.add_item(ui.TextDisplay(
                    "Google Lens could not find any matching images for this search."
                ))
                empty_view.add_item(empty_container)
                await message.edit(view=empty_view)
                return
                
            limited_matches = visual_matches[:15]
            
            filtered_results = []
            for match in limited_matches:
                source = (match.get('source') or '').lower()
                title = (match.get('title') or '').lower()
                link = (match.get('link') or '').lower()
                
                if any(x in source or x in link or x in title for x in [
                    'twitter.com', 'x.com', '/profile', '/avatar', 'profile picture',
                    'pbs.twimg.com', 'facebook.com', 'instagram.com', '/photo.jpg'
                ]):
                    continue
                    
                filtered_results.append(match)
                
            if not filtered_results:
                filtered_results = limited_matches[:5]  # Fallback to first 5 if all filtered
                
            self.user_sessions[user_id] = {
                'results': filtered_results,
                'original_image_url': original_image_url,
                'current_page': 0,
                'message': message
            }
            
            await self.update_results_display(user_id)
            
        except Exception as e:
            logger.error(f"Display results error: {e}")
            error_view = ui.LayoutView()
            error_container = ui.Container(accent_color=None)
            error_container.add_item(ui.TextDisplay("# Display Error"))
            error_container.add_item(ui.Separator())
            error_container.add_item(ui.TextDisplay(f"Failed to display search results: {str(e)}"))
            error_view.add_item(error_container)
            await message.edit(view=error_view)
            
    async def update_results_display(self, user_id: int):
        session_data = self.user_sessions.get(user_id)
        if not session_data:
            return
            
        results = session_data['results']
        current_page = session_data['current_page']
        original_image_url = session_data['original_image_url']
        message = session_data['message']
        
        current_result = results[current_page]
        
        type_indicator = "🔍 **Similar Image**"
        result_number = f"**Result {current_page + 1}** of **{len(results)}**"
        
        description = f"{type_indicator} • {result_number}\n\n"
        
        if current_result.get('title'):
            description += f"**Title:** {current_result['title']}\n"
        if current_result.get('snippet'):
            description += f"**Description:** {current_result['snippet']}\n"
        if current_result.get('source'):
            description += f"**Source:** {current_result['source']}\n"
        if current_result.get('link'):
            description += f"**Link:** [View Original]({current_result['link']})\n"
            
        description += f"\n**Original Image:** [View Image]({original_image_url})"
        
        layout_view = ui.LayoutView(timeout=300.0)
        container = ui.Container(accent_color=None)
        container.add_item(ui.TextDisplay("# ✅ Google Lens Search Results\n*Search completed successfully*"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(description))
        
        container.add_item(ui.Separator())
        gallery = ui.MediaGallery()
        
        if current_result.get('thumbnail'):
            gallery.add_item(
                media=current_result['thumbnail'],
                description=f"Result {current_page + 1}: {current_result.get('title', 'Similar image')}"
            )
        
        container.add_item(gallery)
        
        if len(results) > 1:
            container.add_item(ui.Separator())
            button_row = ui.ActionRow(
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowLeft:1385846432535412758>",
                    custom_id=f"glens_first_{user_id}",
                    style=discord.ButtonStyle.secondary,
                    disabled=(current_page == 0)
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_left:1385846548625363117>",
                    custom_id=f"glens_prev_{user_id}",
                    style=discord.ButtonStyle.secondary,
                    disabled=(current_page == 0)
                ),
                ui.Button(
                    label="",
                    emoji="<:arrow_right:1385846525204103252>",
                    custom_id=f"glens_next_{user_id}",
                    style=discord.ButtonStyle.secondary,
                    disabled=(current_page >= len(results) - 1)
                ),
                ui.Button(
                    label="",
                    emoji="<:SageDoubleArrowRight:1385846409902948362>",
                    custom_id=f"glens_last_{user_id}",
                    style=discord.ButtonStyle.secondary,
                    disabled=(current_page >= len(results) - 1)
                )
            )
            container.add_item(button_row)
            
        layout_view.add_item(container)
        await message.edit(view=layout_view)
        
        if len(results) > 1 and not session_data.get('collector_active'):
            session_data['collector_active'] = True
            asyncio.create_task(self.setup_button_collector(message, user_id))
            
    async def setup_button_collector(self, message, user_id: int):
        def check(interaction: discord.Interaction):
            return (interaction.user.id == user_id and 
                    interaction.data.get('custom_id', '').startswith('glens_') and
                    interaction.data.get('custom_id', '').endswith(f'_{user_id}'))
                    
        try:
            while user_id in self.user_sessions:
                try:
                    interaction = await self.bot.wait_for('interaction', timeout=300.0, check=check)
                    
                    session_data = self.user_sessions.get(user_id)
                    if not session_data:
                        await interaction.response.defer()
                        break
                        
                    await interaction.response.defer()
                    
                    action = interaction.data['custom_id'].split('_')[1]
                    
                    if action == 'first':
                        session_data['current_page'] = 0
                    elif action == 'prev':
                        if session_data['current_page'] > 0:
                            session_data['current_page'] -= 1
                    elif action == 'next':
                        if session_data['current_page'] < len(session_data['results']) - 1:
                            session_data['current_page'] += 1
                    elif action == 'last':
                        session_data['current_page'] = len(session_data['results']) - 1
                        
                    await self.update_results_display(user_id)
                    
                except asyncio.TimeoutError:
                    if user_id in self.user_sessions:
                        del self.user_sessions[user_id]
                    break
                    
        except Exception as e:
            logger.error(f"Button collector error: {e}")

async def setup(bot):
    await bot.add_cog(GoogleLens(bot))

"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
