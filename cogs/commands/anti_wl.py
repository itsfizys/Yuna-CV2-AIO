"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .ext import commands 
import aiosqlite 
from utils .Tools import *
from discord import ui


class WhitelistLayoutView(ui.LayoutView):
    def __init__(self, cog, ctx, member):
        super().__init__(timeout=300.0)
        self.cog = cog
        self.ctx = ctx
        self.member = member

        self.container = ui.Container(accent_color=None)

        options = [
            discord.SelectOption(label="Ban", description="Whitelist a member with ban permission", value="ban"),
            discord.SelectOption(label="Kick", description="Whitelist a member with kick permission", value="kick"),
            discord.SelectOption(label="Prune", description="Whitelist a member with prune permission", value="prune"),
            discord.SelectOption(label="Bot Add", description="Whitelist a member with bot add permission", value="botadd"),
            discord.SelectOption(label="Server Update", description="Whitelist a member with server update permission", value="serverup"),
            discord.SelectOption(label="Member Update", description="Whitelist a member with member update permission", value="memup"),
            discord.SelectOption(label="Channel Create", description="Whitelist a member with channel create permission", value="chcr"),
            discord.SelectOption(label="Channel Delete", description="Whitelist a member with channel delete permission", value="chdl"),
            discord.SelectOption(label="Channel Update", description="Whitelist a member with channel update permission", value="chup"),
            discord.SelectOption(label="Role Create", description="Whitelist a member with role create permission", value="rlcr"),
            discord.SelectOption(label="Role Update", description="Whitelist a member with role update permission", value="rlup"),
            discord.SelectOption(label="Role Delete", description="Whitelist a member with role delete permission", value="rldl"),
            discord.SelectOption(label="Mention Everyone", description="Whitelist a member with mention everyone permission", value="meneve"),
            discord.SelectOption(label="Manage Webhook", description="Whitelist a member with manage webhook permission", value="mngweb")
        ]

        self.container.add_item(ui.TextDisplay(f"# {ctx.guild.name}"))
        self.container.add_item(ui.Separator())

        permissions_text = (
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Ban**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Kick**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Prune**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Bot Add**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Server Update**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Member Update**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Channel Create**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Channel Delete**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417>: **Channel Update**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Role Create**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Role Delete**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Role Update**\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Mention** @everyone\n"
            f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **Webhook Management**"
        )

        if cog.bot.user.avatar:
            self.container.add_item(ui.Section(ui.TextDisplay(permissions_text), accessory=ui.Thumbnail(cog.bot.user.avatar.url)))
        else:
            self.container.add_item(ui.TextDisplay(permissions_text))

        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay(f"**Executor:** {ctx.author.mention}\n**Target:** {member.mention}"))
        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay("Developed by LightCore Development"))
        self.container.add_item(ui.Separator())

        select_row = ui.ActionRow(
            ui.Select(
                placeholder="Choose Your Options",
                min_values=1,
                max_values=len(options),
                options=options,
                custom_id="wl"
            )
        )
        select_row.children[0].callback = self.select_callback
        self.container.add_item(select_row)

        self.add_item(self.container)

    async def select_callback(self, interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("You cannot interact with this.", ephemeral=True)

        fields = {
            'ban': 'Ban',
            'kick': 'Kick',
            'prune': 'Prune',
            'botadd': 'Bot Add',
            'serverup': 'Server Update',
            'memup': 'Member Update',
            'chcr': 'Channel Create',
            'chdl': 'Channel Delete',
            'chup': 'Channel Update',
            'rlcr': 'Role Create',
            'rldl': 'Role Delete',
            'rlup': 'Role Update',
            'meneve': 'Mention Everyone',
            'mngweb': 'Manage Webhooks'
        }

        embed_description = "\n".join(f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **{name}**" for key, name in fields.items())

        values = interaction.data.get('values', [])

        db_conn = await self.cog.db.ensure_connection()
        
        async def update_db():
            for value in values:
                await db_conn.execute(
                    f"UPDATE whitelisted_users SET {value} = ? WHERE guild_id = ? AND user_id = ?",
                    (True, self.ctx.guild.id, self.member.id)
                )
            await db_conn.commit()

        await self.cog.db.execute_with_retries(update_db)

        for value in values:
            embed_description = embed_description.replace(f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **{fields[value]}**", f"<:disable_no:1372374999310274600><:enable_yes:1372375008441143417> : **{fields[value]}**")

        self.container.clear_items()

        self.container.add_item(ui.TextDisplay(f"# {self.ctx.guild.name}"))
        self.container.add_item(ui.Separator())

        if self.cog.bot.user.avatar:
            self.container.add_item(ui.Section(ui.TextDisplay(embed_description), accessory=ui.Thumbnail(self.cog.bot.user.avatar.url)))
        else:
            self.container.add_item(ui.TextDisplay(embed_description))

        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay(f"**Executor:** {self.ctx.author.mention}\n**Target:** {self.member.mention}"))
        self.container.add_item(ui.Separator())
        self.container.add_item(ui.TextDisplay("Developed by LightCore Development"))

        if not interaction.response.is_done():
            await interaction.response.edit_message(view=self)
        else:
            await interaction.edit_original_response(view=self)


class Whitelist (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self .bot .loop .create_task (self .initialize_db ())

    async def initialize_db (self ):
        from db._db import Database
        self .db = Database('db/anti.db')
        db_conn = await self .db .connect()

        async def create_table():
            await db_conn.execute('''
                CREATE TABLE IF NOT EXISTS whitelisted_users (
                    guild_id INTEGER,
                    user_id INTEGER,
                    ban BOOLEAN DEFAULT FALSE,
                    kick BOOLEAN DEFAULT FALSE,
                    prune BOOLEAN DEFAULT FALSE,
                    botadd BOOLEAN DEFAULT FALSE,
                    serverup BOOLEAN DEFAULT FALSE,
                    memup BOOLEAN DEFAULT FALSE,
                    chcr BOOLEAN DEFAULT FALSE,
                    chdl BOOLEAN DEFAULT FALSE,
                    chup BOOLEAN DEFAULT FALSE,
                    rlcr BOOLEAN DEFAULT FALSE,
                    rlup BOOLEAN DEFAULT FALSE,
                    rldl BOOLEAN DEFAULT FALSE,
                    meneve BOOLEAN DEFAULT FALSE,
                    mngweb BOOLEAN DEFAULT FALSE,
                    mngstemo BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            await db_conn.commit()

        await self.db.execute_with_retries(create_table)

    @commands .hybrid_command (name ='whitelist',aliases =['wl'],help ="Whitelists a user from antinuke for a specific action.")

    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )

    async def whitelist(self, ctx, member: discord.Member = None):
        if ctx.guild.member_count < 2:
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# Error"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("<:icon_cross:1372375094336425986> | Your Server Doesn't Meet My 30 Member Criteria"))
            view.add_item(container)
            return await ctx.send(view=view)

        prefix =ctx .prefix 

        db = await self.db.ensure_connection()

        async with db.execute(
        "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
        (ctx .guild .id ,ctx .author .id )
        )as cursor :
            check =await cursor .fetchone ()

        async with db.execute(
        "SELECT status FROM antinuke WHERE guild_id = ?",
        (ctx .guild .id ,)
        )as cursor :
            antinuke =await cursor .fetchone ()

        is_owner =ctx .author .id ==ctx .guild .owner_id 
        if not is_owner and not check :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# <:icon_cross:1372375094336425986> Access Denied"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("Only Server Owner or Extra Owner can Run this Command!"))
            view.add_item(container)
            return await ctx .send (view=view)

        if not antinuke or not antinuke [0 ]:
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay(f"# {ctx.guild.name} Security Settings <:icon_stagemoderator:1337295812102721577>"))
            container.add_item(ui.Separator())
            main_info = f"Ohh No! looks like your server doesn't enabled Antinuke\n\nCurrent Status : <:disable_no:1372374999310274600><:enable_yes:1372375008441143417>\n\nTo enable use `{prefix}antinuke enable`"
            if ctx.bot.user.avatar:
                container.add_item(ui.Section(ui.TextDisplay(main_info), accessory=ui.Thumbnail(ctx.bot.user.avatar.url)))
            else:
                container.add_item(ui.TextDisplay(main_info))
            view.add_item(container)
            return await ctx .send (view=view)

        if not member :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# Whitelist Commands"))
            container.add_item(ui.Separator())
            main_info = "**Adding a user to the whitelist means that no actions will be taken against them if they trigger the Anti-Nuke Module.**"
            if ctx.bot.user.avatar:
                container.add_item(ui.Section(ui.TextDisplay(main_info), accessory=ui.Thumbnail(ctx.bot.user.avatar.url)))
            else:
                container.add_item(ui.TextDisplay(main_info))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f"**Usage**\n<a:Arrowright:1376605813820489820> `{prefix}whitelist @user/id`\n<a:Arrowright:1376605813820489820> `{prefix}wl @user`"))
            view.add_item(container)
            return await ctx .send (view=view)

        async with db.execute (
        "SELECT * FROM whitelisted_users WHERE guild_id = ? AND user_id = ?",
        (ctx .guild .id ,member .id )
        )as cursor :
            data =await cursor .fetchone ()

        if data :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# Already Whitelisted"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f"{member.mention} is already a whitelisted member, **Unwhitelist** the user and try again."))
            view.add_item(container)
            return await ctx .send (view=view)

        async def insert_user():
            db_conn = await self.db.ensure_connection()
            await db_conn.execute(
                "INSERT INTO whitelisted_users (guild_id, user_id) VALUES (?, ?)",
                (ctx.guild.id, member.id)
            )
            await db_conn.commit()

        await self.db.execute_with_retries(insert_user)

        view = WhitelistLayoutView(self, ctx, member)
        msg = await ctx.send(view=view)


    @commands .hybrid_command (name ='whitelisted',aliases =['wlist'],help ="Shows the list of whitelisted users.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,5 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def whitelisted (self ,ctx ):
        if ctx .guild .member_count <2 :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# Error"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("<:icon_cross:1372375094336425986> | Your Server Doesn't Meet My 30 Member Criteria"))
            view.add_item(container)
            return await ctx .send (view=view)

        pre =ctx .prefix 

        db = await self.db.ensure_connection()

        async with db.execute(
        "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
        (ctx .guild .id ,ctx .author .id )
        )as cursor :
            check =await cursor .fetchone ()

        async with db.execute(
        "SELECT status FROM antinuke WHERE guild_id = ?",
        (ctx .guild .id ,)
        )as cursor :
            antinuke =await cursor .fetchone ()

        is_owner =ctx .author .id ==ctx .guild .owner_id 
        if not is_owner and not check :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# <:icon_cross:1372375094336425986> | Access Denied"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("Only Server Owner or Extra Owner can Run this Command!"))
            view.add_item(container)
            return await ctx .send (view=view)

        if not antinuke or not antinuke [0 ]:
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay(f"# {ctx.guild.name} security settings <:icon_stagemoderator:1337295812102721577>"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f"Ohh NO! looks like your server doesn't enabled security\n\nCurrent Status : <:disable_no:1372374999310274600><:enable_yes:1372375008441143417>\n\nTo enable use `{pre}antinuke enable`"))
            view.add_item(container)
            return await ctx .send (view=view)


        async with db.execute (
        "SELECT user_id FROM whitelisted_users WHERE guild_id = ?",
        (ctx .guild .id ,)
        )as cursor :
            data =await cursor .fetchall ()

        if not data :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# No Whitelisted Users"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("No whitelisted users found."))
            view.add_item(container)
            return await ctx .send (view=view)

        whitelisted_users =[self .bot .get_user (user_id [0 ])for user_id in data ]
        whitelisted_users_str =", ".join (f"{user.mention}"for user in whitelisted_users if user )

        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        container.add_item(ui.TextDisplay(f"# Whitelisted Users for {ctx.guild.name}"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(whitelisted_users_str))
        view.add_item(container)
        await ctx .send (view=view)


    @commands .hybrid_command (name ="whitelistreset",aliases =['wlreset'],help ="Resets the whitelisted users.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,10 ,commands .BucketType .user )
    @commands .max_concurrency (1 ,per =commands .BucketType .default ,wait =False )
    @commands .guild_only ()
    @commands .has_permissions (administrator =True )
    async def whitelistreset (self ,ctx ):
        if ctx .guild .member_count <2 :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# Error"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("<:icon_cross:1372375094336425986> | Your Server Doesn't Meet My 30 Member Criteria"))
            view.add_item(container)
            return await ctx .send (view=view)

        pre =ctx .prefix 

        db = await self.db.ensure_connection()

        async with db.execute(
        "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
        (ctx .guild .id ,ctx .author .id )
        )as cursor :
            check =await cursor .fetchone ()

        async with db.execute(
        "SELECT status FROM antinuke WHERE guild_id = ?",
        (ctx .guild .id ,)
        )as cursor :
            antinuke =await cursor .fetchone ()

        is_owner =ctx .author .id ==ctx .guild .owner_id 
        if not is_owner and not check :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# <:icon_cross:1372375094336425986> | Access Denied"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("Only Server Owner or Extra Owner can Run this Command!"))
            view.add_item(container)
            return await ctx .send (view=view)

        if not antinuke or not antinuke [0 ]:
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay(f"# {ctx.guild.name} Security Settings <:icon_stagemoderator:1337295812102721577>"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f"Ohh NO! looks like your server doesn't enabled security\n\nCurrent Status : <:disable_no:1372374999310274600><:enable_yes:1372375008441143417>\n\nTo enable use `{pre}antinuke enable`"))
            view.add_item(container)
            return await ctx .send (view=view)

        async with db.execute (
        "SELECT user_id FROM whitelisted_users WHERE guild_id = ?",
        (ctx .guild .id ,)
        )as cursor :
            data =await cursor .fetchall ()


        if not data :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# No Whitelisted Users"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay("No whitelisted users found."))
            view.add_item(container)
            return await ctx .send (view=view)

        async def delete_all():
            db_conn = await self.db.ensure_connection()
            await db_conn.execute("DELETE FROM whitelisted_users WHERE guild_id = ?", (ctx.guild.id,))
            await db_conn.commit()

        await self.db.execute_with_retries(delete_all)
        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        container.add_item(ui.TextDisplay("# <:icon_tick:1372375089668161597> | Success"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(f"Removed all whitelisted members from {ctx.guild.name}"))
        view.add_item(container)
        await ctx .send (view=view)


"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
