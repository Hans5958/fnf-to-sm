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

import json
import os
# import ffmpeg
import PySimpleGUI as sg
from utils import fnf_to_sm, merge_tracks

VERSION = "v0.2.0-dev"

SM_EXT = ".sm"
SSC_EXT = ".ssc"
FNF_EXT = ".json"

sg.theme("SystemDefault1")

tab1_column1_layout = [
	[sg.Text('Beginner', size=(7,1)), sg.Input(key='inputFileBeginner'), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key='fileBrowseBeginner')],
	[sg.Text('Easy', size=(7,1)), sg.Input(key='inputFileEasy'), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key='fileBrowseEasy')],
	[sg.Text('Medium', size=(7,1)), sg.Input(key='inputFileMedium', enable_events=True), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key='fileBrowseMedium', enable_events=True)],
	[sg.Text('Hard', size=(7,1)), sg.Input(key='inputFileHard'), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key='fileBrowseHard')],
	[sg.Text('Challenge', size=(7,1)), sg.Input(key='inputFileChallenge', disabled=True), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key='fileBrowseChallenge', disabled=True)],
	[sg.Text('Inst', size=(7,1)), sg.Input(key='inputFileInst'), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key='fileBrowseInst')],
	[sg.Text('Voices', size=(7,1)), sg.Input(key='inputFileVoices'), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key='fileBrowseVoices')],
	[sg.Button('Auto-Populate', key='autoPopulate1'), sg.Button('Reset', key='reset1')],
	[sg.Text('Output', size=(7,1)), sg.Input(os.getcwd(), key='inputFolderOutput'), sg.FolderBrowse(key='folderBrowse1')],
	# [sg.Text(size=(40,1), key='output1')],
	# [sg.In(), sg.FileBrowse(file_types=(("JSON Files", "*.json"),))],
	[sg.Button('Go', key='go1'), sg.Button('Exit', key="exit1")],
]

tab1_column2_layout = [
	[sg.Text('Title', size=(6,1)), sg.Input(key="inputTitle")],
	[sg.Text('Subtitle', size=(6,1)), sg.Input(key="inputSubtitle")],
	[sg.Text('Artist', size=(6,1)), sg.Input(key="inputArtist")],
	[sg.Text('Charter', size=(6,1)), sg.Input(key="inputCharter")],
	[sg.Text('Credit', size=(6,1)), sg.Input("fnf-to-sm", key="inputCredit")],
	[sg.Text('Difficulty Value')],
	[
		sg.Text("SBG", size=(4,1)),
		sg.Input(2, key="inputDiffSingleBeginner", size=(2,1)), 
		sg.Text("SEZ", size=(4,1)),
		sg.Input(4, key="inputDiffSingleEasy", size=(2,1)), 
		sg.Text("SMD", size=(4,1)), 
		sg.Input(6, key="inputDiffSingleMedium", size=(2,1)), 
		sg.Text("SHD", size=(4,1)),
		sg.Input(8, key="inputDiffSingleHard", size=(2,1)),
		sg.Text("SCH", size=(4,1)), 
		sg.Input(10, key="inputDiffSingleChallenge", size=(2,1)),
	],
	[
		sg.Text("DBG", size=(4,1)),
		sg.Input(3, key="inputDiffDoubleBeginner", size=(2,1)), 
		sg.Text("DEZ", size=(4,1)), 
		sg.Input(5, key="inputDiffDoubleEasy", size=(2,1)),
		sg.Text("DMD", size=(4,1)), 
		sg.Input(7, key="inputDiffDoubleMedium", size=(2,1)), 
		sg.Text("DHD", size=(4,1)),
		sg.Input(9, key="inputDiffDoubleHard", size=(2,1)),
		sg.Text("DCH", size=(4,1)), 
		sg.Input(11, disabled=True, key="inputDiffDoubleChallenge", size=(2,1)),
	],
	[sg.Text('Derivate mixed Challenge parts from...')],
	[
		sg.Radio('Beginner', group_id="derivateMixedFrom", enable_events=True, key="radioDerivateMixedFromBeginner"), 
		sg.Radio('Easy', group_id="derivateMixedFrom", enable_events=True, key="radioDerivateMixedFromEasy"), 
		sg.Radio('Medium', group_id="derivateMixedFrom", enable_events=True, key="radioDerivateMixedFromMedium"), 
		sg.Radio('Hard', default=True, group_id="derivateMixedFrom", enable_events=True, key="radioDerivateMixedFromHard"), 
		sg.Radio('None', group_id="derivateMixedFrom", enable_events=True, key="radioDerivateMixedFromNone")
	],
	[sg.Text('Banner File Name', size=(15,1)), sg.Input(key="inputBannerFileName", size=(35, 1))],
	[sg.Text('BG File Name', size=(15,1)), sg.Input(key="inputBGFileName", size=(35, 1))],
	[sg.Text('Folder Name', size=(15,1)), sg.Input(key="inputSongFolderName", size=(35, 1))],
]

tab1_layout = [[
	sg.Column(tab1_column1_layout),
	sg.Column(tab1_column2_layout),
]]

tab2_column1_layout = [
	[sg.Text('Easy', size=(7,1)), sg.Input(key='inputFileEasy2'), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key='fileBrowseEasy2')],
	[sg.Text('Medium', size=(7,1)), sg.Input(key='inputFileMedium2', enable_events=True), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key='fileBrowseMedium2', enable_events=True)],
	[sg.Text('Hard', size=(7,1)), sg.Input(key='inputFileHard2'), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key='fileBrowseHard2')],
	[sg.Text('Inst', size=(7,1)), sg.Input(key='inputFileInst2'), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key='fileBrowseInst2')],
	[sg.Text('Voices', size=(7,1)), sg.Input(key='inputFileVoices2'), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key='fileBrowseVoices2')],
	[sg.Button('Auto-Populate', key='autoPopulate2'), sg.Button('Reset', key='reset2')],
	[sg.Text('Output', size=(7,1)), sg.Input(os.getcwd(), key='inputFolderOutput2'), sg.FolderBrowse(key='folderBrowse2')],
	# [sg.Text(size=(40,1), key='output12')],
	# [sg.In(), sg.FileBrowse(file_types=(("JSON Files", "*.json"),))],
	[sg.Button('Go', key='go2'), sg.Button('Exit', key='exit2')],
]

tab2_column2_layout = [
	[sg.Text('Title', size=(6,1)), sg.Input(key="inputTitle2")],
	[sg.Text('Subtitle', size=(6,1)), sg.Input(key="inputSubtitle2")],
	[sg.Text('Artist', size=(6,1)), sg.Input(key="inputArtist2")],
	[sg.Text('Charter', size=(6,1)), sg.Input(key="inputCharter2")],
	[sg.Text('Credit', size=(6,1)), sg.Input("fnf-to-sm", key="inputCredit2")],
	[sg.Text('Difficulty Value')],
	[
		sg.Text("SBG", size=(3,1)),
		sg.Input(2, key="inputDiffSingleBeginner2", size=(2,1)), 
		sg.Text("SEZ", size=(3,1)),
		sg.Input(4, key="inputDiffSingleEasy2", size=(2,1)), 
		sg.Text("SMD", size=(3,1)), 
		sg.Input(6, key="inputDiffSingleMedium2", size=(2,1)), 
		sg.Text("SHD", size=(3,1)),
		sg.Input(8, key="inputDiffSingleHard2", size=(2,1)),
		sg.Text("SCH", size=(3,1)), 
		sg.Input(10, key="inputDiffSingleChallenge2", size=(2,1)),
		sg.Text("SED", size=(3,1)), 
		sg.Input(12, key="inputDiffSingleEdit2", size=(2,1)),
	],
	[
		sg.Text("DEZ", size=(3,1)), 
		sg.Input(5, key="inputDiffDoubleEasy2", size=(2,1)),
		sg.Text("DMD", size=(3,1)), 
		sg.Input(7, key="inputDiffDoubleMedium2", size=(2,1)), 
		sg.Text("DHD", size=(3,1)),
		sg.Input(9, key="inputDiffDoubleHard2", size=(2,1)),
		sg.Text("CEZ", size=(3,1)), 
		sg.Input(4, key="inputDiffCoupleEasy2", size=(2,1)),
		sg.Text("CMD", size=(3,1)), 
		sg.Input(6, key="inputDiffCoupleMedium2", size=(2,1)),
		sg.Text("CHD", size=(3,1)),
		sg.Input(8, key="inputDiffCoupleHard2", size=(2,1)), 
	],
	[sg.Text('Banner File Name', size=(15,1)), sg.Input(key="inputBannerFileName2", size=(35, 1))],
	[sg.Text('BG File Name', size=(15,1)), sg.Input(key="inputBGFileName2", size=(35, 1))],
	[sg.Text('Folder Name', size=(15,1)), sg.Input(key="inputSongFolderName2", size=(35, 1))],
]

tab2_layout = [[
	sg.Column(tab2_column1_layout),
	sg.Column(tab2_column2_layout),
]]

layout = [
	[sg.Text(f"fnf-to-sm (Hans5958 fork) {VERSION}")],
	[sg.TabGroup([[
		sg.Tab('Tab 1', tab1_layout, key='Tab1'), 
		sg.Tab('Tab 2', tab2_layout, key='Tab2')
	]])],
	[
		[sg.Text("Select the files and hit \"Go\".", size=(107,1), key="textProgress")],
		[sg.ProgressBar(1, size=(78,15), orientation='h', key='progressBar1')],
	]
]

def main():

	window = sg.Window("fnf-to-sm GUI", layout, finalize=True)

	# default_values = {}

	# event, values = window.read(timeout=0)
	# for key in window.AllKeysDict.keys():
	# 	if key.startswith('input') or key.startswith('radio'):
	# 		default_values[key] = values[key]

	while True:

		event, values = window.read()
		print(event)

		if event == sg.WINDOW_CLOSED or event == 'Exit':
			break

		elif event.startswith('radioDerivateMixedFrom'):
			if event == "radioDerivateMixedFromNone":
				window['inputFileChallenge'].Update(disabled=False)
				window['fileBrowseChallenge'].Update(disabled=False)
				window['inputDiffDoubleChallenge'].Update(disabled=False)
			else:
				window['inputFileChallenge'].Update(disabled=True)
				window['fileBrowseChallenge'].Update(disabled=True)		
				window['inputDiffDoubleChallenge'].Update(disabled=True)		

		elif event == 'autoPopulate1' or event == 'inputFileMedium':

			infile = values['inputFileMedium']
			override = event == 'autoPopulate1'

			if os.path.isfile(infile):

				infile_name, infile_ext = os.path.splitext(infile)
				infile_dirname = os.path.dirname(infile_name)

				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					
					if values['inputTitle'] == "" or override:
						window['inputTitle'].Update(chart_json["song"]["song"])

					if values['inputSongFolderName'] == "" or override:
						window['inputSongFolderName'].Update(chart_json["song"]["song"])

				if values['inputFileEasy'] == "" or override:
					infile_easy = infile_name + "-easy" + FNF_EXT
					if os.path.isfile(infile_easy):
						window['inputFileEasy'].Update(infile_easy)

				if values['inputFileHard'] == "" or override:
					infile_hard = infile_name + "-hard" + FNF_EXT
					if os.path.isfile(infile_hard):
						window['inputFileHard'].Update(infile_hard)

				if values['inputFileInst'] == "" or override:
					infile_inst = f"{infile_dirname.replace('data', 'songs')}/Inst.ogg"
					if os.path.isfile(infile_inst):
						window['inputFileInst'].Update(infile_inst)

				if values['inputFileVoices'] == "" or override:
					infile_voices = f"{infile_dirname.replace('data', 'songs')}/Voices.ogg"
					if os.path.isfile(infile_voices):
						window['inputFileVoices'].Update(infile_voices)

		elif event == 'autoPopulate2' or event == 'inputFileMedium2':

			infile = values['inputFileMedium2']
			override = event == 'autoPopulate2'

			if os.path.isfile(infile):

				infile_name, infile_ext = os.path.splitext(infile)
				infile_dirname = os.path.dirname(infile_name)

				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					
					if values['inputTitle2'] == "" or override:
						window['inputTitle2'].Update(chart_json["song"]["song"])

					if values['inputSongFolderName2'] == "" or override:
						window['inputSongFolderName2'].Update(chart_json["song"]["song"])

				if values['inputFileEasy2'] == "" or override:
					infile_easy = infile_name + "-easy" + FNF_EXT
					if os.path.isfile(infile_easy):
						window['inputFileEasy2'].Update(infile_easy)

				if values['inputFileHard2'] == "" or override:
					infile_hard = infile_name + "-hard" + FNF_EXT
					if os.path.isfile(infile_hard):
						window['inputFileHard2'].Update(infile_hard)

				if values['inputFileInst2'] == "" or override:
					infile_inst = f"{infile_dirname.replace('data', 'songs')}/Inst.ogg"
					if os.path.isfile(infile_inst):
						window['inputFileInst2'].Update(infile_inst)

				if values['inputFileVoices2'] == "" or override:
					infile_voices = f"{infile_dirname.replace('data', 'songs')}/Voices.ogg"
					if os.path.isfile(infile_voices):
						window['inputFileVoices2'].Update(infile_voices)

		# if values['inputCharter'] == "":
		# 	window['inputCharter'].Update("fnf-to-sm")

		elif event == 'go1':

			chart_jsons = []

			infile = values['inputFileBeginner']
			if infile != "" and os.path.isfile(infile):
				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Beginner"
					chart_json["infile"] = infile
					chart_json["modes"] = (("single", values['inputDiffSingleBeginner']), ("double", values['inputDiffDoubleBeginner']))
					if values['radioDerivateMixedFromBeginner']:
						chart_json["modes"].append(("single-challenge", values['inputDiffSingleChallenge']))
					chart_jsons.append(chart_json)

			infile = values['inputFileEasy']
			if infile != "" and os.path.isfile(infile):
				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Easy"
					chart_json["infile"] = infile
					chart_json["modes"] = [("single", values['inputDiffSingleEasy']), ("double", values['inputDiffDoubleEasy'])]
					if values['radioDerivateMixedFromEasy']:
						chart_json["modes"].append(("single-challenge", values['inputDiffSingleChallenge']))
					chart_jsons.append(chart_json)

			infile = values['inputFileMedium']
			if infile != "" and os.path.isfile(infile):
				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Medium"
					chart_json["infile"] = infile
					chart_json["modes"] = [("single", values['inputDiffSingleMedium']), ("double", values['inputDiffDoubleMedium'])]
					if values['radioDerivateMixedFromMedium']:
						chart_json["modes"].append(("single-challenge", values['inputDiffSingleChallenge']))
					chart_jsons.append(chart_json)

			infile = values['inputFileHard']
			if infile != "" and os.path.isfile(infile):
				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Hard"
					chart_json["infile"] = infile
					chart_json["modes"] = [("single", values['inputDiffSingleHard']), ("double", values['inputDiffDoubleHard'])]
					if values['radioDerivateMixedFromHard']:
						chart_json["modes"].append(("single-challenge", values['inputDiffSingleChallenge']))
					chart_jsons.append(chart_json)

			infile = values['inputFileChallenge']
			if values['radioDerivateMixedFromNone'] and infile != "" and os.path.isfile(infile):
				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Challenge"
					chart_json["infile"] = infile
					chart_json["modes"] = (("single", values['inputDiffSingleChallenge']), ("double", values['inputDiffDoubleChallenge']))
					chart_jsons.append(chart_json)

			if values['inputFolderOutput'] == "":
				output = os.getcwd()
			else:
				output = values['inputFolderOutput']

			window['go1'].Update(disabled=True)
			window['progressBar1'].UpdateBar(0, 1)
			window['textProgress'].Update("Converting FnF .json to .sm...")

			if values['inputFileInst'] != "" and values['inputFileVoices'] != "":
				initial_steps = 1
			else:
				initial_steps = 0

			fnf_to_sm(
				chart_jsons, 
				window=window, 
				song_name=values['inputTitle'],
				song_subtitle=values['inputSubtitle'],
				song_artist=values['inputArtist'], 
				song_charter=values['inputCharter'], 
				song_credit=values['inputCredit'], 
				song_banner_file_name=values['inputBannerFileName'],
				song_bg_file_name=values['inputBGFileName'],
				output_folder=output,
				song_folder_name=values['inputSongFolderName'],
				initial_steps=initial_steps
			)

			if values['inputFileInst'] != "" and values['inputFileVoices'] != "":

				window['textProgress'].Update("Merging tracks...")

				def callback(window):
					window['textProgress'].Update("All done!")
					window['progressBar1'].UpdateBar(1, 1)
					window['go1'].Update(disabled=False)

				merge_tracks(
					inst_track=values['inputFileInst'],
					voices_track=values['inputFileVoices'],
					song_name=values['inputTitle'], 
					output_folder=output,
					song_folder_name=values['inputSongFolderName'],
					callback=callback,
					window=window
				)

			else:

				window['textProgress'].Update("All done!")
				window['progressBar1'].UpdateBar(1, 1)
				window['go1'].Update(disabled=False)

		elif event == 'go2':

			chart_jsons = []

			infile = values['inputFileEasy2']
			if infile != "" and os.path.isfile(infile):
				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Easy"
					chart_json["infile"] = infile
					chart_json["modes"] = [
						("double", values['inputDiffDoubleEasy2']), 
						("couple", values['inputDiffCoupleEasy2']), 
						("single-merged", values['inputDiffSingleEasy2'])
					]
					chart_jsons.append(chart_json)

				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Beginner"
					chart_json["infile"] = infile
					chart_json["modes"] = [("single", values['inputDiffSingleBeginner2'])]
					chart_jsons.append(chart_json)

			infile = values['inputFileMedium2']
			if infile != "" and os.path.isfile(infile):
				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Medium"
					chart_json["infile"] = infile
					chart_json["modes"] = [
						("double", values['inputDiffDoubleMedium2']), 
						("couple", values['inputDiffCoupleMedium2']), 
						("single", values['inputDiffSingleMedium2'])
					]
					chart_jsons.append(chart_json)

				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Hard"
					chart_json["infile"] = infile
					chart_json["modes"] = [("single-merged", values['inputDiffSingleHard2'])]
					chart_jsons.append(chart_json)

			infile = values['inputFileHard2']
			if infile != "" and os.path.isfile(infile):
				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Hard"
					chart_json["infile"] = infile
					chart_json["modes"] = [
						("double", values['inputDiffDoubleHard2']), 
						("couple", values['inputDiffCoupleHard2']), 
					]
					chart_jsons.append(chart_json)

				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Challenge"
					chart_json["infile"] = infile
					chart_json["modes"] = [("single", values['inputDiffSingleChallenge2'])]
					chart_jsons.append(chart_json)

				with open(infile, "r") as chartfile:
					chart_json = json.loads(chartfile.read().strip('\0'))
					chart_json["diff"] = "Edit"
					chart_json["infile"] = infile
					chart_json["modes"] = [("single-merged", values['inputDiffSingleEdit2'])]
					chart_jsons.append(chart_json)

			if values['inputFolderOutput2'] == "":
				output = os.getcwd()
			else:
				output = values['inputFolderOutput2']

			window['go2'].Update(disabled=True)
			window['progressBar1'].UpdateBar(0, 1)
			window['textProgress'].Update("Converting FnF .json to .sm...")

			if values['inputFileInst'] != "" and values['inputFileVoices'] != "":
				initial_steps = 1
			else:
				initial_steps = 0

			fnf_to_sm(
				chart_jsons, 
				window=window, 
				song_name=values['inputTitle2'],
				song_subtitle=values['inputSubtitle2'],
				song_artist=values['inputArtist2'], 
				song_charter=values['inputCharter2'], 
				song_credit=values['inputCredit2'], 
				song_banner_file_name=values['inputBannerFileName2'],
				song_bg_file_name=values['inputBGFileName2'],
				output_folder=output,
				song_folder_name=values['inputSongFolderName2'],
				initial_steps=initial_steps
			)

			if values['inputFileInst2'] != "" and values['inputFileVoices2'] != "":

				window['textProgress'].Update("Merging tracks...")

				def callback(window):
					window['textProgress'].Update("All done!")
					window['progressBar1'].UpdateBar(1, 1)
					window['go2'].Update(disabled=False)

				merge_tracks(
					inst_track=values['inputFileInst2'],
					voices_track=values['inputFileVoices2'],
					song_name=values['inputTitle2'], 
					output_folder=output,
					song_folder_name=values['inputSongFolderName2'],
					callback=callback,
					window=window
				)

			else:

				window['textProgress'].Update("All done!")
				window['progressBar1'].UpdateBar(1, 1)
				window['go2'].Update(disabled=False)

		elif event == "Reset":
			for key in default_values.keys(): 
				print(key)
				print(default_values[key])
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
