﻿# this script is copypasted from the first Friendsim so if I left anything weird in here OOPS. MY B
# tip for anyone scoping the files this is what all game dev is like

# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

init -2 python:
    
    import re
    import os
    import os.path

    #Achievements

    # Persistent variable tracking if the user wants to see flashing images or not.

    if persistent.flash is None:

        persistent.flash = True

    if persistent.firstscreen is None:

        persistent.firstscreen = True
        

    # Used for open/close eyes animation

    def eyewarp(x):

        return x**1.33

    def eyewarpaxe(x):

        return 1.0 - (1.0 - x)**0.15

    # Used for sprite overlay colors e.x. zap effect

    def silhouette_matrix (r,g,b,a=1.0):
        return im.matrix((0, 0, 0, 0, r,
                          0, 0, 0, 0, g,
                          0, 0, 0, 0, b,
                          0, 0, 0, a, 0,))
    def silhouette (filename, r,g,b, a = 1.0):
        return im.MatrixColor (Image (filename), silhouette_matrix (r,g,b,a))

define narrator = Character(window_background="gui/textbox_narration.png", what_font='courbd.ttf', what_size=22,  color='#000000', what_color='#000000', what_ypos=26)#, window_ypos= #window_ypos=741)
define op = Character(window_background="gui/textbox_blank.png", what_font='courbd.ttf', what_size=28,  color='#FFFFFF', what_color='#FFFFFF', what_xalign=0.5, what_text_align=0.5)
define fscreen = Character(window_background="gui/textbox_blank.png", what_font='courbd.ttf', what_size=28, color='#FFFFFF', what_color='#FFFFFF', what_xalign=0.5, what_text_align=0.5, what_ypos=-360, what_xsize=1080)



# Game start

label help:

    call screen help

    return

label start:

    $ achievement.sync()

    # This is used to easily add a formatted '>' to the start of choices in menus.
    $ pick = "{color=#000000}>{/color}"

    $ quick_menu = False

    jump start2

label start2:

    # Stop main menu music, or any other music playing, and transition to volume select.
    stop music fadeout 1.5

    show image "gui/main_menu.png"

    window hide

    scene black with Dissolve(1.5)

    $ main_menu = True

    call screen vol_select() with Dissolve(1.0)

    return


label ending(card="blackcover", win=True, fadetoblack=True):

    if fadetoblack:

        scene black with Dissolve (0.5)

    $ renpy.pause(0.5)

    $ quick_menu = False

    if win:

        play music "music/victory_jingle.mp3" fadeout 1.0 noloop

    else:

        play music "music/game_over.mp3" fadeout 1.0 noloop

    scene expression card with Dissolve(1.0)

    $ renpy.pause()

    stop music fadeout 1.0

    scene black with Dissolve(1.0)

    return
