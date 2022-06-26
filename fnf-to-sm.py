# fnf-to-sm.py
# FNF to SM converter
# Copyright (C) 2021 shockdude

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <https://www.gnu.org/licenses/>.

# Built from the original chart-to-sm.js by Paturages, released under GPL3 with his permission

# import ffmpeg
import PySimpleGUI as sg
from modules.legacy_tab import legacy_layout, legacy_eventlistener
from modules.edit_tab import edit_layout, edit_eventlistener
from modules.edit2_tab import edit2_layout, edit2_eventlistener
from modules.edit2a_tab import edit2a_layout, edit2a_eventlistener
from modules.sm_tab import sm_layout, sm_eventlistener

VERSION = "v0.2.0-dev"

sg.theme("SystemDefault1")

layout = [
	[sg.Text(f"fnf-to-sm (Hans5958 fork) {VERSION}")],
	[sg.TabGroup([[
		sg.Tab('Edit 2', edit2_layout, key='edit2_tab'),
		sg.Tab('Edit 2 (Advanced)', edit2a_layout, key='edit2a_tab'),
		sg.Tab('StepMania', sm_layout, key='sm_tab'),
		sg.Tab('Edit', edit_layout, key='edit_tab'),
		sg.Tab('Legacy', legacy_layout, key='legacy_tab'), 
	]])],
	[
		[sg.Text("Select the files and hit \"Go\".", size=(107,1), key="textProgress")],
		[sg.ProgressBar(1, size=(78,15), orientation='h', key='progressBar')],
	]
]

def main():

	window = sg.Window("fnf-to-sm GUI", layout, finalize=True)

	default_values = {}

	event, values = window.read(timeout=0)
	for key in window.AllKeysDict.keys():
		if type(key) is str and len(key.split('_')) > 1:
			key_name = key.split('_')[1]
			print(key_name)
			if key_name.startswith('input') or key_name.startswith('radio'):
				default_values[key] = values[key]

	while True:

		event, values = window.read()
		print(event)

		if event == sg.WINDOW_CLOSED or event.endswith('_exit'):
			break

		elif legacy_eventlistener(event, values, window):
			continue

		elif edit_eventlistener(event, values, window):
			continue

		elif edit2_eventlistener(event, values, window):
			continue

		elif edit2a_eventlistener(event, values, window):
			continue

		elif sm_eventlistener(event, values, window):
			continue

		elif event.endswith('_reset'):
			print('goes')
			tab_id = event.split('_')[0]
			for key in default_values.keys(): 
				if key.startswith(tab_id):
					window[key].Update(default_values[key])

	window.close()

	# if len(sys.argv) < 2:
	# 	print("Error: not enough arguments")
	# 	usage()
	
	# infile = sys.argv[1]
	# infile_name, infile_ext = os.path.splitext(os.path.basename(infile))
	# if infile_ext == FNF_EXT:
	# 	fnf_to_sm(infile)
	# elif infile_ext == SM_EXT:
	# 	sm_to_fnf(infile)
	# else:
	# 	print("Error: unsupported file {}".format(infile))
	# 	usage()

if __name__ == "__main__":
	main()
