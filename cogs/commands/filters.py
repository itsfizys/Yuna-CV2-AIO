"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
from discord .ext import commands 
from typing import Union 
from utils .Tools import *

class FilterCog (commands .Cog ):
    def __init__ (self ,bot :commands .Bot ):
        self .bot =bot 
        self .active_filters ={}

    @commands .hybrid_group (invoke_without_command =True )
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    async def filter (self ,ctx :commands .Context ):
        await ctx .send ("Filters are currently disabled.")

    @filter .command (help ="Enable a filter.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    async def enable (self ,ctx :commands .Context ):
        await ctx .send ("Music filters are no longer supported as the music feature has been removed.")

    @filter .command (help ="Disable the current filter.")
    @blacklist_check ()
    @ignore_check ()
    @commands .cooldown (1 ,3 ,commands .BucketType .user )
    async def disable (self ,ctx :commands .Context ):
        await ctx .send ("Music filters are no longer supported.")

"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
