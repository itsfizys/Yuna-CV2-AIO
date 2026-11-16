"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .ext import commands 
from discord .ui import Button ,View 
from discord import Member 
from utils import Paginator ,DescriptionEmbedPaginator 
from datetime import timedelta 
import asyncio 

class Global (commands .Cog ):
    def __init__ (self ,client ):
        self .client =client 
        self .local_frozen_nicks ={}
        self .client .frozen_nicknames ={}

    @commands .group (name ="global",invoke_without_command =True )
    @commands .is_owner ()
    async def global_command (self ,ctx :commands .Context ):
        if ctx .subcommand_passed is None :
            await ctx .send_help (ctx .command )
            ctx .command .reset_cooldown (ctx )

    @global_command .command (name ="ban",help ="Bans the user from all mutual guilds.")
    @commands .is_owner ()
    async def global_ban (self ,ctx :commands .Context ,user :discord .User ,reason :str ="Severe violations of Discord's terms of service."):
        from discord import ui
        
        mutual_guilds =[guild for guild in self .client .guilds if guild .get_member (user .id )]
        mutual_count =len (mutual_guilds )

        view = ui.LayoutView()
        container = ui.Container(accent_color=0xED4245)
        
        container.add_item(ui.TextDisplay(f"# ⚠️ Global Ban Confirmation"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            f"**Target User:** {user.display_name} ({user.mention})\n"
            f"**User ID:** `{user.id}`\n"
            f"**Mutual Guilds:** {mutual_count}\n"
            f"**Reason:** {reason}\n\n"
            f"**Requestor:** {ctx.author.mention}"
        ))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay("⚠️ **This action will ban the user from all mutual guilds. Are you sure?**"))
        
        yes_button = ui.Button(label="Confirm Ban", style=discord.ButtonStyle.danger)
        no_button = ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        
        action_row = ui.ActionRow()
        action_row.add_item(yes_button)
        action_row.add_item(no_button)
        container.add_item(action_row)
        
        view.add_item(container)
        
        msg = await ctx.send(view=view)

        async def confirm_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            
            processing_view = ui.LayoutView()
            processing_container = ui.Container(accent_color=0xFEE75C)
            processing_container.add_item(ui.TextDisplay(f"# 🔄 Processing Global Ban\n\nBanning {user.display_name} from {mutual_count} guilds..."))
            processing_view.add_item(processing_container)
            await interaction.response.edit_message(view=processing_view)
            
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    await guild.ban(user, reason=reason)
                    success.append(guild.name)
                except:
                    failure.append(guild.name)
            
            result_view = ui.LayoutView()
            result_container = ui.Container(accent_color=0x57F287 if len(failure) == 0 else 0xFEE75C)
            
            result_container.add_item(ui.TextDisplay(f"# ✅ Global Ban Complete"))
            result_container.add_item(ui.Separator())
            result_container.add_item(ui.TextDisplay(
                f"**Target User:** {user.display_name}\n"
                f"**Total Guilds:** {mutual_count}\n"
                f"**✅ Success:** {len(success)} guilds\n"
                f"**❌ Failed:** {len(failure)} guilds"
            ))
            
            if success:
                success_button = ui.Button(label=f"View Successful ({len(success)})", style=discord.ButtonStyle.success)
                
                async def list_success_callback(inter):
                    if inter.user != ctx.author:
                        return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                    entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                    paginator = Paginator(
                        source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Bans [{len(success)}]", color=0x000000, per_page=10),
                        ctx=ctx
                    )
                    await paginator.paginate()
                    await inter.response.defer()
                
                success_button.callback = list_success_callback
                action_row = ui.ActionRow()
                action_row.add_item(success_button)
                
                if failure:
                    failure_button = ui.Button(label=f"View Failed ({len(failure)})", style=discord.ButtonStyle.danger)
                    
                    async def list_failure_callback(inter):
                        if inter.user != ctx.author:
                            return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                        entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                        paginator = Paginator(
                            source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Failed Bans [{len(failure)}]", color=0x000000, per_page=10),
                            ctx=ctx
                        )
                        await paginator.paginate()
                        await inter.response.defer()
                    
                    failure_button.callback = list_failure_callback
                    action_row.add_item(failure_button)
                
                result_container.add_item(action_row)
            
            result_view.add_item(result_container)
            await interaction.edit_original_response(view=result_view)

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm_callback
        no_button.callback = cancel_callback

    @global_command .command (name ="kick",help ="Kicks the user from all mutual guilds.")
    @commands .is_owner ()
    async def global_kick (self ,ctx :commands .Context ,user :discord .User ,reason :str ="Severe violations of Discord's terms of service."):
        from discord import ui
        
        mutual_guilds =[guild for guild in self .client .guilds if guild .get_member (user .id )]
        mutual_count =len (mutual_guilds )

        view = ui.LayoutView()
        container = ui.Container(accent_color=0xFEE75C)
        
        container.add_item(ui.TextDisplay(f"# ⚠️ Global Kick Confirmation"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            f"**Target User:** {user.display_name} ({user.mention})\n"
            f"**User ID:** `{user.id}`\n"
            f"**Mutual Guilds:** {mutual_count}\n"
            f"**Reason:** {reason}\n\n"
            f"**Requestor:** {ctx.author.mention}"
        ))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay("⚠️ **This action will kick the user from all mutual guilds. Are you sure?**"))
        
        yes_button = ui.Button(label="Confirm Kick", style=discord.ButtonStyle.danger)
        no_button = ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        
        action_row = ui.ActionRow()
        action_row.add_item(yes_button)
        action_row.add_item(no_button)
        container.add_item(action_row)
        
        view.add_item(container)
        
        msg = await ctx.send(view=view)

        async def confirm_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            
            processing_view = ui.LayoutView()
            processing_container = ui.Container(accent_color=0xFEE75C)
            processing_container.add_item(ui.TextDisplay(f"# 🔄 Processing Global Kick\n\nKicking {user.display_name} from {mutual_count} guilds..."))
            processing_view.add_item(processing_container)
            await interaction.response.edit_message(view=processing_view)
            
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    await guild.kick(user, reason=reason)
                    success.append(guild.name)
                except:
                    failure.append(guild.name)
            
            result_view = ui.LayoutView()
            result_container = ui.Container(accent_color=0x57F287 if len(failure) == 0 else 0xFEE75C)
            
            result_container.add_item(ui.TextDisplay(f"# ✅ Global Kick Complete"))
            result_container.add_item(ui.Separator())
            result_container.add_item(ui.TextDisplay(
                f"**Target User:** {user.display_name}\n"
                f"**Total Guilds:** {mutual_count}\n"
                f"**✅ Success:** {len(success)} guilds\n"
                f"**❌ Failed:** {len(failure)} guilds"
            ))
            
            if success:
                success_button = ui.Button(label=f"View Successful ({len(success)})", style=discord.ButtonStyle.success)
                
                async def list_success_callback(inter):
                    if inter.user != ctx.author:
                        return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                    entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                    paginator = Paginator(
                        source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Kicks [{len(success)}]", color=0x000000, per_page=10),
                        ctx=ctx
                    )
                    await paginator.paginate()
                    await inter.response.defer()
                
                success_button.callback = list_success_callback
                action_row = ui.ActionRow()
                action_row.add_item(success_button)
                
                if failure:
                    failure_button = ui.Button(label=f"View Failed ({len(failure)})", style=discord.ButtonStyle.danger)
                    
                    async def list_failure_callback(inter):
                        if inter.user != ctx.author:
                            return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                        entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                        paginator = Paginator(
                            source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Failed Kicks [{len(failure)}]", color=0x000000, per_page=10),
                            ctx=ctx
                        )
                        await paginator.paginate()
                        await inter.response.defer()
                    
                    failure_button.callback = list_failure_callback
                    action_row.add_item(failure_button)
                
                result_container.add_item(action_row)
            
            result_view.add_item(result_container)
            await interaction.edit_original_response(view=result_view)

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm_callback
        no_button.callback = cancel_callback

    @global_command .command (name ="timeout",help ="Timeouts the user for 28 days in all mutual guilds.")
    @commands .is_owner ()
    async def global_timeout (self ,ctx :commands .Context ,user :discord .User ,reason :str ="Severe violations of Discord's terms of service."):
        from discord import ui
        
        mutual_guilds =[guild for guild in self .client .guilds if guild .get_member (user .id )]
        mutual_count =len (mutual_guilds )

        view = ui.LayoutView()
        container = ui.Container(accent_color=0xFEE75C)
        
        container.add_item(ui.TextDisplay(f"# ⚠️ Global Timeout Confirmation"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            f"**Target User:** {user.display_name} ({user.mention})\n"
            f"**User ID:** `{user.id}`\n"
            f"**Mutual Guilds:** {mutual_count}\n"
            f"**Timeout Duration:** 28 days\n"
            f"**Reason:** {reason}\n\n"
            f"**Requestor:** {ctx.author.mention}"
        ))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay("⚠️ **This action will timeout the user for 28 days in all mutual guilds. Are you sure?**"))
        
        yes_button = ui.Button(label="Confirm Timeout", style=discord.ButtonStyle.danger)
        no_button = ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        
        action_row = ui.ActionRow()
        action_row.add_item(yes_button)
        action_row.add_item(no_button)
        container.add_item(action_row)
        
        view.add_item(container)
        
        msg = await ctx.send(view=view)

        async def confirm_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            
            processing_view = ui.LayoutView()
            processing_container = ui.Container(accent_color=0xFEE75C)
            processing_container.add_item(ui.TextDisplay(f"# 🔄 Processing Global Timeout\n\nTiming out {user.display_name} in {mutual_count} guilds..."))
            processing_view.add_item(processing_container)
            await interaction.response.edit_message(view=processing_view)
            
            success, failure = [], []
            time_delta = timedelta(days=28)
            
            for guild in mutual_guilds:
                member = guild.get_member(user.id)
                if member:
                    try:
                        await member.edit(timed_out_until=discord.utils.utcnow() + time_delta, reason=reason)
                        success.append(guild.name)
                    except:
                        failure.append(guild.name)
            
            result_view = ui.LayoutView()
            result_container = ui.Container(accent_color=0x57F287 if len(failure) == 0 else 0xFEE75C)
            
            result_container.add_item(ui.TextDisplay(f"# ✅ Global Timeout Complete"))
            result_container.add_item(ui.Separator())
            result_container.add_item(ui.TextDisplay(
                f"**Target User:** {user.display_name}\n"
                f"**Total Guilds:** {mutual_count}\n"
                f"**✅ Success:** {len(success)} guilds\n"
                f"**❌ Failed:** {len(failure)} guilds"
            ))
            
            if success:
                success_button = ui.Button(label=f"View Successful ({len(success)})", style=discord.ButtonStyle.success)
                
                async def list_success_callback(inter):
                    if inter.user != ctx.author:
                        return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                    entries = [f"{i+1}. {name}" for i, name in enumerate(success)]
                    paginator = Paginator(
                        source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Timeouts [{len(success)}]", color=0x000000, per_page=10),
                        ctx=ctx
                    )
                    await paginator.paginate()
                    await inter.response.defer()
                
                success_button.callback = list_success_callback
                action_row = ui.ActionRow()
                action_row.add_item(success_button)
                
                if failure:
                    failure_button = ui.Button(label=f"View Failed ({len(failure)})", style=discord.ButtonStyle.danger)
                    
                    async def list_failure_callback(inter):
                        if inter.user != ctx.author:
                            return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                        entries = [f"{i+1}. {name}" for i, name in enumerate(failure)]
                        paginator = Paginator(
                            source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Failed Timeouts [{len(failure)}]", color=0x000000, per_page=10),
                            ctx=ctx
                        )
                        await paginator.paginate()
                        await inter.response.defer()
                    
                    failure_button.callback = list_failure_callback
                    action_row.add_item(failure_button)
                
                result_container.add_item(action_row)
            
            result_view.add_item(result_container)
            await interaction.edit_original_response(view=result_view)

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm_callback
        no_button.callback = cancel_callback


    @global_command .command (name ="nick",help ="Changes the nickname of a user in all mutual guilds.")
    @commands .is_owner ()
    async def global_nick (self ,ctx :commands .Context ,user :discord .User ,*,name :str ):
        from discord import ui
        
        if len (name )>32 :
            return await ctx .send ("Nickname cannot exceed 32 characters. Please provide a shorter nickname.")

        mutual_guilds =[guild for guild in self .client .guilds if guild .get_member (user .id )]
        mutual_count =len (mutual_guilds )

        view = ui.LayoutView()
        container = ui.Container(accent_color=0x5865F2)
        
        container.add_item(ui.TextDisplay(f"# ⚠️ Global Nickname Change Confirmation"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            f"**Target User:** {user.display_name} ({user.mention})\n"
            f"**User ID:** `{user.id}`\n"
            f"**Mutual Guilds:** {mutual_count}\n"
            f"**New Nickname:** {name}\n\n"
            f"**Requestor:** {ctx.author.mention}"
        ))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay("⚠️ **This action will change the user's nickname in all mutual guilds. Are you sure?**"))
        
        yes_button = ui.Button(label="Confirm Change", style=discord.ButtonStyle.success)
        no_button = ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        
        action_row = ui.ActionRow()
        action_row.add_item(yes_button)
        action_row.add_item(no_button)
        container.add_item(action_row)
        
        view.add_item(container)
        
        msg = await ctx.send(view=view)

        async def confirm_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            
            processing_view = ui.LayoutView()
            processing_container = ui.Container(accent_color=0x5865F2)
            processing_container.add_item(ui.TextDisplay(f"# 🔄 Processing Global Nickname Change\n\nChanging {user.display_name}'s nickname in {mutual_count} guilds..."))
            processing_view.add_item(processing_container)
            await interaction.response.edit_message(view=processing_view)
            
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    member = guild.get_member(user.id)
                    if member:
                        await member.edit(nick=name)
                        success.append(guild.name)
                except:
                    failure.append(guild.name)
            
            result_view = ui.LayoutView()
            result_container = ui.Container(accent_color=0x57F287 if len(failure) == 0 else 0xFEE75C)
            
            result_container.add_item(ui.TextDisplay(f"# ✅ Global Nickname Change Complete"))
            result_container.add_item(ui.Separator())
            result_container.add_item(ui.TextDisplay(
                f"**Target User:** {user.display_name}\n"
                f"**New Nickname:** {name}\n"
                f"**Total Guilds:** {mutual_count}\n"
                f"**✅ Success:** {len(success)} guilds\n"
                f"**❌ Failed:** {len(failure)} guilds"
            ))
            
            if success:
                success_button = ui.Button(label=f"View Successful ({len(success)})", style=discord.ButtonStyle.success)
                
                async def list_success_callback(inter):
                    if inter.user != ctx.author:
                        return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                    entries = [f"{i+1}. {guild_name}" for i, guild_name in enumerate(success)]
                    paginator = Paginator(
                        source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Nickname Changes [{len(success)}]", color=0x000000, per_page=10),
                        ctx=ctx
                    )
                    await paginator.paginate()
                    await inter.response.defer()
                
                success_button.callback = list_success_callback
                action_row = ui.ActionRow()
                action_row.add_item(success_button)
                
                if failure:
                    failure_button = ui.Button(label=f"View Failed ({len(failure)})", style=discord.ButtonStyle.danger)
                    
                    async def list_failure_callback(inter):
                        if inter.user != ctx.author:
                            return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                        entries = [f"{i+1}. {guild_name}" for i, guild_name in enumerate(failure)]
                        paginator = Paginator(
                            source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Failed Nickname Changes [{len(failure)}]", color=0x000000, per_page=10),
                            ctx=ctx
                        )
                        await paginator.paginate()
                        await inter.response.defer()
                    
                    failure_button.callback = list_failure_callback
                    action_row.add_item(failure_button)
                
                result_container.add_item(action_row)
            
            result_view.add_item(result_container)
            await interaction.edit_original_response(view=result_view)

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm_callback
        no_button.callback = cancel_callback


    @global_command .command (name ="clearnick",help ="Clears the nickname of a user in all mutual guilds.")
    @commands .is_owner ()
    async def global_clearnick (self ,ctx :commands .Context ,user :discord .User ):
        from discord import ui
        
        mutual_guilds =[guild for guild in self .client .guilds if guild .get_member (user .id )]
        mutual_count =len (mutual_guilds )

        view = ui.LayoutView()
        container = ui.Container(accent_color=0x5865F2)
        
        container.add_item(ui.TextDisplay(f"# ⚠️ Global Nickname Clear Confirmation"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            f"**Target User:** {user.display_name} ({user.mention})\n"
            f"**User ID:** `{user.id}`\n"
            f"**Mutual Guilds:** {mutual_count}\n\n"
            f"**Requestor:** {ctx.author.mention}"
        ))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay("⚠️ **This action will clear the user's nickname in all mutual guilds. Are you sure?**"))
        
        yes_button = ui.Button(label="Confirm Clear", style=discord.ButtonStyle.success)
        no_button = ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        
        action_row = ui.ActionRow()
        action_row.add_item(yes_button)
        action_row.add_item(no_button)
        container.add_item(action_row)
        
        view.add_item(container)
        
        msg = await ctx.send(view=view)

        async def confirm_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            
            processing_view = ui.LayoutView()
            processing_container = ui.Container(accent_color=0x5865F2)
            processing_container.add_item(ui.TextDisplay(f"# 🔄 Processing Global Nickname Clear\n\nClearing {user.display_name}'s nickname in {mutual_count} guilds..."))
            processing_view.add_item(processing_container)
            await interaction.response.edit_message(view=processing_view)
            
            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    member = guild.get_member(user.id)
                    if member:
                        await member.edit(nick=None)
                        success.append(guild.name)
                except:
                    failure.append(guild.name)
            
            result_view = ui.LayoutView()
            result_container = ui.Container(accent_color=0x57F287 if len(failure) == 0 else 0xFEE75C)
            
            result_container.add_item(ui.TextDisplay(f"# ✅ Global Nickname Clear Complete"))
            result_container.add_item(ui.Separator())
            result_container.add_item(ui.TextDisplay(
                f"**Target User:** {user.display_name}\n"
                f"**Total Guilds:** {mutual_count}\n"
                f"**✅ Success:** {len(success)} guilds\n"
                f"**❌ Failed:** {len(failure)} guilds"
            ))
            
            if success:
                success_button = ui.Button(label=f"View Successful ({len(success)})", style=discord.ButtonStyle.success)
                
                async def list_success_callback(inter):
                    if inter.user != ctx.author:
                        return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                    entries = [f"{i+1}. {guild_name}" for i, guild_name in enumerate(success)]
                    paginator = Paginator(
                        source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Nickname Clears [{len(success)}]", color=0x000000, per_page=10),
                        ctx=ctx
                    )
                    await paginator.paginate()
                    await inter.response.defer()
                
                success_button.callback = list_success_callback
                action_row = ui.ActionRow()
                action_row.add_item(success_button)
                
                if failure:
                    failure_button = ui.Button(label=f"View Failed ({len(failure)})", style=discord.ButtonStyle.danger)
                    
                    async def list_failure_callback(inter):
                        if inter.user != ctx.author:
                            return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                        entries = [f"{i+1}. {guild_name}" for i, guild_name in enumerate(failure)]
                        paginator = Paginator(
                            source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Failed Nickname Clears [{len(failure)}]", color=0x000000, per_page=10),
                            ctx=ctx
                        )
                        await paginator.paginate()
                        await inter.response.defer()
                    
                    failure_button.callback = list_failure_callback
                    action_row.add_item(failure_button)
                
                result_container.add_item(action_row)
            
            result_view.add_item(result_container)
            await interaction.edit_original_response(view=result_view)

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm_callback
        no_button.callback = cancel_callback


    @global_command .command (name ="freezenick",help ="Freezes a user's nickname in all mutual guilds.")
    @commands .is_owner ()
    async def global_freezenick (self ,ctx :commands .Context ,user :discord .User ,*,name :str ):
        from discord import ui
        
        if len (name )>32 :
            return await ctx .send ("Nickname cannot exceed 32 characters. Please provide a shorter nickname.")

        if not hasattr (self .client ,"frozen_nicknames"):
            self .client .frozen_nicknames ={}

        mutual_guilds =[guild for guild in self .client .guilds if guild .get_member (user .id )]
        mutual_count =len (mutual_guilds )

        view = ui.LayoutView()
        container = ui.Container(accent_color=0x5865F2)
        
        container.add_item(ui.TextDisplay(f"# ⚠️ Global Nickname Freeze Confirmation"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            f"**Target User:** {user.display_name} ({user.mention})\n"
            f"**User ID:** `{user.id}`\n"
            f"**Mutual Guilds:** {mutual_count}\n"
            f"**Frozen Nickname:** {name}\n\n"
            f"**Requestor:** {ctx.author.mention}"
        ))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay("⚠️ **This action will freeze the user's nickname in all mutual guilds. The nickname will be automatically restored if changed. Are you sure?**"))
        
        yes_button = ui.Button(label="Confirm Freeze", style=discord.ButtonStyle.success)
        no_button = ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        
        action_row = ui.ActionRow()
        action_row.add_item(yes_button)
        action_row.add_item(no_button)
        container.add_item(action_row)
        
        view.add_item(container)
        
        msg = await ctx.send(view=view)

        async def confirm_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            
            processing_view = ui.LayoutView()
            processing_container = ui.Container(accent_color=0x5865F2)
            processing_container.add_item(ui.TextDisplay(f"# 🔄 Processing Global Nickname Freeze\n\nFreezing {user.display_name}'s nickname in {mutual_count} guilds..."))
            processing_view.add_item(processing_container)
            await interaction.response.edit_message(view=processing_view)
            
            self.client.frozen_nicknames[user.id] = {
                "name": name,
                "guild_ids": [guild.id for guild in mutual_guilds],
            }

            success, failure = [], []
            for guild in mutual_guilds:
                try:
                    member = guild.get_member(user.id)
                    if member:
                        await member.edit(nick=name)
                        success.append(guild.name)
                except:
                    failure.append(guild.name)
            
            result_view = ui.LayoutView()
            result_container = ui.Container(accent_color=0x57F287 if len(failure) == 0 else 0xFEE75C)
            
            result_container.add_item(ui.TextDisplay(f"# ✅ Global Nickname Freeze Active"))
            result_container.add_item(ui.Separator())
            result_container.add_item(ui.TextDisplay(
                f"**Target User:** {user.display_name}\n"
                f"**Frozen Nickname:** {name}\n"
                f"**Total Guilds:** {mutual_count}\n"
                f"**✅ Success:** {len(success)} guilds\n"
                f"**❌ Failed:** {len(failure)} guilds\n\n"
                f"*The nickname will be automatically restored if changed.*"
            ))
            
            success_button = ui.Button(label=f"View Successful ({len(success)})", style=discord.ButtonStyle.success)
            stop_button = ui.Button(label="Stop Freezing", style=discord.ButtonStyle.danger)
            
            async def list_success_callback(inter):
                if inter.user != ctx.author:
                    return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                entries = [f"{i+1}. {guild_name}" for i, guild_name in enumerate(success)]
                paginator = Paginator(
                    source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Successful Freezes [{len(success)}]", color=0x000000, per_page=10),
                    ctx=ctx
                )
                await paginator.paginate()
                await inter.response.defer()
            
            async def stop_freeze_callback(inter):
                if inter.user != ctx.author:
                    return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                self.client.frozen_nicknames.pop(user.id, None)
                await inter.response.send_message(f"Nickname freezing stopped for {user.name}.", ephemeral=True)
            
            success_button.callback = list_success_callback
            stop_button.callback = stop_freeze_callback
            
            action_row = ui.ActionRow()
            action_row.add_item(success_button)
            
            if failure:
                failure_button = ui.Button(label=f"View Failed ({len(failure)})", style=discord.ButtonStyle.secondary)
                
                async def list_failure_callback(inter):
                    if inter.user != ctx.author:
                        return await inter.response.send_message("This interaction is not for you.", ephemeral=True)
                    entries = [f"{i+1}. {guild_name}" for i, guild_name in enumerate(failure)]
                    paginator = Paginator(
                        source=DescriptionEmbedPaginator(entries=entries, description="", title=f"Failed Freezes [{len(failure)}]", color=0x000000, per_page=10),
                        ctx=ctx
                    )
                    await paginator.paginate()
                    await inter.response.defer()
                
                failure_button.callback = list_failure_callback
                action_row.add_item(failure_button)
            
            action_row.add_item(stop_button)
            result_container.add_item(action_row)
            
            result_view.add_item(result_container)
            await interaction.edit_original_response(view=result_view)
            self.client.loop.create_task(self.nickname_freeze_task(user.id))

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                return await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            await interaction.message.delete()

        yes_button.callback = confirm_callback
        no_button.callback = cancel_callback

    async def nickname_freeze_task (self ,user_id :int ):
        while user_id in self .client .frozen_nicknames :
            user_data =self .client .frozen_nicknames [user_id ]
            frozen_name =user_data ["name"]
            guild_ids =user_data ["guild_ids"]

            for guild_id in guild_ids :
                guild =self .client .get_guild (guild_id )
                if not guild :
                    continue 
                member =guild .get_member (user_id )
                if member and member .nick !=frozen_name :
                    try :
                        await member .edit (nick =frozen_name )
                    except :
                        pass 

            await asyncio .sleep (10 )



    @global_command .command (name ="unfreezenick",help ="Unfreezes a user's nickname in all mutual guilds.")
    @commands .is_owner ()
    async def global_unfreezenick (self ,ctx :commands .Context ,user :discord .User ):
        if not hasattr (self .client ,"frozen_nicknames"):
            self .client .frozen_nicknames ={}

        if user .id not in self .client .frozen_nicknames :
            return await ctx .send (f"<:icon_cross:1372375094336425986> | {user.name}'s nickname is not being frozen.")

        del self .client .frozen_nicknames [user .id ]
        await ctx .send (f"<:icon_tick:1372375089668161597> | Nickname freezing stopped for {user.name}.")


    @commands .command (name ="freezenick",help ="Freezes a member's nickname in the current server.")
    @commands .has_permissions (manage_nicknames =True )
    async def freeze_nickname (self ,ctx :commands .Context ,member :Member ,*,nickname :str ):
        guild_id =ctx .guild .id 
        if guild_id not in self .local_frozen_nicks :
            self .local_frozen_nicks [guild_id ]={}

        if member .id in self .local_frozen_nicks [guild_id ]:
            return await ctx .send (f"{member.mention}'s nickname is already being frozen.")


        try :
            await member .edit (nick =nickname )
            self .local_frozen_nicks [guild_id ][member .id ]=nickname 
            await ctx .send (f"Freezing {member.mention}'s nickname as '{nickname}'.")
        except :
            return await ctx .send (f"Could not change {member.mention}'s nickname due to insufficient permissions.")

        async def monitor_nickname ():
            while member .id in self .local_frozen_nicks .get (guild_id ,{}):
                if member .nick !=nickname :
                    try :
                        await member .edit (nick =nickname )
                    except :
                        self .local_frozen_nicks [guild_id ].pop (member .id ,None )
                        await ctx .send (f"Stopped monitoring {member.mention}'s nickname due to insufficient permissions.")
                        break 
                await asyncio .sleep (10 )

            if not self .local_frozen_nicks [guild_id ]:
                del self .local_frozen_nicks [guild_id ]

        self .client .loop .create_task (monitor_nickname ())

    @commands .command (name ="unfreezenick",help ="Unfreezes a member's nickname in the current server.")
    @commands .has_permissions (manage_nicknames =True )
    async def unfreeze_nickname (self ,ctx :commands .Context ,member :Member ):
        guild_id =ctx .guild .id 
        if guild_id in self .local_frozen_nicks and member .id in self .local_frozen_nicks [guild_id ]:
            self .local_frozen_nicks [guild_id ].pop (member .id ,None )
            if not self .local_frozen_nicks [guild_id ]:
                del self .local_frozen_nicks [guild_id ]
            await ctx .send (f"<:icon_tick:1372375089668161597> | Stopped freezing {member.mention}'s nickname.")
        else :
            await ctx .send (f"<:icon_cross:1372375094336425986> | {member.mention}'s nickname is not currently being frozen.")



"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
