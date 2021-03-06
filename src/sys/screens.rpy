python:
    """
    Custom screens:
        Custom volume select
        Custom warnings
        Custom credits
        Developer mode menu
        Mouse utilities
        Developer boxes, both main menu and ingame
        Variable watcher
    """


init offset = 0

init python:
    if persistent.developer is not None:
        config.developer = persistent.developer

    def ToggleDevModeMenu():
        message = "Developer mode is currently [[{}].\n\nEnabling developer mode will enable the console and reload the game.\nToggle developer mode?".format(
            "ON" if config.developer else "OFF")
        return ShowMenu(
            "confirm", message, 
            (Hide("confirm"), ToggleDevMode), 
            (Hide("confirm"))
        )()

    def ToggleDevMode():
        """Toggles developer mode and then reloads the game."""
        config.developer = not config.developer
        SetField(persistent, 'developer', config.developer)()
        _reload_game()

    store.mousex, store.mousey = 200, 200
    def getMousePosition():
        """Stores the current mouse position at store.mousex, store.mousey."""
        store.mousex, store.mousey = renpy.get_mouse_pos()

    # Add devbox
    config.overlay_screens.append("ingame_devbox_loader")

# Styles and other for menu, defined in overrides

style fse_volume_select_title:
    font "verdana.ttf" 
    size 48 
    xalign 0.5 
    color "#b4b4b5"

style fse_volume_select_subtitle:
    font "verdana.ttf" 
    size 38 
    xalign 0.5 
    color gui.accent_color

style fse_volume_select_author:
    font "verdana.ttf" 
    size 12 
    xalign 1.0 
    text_align 1.0 
    color "#b4b4b5" 

style mainmenu_devbox_frame:
    xalign 1.0
    yalign 1.0
    spacing -10

style mainmenu_devbox_button:
    xalign 1.0 

style mainmenu_devbox_button_text is confirm_prompt_text:
    idle_color gui.idle_color
    text_align 1.0

style mainmenu_devbox_text is mainmenu_devbox_button_text

screen mainmenu_devbox:
    key "trickster" action ToggleDevModeMenu
    key "game_menu" action Hide("mainmenu_devbox")
    key "hide_windows" action Hide("mainmenu_devbox")

    modal True
    add "gui/overlay/confirm.png"
    frame:
        anchor (0.0, 0.0)
        xpos mousex
        ypos mousey
        style_prefix "mainmenu_devbox"
        vbox:
            # background Solid("#0A0")
            textbutton "Music Player" action Hide("mainmenu_devbox"), ShowMenu("__p__music_room")
            textbutton "Displayables" action Hide("mainmenu_devbox"), ShowMenu("__p__panel_room")
            textbutton "Characters" action Hide("mainmenu_devbox"), ShowMenu("__p__sayer_room")
            # textbutton "Credits+" action Hide("mainmenu_devbox"), ShowMenu("dlc_credits")
            # textbutton "Warnings+" action Hide("mainmenu_devbox"), ShowMenu("dlc_warnings")
            null height 12
            textbutton "Clear achievements" action Hide("mainmenu_devbox"), ShowMenu(
                "confirm", "Are you sure you want to clear all your achievements?", 
                (Hide("confirm"), achievement.clear_all), 
                (Hide("confirm"))
            )
            if config.developer:
                textbutton "Reload (Shift+R)" action _reload_game
            textbutton "Developer Tools" action ToggleDevModeMenu

label __p__NewWatchAction:
    $ __p__expr = renpy.input(prompt="Expression to watch")
    $ renpy.watch(__p__expr)
    $ renpy.show_screen("_trace_screen")
    return 

screen ingame_devbox:

    # on "show" action getMousePosition

    key "trickster" action ToggleDevModeMenu
    key "game_menu" action Return()
    key "hide_windows" action Return()
    modal True
    add "gui/overlay/confirm.png"
    frame:
        anchor (0.0, 0.0)
        xpos mousex
        ypos mousey
        style_prefix "mainmenu_devbox"
        vbox:
            # background Solid("#0A0")
            textbutton "Watcher" action Call("__p__NewWatchAction"), Return()
            textbutton "Unwatch All" action (lambda: map(renpy.unwatch, _console.traced_expressions)), Return()
            null height 12
            textbutton "Reload (Ctrl+R)" action _reload_game
            textbutton "Developer Tools" action ToggleDevModeMenu
            

define fse_block_devbox = False
screen ingame_devbox_loader:
    if config.developer and not fse_block_devbox:
        key "trickster" action getMousePosition, ShowMenu('ingame_devbox')


# Extended choice screen allowing more choices if possible
# https://www.renpy.org/doc/html/screen_special.html#choice

screen choice_scrollable(items):
    ### A scrollable choice menu for very long selections.
    ### Invoke with
    ### >>> menu (screen="choice_scrollable"):
    ### >>>     "[pick] option":
    ### >>>     ...

    style_prefix "choice"
    viewport:
        xsize 820
        ysize 600
        xalign 0.5

        mousewheel True
        scrollbars ("vertical" if len(items) > 8 else None)

        side_yfill True

        style_prefix "choice"

        vbox:
            for i in items:
                textbutton i.caption action i.action


style __p__spoiler_button_show:
    background "#E5E5E5" 
    hover_background "#C7C9CB"

style __p__spoiler_text_show:
    color "#32363B"

style __p__spoiler_button_hide:
    background "#B9BBBE" 
    hover_background "#C7C9CB"

style __p__spoiler_text_hide:
    color "#B9BBBE"
    hover_color "#C7C9CB"

screen spoiler_box(label, content, warningoffset=42):
    default spoil_style_state_text = "__p__spoiler_text_hide"
    default spoil_style_state_button = "__p__spoiler_button_hide"
    hbox:
        text label + ": "
        textbutton content style spoil_style_state_button text_style spoil_style_state_text action [
            ToggleLocalVariable("spoil_style_state_button", "__p__spoiler_button_hide", "__p__spoiler_button_show"),
            ToggleLocalVariable("spoil_style_state_text", "__p__spoiler_text_hide", "__p__spoiler_text_show"),
        ]
            
define dlc_volumes_icons = {}
init python:
    def getDlcVolumeIcons(volume):
        key = (volume["package_id"], volume["volume_id"])
        cached = dlc_volumes_icons.get(key)
        if cached:
            return cached
        try:
            img_small = "custom_assets_{package_id}/volumeselect_{volume_id}_small.png".format(**jsonReEscape(volume))
            renpy.file(img_small)
        except:
            img_small = Composite(
                (103, 103),
                (0, 0), "{{assets}}/volumeselect_fallback_small.png",
                (0, 0), Text("assets/\nvolumeselect_\n{volume_id}_\nsmall.png".format(**jsonReEscape(volume)), xsize=103)
            )
        try:
            img_norm = "custom_assets_{package_id}/volumeselect_{volume_id}.png".format(**jsonReEscape(volume))
            renpy.file(img_norm)
        except:
            img_norm = Composite(
                (153, 149),
                (0, 0), "{{assets}}/volumeselect_fallback.png",
                (0, 0), Text("assets/\nvolumeselect_\n{volume_id}.png".format(**jsonReEscape(volume)), xsize=103)
            )
        tup = (img_small, img_norm,)
        dlc_volumes_icons[key] = tup
        return tup

define dlc_volumes_data = []
screen vol_select_custom():

    use game_menu_volumes(_("Friend Select")):

        default icon = "gui/volumeselect_icon_blank.png"
        default title = "Volume Select"

        default subtitle = "Hover over an icon!"
        default author = ""

        $ num_cols = 8

        $ volumes_by_author = sorted(dlc_volumes_data, key=lambda v: v["author"])
                    
        # fixed area contains overlapping elements
        fixed:
            xpos 10
            image "gui/volumeselect_background.png" xpos 30
            image icon xpos 50 ypos 15
            text title xpos 526 ypos 32 style "fse_volume_select_title"
            text subtitle xpos 526 ypos 90  style "fse_volume_select_subtitle"
            text author xpos 860 ypos 160 style "fse_volume_select_author"

        viewport:
            mousewheel True
            scrollbars ("vertical" if len(dlc_volumes_data) > (num_cols*3) else None)
            ypos 180
            ysize 350

            vbox:
                null height 20
                vpgrid:
                    xpos 10
                    cols num_cols
                    spacing 10

                    for volume in volumes_by_author:
                        $ img_small, img_norm = getDlcVolumeIcons(volume)
                        imagebutton idle img_small action Jump("custom_entry_{package_id}_{volume_id}".format(**jsonReEscape(volume))) hovered[
                            SetScreenVariable("icon", img_norm), 
                            SetScreenVariable("title", volume.get("title", "")), 
                            SetScreenVariable("subtitle", volume.get("subtitle", "")),
                            SetScreenVariable("author", volume.get("author", ""))
                        ] unhovered[        
                            SetScreenVariable("icon", "gui/volumeselect_icon_blank.png"), 
                            SetScreenVariable("title", "Volume Select"), 
                            SetScreenVariable("subtitle", "Hover over an icon!"),
                            SetScreenVariable("author", "")
                        ] alt volume.get("subtitle", "")
                # these buttons will jump to selected volume, and make the volume number/title appear in the fixed area

        text fse_vol_select_suffix xalign 0.5 text_align 0.5 ypos 540
        # text customVolumeSplash() 



define dlc_credits_data = {}  # Overwritten in custom_credits.rpy
define dlc_credits_sort = {
    "LIST": [],
    "DICT": []
}

screen dlc_credits():
    tag menu
    use game_menu(_("Credits"), scroll="viewport"):
        style_prefix "about"
        vbox:
            spacing 14

            # There's no goddamned reason "store" should be required here. I can't puzzle it. Screen side effects?
            # alienoid says: "Looks like you weren't quite prepared for what was in `store` huh"
            
            # We COULD do this processing in advance, but we want to make it
            # easy to manually override the dlc_credits_sort config variable
            $ store.dlc_credits_sort_temp = [s.lower() for s in dlc_credits_sort.get("LIST", [])] 
            $ sorted_credits_list = sorted(
                dlc_credits_data.get("LIST", {}).items(),
                key=(lambda (role, _): store.dlc_credits_sort_temp.index(role.lower()) if role.lower() in store.dlc_credits_sort_temp else 999)
            )

            $ store.dlc_credits_sort_temp = [s.lower() for s in dlc_credits_sort.get("DICT", [])] 
            $ sorted_credits_dict = sorted(
                dlc_credits_data.get("DICT", {}).items(),
                key=(lambda (role, _): store.dlc_credits_sort_temp.index(role.lower()) if role.lower() in store.dlc_credits_sort_temp else 999)
            )

            for role, list_ in sorted_credits_list:
                text role text_align 0.5 color gui.accent_color size 30
                for name in list_:
                    hbox:
                        text name text_align 0.0 min_width 440

            for role, person_credits in sorted_credits_dict:
                text role text_align 0.5 color gui.accent_color size 30
                for name, list_ in person_credits.items():
                    hbox:
                        text name text_align 0.0 min_width 440
                        vbox:
                            for item in list_:
                                text item text_align 0.0


            text "\n\n" text_align 1.0

            for text_ in dlc_credits_data.get("POSTSCRIPT", []):
                text text_


define dlc_warning_data = {}  # Overwritten in custom_warnings.rpy
screen dlc_warnings():
    tag menu
    use game_menu(_("Warnings"), scroll="viewport"):
        hbox:
            text fse_warnings_prefix

        for title, warning in dlc_warning_data.items():
            use spoiler_box(title, warning)


screen dlc_achievements():
    tag menu
    use game_menu(_("Achievements"), scroll="viewport"):
        style_prefix "about"
        vpgrid:
            cols 10
            xspacing 20
            yspacing 20

            for ach in dlc_achievements_data:
                if achievement.has(ach.get("_id")):
                    imagebutton idle ach.get("_img_unlocked") action NullAction() hovered Show("ach_desc", None, ach.get("name", "name"), ach.get("desc", "desc")) unhovered Hide("ach_desc")
                else:
                    imagebutton idle ach.get("_img_locked") action NullAction() hovered Show("ach_desc", None, ach.get("name", "name"), ach.get("hint", "hint")) unhovered Hide("ach_desc")

screen ach_desc(ach_name, ach_description):

    vbox:

        xpos 320 ypos 465

        text ach_name
        text ach_description
