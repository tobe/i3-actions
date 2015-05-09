#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.4'

import sys
import subprocess
from subprocess import Popen, PIPE

try:
    import i3ipc
except ImportError:
    print('i3-modp cannot work without i3ipc. Exiting...')
    exit()

class i3actions(object):

    def __init__(self):
        self.dmenu_args = ['/usr/bin/dmenu'] + ['-b', '-i'] # Refer to docs about this one. Make it more appealing here.

        # Handle the input argument
        if len(sys.argv) < 2:
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

    def dmenu(self, data, lines):
        data = bytes(str.join('\n', data), 'UTF-8') # Join all the newline and UTF-8 encode it.
        try:
            p = Popen(self.dmenu_args + ['-l', str(lines)], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except ValueError as e:
            print('Popen construct failed: %s' % e.message)
            sys.exit(1)
        except OSError as e:
            print('OSError: %s' % e.message)

        stdout, stderr = p.communicate(data)
        if(stderr): print('stderr: %s' % stderr) # Could be useful for debugging?

        return stdout

    def get_window_names(self):
        outputs = self.connection.get_tree().leaves()

        windows = []
        for w in outputs:
            windows.append(w.name)

        return windows

    def jump_to(self):
        windows = self.get_window_names()

        # Send the command, receive it and decode it.
        cmd = self.dmenu(windows, len(windows)).decode('UTF-8').strip()

        # Just execute...
        self.connection.command('[title="%s"] focus' % cmd)

    def move_here(self):
        # Get all the windows
        windows = self.get_window_names()

        # Find the name of the focused workspace!
        outputs = self.connection.get_workspaces()
        focused = None
        for ws in outputs:
            if ws.focused: focused = ws.name

        # Find the target window user wants to move...
        target_window = self.dmenu(windows, len(windows)).decode('UTF-8').strip()

        # Issue the command
        self.connection.command('[title="%s"] move container to workspace %s' % (target_window, focused))

    def ch_layout(self):
        req_layout = self.dmenu(['default', 'tabbed', 'stacking', 'splitv', 'splith'], 5).decode('UTF-8').strip()

        self.connection.command('layout %s' % req_layout)

    def first_free(self):
        workspaces = []
        i = 1
        for ws in self.connection.get_workspaces():
            if i == ws.num:
                i = i+1
                continue
            else:
                break

        self.connection.command('workspace number %d' % i)

if __name__ == '__main__':
    i3actions()
