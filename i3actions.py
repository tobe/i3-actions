#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__version__ = '1.4'

import sys
import subprocess
from subprocess import Popen, PIPE
from collections import OrderedDict
from os.path import expanduser
import re

try:
    import i3ipc
except ImportError:
    print('i3actions cannot work without i3ipc. Exiting...')
    exit()

class i3actions(object):

    def __init__(self):
        self.dmenu_args   = ['/usr/bin/dmenu'] + ['-b', '-i'] # Refer to docs about this one. Make it more appealing here.
        self.layout_items = OrderedDict([
                                ('default', 'default'),
                                ('tabbed', 'tabbed'), 
                                ('stacking', 'stacking'),
                                ('splitv', 'split vertically'), 
                                ('splith', 'split horizontally')
                            ])
        self.menu_items   = OrderedDict([
                                ('ch_layout', 'change layout'),
                                ('first_free', 'first free workspace'),
                                ('jump_to', 'jump to...'),
                                ('kill', 'kill'),
                                ('marks_add', 'mark: add'),
                                ('marks_jump', 'mark: jump to'),
                                ('marks_remove', 'mark: remove'),
                                ('move_here', 'move to here'),
                                ('rename', 'rename workspace'),
                                ('restore', 'restore workspaces')
                            ])
        self.main_output  = 'CRT2'

        # Handle the input argument
        if(len(sys.argv)) < 2:
            print('Usage: %s ACTION' % sys.argv[0])
            sys.exit(1)

        # Register the socket
        try:
            self.connection = i3ipc.Connection()
        except Exception as e:
            print(e.message)

        # Handle the corresponding function
        try:
            action = getattr(self, sys.argv[1])
        except AttributeError:
            print('action %s: not found.' % sys.argv[1])
            sys.exit(1)
        else:
            action()

        sys.exit(0) # Maybe you can chain this with some unix tools?

    def _dmenu(self, data, lines, prompt = None):
        """Internal function that calls dmenu, pipes a list of arguments to it, catches the response and then returns it.
        This is used throughout the project in order to efficiently call dmenu.
        The data passed is UTF-8 encoded and decoded+stripped from any newlines when returned.

        Arguments:
            data (dict):  a dictionary containing the data to be piped to dmenu. Values will be displayed to the user and the corresponding *key* will be returned
                          This is so you can pass window IDs and show the window names to the user. In such example, an ID would be returned.
            lines (int):  number of lines the data dictionary has.
            prompt (str): dmenu -p parameter. It just shows a prompt so you know what you're actually doing.
        Returns:
            id (mixed): The key of the dictionary supplied.
        """
        ddata = bytes(str.join('\n', list(data.values())), 'UTF-8') # Join all the newline and UTF-8 encode it.

        try:
            if prompt: self.dmenu_args = self.dmenu_args + ['-p', prompt]
            p = Popen(self.dmenu_args + ['-l', str(lines)], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except ValueError as e:
            print('Popen construct failed: %s' % e.message)
            sys.exit(1)
        except OSError as e:
            print('OSError: %s' % e.message)
            sys.exit(1)

        stdout, stderr = p.communicate(ddata)
        if stderr: print('stderr: %s' % stderr)

        # Decode and strip newline from dmenu's return
        stdout = stdout.decode('UTF-8').strip()

        # We need to get the key by the value the user chooses. Remember the key is the ID, the value is the actual name.
        for id, name in data.items():
            if(name == stdout): # They match
                return id # Return the ID to the parent (caller) function

    def _dmenu_null(self, prompt):
        """See self._dmenu (above). Doesn't accept any data as it does not pipe anything to dmenu (just used to display a prompt instead of i3-input)

        Arguments:
            prompt (str): dmenu -p parameter. It just shows a prompt so you know what you're actually doing.
        Returns:
            mixed: user input
        """
        try:
            p = Popen(self.dmenu_args + ['-l', '1', '-p', prompt], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except OSError as e:
            print('OSError: %s' % e.message)
            sys.exit(1)

        new_name, stderr = p.communicate('') # Pipe nothing, dirty but we have to do this in order for dmenu to show.
        return new_name.decode('UTF-8').strip() # And just return what user entered. Simple as that.

    def _get_window_names(self):
        """Internal function. Returns the names of all windows in every workspace.

        Returns:
            windows (dict): a dictionary containing window IDs and names (id => name)
        """
        outputs = self.connection.get_tree().leaves()

        windows = {}
        for w in outputs:
            if(w.name in windows): continue # This makes sure there are no duplicates. Refer to docs about this one.
            windows[w.id] = w.name

        return windows

    def jump_to(self):
        """Jumps to any window on any workspace."""
        windows = self._get_window_names()

        # Send the command, receive the output. This will return the ID of the window, of course.
        cmd = self._dmenu(windows, len(windows), 'jump to:')

        # Just execute...
        self.connection.command('[con_id="%d"] focus' % cmd)

    def move_here(self):
        """Moves any window to the currently focused workspace."""
        # Get all the windows
        windows = self._get_window_names()

        # Find the name of the focused workspace!
        outputs = self.connection.get_workspaces()
        for ws in outputs:
            if ws.focused: focused = ws.name

        # Find the target window user wants to move...
        target_window = self._dmenu(windows, len(windows), 'move here:')

        # Issue the command
        self.connection.command('[con_id="%s"] move container to workspace %s' % (target_window, focused))

    def ch_layout(self):
        """Displays a list of choosable layouts."""
        req_layout = self._dmenu(self.layout_items, len(self.layout_items), 'layout:')
        self.connection.command('layout %s' % req_layout)

    def first_free(self):
        """Jumps to the first free workspace."""
        workspaces = []
        i = 1
        for ws in self.connection.get_workspaces():
            if(i == ws.num and ws.output == self.main_output):
                i = i+1
                continue
            else:
                break

        self.connection.command('workspace number %d' % i)

    def kill(self):
        """Kills any window the user chooses on any workspace (WM_DELETE)"""
        # Grab the window names
        windows = self._get_window_names()

        # Show dmenu
        victim = self._dmenu(windows, len(windows), 'kill:')

        # Execute the command
        self.connection.command('[con_id="%s"] kill' % victim)

    def marks_jump(self, remove = False):
        """Jumps to any user-set marks."""
        # Retrieve a list of marks.
        marked = self.connection.get_tree().leaves()

        marks = {}
        for l in marked:
            if l.mark != None: marks[l.mark] = '%s' % l.mark

        if len(marks) == 0:
            marks[0] = '(there are no marks)'

        # Now that we have a dictionary of marks, show it to the user.
        chosen_mark = self._dmenu(marks, len(marks), 'goto mark:')

        # Remove the mark (unmark)!
        if remove:
            self.connection.command('unmark %s' % chosen_mark)
        else: # Focus the mark!
            self.connection.command('[con_mark="%s"] focus' % chosen_mark)

    def marks_remove(self):
        """Removes the chosen user-set mark."""
        self.marks_jump(1)

    def marks_add(self):
        """Adds a mark (of the currently focused window)."""
        # Let's ask the user for a mark name
        mark = self._dmenu_null('mark as:')

        # And now we set the mark?
        if mark and mark != 'None': self.connection.command('mark %s' % mark)

    def rename(self):
        """Renames the currently focused workspace."""
        # Get all the workspaces
        workspaces = self.connection.get_workspaces()

        # Find the current workspace ID, not the name
        for ws in workspaces:
            if ws.focused: ws_current = ws.num

        # Prompt the user for a new name
        new_name = self._dmenu_null('rename to:')

        # If the user entered a name then rename
        if new_name:
            self.connection.command('rename workspace to %d:%s' % (ws_current, new_name))

    def show_menu(self):
        """Shows the customizable menu containing i3actions' actions."""
        # Just send the list to the dmenu command and that's about it.
        action = self._dmenu(self.menu_items, len(self.menu_items), 'action:')

        if action == None: return

        # Now let's see whether it exists or not!
        try:
            action = getattr(self, action)
        except AttributeError:
            print('action %s: not found.' % action)
        else:
            action() # Call it.

    def restore(self):
        """Restores all workspace names to the ones defined in the config file (default)"""
        # Get homedir
        home = expanduser('~')

        # Try to grab the config file
        try:
            fp = open(home + '/.i3/config', 'r')
        except IOError as e:
            print('Failed to open the config: %s' % e.message)
            sys.exit(1)

        # Read the file
        data = fp.read()
        if not data: return

        # Compile my poor regex. The reason why (.*) is there is that it can really be anything. Even japanese for "one" -> "一"
        regex = re.compile("^workspace (.*) output [a-zA-Z0-9-_]*", re.IGNORECASE|re.MULTILINE|re.UNICODE)

        workspaces = regex.findall(data)
        if not workspaces: return

        # Get all current workspaces.
        workspaces_now = self.connection.get_workspaces()

        # Now count from the first workspace to the nth workspace.
        i = 0
        for ws in workspaces:
            # Execute the command for each workspace.
            self.connection.command('rename workspace %s to %s' % (workspaces_now[i]['name'], ws))
            i = i+1

if __name__ == '__main__':
    i3actions()
