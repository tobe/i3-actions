#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.4'
__verbose__ = True

import sys
import subprocess
from subprocess import Popen, PIPE

try:
    import i3ipc
except ImportError:
    print('i3-actions cannot work without i3ipc. Exiting...')
    exit()

class i3actions(object):

    def __init__(self):
        self.dmenu_args = ['/usr/bin/dmenu'] + ['-b', '-i'] # Refer to docs about this one. Make it more appealing here.
        self.main_output = 'CRT2'

        # Handle the input argument
        if(len(sys.argv)) < 2:
            print('Usage: %s ACTION\n\nWhere ACTION is either one of these: jump_to, move_here' % sys.argv[0])
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
        ddata = bytes(str.join('\n', list(data.values())), 'UTF-8') # Join all the newline and UTF-8 encode it.

        try:
            if(prompt): self.dmenu_args = self.dmenu_args + ['-p', prompt]
            p = Popen(self.dmenu_args + ['-l', str(lines)], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except ValueError as e:
            print('Popen construct failed: %s' % e.message)
            sys.exit(1)
        except OSError as e:
            print('OSError: %s' % e.message)
            sys.exit(1)

        stdout, stderr = p.communicate(ddata)
        if(stderr): print('stderr: %s' % stderr) # Could be useful for debugging?

        # Decode and strip newline from dmenu's return
        stdout = stdout.decode('UTF-8').strip()

        # We need to get the key by the value the user chooses. Remember the key is the ID, the value is the actual name.
        for id, name in data.items():
            if(name == stdout): # They match
                return id # Return the ID to the parent (caller) function

    def _get_window_names(self):
        outputs = self.connection.get_tree().leaves()

        windows = {}
        for w in outputs:
            if(w.name in windows): continue # This makes sure there are no duplicates. Refer to docs about this one.
            windows[w.id] = w.name

        return windows

    def jump_to(self):
        windows = self._get_window_names()

        # Send the command, receive the output. This will return the ID of the window, of course.
        cmd = self._dmenu(windows, len(windows))
        if(__verbose__): print(cmd)

        # Just execute...
        self.connection.command('[con_id="%d"] focus' % cmd)

    def move_here(self):
        # Get all the windows
        windows = self._get_window_names()

        # Find the name of the focused workspace!
        outputs = self.connection.get_workspaces()
        focused = None
        for ws in outputs:
            if(ws.focused): focused = ws.name

        # Find the target window user wants to move...
        target_window = self._dmenu(windows, len(windows)).decode('UTF-8').strip()

        # Issue the command
        self.connection.command('[title="%s"] move container to workspace %s' % (target_window, focused))

    def ch_layout(self):
        req_layout = self._dmenu(['default', 'tabbed', 'stacking', 'splitv', 'splith'], 5).decode('UTF-8').strip()

        self.connection.command('layout %s' % req_layout)

    def first_free(self):
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
        pass

    def rename(self):
        # Get all the workspaces
        workspaces = self.connection.get_workspaces()

        # Find the current workspace ID, not the name
        for ws in workspaces:
            if(ws.focused): ws_current = ws.num

        # Prompt the user for a new name
        #self._dmenu(0, )
        pass

if __name__ == '__main__':
    i3actions()
