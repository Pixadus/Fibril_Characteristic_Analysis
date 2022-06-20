#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sat 6.18.22
@title: Fibril Tracing
@author: Parker Lamb
@description: Helper program used to perform a variety of functions related
to fibril analysis. 
@usage: "python main.py"
"""

import urwid

# Setup
def quit(key):
    if key in ["q", "Q"]:
        raise urwid.ExitMainLoop()

def intro_text():
    fa_text = urwid.BigText("Fibril Analysis", urwid.font.HalfBlock5x4Font())
    fa_text = urwid.Padding(fa_text, width='clip')
    fa_text = urwid.Filler(fa_text,"top",None,3)
    return(fa_text)

def outro_text():
    qa_text = urwid.Text("? for help, q to exit")
    qa_text = urwid.Filler(qa_text,"bottom")
    return(qa_text)

# --- START MENU ---
# Menu choices

canvas_setup = {
    'Manually trace fibrils': [
        urwid.Text(["Manually trace fibrils", u'\n']),
        ],
    'Automatically trace fibrils': [
        urwid.Text(["Automatically trace fibrils", u'\n']),
        ],
    'Characterize fibril set': [
        urwid.Text(["Characterize fibril set", u'\n']),
        ],
    'Generate histograms': [
        urwid.Text(["Generate histograms", u'\n']),
        ],
    'Helper functions': [
        urwid.Text(["Helper functions", u'\n']),
        ]
}

# Menu instance
def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices:
        button = urwid.Button(c)
        urwid.connect_signal(button, 'click', item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

# Function called when an item is selected
def item_chosen(button, choice):
    # selector.original_widget is going to be our "canvas" now
    selector.original_widget = urwid.Filler(
        urwid.Pile(canvas_setup[choice])
        )

# --- END MENU ---

if __name__ == "__main__":
    intro = intro_text()
    div = urwid.Filler(urwid.Divider())
    selector = urwid.Padding(menu(u'Select One', canvas_setup.keys()))
    outro = outro_text()
    pile = urwid.Pile([
        intro,
        selector,
        outro
        ])

    urwid.MainLoop(pile, unhandled_input=quit).run()