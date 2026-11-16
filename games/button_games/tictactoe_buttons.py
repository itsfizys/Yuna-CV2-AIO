"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
from __future__ import annotations 

from typing import ClassVar ,Optional 

import discord 
from discord .ext import commands 

from ..tictactoe import Tictactoe 
from ..utils import *


class TTTButton (discord .ui .Button ["TTTView"]):
    def __init__ (self ,label :str ,style :discord .ButtonStyle ,*,row :int ,col :int ):
        super ().__init__ (
        label =label ,
        style =style ,
        row =row ,
        )

        self .col =col 

    async def callback (self ,interaction :discord .Interaction )->None :
        user =interaction .user 
        game =self .view .game 

        if user not in (game .cross ,game .circle ):
            return await interaction .response .send_message (
            "You are not part of this game!",ephemeral =True 
            )

        if user !=game .turn :
            return await interaction .response .send_message (
            "it is not your turn!",ephemeral =True 
            )

        self .label =game .player_to_emoji [user ]
        self .disabled =True 

        game .board [self .row ][self .col ]=self .label 
        game .turn =game .circle if user ==game .cross else game .cross 

        tie =all (button .disabled for button in self .view .children [0 ].children [-1 ].children )

        if game_over :=game .is_game_over (tie =tie ):
            if game .winning_indexes :
                self .view .disable_button_grid ()
                game .create_streak ()
            self .view .stop ()

        self .view .update_display (game_over =game_over or tie )
        await interaction .response .edit_message (view =self .view )


class TTTView (discord .ui .LayoutView ):
    def __init__ (self ,game :BetaTictactoe ,*,timeout :float )->None :
        super ().__init__ (timeout =timeout )

        self .game =game 
        self .setup_view ()
    
    def setup_view (self ):
        self .clear_items ()
        container =self .game .make_view_content ()
        container .add_item (discord .ui .Separator ())
        
        for x ,row in enumerate (self .game .board ):
            action_row =discord .ui .ActionRow ()
            for y ,square in enumerate (row ):
                button =TTTButton (
                label =square ,
                style =self .game .button_style ,
                row =x ,
                col =y ,
                )
                action_row .add_item (button )
            container .add_item (action_row )
        
        self .add_item (container )
    
    def update_display (self ,game_over :bool =False ):
        container =self .children [0 ]
        container .children [0 ]=discord .ui .TextDisplay ("# ⭕ Tic-Tac-Toe")
        container .children [1 ]=discord .ui .Separator ()
        
        if game_over :
            status =f"{self.game.winner.mention} won!"if self .game .winner else "Tie"
            description =f"**Game over**\n{status}"
        else :
            description =f"**Turn:** {self.game.turn.mention}\n**Piece:** `{self.game.player_to_emoji[self.game.turn]}`"
        
        container .children [2 ]=discord .ui .TextDisplay (description )
    
    def disable_button_grid (self ):
        container =self .children [0 ]
        for item in container .children [4 :]:
            if isinstance (item ,discord .ui .ActionRow ):
                for button in item .children :
                    if isinstance (button ,discord .ui .Button ):
                        button .disabled =True


class BetaTictactoe (Tictactoe ):
    """
    Tictactoe(buttons) game
    """

    BLANK :ClassVar [str ]="\u200b"
    CIRCLE :ClassVar [str ]="O"
    CROSS :ClassVar [str ]="X"

    def create_streak (self )->None :
        container =self .view .children [0 ]
        button_rows =[]
        for item in container .children [4 :]:
            if isinstance (item ,discord .ui .ActionRow ):
                button_rows .append (item .children )
        
        for row ,col in self .winning_indexes :
            button :TTTButton =button_rows [row ][col ]
            button .style =self .win_button_style 

    async def start (
    self ,
    ctx :commands .Context [commands .Bot ],
    button_style :discord .ButtonStyle =discord .ButtonStyle .green ,
    *,
    embed_color :DiscordColor =DEFAULT_COLOR ,
    win_button_style :discord .ButtonStyle =discord .ButtonStyle .red ,
    timeout :Optional [float ]=None ,
    )->discord .Message :
        """
        starts the tictactoe(buttons) game

        Parameters
        ----------
        ctx : commands.Context
            the context of the invokation command
        button_style : discord.ButtonStyle, optional
            the primary button style to use, by default discord.ButtonStyle.green
        embed_color : DiscordColor, optional
            the color of the game embed, by default DEFAULT_COLOR
        win_button_style : discord.ButtonStyle, optional
            the button style to use to show the winning line, by default discord.ButtonStyle.red
        timeout : Optional[float], optional
            the timeout for the view, by default None

        Returns
        -------
        discord.Message
            returns the game message
        """
        self .embed_color =discord .Color .random ()
        self .button_style =button_style 
        self .win_button_style =win_button_style 

        self .view =TTTView (self ,timeout =timeout )
        self .message =await ctx .send (view =self .view )

        await double_wait (
        wait_for_delete (ctx ,self .message ,user =(self .cross ,self .circle )),
        self .view .wait (),
        )

        return self .message 

"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
