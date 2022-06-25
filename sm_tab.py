import json
import os
import shutil
from ssl import DefaultVerifyPaths
# import ffmpeg
import PySimpleGUI as sg
from core import fnf_to_sm, merge_tracks, SM_EXT, SSC_EXT, FNF_EXT, parse_sm, sm_to_fnf

sg.theme("SystemDefault1")

col1_layout = [
	[sg.Text("Simfile", size=(7,1)), sg.Input(key="sm_inputFileSimfile", enable_events=True), sg.FileBrowse(file_types=(("Stepmania simfile", "*.sm"),), key="sm_fileBrowseSimfile")],
	[sg.Text("Easy", size=(7,1)), sg.Combo([], key="sm_comboEasyChart", size=(52,1), readonly=True)],
	[sg.Text("Medium", size=(7,1)), sg.Combo([], key="sm_comboMediumChart", size=(52,1), readonly=True)],
	[sg.Text("Hard", size=(7,1)), sg.Combo([], key="sm_comboHardChart", size=(52,1), readonly=True)],
	[sg.Button("Auto-Populate", key="sm_autoPopulate"), sg.Button("Reset", key="sm_reset")],
	[sg.Text("Output", size=(7,1)), sg.Input(os.path.join(os.getcwd(), 'output'), key="sm_inputFolderOutput"), sg.FolderBrowse(key="folderBrowse")],
	# [sg.Text(size=(40,1), key="output1")],
	# [sg.In(), sg.FileBrowse(file_types=(("JSON Files", "*.json"),))],
	[sg.Button("Go", key="sm_go"), sg.Button("Exit", key="sm_exit")],
]

col2_layout = [
	[sg.Text("Chart format")],
	[
		sg.Radio("Original (Old)", group_id="sm_format", enable_events=True, key="sm_formatOld", default=True), 
		sg.Radio("Original (New)", group_id="sm_format", enable_events=True, key="sm_formatNew", default=True), 
		sg.Radio("Psych Engine", group_id="sm_format", enable_events=True, key="sm_formatPsych"), 
		sg.Radio("Kade Engine", group_id="sm_format", enable_events=True, key="sm_formatKade"), 
	],
	[sg.Text("Folder Name", size=(15,1)), sg.Input(key="sm_inputSongFolderName", size=(35, 1), default_text='tutorial')],
]

sm_layout = [[
	sg.Column(col1_layout),
	sg.Column(col2_layout),
]]


def sm_eventlistener(event: str, values, window): 

	if event == "sm_autoPopulate" or event == "sm_inputFileSimfile":

		infile = values["sm_inputFileSimfile"]
		override = event == "autoPopulate"

		if os.path.isfile(infile):

			infile_name, infile_ext = os.path.splitext(infile)
			infile_dirname = os.path.dirname(infile_name)
			chart_notes = [""]
			chart_notes_index = [-1]

			with open(infile, "r") as chartfile:
				sm_chart = parse_sm(chartfile)
				index_temp = -1
				for notes in sm_chart['notes']:
					index_temp += 1
					if (notes['type'] != "dance-single"): 
						continue
					chart_notes.append(f"{notes['type']} {notes['author']} {notes['diff']} {notes['diffNum']} {notes['groove']}")
					chart_notes_index.append(index_temp)

				window["sm_comboEasyChart"].Update(values=chart_notes)
				window["sm_comboMediumChart"].Update(values=chart_notes)
				window["sm_comboHardChart"].Update(values=chart_notes)

				# print(chart_simfile)

			# if values["sm_inputFileSimfile"] == "" or override:
			# 	infile_easy = infile_name + "-easy" + FNF_EXT
			# 	if os.path.isfile(infile_easy):
			# 		window["sm_inputFileSimfile"].Update(infile_easy)


	# if values["sm_inputCharter"] == "":
	# 	window["sm_inputCharter"].Update("fnf-to-sm")

	elif event == "sm_go":

		chart_jsons = []
		
		infile = values["sm_inputFileSimfile"]
		
		if infile != "" and os.path.isfile(infile):

			chart_notes = [""]
			chart_notes_index = [-1]

			with open(infile, "r") as chartfile:
				sm_chart = parse_sm(chartfile)
				index_temp = -1
				for notes in sm_chart['notes']:
					index_temp += 1
					if (notes['type'] != "dance-single"): 
						continue
					chart_notes.append(f"{notes['type']} {notes['author']} {notes['diff']} {notes['diffNum']} {notes['groove']}")
					chart_notes_index.append(index_temp)

				easy_index = chart_notes_index[chart_notes.index(values["sm_comboEasyChart"])]
				medium_index = chart_notes_index[chart_notes.index(values["sm_comboMediumChart"])]
				hard_index = chart_notes_index[chart_notes.index(values["sm_comboHardChart"])]

		if values["sm_inputFolderOutput"] == "":
			output_folder = os.getcwd()
		else:
			output_folder = values["sm_inputFolderOutput"]

		window["sm_go"].Update(disabled=True)
		window["progressBar"].UpdateBar(0, 1)
		window["textProgress"].Update("Converting .sm to FNF .json...")

		song_folder_name = values["sm_inputSongFolderName"]

		if values['sm_formatOld']: format = 'old' #TODO
		elif values['sm_formatNew']: format = 'new' #TODO
		elif values['sm_formatPsych']: format = 'psych' #TODO
		elif values['sm_formatKade']: format = 'kade' #TODO

		elif format == 'old':
			sm_chart['title'] = 'Tutorial'
			os.makedirs(os.path.join(output_folder, 'data', 'tutorial'), exist_ok=True)
			os.makedirs(os.path.join(output_folder, 'songs', 'tutorial'), exist_ok=True)
			path_easy = os.path.join(output_folder, 'data', 'tutorial', 'tutorial-easy.json')
			path_medium = os.path.join(output_folder, 'data', 'tutorial', 'tutorial.json')
			path_hard = os.path.join(output_folder, 'data', 'tutorial', 'tutorial-hard.json')
			path_song = os.path.join(output_folder, 'songs', 'tutorial', 'Inst.ogg')
		if format == 'new':
			sm_chart['title'] = 'Tutorial'
			os.makedirs(os.path.join(output_folder, 'data', 'tutorial'), exist_ok=True)
			os.makedirs(os.path.join(output_folder, 'music'), exist_ok=True)
			path_easy = os.path.join(output_folder, 'data', 'tutorial', 'tutorial-easy.json')
			path_medium = os.path.join(output_folder, 'data', 'tutorial', 'tutorial.json')
			path_hard = os.path.join(output_folder, 'data', 'tutorial', 'tutorial-hard.json')
			path_song = os.path.join(output_folder, 'music', 'Tutorial-Inst.ogg')
		elif format == 'kade':
			sm_chart['title'] = 'Tutorial'
			os.makedirs(os.path.join(output_folder, 'data', 'songs', 'tutorial'), exist_ok=True)
			os.makedirs(os.path.join(output_folder, 'songs', 'tutorial'), exist_ok=True)
			path_easy = os.path.join(output_folder, 'data', 'songs', 'tutorial', 'tutorial-easy.json')
			path_medium = os.path.join(output_folder, 'data', 'songs', 'tutorial', 'tutorial.json')
			path_hard = os.path.join(output_folder, 'data', 'songs', 'tutorial', 'tutorial-hard.json')
			path_song = os.path.join(output_folder, 'songs', 'tutorial', 'Inst.ogg')
			with open(os.path.join(output_folder, 'data', 'songs', 'tutorial', 'modchart.lua'), 'w') as outfile:
				outfile.write('-- sinkhole')
		elif format == 'psych':
			safe_name = sm_chart['title'].lower().replace(' ', '')
			os.makedirs(os.path.join(output_folder, song_folder_name, 'data', safe_name), exist_ok=True)
			os.makedirs(os.path.join(output_folder, song_folder_name, 'music', safe_name), exist_ok=True)
			os.makedirs(os.path.join(output_folder, song_folder_name, 'week'), exist_ok=True)
			os.makedirs(os.path.join(output_folder, song_folder_name, 'images', 'storymenu'), exist_ok=True)
			path_easy = os.path.join(output_folder, song_folder_name, 'data', safe_name, safe_name + '-easy.json')
			path_medium = os.path.join(output_folder, song_folder_name, 'data', safe_name, safe_name + '.json')
			path_hard = os.path.join(output_folder, song_folder_name, 'data', safe_name, safe_name + '-hard.json')
			path_song = os.path.join(output_folder, song_folder_name, 'music', safe_name, 'Inst.ogg')
			week_json = {
				"songs": [
					[safe_name, "gf", [165, 0, 77]]
				],

				"weekCharacters": [
					"",
					"bf",
					"gf"
				],
				"weekBackground": "stage",

				"storyName": sm_chart['title'],
				"weekBefore": "tutorial",
				"weekName": "Week SM",
				"startUnlocked": True,

				"hideStoryMode": False,
				"hideFreeplay": False,
				"difficulties": "Easy, Normal, Hard",
			}
			with open(os.path.join(output_folder, song_folder_name, 'week', safe_name + '.json'), 'w') as outfile:
				outfile.write(json.dumps(week_json))
			week_json = {
				"name": sm_chart['title'],
				"description": "Converted with fnf-to-sm",
				"restart": False,
				"color": [170, 0, 255]
			}
			with open(os.path.join(output_folder, song_folder_name, 'pack.json'), 'w') as outfile:
				outfile.write(json.dumps(week_json))
			shutil.copyfile(os.path.join(os.getcwd(), 'blank.png'), os.path.join(output_folder, song_folder_name, 'images', 'storymenu', safe_name + '.png'))
				

		easy_chartfile, medium_chartfile, hard_chartfile = sm_to_fnf(
			sm_chart,
			easy_index,
			medium_index,
			hard_index,			
		)

		if easy_chartfile:
			with open(path_easy, "w") as outfile:
				outfile.write(easy_chartfile)
		if medium_chartfile:
			with open(path_medium, "w") as outfile:
				outfile.write(medium_chartfile)
		if hard_chartfile:
			with open(path_hard, "w") as outfile:
				outfile.write(hard_chartfile)

		shutil.copyfile(os.path.join(infile, '..', sm_chart['metadata']['music']), path_song)

		window["textProgress"].Update("All done!")
		window["progressBar"].UpdateBar(1, 1)
		window["sm_go"].Update(disabled=False)

	else:

		return False
	
	return True