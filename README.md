## what is i3-actions?

i3-actions is a python3 utility for i3-wm which *mostly* makes *window managment* simpler and 
faster by 
integrating with **dmenu**.

It features:
- jumping to windows
- moving windows to the current workspace
- changing the layout of the current workspace
- jumping to the first **free** workspace
- killing applications
- renaming workspaces on fly
- working with marks (adding, removing, jumping to)
- ~~scratchpad support? someday maybe...~~

## requirements/dependencies?
In order to use i3-actions, you will need the following:
* Python 3 (tested with ```Python 3.4.3```)
* ```i3-wm``` and ```dmenu```, obviously.
* [i3ipc](https://github.com/acrisci/i3ipc-python) installed

## installation
Before you can install the project, some things need to be set up in ```i3actions.py``` file.  
Once you are done with tweaking, just run ``./setup.py install``.

### launching dmenu
Adjust ```self.dmenu_args``` in order to point the script to the correct location of dmenu 
(first list)

You can do this by issuing ```type dmenu``` within a terminal.  
If you'd like to make it more appealing, you can change the second list by providing more 
dmenu arguments.

**Example**:  
Let ```dmenu``` be at ```/usr/bin/dmenu```. Let it appear on bottom with the normal background 
color of #000, normal foreground color of #ff0000 and the select background color of #000:
```python
self.dmenu_args = ['/usr/bin/dmenu'] + ['-b', '-i', '-nb', '#000', '-nf', '#ff0000', '-sb', '#000']
```
(Note: ``-i`` stands for case-insensitive matching)

### layout items
Edit ``self.layout_items`` in order to choose which of the entries appear when you execute the ``ch_layout`` action.  
Sometimes when you use this action you don't want them all to appear, or perhaps you'd like to have your own labels.  
This is an ordered list.

Same goes for ``self.menu_items``.  
This comes into play when you execute the action ``show_menu``. 

### main monitor output
When you use the action ``first_free``, i3actions will jump to the first free workspace on the 
output ``self.main_output``.  
This is important if you have more than one monitor and you don't want to focus the first free 
workspace on your secondary monitor(s).

## using it
In order to execute a certain action, all you need to do is call ``i3actions.py ACTION`` where 
``ACTION`` is the name of the action (or, a function if you look at the source code).  
Of course, the point is not to call it from a terminal, but to have some actions bound to your 
keyboard.  
We do this by editing ``~/.i3/config`` and adding something like:

```bash
bindsym $mod+p exec i3actions.py jump_to
```
This will execute the ``jump_to`` action every time ``$mod+p`` is pressed.  
I personally use this as a ``ctrlp`` motion.

If you run out of keys, or don't want to assign a key for every action, you can always assign 
one for the menu. I use it like so:

```bash
bindsym $mod+m exec i3actions.py show_menu
```

### list of actions

| Action name        | Description |
| ------------- |:-------------:|
| jump_to      | Jumps to the first free workspace |
| move_here    | Moves the selected window to the current workspace |
| ch_layout | Shows a menu with possible layouts (defined by the user) |
| first_free| Jumps to the first free workspace on the ``self.main_output`` output|
| kill | Kills any window the user chooses on any workspace (WM_DELETE) |
| marks_jump| Jumps to any user-set marks|
| marks_remove| Removes the chosen user-set mark|
| marks_add| Adds a mark (of the currently focused window)|
| rename | Renames the currently focused workspace on-fly|
| show_menu | Shows the customizable menu containing i3actions' actions|
| restore | Restores all workspace names to the ones defined in the config file (default)|

### notes
#### ch_layout
You can manipulate the menu by changing ``self.layout_items``
#### show_menu
You can manipulate the menu by changing ``self.menu_items``
#### restore
This function will restore ALL the workspace names by reading the configuration file once 
called. This function reads ``~/.i3/config`` only.
 
In order for this not to mess up your workspaces, your i3 configuration file should have the 
following workspace notation:

```bash
workspace <Name within ""> output <Your output/monitor whatever>
```
or if the workspace has only a number (no name):

```bash
workspace <Number> output <Your output/monitor whatever>
```

**In essence**, the *output* part is __needed__.

**Example**:  
Let the first workspace have a name of ``1: www`` and the second one no name, but a number 
``2``:

```bash
workspace "1: www" output CRT2
workspace 2 output CRT2
```

Why is this important? A regular expression is used (look at the function ``restore`` for an 
explanation)

**How to move to workspaces with names assigned to them?**  
[Read about it 
here](http://i3wm.org/docs/userguide.html#_changing_named_workspaces_moving_to_workspaces).

**Example**:  
Lets declare a keybind to move to the first workspace (= workspace number one)
```bash
bindsym $mod+1 workspace number 1
```

## things worth mentioning
*Terminals have the same title, it doesn't change when running a process*:  
[zsh](http://www.zsh.org/) solves this with 
[oh-my-zsh](https://github.com/robbyrussell/oh-my-zsh).

*Two windows with the same title (name)*:  
Use marks.

## license
MIT

**Disclaimer**: i3actions has nothing to do with i3. It's just a third-party script.
