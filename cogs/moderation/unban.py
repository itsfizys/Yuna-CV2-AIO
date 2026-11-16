"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .ext import commands 
from discord import ui 
from utils .Tools import *

class BanContainer(ui.Container):
    def __init__(self, user, author):
        super().__init__(accent_color=None)
        self.user = user
        self.author = author
        
        self.add_item(ui.TextDisplay(f"**{user.name} is Not Banned!**\n\n**Requested User is not banned in this server.**\n\n__Ban__: Click on the `Ban` button to ban the mentioned user."))
        
        self.ban_row = ui.ActionRow()
        self.ban_row.add_item(ui.Button(label="Ban", style=discord.ButtonStyle.danger, custom_id="ban_user"))
        self.ban_row.add_item(ui.Button(emoji="<:delete:1372988987836469450>", style=discord.ButtonStyle.gray, custom_id="delete_message"))
        self.add_item(self.ban_row)

class UnbanSuccessContainer(ui.Container):
    def __init__(self, user, author, dm_status, reason):
        super().__init__(accent_color=None)
        self.user = user
        self.author = author
        
        description = f"**Successfully Unbanned {user.name}**\n\n"
        description += f"**Target User:** [{user}](https://discord.com/users/{user.id})\n"
        description += f"**User Mention:** {user.mention}\n"
        description += f"**DM Sent:** {dm_status}\n"
        description += f"**Reason:** {reason}\n\n"
        description += f"**Moderator:** {author.mention}"
        
        self.add_item(ui.TextDisplay(description))
        
        self.action_row = ui.ActionRow()
        self.action_row.add_item(ui.Button(label="Ban", style=discord.ButtonStyle.danger, custom_id="ban_user"))
        self.action_row.add_item(ui.Button(emoji="<:delete:1372988987836469450>", style=discord.ButtonStyle.gray, custom_id="delete_message"))
        self.add_item(self.action_row)

class BanSuccessContainer(ui.Container):
    def __init__(self, user, author, dm_status, reason):
        super().__init__(accent_color=None)
        self.user = user
        self.author = author
        
        description = f"**Successfully Banned {user.name}**\n\n"
        description += f"**Target User:** [{user}](https://discord.com/users/{user.id})\n"
        description += f"**User Mention:** {user.mention}\n"
        description += f"**DM Sent:** {dm_status}\n"
        description += f"**Reason:** {reason}\n\n"
        description += f"**Moderator:** {author.mention}"
        
        self.add_item(ui.TextDisplay(description))

class ReasonModal(ui.Modal):
    def __init__(self, user, author, view):
        super().__init__(title="Ban Reason")
        self.user = user
        self.author = author
        self.view = view
        self.reason_input = ui.TextInput(
            label="Reason for Banning",
            placeholder="Provide a reason for banning or leave it blank for no reason.",
            required=False,
            max_length=2000,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason_input.value or "No reason provided"
        
        try:
            await self.user.send(f"<:warning:1372989665115901994> You have been Banned from **{self.author.guild.name}** by **{self.author}**. Reason: {reason}")
            dm_status = "Yes"
        except (discord.Forbidden, discord.HTTPException):
            dm_status = "No"

        try:
            await interaction.guild.ban(self.user, reason=f"Ban requested by {self.author}")
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

        success_container = BanSuccessContainer(self.user, self.author, dm_status, reason)
        self.view.clear_items()
        self.view.add_item(success_container)
        
        try:
            await interaction.response.edit_message(view=self.view)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

class UnbanLayoutView(ui.LayoutView):
    def __init__(self, user, author, is_banned=True, dm_status=None, reason=None):
        super().__init__(timeout=120.0)
        self.user = user
        self.author = author
        self.message = None
        
        if is_banned:
            container = UnbanSuccessContainer(user, author, dm_status, reason)
        else:
            container = BanContainer(user, author)
            
        self.add_item(container)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You are not allowed to interact with this!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for container in self.children:
            if hasattr(container, 'ban_row'):
                for item in container.ban_row.children:
                    item.disabled = True
            elif hasattr(container, 'action_row'):
                for item in container.action_row.children:
                    item.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    async def interaction_handler(self, interaction: discord.Interaction):
        """Handle all interactions for this view"""
        if not await self.interaction_check(interaction):
            return
            
        custom_id = interaction.data.get("custom_id")
        
        if custom_id == "ban_user":
            modal = ReasonModal(user=self.user, author=self.author, view=self)
            await interaction.response.send_modal(modal)
        elif custom_id == "delete_message":
            try:
                await interaction.message.delete()
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(0, 0, 0)

    def get_user_avatar(self, user):
        return user.avatar.url if user.avatar else user.default_avatar.url

    @commands.hybrid_command(
        name="unban",
        help="Unbans a user from the Server",
        usage="unban <member>",
        aliases=["forgive", "pardon"]
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason=None):
        bans = [entry async for entry in ctx.guild.bans()]
        
        if not any(ban_entry.user.id == user.id for ban_entry in bans):
            view = UnbanLayoutView(user=user, author=ctx.author, is_banned=False)
            message = await ctx.reply(view=view)
            view.message = message
            return

        try:
            await user.send(f"<:icon_tick:1372375089668161597> You have been unbanned from **{ctx.guild.name}** by **{ctx.author}**. Reason: {reason or 'No reason provided'}")
            dm_status = "Yes"
        except (discord.Forbidden, discord.HTTPException):
            dm_status = "No"

        await ctx.guild.unban(user, reason=f"Unban requested by {ctx.author} for reason: {reason or 'No reason provided'}")

        reasonn = reason or "No reason provided"
        
        view = UnbanLayoutView(user=user, author=ctx.author, is_banned=True, dm_status=dm_status, reason=reasonn)
        message = await ctx.reply(view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(Unban(bot))


"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
