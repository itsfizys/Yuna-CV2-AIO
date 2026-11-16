"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
from __future__ import annotations 

from typing import Optional 
import discord 
from discord .ext import commands 

from ..chess_game import Chess 
from .wordle_buttons import WordInputButton 
from ..utils import DiscordColor ,DEFAULT_COLOR ,BaseView 


class ChessInput (discord .ui .Modal ,title ="Make your move"):
    def __init__ (self ,view :ChessView )->None :
        super ().__init__ ()
        self .view =view 

        self .move_from =discord .ui .TextInput (
        label ="from coordinate",
        style =discord .TextStyle .short ,
        required =True ,
        min_length =2 ,
        max_length =2 ,
        )

        self .move_to =discord .ui .TextInput (
        label ="to coordinate",
        style =discord .TextStyle .short ,
        required =True ,
        min_length =2 ,
        max_length =2 ,
        )

        self .add_item (self .move_from )
        self .add_item (self .move_to )

    async def on_submit (self ,interaction :discord .Interaction )->discord .Message :
        game =self .view .game 
        from_coord =self .move_from .value .strip ().lower ()
        to_coord =self .move_to .value .strip ().lower ()

        uci =from_coord +to_coord 

        try :
            is_valid_uci =game .board .parse_uci (uci )
        except ValueError :
            is_valid_uci =False 

        if not is_valid_uci :
            return await interaction .response .send_message (
            f"Invalid coordinates for move: `{from_coord} -> {to_coord}`",
            ephemeral =True ,
            )
        else :
            await game .place_move (uci )

            if game .board .is_game_over ():
                result_view =await game .fetch_results ()
                return await interaction .response .edit_message (view =result_view )
            else :
                self .view .setup_view ()
                return await interaction .response .edit_message (view =self .view )


class ChessButton (WordInputButton ):
    view :ChessView 

    async def callback (self ,interaction :discord .Interaction )->None :
        game =self .view .game 
        if interaction .user not in (game .black ,game .white ):
            return await interaction .response .send_message (
            "You are not part of this game!",ephemeral =True 
            )
        else :
            if self .label =="Cancel":
                self .view .disable_all ()
                await interaction .message .edit (view =self .view )
                await interaction .response .send_message (f"**Game Over!** Cancelled")
                return self .view .stop ()
            else :
                if interaction .user !=game .turn :
                    return await interaction .response .send_message (
                    "It is not your turn yet!",ephemeral =True 
                    )
                else :
                    return await interaction .response .send_modal (ChessInput (self .view ))


class ChessView (discord .ui .LayoutView ):
    def __init__ (self ,game :BetaChess ,*,timeout :float )->None :
        super ().__init__ (timeout =timeout )

        self .game =game 
        self .setup_view ()
    
    def setup_view (self ):
        self .clear_items ()
        container =discord .ui .Container (accent_color =None )
        
        container .add_item (discord .ui .TextDisplay ("# ♟️ Chess Game"))
        container .add_item (discord .ui .Separator ())
        
        game_info =f"**Turn:** `{self.game.turn}`\n**Color:** `{self.game.get_color()}`\n**Check:** `{self.game.board.is_check()}`"
        container .add_item (discord .ui .TextDisplay (game_info ))
        
        container .add_item (discord .ui .Separator ())
        
        last_move_text =f"**Last Move:**\n```yml\n{self.game.last_move.get('color', '-')}: {self.game.last_move.get('move', '-')}\n```"
        container .add_item (discord .ui .TextDisplay (last_move_text ))
        
        media =discord .ui .MediaGallery ()
        media .add_item (media =f"{self.game.BASE_URL}{self.game.board.board_fen()}")
        container .add_item (media )
        
        container .add_item (discord .ui .Separator ())
        
        action_row =discord .ui .ActionRow ()
        inpbutton =ChessButton ()
        inpbutton .label ="Make your move!"
        action_row .add_item (inpbutton )
        action_row .add_item (ChessButton (cancel_button =True ))
        container .add_item (action_row )
        
        self .add_item (container )


class BetaChess (Chess ):
    """
    Chess(buttons) Game
    """

    async def start (
    self ,
    ctx :commands .Context [commands .Bot ],
    *,
    embed_color :DiscordColor =DEFAULT_COLOR ,
    timeout :Optional [float ]=None ,
    )->discord .Message :
        """
        starts the Chess(buttons) Game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        timeout : Optional[float], optional
            the timeout for the view, by default None

        Returns
        -------
        discord.Message
            returns the game message
        """
        self .embed_color =discord .Color .random ()

        self .view =ChessView (self ,timeout =timeout )
        self .message =await ctx .send (view =self .view )

        await self .view .wait ()
        return self .message 

"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
