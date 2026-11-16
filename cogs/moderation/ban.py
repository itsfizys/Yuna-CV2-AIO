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
        
        self.action_row = ui.ActionRow()
        self.action_row.add_item(ui.Button(label="Unban", style=discord.ButtonStyle.success, custom_id="unban_user"))
        self.action_row.add_item(ui.Button(emoji="<:delete:1372988987836469450>", style=discord.ButtonStyle.gray, custom_id="delete_message"))
        self.add_item(self.action_row)

class AlreadyBannedContainer(ui.Container):
    def __init__(self, user, author):
        super().__init__(accent_color=None)
        self.user = user
        self.author = author
        
        self.add_item(ui.TextDisplay(f"**{user.name} is Already Banned!**\n\n**Requested User is already banned in this server.**\n\n__Unban__: Click on the `Unban` button to unban the mentioned user."))
        
        self.action_row = ui.ActionRow()
        self.action_row.add_item(ui.Button(label="Unban", style=discord.ButtonStyle.success, custom_id="unban_user"))
        self.action_row.add_item(ui.Button(emoji="<:delete:1372988987836469450>", style=discord.ButtonStyle.gray, custom_id="delete_message"))
        self.add_item(self.action_row)

class UnbanModal(ui.Modal):
    def __init__(self, user, author, view):
        super().__init__(title="Unban Reason")
        self.user = user
        self.author = author
        self.view = view
        self.reason_input = ui.TextInput(
            label="Reason for Unbanning",
            placeholder="Provide a reason to unban or leave it blank for no reason.",
            required=False,
            max_length=2000,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason_input.value or "No reason provided"
        
        try:
            await self.user.send(f"<:icon_tick:1372375089668161597> You have been Unbanned from **{self.author.guild.name}** by **{self.author}**. Reason: {reason}")
            dm_status = "Yes"
        except (discord.Forbidden, discord.HTTPException):
            dm_status = "No"

        try:
            await interaction.guild.unban(self.user, reason=f"Unban requested by {self.author}")
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

        from .unban import UnbanSuccessContainer
        success_container = UnbanSuccessContainer(self.user, self.author, dm_status, reason)
        self.view.clear_items()
        self.view.add_item(success_container)
        
        try:
            await interaction.response.edit_message(view=self.view)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

class BanLayoutView(ui.LayoutView):
    def __init__(self, user, author, is_banned=False, dm_status=None, reason=None):
        super().__init__(timeout=120.0)
        self.user = user
        self.author = author
        self.message = None
        
        if is_banned:
            container = AlreadyBannedContainer(user, author)
        else:
            container = BanSuccessContainer(user, author, dm_status, reason)
            
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
        
        if custom_id == "unban_user":
            modal = UnbanModal(user=self.user, author=self.author, view=self)
            await interaction.response.send_modal(modal)
        elif custom_id == "delete_message":
            try:
                await interaction.message.delete()
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass 



class Ban (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .color =discord .Color .from_rgb (0 ,0 ,0 )

    def get_user_avatar (self ,user ):
        return user .avatar .url if user .avatar else user .default_avatar .url 

    @commands .hybrid_command (
    name ="ban",
    help ="Bans a user from the Server",
    usage ="ban <member>",
    aliases =["fuckban","hackban"])
    @blacklist_check ()
    @ignore_check ()
    @top_check ()
    @commands .cooldown (1 ,10 ,commands .BucketType .member )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (ban_members =True )
    @commands .bot_has_permissions (ban_members =True )
    async def ban (self ,ctx ,user :discord .User ,*,reason =None ):

        member =ctx .guild .get_member (user .id )
        if not member :
            try :
                user =await self .bot .fetch_user (user .id )
            except discord .NotFound :
                await ctx .send (f"User with ID {user.id} not found.")
                return 

        bans =[entry async for entry in ctx .guild .bans ()]
        if any (ban_entry .user .id ==user .id for ban_entry in bans ):
            view = BanLayoutView(user=user, author=ctx.author, is_banned=True)
            message = await ctx.reply(view=view)
            view.message = message
            return 

        if member ==ctx .guild .owner :
            error =discord .Embed (color =self .color ,description ="I can't ban the Server Owner!")
            error .set_author (name ="Error Banning User",icon_url ="https://i.ibb.co/TxtQNnyH/2400e46b-9674-4142-b2dc-73244e769c3b.png")
            error .set_footer (text =f"Requested by {ctx.author}",icon_url =self .get_user_avatar (ctx .author ))
            await ctx.reply(embed=error)
            return 

        if isinstance (member ,discord .Member )and member .top_role >=ctx .guild .me .top_role :
            error =discord .Embed (color =self .color ,description ="I can't ban a user with a higher or equal role!")
            error .set_footer (text =f"Requested by {ctx.author}",icon_url =self .get_user_avatar (ctx .author ))
            error .set_author (name ="Error Banning User",icon_url ="https://i.ibb.co/TxtQNnyH/2400e46b-9674-4142-b2dc-73244e769c3b.png")
            await ctx.reply(embed=error)
            return 

        if isinstance (member ,discord .Member ):
            if ctx .author !=ctx .guild .owner :
                if member .top_role >=ctx .author .top_role :
                    error =discord .Embed (color =self .color ,description ="You can't ban a user with a higher or equal role!")
                    error .set_footer (text =f"Requested by {ctx.author}",icon_url =self .get_user_avatar (ctx .author ))
                    error .set_author (name ="Error Banning User",icon_url ="https://i.ibb.co/TxtQNnyH/2400e46b-9674-4142-b2dc-73244e769c3b.png")
                    await ctx.reply(embed=error)
                    return 

        try :
            await user .send (f"<:icon_danger:1373170993236803688> You have been banned from **{ctx.guild.name}** by **{ctx.author}**. Reason: {reason or 'No reason provided'}")
            dm_status ="Yes"
        except discord .Forbidden :
            dm_status ="No"
        except discord .HTTPException :
            dm_status ="No"

        await ctx .guild .ban (user ,reason =f"Ban requested by {ctx.author} for reason: {reason or 'No reason provided'}")

        reasonn = reason or "No reason provided"
        
        view = BanLayoutView(user=user, author=ctx.author, is_banned=False, dm_status=dm_status, reason=reasonn)
        message = await ctx.reply(view=view)
        view.message = message 




async def setup(bot):
    await bot.add_cog(Ban(bot))

"""
@Author: LightCore
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development)
    + for any queries reach out Community or DM me.
"""
"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
