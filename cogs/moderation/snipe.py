"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .ext import commands 
from datetime import datetime ,timezone 
from utils .Tools import *



class Snipe (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .snipes ={}
        self .editsnipes ={}

    @commands .Cog .listener ()
    async def on_message_delete (self ,message ):
        if not message .guild or message .author .bot :
            return 
        if message .channel .id not in self .snipes :
            self .snipes [message .channel .id ]=[]
        if len (self .snipes [message .channel .id ])>=10 :
            self .snipes [message .channel .id ].pop (0 )

        attachments =[]
        if message .attachments :
            attachments =[{'name':attachment .filename ,'url':attachment .url }for attachment in message .attachments ]


        deleted_at =int (datetime .now (timezone .utc ).timestamp ())

        self .snipes [message .channel .id ].insert (0 ,{
        'author_name':message .author .name ,
        'author_display_name':message .author .display_name ,
        'author_avatar':message .author .avatar .url if message .author .avatar else None ,
        'author_id':message .author .id ,
        'content':message .content or None ,
        'deleted_at':deleted_at ,
        'attachments':attachments 
        })

    @commands .Cog .listener ()
    async def on_message_edit (self ,before ,after ):
        if not before .guild or before .author .bot :
            return 
        if before .content == after .content :
            return
        if before .channel .id not in self .editsnipes :
            self .editsnipes [before .channel .id ]=[]
        if len (self .editsnipes [before .channel .id ])>=10 :
            self .editsnipes [before .channel .id ].pop (0 )

        attachments_before =[]
        if before .attachments :
            attachments_before =[{'name':attachment .filename ,'url':attachment .url }for attachment in before .attachments ]

        attachments_after =[]
        if after .attachments :
            attachments_after =[{'name':attachment .filename ,'url':attachment .url }for attachment in after .attachments ]

        edited_at =int (datetime .now (timezone .utc ).timestamp ())

        self .editsnipes [before .channel .id ].insert (0 ,{
        'author_name':before .author .name ,
        'author_display_name':before .author .display_name ,
        'author_avatar':before .author .avatar .url if before .author .avatar else None ,
        'author_id':before .author .id ,
        'content_before':before .content or None ,
        'content_after':after .content or None ,
        'edited_at':edited_at ,
        'attachments_before':attachments_before ,
        'attachments_after':attachments_after 
        })

    @commands .hybrid_command (name ='snipe',help ="Shows the recently deleted messages in the channel.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    async def snipe (self ,ctx ):
        channel_snipes =self .snipes .get (ctx .channel .id ,[])
        if not channel_snipes :
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay("🔍 **Message Snipe**\n\nNo recently deleted messages found in this channel."),
                accent_color=None
            )
            error_view.add_item(error_container)
            await ctx.send(view=error_view)
            return 

        channel_snipes = channel_snipes[:5]
        
        view = SnipeView(channel_snipes, 0)
        await ctx.send(view=view)

    @commands .hybrid_command (name ='editsnipe',help ="Shows the recently edited messages in the channel.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    async def editsnipe (self ,ctx ):
        channel_editsnipes =self .editsnipes .get (ctx .channel .id ,[])
        if not channel_editsnipes :
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay("🔍 **Message Edit Snipe**\n\nNo recently edited messages found in this channel."),
                accent_color=None
            )
            error_view.add_item(error_container)
            await ctx.send(view=error_view)
            return 

        channel_editsnipes = channel_editsnipes[:5]
        
        view = EditSnipeView(channel_editsnipes, 0)
        await ctx.send(view=view)

class SnipeView(discord.ui.LayoutView):
    def __init__(self, snipes, current_page=0):
        super().__init__(timeout=300.0)
        self.snipes = snipes
        self.current_page = current_page
        self.total_pages = len(snipes)
        
        self.container = discord.ui.Container(accent_color=None)
        self.setup_content()
        self.add_item(self.container)
        
        self.setup_buttons()
    
    def setup_content(self):
        """Set up the content for current page"""
        self.container.clear_items()
        
        current_snipe = self.snipes[self.current_page]
        uid = current_snipe['author_id']
        display_name = current_snipe['author_name']
        deleted_at = current_snipe['deleted_at']
        
        self.container.add_item(discord.ui.TextDisplay(f"**Deleted Messages Retrieved**"))
        self.container.add_item(discord.ui.Separator())
        
        server_display_name = current_snipe.get('author_display_name', display_name)
        author_info = f"Author: [{server_display_name}](https://discord.com/users/{uid})"
        self.container.add_item(discord.ui.TextDisplay(author_info))
        
        sent_at = f"Sent at: <t:{deleted_at}:F>"
        self.container.add_item(discord.ui.TextDisplay(sent_at))
        
        content = current_snipe['content'] or 'No text content'
        self.container.add_item(discord.ui.TextDisplay(f"__**Message Content**__\n```{content}```"))
        
        if current_snipe['attachments']:
            attachment_links = "\n".join([f"[{attachment['name']}]({attachment['url']})" for attachment in current_snipe['attachments']])
            self.container.add_item(discord.ui.TextDisplay(f"**📎 Attachments:**\n{attachment_links}"))
        
        self.container.add_item(discord.ui.Separator())
    
    def setup_buttons(self):
        """Set up navigation buttons"""
        if self.total_pages <= 1:
            return
            
        action_row = discord.ui.ActionRow()
        
        left_button = discord.ui.Button(
            emoji="<:ArrowLeft:1421555578701877303>",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_page == 0)
        )
        left_button.callback = self.previous_page
        action_row.add_item(left_button)
        
        delete_button = discord.ui.Button(
            emoji="<:dustbin:1421555656518930485>",
            style=discord.ButtonStyle.danger
        )
        delete_button.callback = self.delete_message
        action_row.add_item(delete_button)
        
        right_button = discord.ui.Button(
            emoji="<:ArrowRight:1421555573522174004>",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_page == self.total_pages - 1)
        )
        right_button.callback = self.next_page
        action_row.add_item(right_button)
        
        self.container.add_item(action_row)
    
    async def previous_page(self, interaction: discord.Interaction):
        """Navigate to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.setup_content()
            self.setup_buttons()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.defer()
    
    async def next_page(self, interaction: discord.Interaction):
        """Navigate to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.setup_content()
            self.setup_buttons()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.defer()
    
    async def delete_message(self, interaction: discord.Interaction):
        """Delete the container/message"""
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        if interaction.message is None:
            return
            
        try:
            await interaction.message.delete()
        except discord.Forbidden:
            await interaction.followup.edit_message(interaction.message.id, content="Message deleted.", view=None)
        except discord.NotFound:
            pass
        finally:
            self.stop() 

class EditSnipeView(discord.ui.LayoutView):
    def __init__(self, editsnipes, current_page=0):
        super().__init__(timeout=300.0)
        self.editsnipes = editsnipes
        self.current_page = current_page
        self.total_pages = len(editsnipes)
        
        self.container = discord.ui.Container(accent_color=None)
        self.setup_content()
        self.add_item(self.container)
        
        self.setup_buttons()
    
    def setup_content(self):
        """Set up the content for current page"""
        self.container.clear_items()
        
        current_editsnipe = self.editsnipes[self.current_page]
        uid = current_editsnipe['author_id']
        display_name = current_editsnipe['author_name']
        edited_at = current_editsnipe['edited_at']
        
        self.container.add_item(discord.ui.TextDisplay(f"**Edited Messages Retrieved**"))
        self.container.add_item(discord.ui.Separator())
        
        server_display_name = current_editsnipe.get('author_display_name', display_name)
        author_info = f"Author: [{server_display_name}](https://discord.com/users/{uid})"
        self.container.add_item(discord.ui.TextDisplay(author_info))
        
        edited_time = f"Edited at: <t:{edited_at}:F>"
        self.container.add_item(discord.ui.TextDisplay(edited_time))
        
        content_before = current_editsnipe['content_before'] or 'No text content'
        self.container.add_item(discord.ui.TextDisplay(f"__**Message Content**__\n```{content_before}```"))
        
        if current_editsnipe['attachments_before']:
            attachment_links = "\n".join([f"[{attachment['name']}]({attachment['url']})" for attachment in current_editsnipe['attachments_before']])
            self.container.add_item(discord.ui.TextDisplay(f"**📎 Attachments:**\n{attachment_links}"))
        
        self.container.add_item(discord.ui.Separator())
    
    def setup_buttons(self):
        """Set up navigation buttons"""
        if self.total_pages <= 1:
            return
            
        action_row = discord.ui.ActionRow()
        
        left_button = discord.ui.Button(
            emoji="<:ArrowLeft:1421555578701877303>",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_page == 0)
        )
        left_button.callback = self.previous_page
        action_row.add_item(left_button)
        
        delete_button = discord.ui.Button(
            emoji="<:dustbin:1421555656518930485>",
            style=discord.ButtonStyle.danger
        )
        delete_button.callback = self.delete_message
        action_row.add_item(delete_button)
        
        right_button = discord.ui.Button(
            emoji="<:ArrowRight:1421555573522174004>",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_page == self.total_pages - 1)
        )
        right_button.callback = self.next_page
        action_row.add_item(right_button)
        
        self.container.add_item(action_row)
    
    async def previous_page(self, interaction: discord.Interaction):
        """Navigate to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.setup_content()
            self.setup_buttons()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.defer()
    
    async def next_page(self, interaction: discord.Interaction):
        """Navigate to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.setup_content()
            self.setup_buttons()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.defer()
    
    async def delete_message(self, interaction: discord.Interaction):
        """Delete the container/message"""
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        if interaction.message is None:
            return
            
        try:
            await interaction.message.delete()
        except discord.Forbidden:
            await interaction.followup.edit_message(interaction.message.id, content="Message deleted.", view=None)
        except discord.NotFound:
            pass
        finally:
            self.stop() 


"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
