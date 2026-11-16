"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
from __future__ import annotations 

from typing import Optional 
import random 

import discord 
from discord .ext import commands 

from ..rps import RockPaperScissors 
from ..utils import DiscordColor ,DEFAULT_COLOR ,BaseView 


class RPSButton (discord .ui .Button ["RPSView"]):
    def __init__ (self ,emoji :str ,*,style :discord .ButtonStyle )->None :
        super ().__init__ (
        label ="\u200b",
        emoji =emoji ,
        style =style ,
        )

    def get_choice (self ,user :discord .User ,other :bool =False )->Optional [str ]:
        game =self .view .game 
        if other :
            return game .player2_choice if user ==game .player2 else game .player1_choice 
        else :
            return game .player1_choice if user ==game .player1 else game .player2_choice 

    async def callback (self ,interaction :discord .Interaction )->None :
        game =self .view .game 
        players =(game .player1 ,game .player2 )if game .player2 else (game .player1 ,)

        if interaction .user not in players :
            return await interaction .response .send_message (
            "This is not your game!",ephemeral =True 
            )
        else :
            if not game .player2 :
                bot_choice =random .choice (game .OPTIONS )
                user_choice =str (self .emoji) 

                if user_choice ==bot_choice :
                    description =f"**Tie!**\nWe both picked {user_choice}"
                else :
                    if game .check_win (bot_choice ,user_choice ):
                        description =f"**You Won!**\nYou picked {user_choice} and I picked {bot_choice}."
                    else :
                        description =f"**You Lost!**\nI picked {bot_choice} and you picked {user_choice}."

                self .view .disable_buttons ()
                self .view .stop ()
                self .view .update_result (description )

            else :
                if self .get_choice (interaction .user ):
                    return await interaction .response .send_message (
                    "You have already chosen!",ephemeral =True 
                    )

                other_player_choice =self .get_choice (interaction .user ,other =True )

                if interaction .user ==game .player1 :
                    game .player1_choice =str (self .emoji) 

                    if not other_player_choice :
                        description =f"Select a button to play!\n\n{game.player1.mention} has chosen...\n*Waiting for {game.player2.mention} to choose...*"
                        self .view .update_result (description )
                else :
                    game .player2_choice =str (self .emoji) 

                    if not other_player_choice :
                        description =f"Select a button to play!\n\n{game.player2.mention} has chosen...\n*Waiting for {game.player1.mention} to choose...*"
                        self .view .update_result (description )

                if game .player1_choice and game .player2_choice :
                    if game .player1_choice ==game .player2_choice :
                        description =f"**Tie!**\nBoth {game.player1.mention} and {game.player2.mention} picked {game.player1_choice}."
                    else :
                        who_won =(
                        game .player1 
                        if game .check_win (game .player2_choice ,game .player1_choice )
                        else game .player2 
                        )

                        description =(
                        f"**{who_won.mention} Won!**"
                        f"\n\n{game.player1.mention} chose {game.player1_choice}."
                        f"\n{game.player2.mention} chose {game.player2_choice}."
                        )

                    self .view .disable_buttons ()
                    self .view .stop ()
                    self .view .update_result (description )

            return await interaction .response .edit_message (view =self .view )


class RPSView (discord .ui .LayoutView ):
    game :BetaRockPaperScissors 

    def __init__ (
    self ,
    game :BetaRockPaperScissors ,
    *,
    button_style :discord .ButtonStyle ,
    timeout :float ,
    )->None :

        super ().__init__ (timeout =timeout )

        self .button_style =button_style 
        self .game =game 
        self .setup_view ()
    
    def setup_view (self ):
        self .clear_items ()
        container =discord .ui .Container (accent_color =None )
        
        container .add_item (discord .ui .TextDisplay ("# 🪨 Rock Paper Scissors"))
        container .add_item (discord .ui .Separator ())
        container .add_item (discord .ui .TextDisplay ("Select a button to play!"))
        container .add_item (discord .ui .Separator ())
        
        action_row =discord .ui .ActionRow ()
        for option in self .game .OPTIONS :
            action_row .add_item (RPSButton (option ,style =self .button_style ))
        container .add_item (action_row )
        
        self .add_item (container )
    
    def update_result (self ,description :str ):
        container =self .children [0 ]
        container .children [2 ]=discord .ui .TextDisplay (description )
    
    def disable_buttons (self ):
        container =self .children [0 ]
        action_row =container .children [4 ]
        for button in action_row .children :
            button .disabled =True


class BetaRockPaperScissors (RockPaperScissors ):
    """
    RockPaperScissors(buttons) game
    """

    player1 :discord .User 

    def __init__ (self ,other_player :Optional [discord .User ]=None )->None :
        self .player2 =other_player 

        if self .player2 :
            self .player1_choice :Optional [str ]=None 
            self .player2_choice :Optional [str ]=None 

    async def start (
    self ,
    ctx :commands .Context [commands .Bot ],
    *,
    button_style :discord .ButtonStyle =discord .ButtonStyle .blurple ,
    embed_color :DiscordColor =DEFAULT_COLOR ,
    timeout :Optional [float ]=None ,
    )->discord .Message :
        if ctx .author ==self .player2 :
            view =discord .ui .LayoutView ()
            container =discord .ui .Container (accent_color =None )
            container .add_item (discord .ui .TextDisplay ("<:LightCore_notify:1227866804630720565> **Access Denied**\nYou cannot play against yourself!"))
            view .add_item (container )
            return await ctx .reply (view =view )

        """
        Starts the Rock Paper Scissors (buttons) game.

        Parameters
        ----------
        ctx : commands.Context
            The context of the invoking command.
        button_style : discord.ButtonStyle, optional
            The primary button style to use, by default discord.ButtonStyle.blurple.
        embed_color : DiscordColor, optional
            The color of the game embed, by default DEFAULT_COLOR.
        timeout : Optional[float], optional
            The timeout for the view, by default None.

        Returns
        -------
        discord.Message
            Returns the game message.
        """
        self .player1 =ctx .author 

        self .view =RPSView (self ,button_style =button_style ,timeout =timeout if timeout else 180 )
        self .message =await ctx .send (view =self .view )

        await self .view .wait ()
        return self .message 

"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
