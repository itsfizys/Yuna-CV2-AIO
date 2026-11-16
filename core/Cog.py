"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
from __future__ import annotations 

from discord .ext import commands 

__all__ =("Cog",)


class Cog (commands .Cog ):

    def __init__ (self ,*args ,**kwargs )->None :
        super ().__init__ (*args ,**kwargs )

    def __str__ (self )->str :
        return "{0.__class__.__name__}".format (self )
"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
