"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""

import discord
from discord.ext import commands
from discord import ui
from utils.Tools import *
import asyncio

class UnbanAllProgressContainer(ui.Container):
    def __init__(self, guild_name, total_bans):
        super().__init__(accent_color=None)
        self.total_bans = total_bans
        
        description = f"**Mass Unban in Progress**\n\n"
        description += f"**Server:** {guild_name}\n"
        description += f"**Total Bans to Process:** {total_bans}\n"
        description += f"**Status:** Processing...\n\n"
        description += "⏳ Please wait while all banned users are being unbanned."
        
        self.add_item(ui.TextDisplay(description))

class UnbanAllResultContainer(ui.Container):
    def __init__(self, guild_name, total_bans, success_count, failed_count, author):
        super().__init__(accent_color=None)
        
        description = f"**Mass Unban Completed**\n\n"
        description += f"**Server:** {guild_name}\n"
        description += f"**Total Bans Processed:** {total_bans}\n"
        description += f"**Successfully Unbanned:** {success_count}\n"
        description += f"**Failed to Unban:** {failed_count}\n\n"
        description += f"**Moderator:** {author.mention}"
        
        if success_count == total_bans:
            description += "\n\n✅ All users have been successfully unbanned!"
        elif success_count > 0:
            description += f"\n\n⚠️ {failed_count} users could not be unbanned (likely due to permissions or errors)."
        else:
            description += "\n\n❌ No users could be unbanned. Check bot permissions."
        
        self.add_item(ui.TextDisplay(description))

class ConfirmUnbanAllContainer(ui.Container):
    def __init__(self, guild_name, ban_count, author):
        super().__init__(accent_color=None)
        
        description = f"**⚠️ MASS UNBAN CONFIRMATION ⚠️**\n\n"
        description += f"**Server:** {guild_name}\n"
        description += f"**Total Banned Users:** {ban_count}\n\n"
        description += "**Are you sure you want to unban ALL users?**\n"
        description += "This action cannot be undone!\n\n"
        description += f"**Moderator:** {author.mention}"
        
        self.add_item(ui.TextDisplay(description))
        
        self.action_row = ui.ActionRow()
        self.action_row.add_item(ui.Button(label="✅ Confirm", style=discord.ButtonStyle.danger, custom_id="confirm_unbanall"))
        self.action_row.add_item(ui.Button(label="❌ Cancel", style=discord.ButtonStyle.secondary, custom_id="cancel_unbanall"))
        self.add_item(self.action_row)

class UnbanAllView(ui.LayoutView):
    def __init__(self, author, guild, ban_list):
        super().__init__(timeout=60.0)
        self.author = author
        self.guild = guild
        self.ban_list = ban_list
        self.message = None
        self.confirmed = False
        
        container = ConfirmUnbanAllContainer(guild.name, len(ban_list), author)
        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You are not allowed to interact with this!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for container in self.children:
            if hasattr(container, 'action_row'):
                for item in container.action_row.children:
                    item.disabled = True
        
        if self.message and not self.confirmed:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    async def interaction_handler(self, interaction: discord.Interaction):
        """Handle all interactions for this view"""
        if not await self.interaction_check(interaction):
            return
            
        custom_id = interaction.data.get("custom_id")
        
        if custom_id == "confirm_unbanall":
            self.confirmed = True
            await self.process_unban_all(interaction)
        elif custom_id == "cancel_unbanall":
            self.clear_items()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("**Mass Unban Cancelled**\n\nThe mass unban operation has been cancelled by the moderator."))
            self.add_item(container)
            await interaction.response.edit_message(view=self)

    async def process_unban_all(self, interaction: discord.Interaction):
        """Process the mass unban operation"""
        self.clear_items()
        progress_container = UnbanAllProgressContainer(self.guild.name, len(self.ban_list))
        self.add_item(progress_container)
        await interaction.response.edit_message(view=self)
        
        success_count = 0
        failed_count = 0
        
        for ban_entry in self.ban_list:
            try:
                await self.guild.unban(ban_entry.user, reason=f"Mass unban requested by {self.author}")
                success_count += 1
                
                await asyncio.sleep(0.5)
                
            except Exception:
                failed_count += 1
        
        self.clear_items()
        result_container = UnbanAllResultContainer(
            self.guild.name, 
            len(self.ban_list), 
            success_count, 
            failed_count, 
            self.author
        )
        self.add_item(result_container)
        
        try:
            await self.message.edit(view=self)
        except Exception:
            pass

class UnbanAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(0, 0, 0)

    @commands.hybrid_command(
        name="unbanall",
        help="Unbans all users from the server",
        usage="unbanall",
        aliases=["massunban", "unban-all"]
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.max_concurrency(1, per=commands.BucketType.guild, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unbanall(self, ctx):
        ban_list = [entry async for entry in ctx.guild.bans()]
        
        if not ban_list:
            embed = discord.Embed(
                title="No Banned Users",
                description="There are no banned users in this server.",
                color=self.color
            )
            await ctx.send(embed=embed)
            return
        
        view = UnbanAllView(author=ctx.author, guild=ctx.guild, ban_list=ban_list)
        message = await ctx.reply(view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(UnbanAll(bot))

"""
@Author: LightCore
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development)
    + for any queries reach out Community or DM me.
"""
