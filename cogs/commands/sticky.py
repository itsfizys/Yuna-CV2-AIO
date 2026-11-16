"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord
import aiosqlite
import json
from discord import ui
from discord.ext import commands
from utils.Tools import *


class StickySetupView(ui.LayoutView):
    def __init__(self, ctx, sticky_cog):
        super().__init__(timeout=300.0)
        self.ctx = ctx
        self.sticky_cog = sticky_cog
        self.container = ui.Container(accent_color=None)
        
        self.setup_content()
        self.add_item(self.container)

    def setup_content(self):
        self.container.clear_items()
        
        self.container.add_item(ui.TextDisplay("# Sticky Setup"))
        self.container.add_item(ui.Separator())
        
        self.container.add_item(
            ui.TextDisplay(
                "Choose the type of sticky message you want to create:\n\n"
                "**Container:** Create a sticky message with title, content, and optional thumbnail.\n"
                "**Text:** Create a simple text-based sticky message."
            )
        )
        
        self.container.add_item(ui.Separator())
        
        button_row = ui.ActionRow(
            ui.Button(
                label="Container",
                style=discord.ButtonStyle.primary,
                custom_id="container_button"
            ),
            ui.Button(
                label="Text",
                style=discord.ButtonStyle.secondary,
                custom_id="text_button"
            )
        )
        button_row.children[0].callback = self.container_button_callback
        button_row.children[1].callback = self.text_button_callback
        self.container.add_item(button_row)

    async def container_button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You cannot interact with this menu.", ephemeral=True)
            return
        
        modal = ContainerModal(self.ctx, self.sticky_cog)
        await interaction.response.send_modal(modal)

    async def text_button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You cannot interact with this menu.", ephemeral=True)
            return
        
        modal = TextModal(self.ctx, self.sticky_cog)
        await interaction.response.send_modal(modal)

    async def on_timeout(self):
        try:
            self.container.clear_items()
            self.container.add_item(ui.TextDisplay("# Setup Timeout"))
            self.container.add_item(ui.Separator())
            self.container.add_item(ui.TextDisplay("Setup session expired after 5 minutes of no interaction."))
        except:
            pass


class ContainerModal(ui.Modal, title="Container Sticky Setup"):
    def __init__(self, ctx, sticky_cog):
        super().__init__()
        self.ctx = ctx
        self.sticky_cog = sticky_cog
        
        self.title_input = ui.TextInput(
            label="Title",
            placeholder="Enter the title for your sticky message",
            required=True,
            max_length=100
        )
        self.add_item(self.title_input)
        
        self.content_input = ui.TextInput(
            label="Content",
            placeholder="Enter the main content",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )
        self.add_item(self.content_input)
        
        self.thumbnail_input = ui.TextInput(
            label="Thumbnail Link (Optional)",
            placeholder="Enter image URL for thumbnail (optional)",
            required=False,
            max_length=500
        )
        self.add_item(self.thumbnail_input)

    async def on_submit(self, interaction: discord.Interaction):
        embed_data = {
            "title": self.title_input.value,
            "content": self.content_input.value
        }
        
        if self.thumbnail_input.value:
            embed_data["thumbnail"] = self.thumbnail_input.value
        
        async with aiosqlite.connect("db/stickymessages.db") as db:
            await db.execute(
                """INSERT OR REPLACE INTO sticky_messages 
                (guild_id, channel_id, message_type, embed_data, enabled)
                VALUES (?, ?, ?, ?, 1)""",
                (self.ctx.guild.id, self.ctx.channel.id, 'container', json.dumps(embed_data))
            )
            await db.commit()
        
        success_container = ui.Container(accent_color=None)
        success_container.add_item(ui.TextDisplay("# ✅ Sticky Setup Complete"))
        success_container.add_item(ui.Separator())
        
        success_text = (
            f"**Title:** {self.title_input.value}\n"
            f"**Content:** {self.content_input.value[:150]}{'...' if len(self.content_input.value) > 150 else ''}\n"
        )
        if self.thumbnail_input.value:
            success_text += f"**Thumbnail:** {self.thumbnail_input.value}\n"
        success_text += f"\nSticky message has been set up in {self.ctx.channel.mention}"
        
        success_container.add_item(ui.TextDisplay(success_text))
        
        success_view = ui.LayoutView()
        success_view.add_item(success_container)
        
        await interaction.response.edit_message(view=success_view)


class TextModal(ui.Modal, title="Text Sticky Setup"):
    def __init__(self, ctx, sticky_cog):
        super().__init__()
        self.ctx = ctx
        self.sticky_cog = sticky_cog
        
        self.content_input = ui.TextInput(
            label="Content",
            placeholder="Enter your sticky message content",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )
        self.add_item(self.content_input)

    async def on_submit(self, interaction: discord.Interaction):
        async with aiosqlite.connect("db/stickymessages.db") as db:
            await db.execute(
                """INSERT OR REPLACE INTO sticky_messages 
                (guild_id, channel_id, message_type, message_content, enabled)
                VALUES (?, ?, ?, ?, 1)""",
                (self.ctx.guild.id, self.ctx.channel.id, 'text', self.content_input.value)
            )
            await db.commit()
        
        success_container = ui.Container(accent_color=None)
        success_container.add_item(ui.TextDisplay("# ✅ Sticky Setup Complete"))
        success_container.add_item(ui.Separator())
        success_container.add_item(
            ui.TextDisplay(
                f"**Content:** {self.content_input.value[:200]}{'...' if len(self.content_input.value) > 200 else ''}\n\n"
                f"Sticky message has been set up in {self.ctx.channel.mention}"
            )
        )
        
        success_view = ui.LayoutView()
        success_view.add_item(success_container)
        
        await interaction.response.edit_message(view=success_view)


class StickyListView(ui.LayoutView):
    def __init__(self, ctx, sticky_messages):
        super().__init__(timeout=300.0)
        self.ctx = ctx
        self.sticky_messages = sticky_messages
        self.container = ui.Container(accent_color=None)
        
        self.setup_content()
        self.add_item(self.container)

    def setup_content(self):
        self.container.clear_items()
        
        self.container.add_item(ui.TextDisplay("# Sticky Messages List"))
        self.container.add_item(ui.Separator())
        
        if not self.sticky_messages:
            self.container.add_item(ui.TextDisplay("No sticky messages found in this server."))
        else:
            for idx, sticky in enumerate(self.sticky_messages, 1):
                channel = self.ctx.guild.get_channel(sticky['channel_id'])
                channel_mention = channel.mention if channel else f"Unknown Channel ({sticky['channel_id']})"
                status = "🟢 Enabled" if sticky['enabled'] else "🔴 Disabled"
                
                sticky_info = (
                    f"**{idx}. {channel_mention}**\n"
                    f"Type: `{sticky['message_type']}`\n"
                    f"Status: {status}\n"
                )
                
                if sticky['message_type'] == 'text':
                    content_preview = sticky['message_content'][:50] + "..." if sticky['message_content'] and len(sticky['message_content']) > 50 else sticky['message_content']
                    sticky_info += f"Preview: {content_preview}\n"
                elif sticky['message_type'] == 'container' and sticky['embed_data']:
                    try:
                        data = json.loads(sticky['embed_data'])
                        sticky_info += f"Title: {data.get('title', 'N/A')}\n"
                    except:
                        pass
                
                self.container.add_item(ui.TextDisplay(sticky_info))
                if idx < len(self.sticky_messages):
                    self.container.add_item(ui.Separator())


class StickyConfigView(ui.LayoutView):
    def __init__(self, ctx, sticky_data):
        super().__init__(timeout=300.0)
        self.ctx = ctx
        self.sticky_data = sticky_data
        self.container = ui.Container(accent_color=None)
        
        self.setup_content()
        self.add_item(self.container)

    def setup_content(self):
        self.container.clear_items()
        
        self.container.add_item(ui.TextDisplay("# Sticky Message Configuration"))
        self.container.add_item(ui.Separator())
        
        if not self.sticky_data:
            self.container.add_item(ui.TextDisplay("No sticky message found in this channel."))
        else:
            status = "🟢 Enabled" if self.sticky_data['enabled'] else "🔴 Disabled"
            
            config_text = (
                f"**Channel:** {self.ctx.channel.mention}\n"
                f"**Type:** `{self.sticky_data['message_type']}`\n"
                f"**Status:** {status}\n"
                f"**Delay:** {self.sticky_data['delay_seconds']} seconds\n"
                f"**Trigger Count:** {self.sticky_data['trigger_count']} messages\n"
                f"**Ignore Bots:** {'Yes' if self.sticky_data['ignore_bots'] else 'No'}\n"
                f"**Ignore Commands:** {'Yes' if self.sticky_data['ignore_commands'] else 'No'}\n"
                f"**Auto Delete:** {self.sticky_data['auto_delete_after']} seconds (0 = disabled)\n"
            )
            
            self.container.add_item(ui.TextDisplay(config_text))
            
            if self.sticky_data['message_type'] == 'text' and self.sticky_data['message_content']:
                self.container.add_item(ui.Separator())
                self.container.add_item(ui.TextDisplay(f"**Content:**\n{self.sticky_data['message_content']}"))
            elif self.sticky_data['message_type'] == 'container' and self.sticky_data['embed_data']:
                try:
                    data = json.loads(self.sticky_data['embed_data'])
                    self.container.add_item(ui.Separator())
                    content_text = (
                        f"**Title:** {data.get('title', 'N/A')}\n"
                        f"**Content:** {data.get('content', 'N/A')}"
                    )
                    if data.get('thumbnail'):
                        content_text += f"\n**Thumbnail:** {data.get('thumbnail')}"
                    self.container.add_item(ui.TextDisplay(content_text))
                except:
                    pass


class Sticky(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.setup_database())

    async def setup_database(self):
        async with aiosqlite.connect("db/stickymessages.db") as db:
            await db.execute(
                """CREATE TABLE IF NOT EXISTS sticky_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message_type TEXT,
                    message_content TEXT,
                    embed_data TEXT,
                    enabled INTEGER DEFAULT 1,
                    last_message_id INTEGER,
                    delay_seconds INTEGER DEFAULT 0,
                    trigger_count INTEGER DEFAULT 0,
                    ignore_bots INTEGER DEFAULT 1,
                    ignore_commands INTEGER DEFAULT 1,
                    auto_delete_after INTEGER DEFAULT 0
                )"""
            )
            await db.commit()

    @commands.group(name="sticky", invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    @blacklist_check()
    @ignore_check()
    async def sticky(self, ctx):
        await ctx.send_help(ctx.command)

    @sticky.command(name="setup")
    @commands.has_permissions(manage_channels=True)
    async def sticky_setup(self, ctx):
        view = StickySetupView(ctx, self)
        await ctx.reply(view=view)

    @sticky.command(name="remove")
    @commands.has_permissions(manage_channels=True)
    async def sticky_remove(self, ctx):
        async with aiosqlite.connect("db/stickymessages.db") as db:
            cursor = await db.execute(
                "SELECT last_message_id FROM sticky_messages WHERE guild_id = ? AND channel_id = ?",
                (ctx.guild.id, ctx.channel.id)
            )
            sticky = await cursor.fetchone()
            
            if not sticky:
                return
            
            last_message_id = sticky[0]
            
            if last_message_id:
                try:
                    old_message = await ctx.channel.fetch_message(last_message_id)
                    await old_message.delete()
                except:
                    pass
            
            await db.execute(
                "DELETE FROM sticky_messages WHERE guild_id = ? AND channel_id = ?",
                (ctx.guild.id, ctx.channel.id)
            )
            await db.commit()
        
        await ctx.message.add_reaction("✅")

    @sticky.command(name="list")
    @commands.has_permissions(manage_channels=True)
    async def sticky_list(self, ctx):
        async with aiosqlite.connect("db/stickymessages.db") as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM sticky_messages WHERE guild_id = ?",
                (ctx.guild.id,)
            )
            rows = await cursor.fetchall()
            sticky_messages = [dict(row) for row in rows]
        
        view = StickyListView(ctx, sticky_messages)
        await ctx.reply(view=view)

    @sticky.command(name="toggle")
    @commands.has_permissions(manage_channels=True)
    async def sticky_toggle(self, ctx):
        async with aiosqlite.connect("db/stickymessages.db") as db:
            cursor = await db.execute(
                "SELECT enabled FROM sticky_messages WHERE guild_id = ? AND channel_id = ?",
                (ctx.guild.id, ctx.channel.id)
            )
            row = await cursor.fetchone()
            
            if not row:
                error_container = ui.Container(accent_color=None)
                error_container.add_item(ui.TextDisplay("# ❌ No Sticky Found"))
                error_container.add_item(ui.Separator())
                error_container.add_item(ui.TextDisplay("There is no sticky message set up in this channel."))
                
                error_view = ui.LayoutView()
                error_view.add_item(error_container)
                
                await ctx.reply(view=error_view)
                return
            
            current_state = row[0]
            new_state = 0 if current_state else 1
            
            await db.execute(
                "UPDATE sticky_messages SET enabled = ? WHERE guild_id = ? AND channel_id = ?",
                (new_state, ctx.guild.id, ctx.channel.id)
            )
            await db.commit()
        
        status = "enabled" if new_state else "disabled"
        emoji = "🟢" if new_state else "🔴"
        
        success_container = ui.Container(accent_color=None)
        success_container.add_item(ui.TextDisplay(f"# {emoji} Sticky {status.title()}"))
        success_container.add_item(ui.Separator())
        success_container.add_item(ui.TextDisplay(f"Sticky message has been {status} in {ctx.channel.mention}"))
        
        success_view = ui.LayoutView()
        success_view.add_item(success_container)
        
        await ctx.reply(view=success_view)

    @sticky.command(name="edit")
    @commands.has_permissions(manage_channels=True)
    async def sticky_edit(self, ctx):
        async with aiosqlite.connect("db/stickymessages.db") as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM sticky_messages WHERE guild_id = ? AND channel_id = ?",
                (ctx.guild.id, ctx.channel.id)
            )
            row = await cursor.fetchone()
            
            if not row:
                error_container = ui.Container(accent_color=None)
                error_container.add_item(ui.TextDisplay("# ❌ No Sticky Found"))
                error_container.add_item(ui.Separator())
                error_container.add_item(ui.TextDisplay("There is no sticky message set up in this channel to edit."))
                
                error_view = ui.LayoutView()
                error_view.add_item(error_container)
                
                await ctx.reply(view=error_view)
                return
            
            sticky_data = dict(row)
        
        view = StickySetupView(ctx, self)
        
        info_container = ui.Container(accent_color=None)
        info_container.add_item(ui.TextDisplay("# ✏️ Edit Sticky Message"))
        info_container.add_item(ui.Separator())
        info_container.add_item(
            ui.TextDisplay(
                "Click a button below to edit your sticky message.\n"
                "The new content will replace the existing one."
            )
        )
        
        info_view = ui.LayoutView()
        info_view.add_item(info_container)
        
        await ctx.reply(view=view)

    @sticky.command(name="config")
    @commands.has_permissions(manage_channels=True)
    async def sticky_config(self, ctx):
        async with aiosqlite.connect("db/stickymessages.db") as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM sticky_messages WHERE guild_id = ? AND channel_id = ?",
                (ctx.guild.id, ctx.channel.id)
            )
            row = await cursor.fetchone()
            sticky_data = dict(row) if row else None
        
        view = StickyConfigView(ctx, sticky_data)
        await ctx.reply(view=view)


async def setup(bot):
    await bot.add_cog(Sticky(bot))
