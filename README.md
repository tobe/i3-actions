## what is i3-actions?

i3-actions is a python3 utility for i3-wm which *mostly* makes *window managment* simpler and faster by 
integrating with **dmenu**.

It features:
- jumping to windows
- moving windows to the current workspace
- changing the layout of the current workspace
- jumping to the first **free** workspace
- killing applications
- renaming workspaces on fly

Keep in mind some of these have yet to be fully implemented.

## what are the requirements/dependencies?
* Python3 (tested with ```Python 3.4.3```)
* ```i3-wm``` and ```dmenu```, obviously.
* [i3ipc](https://github.com/acrisci/i3ipc-python) installed

## installation and setup
There is no ```setup.py``` at the moment, however you can install it by downloading and running 
```i3-actions.py```. I will add the setup information once it's barely useful. At the moment it's a dirty 
playground since I'm learning about i3ipc as I'm coding this.

**However**, if you'd like to give it a try, this should work:
```bash
cd /tmp; wget -O i3-actions.py https://raw.githubusercontent.com/infyhr/i3-actions/master/i3-actions.py && python3 ./i3-actions.py jump_to
```

If you get a dmenu instance containing the names of windows you've got open, congratulations, it works out of the 
box. Now select one, hit return and you should move to that window.

It will not work if you've got dmenu installed in a location other than ```/usr/bin```, but no worries, you can 
change this.

## configuration
TBA

## license
MIT
