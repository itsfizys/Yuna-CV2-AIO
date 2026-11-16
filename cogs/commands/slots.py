"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .ext import commands 
import random 
from utils .Tools import *


class Slots (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 
        self.symbols = [
            "🍒",  # Cherry
            "🍋",  # Lemon
            "🍊",  # Orange
            "🍇",  # Grapes
            "🔔",  # Bell
            "💎"   # Diamond (jackpot)
        ]

    @commands .command (aliases =['slot'])
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    async def slots (self ,ctx :commands .Context ):
        try :
            result1 = random.choice(self.symbols)
            result2 = random.choice(self.symbols)
            result3 = random.choice(self.symbols)
            
            if result1 == result2 == result3:
                if result1 == "💎":
                    result = "JACKPOT! 💎💎💎"
                    result_emoji = "🎰"
                    color = "won"
                else:
                    result = "YOU WIN!"
                    result_emoji = "🎉"
                    color = "won"
            elif result1 == result2 or result2 == result3 or result1 == result3:
                result = "Small Win!"
                result_emoji = "✨"
                color = "partial"
            else:
                result = "Try Again!"
                result_emoji = "😔"
                color = "lost"

            view = discord.ui.LayoutView()
            container = discord.ui.Container(accent_color=None)
            
            container.add_item(discord.ui.TextDisplay(f"# 🎰 Slot Machine"))
            container.add_item(discord.ui.Separator())
            
            slot_display = f"**║ {result1} ║ {result2} ║ {result3} ║**"
            container.add_item(discord.ui.TextDisplay(slot_display))
            
            container.add_item(discord.ui.Separator())
            
            if color == "won":
                result_text = f"{result_emoji} **{result}**\n{ctx.author.mention} You won the slots!"
            elif color == "partial":
                result_text = f"{result_emoji} **{result}**\n{ctx.author.mention} Two symbols matched!"
            else:
                result_text = f"{result_emoji} **{result}**\n{ctx.author.mention} Better luck next time!"
            
            container.add_item(discord.ui.TextDisplay(result_text))
            
            view.add_item(container)
            await ctx.reply(view=view, mention_author=False)
            
        except Exception as e :
            print (f"Slots error: {e}")



"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
