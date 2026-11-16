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
import os
from typing import Optional, List
from utils.logger import logger

class GoogleSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="google", aliases=["g"])
    async def google(self, ctx, *, query: Optional[str] = None):
        """Search Google for anything you want"""
        
        try:
            serp_api_key = os.getenv('SERPAPI_KEY')
            if not serp_api_key:
                error_view = ui.LayoutView()
                error_container = ui.Container(accent_color=None)
                error_container.add_item(ui.TextDisplay("# ❌ Google Search Unavailable"))
                error_container.add_item(ui.Separator())
                error_container.add_item(ui.TextDisplay(
                    "SerpAPI key is not configured. Please contact the bot administrator to set up Google search functionality."
                ))
                error_view.add_item(error_container)
                await ctx.send(view=error_view)
                return
                
            if not query:
                error_view = ui.LayoutView()
                error_container = ui.Container(accent_color=None)
                error_container.add_item(ui.TextDisplay("# ❌ Missing Query"))
                error_container.add_item(ui.Separator())
                error_container.add_item(ui.TextDisplay(
                    "Please provide something to search for!\n\n"
                    "**Usage:** `google <search query>`\n"
                    "**Example:** `google how to make pizza`"
                ))
                error_view.add_item(error_container)
                await ctx.send(view=error_view)
                return
                
            blacklisted_words = [
                'porn', 'pussy', 'naked', 'vagina', 'dick', 'sex', 'xxx', 'nude', 'nsfw',
                'boobs', 'tits', 'penis', 'cock', 'fuck', 'shit', 'bitch', 'ass', 'anal',
                'orgasm', 'masturbate', 'horny', 'lesbian', 'gay porn', 'milf', 'teen sex',
                'adult', 'erotic', 'fetish', 'hardcore', 'blowjob', 'cumshot', 'threesome'
            ]
            
            query_lower = query.lower()
            if any(word.lower() in query_lower for word in blacklisted_words):
                blocked_view = ui.LayoutView()
                blocked_container = ui.Container(accent_color=None)
                blocked_container.add_item(ui.TextDisplay("# 🚫 Search Blocked"))
                blocked_container.add_item(ui.Separator())
                blocked_container.add_item(ui.TextDisplay(
                    "Your search query contains inappropriate content that is not allowed.\n\n"
                    "Please use appropriate search terms only."
                ))
                blocked_view.add_item(blocked_container)
                await ctx.send(view=blocked_view)
                return
                
            loading_view = ui.LayoutView()
            loading_container = ui.Container(accent_color=None)
            loading_container.add_item(ui.TextDisplay("# ⏳ Searching Google"))
            loading_container.add_item(ui.Separator())
            loading_container.add_item(ui.TextDisplay(
                f"Searching for: **{query}**\nFetching results from Google..."
            ))
            loading_view.add_item(loading_container)
            loading_msg = await ctx.send(view=loading_view)
            
            async with aiohttp.ClientSession() as session:
                params = {
                    'engine': 'google',
                    'q': query,
                    'api_key': serp_api_key
                }
                async with session.get('https://serpapi.com/search', params=params) as resp:
                    if resp.status != 200:
                        raise Exception(f"API returned status {resp.status}")
                    search_results = await resp.json()
                    
            if not search_results.get('organic_results') or len(search_results['organic_results']) == 0:
                no_results_view = ui.LayoutView()
                no_results_container = ui.Container(accent_color=None)
                no_results_container.add_item(ui.TextDisplay("# ❌ No Results Found"))
                no_results_container.add_item(ui.Separator())
                no_results_container.add_item(ui.TextDisplay(
                    f"No results found for: **{query}**\n\n"
                    "Try using different keywords or check your spelling."
                ))
                no_results_view.add_item(no_results_container)
                await loading_msg.edit(view=no_results_view)
                return
                
            all_results = search_results['organic_results'][:25]
            items_per_page = 5
            total_pages = (len(all_results) + items_per_page - 1) // items_per_page
            current_page = 1
            
            async def create_page_view(page: int):
                start_index = (page - 1) * items_per_page
                end_index = min(start_index + items_per_page, len(all_results))
                page_results = all_results[start_index:end_index]
                
                results_text = ""
                for i, result in enumerate(page_results):
                    result_num = start_index + i + 1
                    title = result.get('title', 'No title')
                    link = result.get('link', '#')
                    snippet = result.get('snippet', 'No description available')
                    
                    results_text += f"**{result_num}.** [{title}]({link})\n{snippet}\n\n"
                    
                layout_view = ui.LayoutView(timeout=300.0)
                container = ui.Container(accent_color=None)
                container.add_item(ui.TextDisplay(f"# 🔍 Google Search Results\n**Query:** {query}"))
                container.add_item(ui.Separator())
                container.add_item(ui.TextDisplay(results_text.strip()))
                container.add_item(ui.Separator())
                container.add_item(ui.TextDisplay(
                    f"**Page {page} of {total_pages}** • Showing {len(page_results)} of {len(all_results)} results"
                ))
                
                if total_pages > 1:
                    button_row = ui.ActionRow(
                        ui.Button(
                            label="",
                            emoji="<:SageDoubleArrowLeft:1385846432535412758>",
                            custom_id="google_home",
                            style=discord.ButtonStyle.secondary,
                            disabled=(page == 1)
                        ),
                        ui.Button(
                            label="",
                            emoji="<:arrow_left:1385846548625363117>",
                            custom_id="google_back",
                            style=discord.ButtonStyle.secondary,
                            disabled=(page == 1)
                        ),
                        ui.Button(
                            label="",
                            emoji="<:arrow_right:1385846525204103252>",
                            custom_id="google_next",
                            style=discord.ButtonStyle.secondary,
                            disabled=(page == total_pages)
                        ),
                        ui.Button(
                            label="",
                            emoji="<:SageDoubleArrowRight:1385846409902948362>",
                            custom_id="google_last",
                            style=discord.ButtonStyle.secondary,
                            disabled=(page == total_pages)
                        )
                    )
                    container.add_item(button_row)
                    
                layout_view.add_item(container)
                return layout_view
                
            initial_view = await create_page_view(current_page)
            result_message = await loading_msg.edit(view=initial_view)
            
            if total_pages > 1:
                def check(interaction: discord.Interaction):
                    return (interaction.user.id == ctx.author.id and
                            interaction.message and
                            interaction.message.id == result_message.id)
                            
                while True:
                    try:
                        interaction = await self.bot.wait_for('interaction', timeout=300.0, check=check)
                        await interaction.response.defer()
                        
                        custom_id = interaction.data.get('custom_id')
                        
                        if custom_id == 'google_home':
                            current_page = 1
                        elif custom_id == 'google_back':
                            if current_page > 1:
                                current_page -= 1
                        elif custom_id == 'google_next':
                            if current_page < total_pages:
                                current_page += 1
                        elif custom_id == 'google_last':
                            current_page = total_pages
                            
                        updated_view = await create_page_view(current_page)
                        await interaction.edit_original_response(view=updated_view)
                        
                    except Exception:
                        break
                        
        except Exception as e:
            logger.error(f"Google search error: {e}")
            
            error_message = "An error occurred while searching Google."
            if "API key" in str(e):
                error_message = "Invalid SerpAPI key. Please contact the bot administrator."
            elif "rate limit" in str(e).lower() or "quota" in str(e).lower():
                error_message = "Google search rate limit exceeded. Please try again later."
                
            error_view = ui.LayoutView()
            error_container = ui.Container(accent_color=None)
            error_container.add_item(ui.TextDisplay("# ❌ Search Failed"))
            error_container.add_item(ui.Separator())
            error_container.add_item(ui.TextDisplay(
                f"{error_message}\n\n"
                "Please try again with a different query or contact support if the issue persists."
            ))
            error_view.add_item(error_container)
            await ctx.send(view=error_view)

async def setup(bot):
    await bot.add_cog(GoogleSearch(bot))

"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
