"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord.ext import commands
from discord import ui
import functools 
from utils.Tools import *


class HelpLayout(ui.LayoutView):
    def __init__(self, mapping: dict, ctx: commands.Context, homeembed: discord.Embed, ui_type: int):
        super().__init__(timeout=300.0)
        self.mapping, self.ctx, self.home = mapping, ctx, homeembed
        self.current_page = "home"
        
        self.container = ui.Container(accent_color=None)
        
        self.setup_home_content()
        
        self.add_item(self.container)
        
    def setup_home_content(self):
        """Set up the home page content"""
        self.container.clear_items()
        
        self.container.add_item(ui.TextDisplay(f"# {self.home.title}"))
        self.container.add_item(ui.Separator())
        
        if self.home.description:
            self.container.add_item(ui.TextDisplay(self.home.description))
            self.container.add_item(ui.Separator())
            
        for field in self.home.fields:
            field_text = f"**{field.name}**\n{field.value}"
            self.container.add_item(ui.TextDisplay(field_text))
            
        
    def setup_cog_content(self, cog_name):
        """Not used anymore - no categories"""
        pass
        
    async def select_callback(self, interaction: discord.Interaction):
        """Not used anymore - no select menu"""
        pass
        
    def get_cogs(self):
        return []
        
    def gen_pages(self):
        """Not used anymore - no categories"""
        return [], {}
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author


View = HelpLayout  # For any existing code that uses View

"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""