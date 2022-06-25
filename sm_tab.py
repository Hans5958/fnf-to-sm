import json
import os
import shutil
from ssl import DefaultVerifyPaths
# import ffmpeg
import PySimpleGUI as sg
from core import fnf_to_sm, merge_tracks, SM_EXT, SSC_EXT, FNF_EXT, parse_sm, sm_to_fnf

sg.theme("SystemDefault1")

col1_layout = [
	[sg.Text("Simfile", size=(7,1)), sg.Input(key="sm_inputFileSimfile", enable_events=True), sg.FileBrowse(file_types=(("StepMania simfile", "*.sm"), ("StepMania simfile", "*.ssc")), key="sm_fileBrowseSimfile")],
	[sg.Text("Easy", size=(7,1)), sg.Combo([], key="sm_comboEasyChart", size=(52,1), readonly=True)],
	[sg.Text("Medium", size=(7,1)), sg.Combo([], key="sm_comboMediumChart", size=(52,1), readonly=True)],
	[sg.Text("Hard", size=(7,1)), sg.Combo([], key="sm_comboHardChart", size=(52,1), readonly=True)],
	[sg.Button("Auto-Populate", key="sm_autoPopulate"), sg.Button("Reset", key="sm_reset")],
	[sg.Text("Output", size=(7,1)), sg.Input(os.path.join(os.getcwd(), 'output'), key="sm_inputFolderOutput"), sg.FolderBrowse(key="sm_folderBrowse")],
	# [sg.Text(size=(40,1), key="output1")],
	# [sg.In(), sg.FileBrowse(file_types=(("JSON Files", "*.json"),))],
	[sg.Button("Go", key="sm_go"), sg.Button("Exit", key="sm_exit")],
]

col2_layout = [
	[sg.Text("ID", size=(6,1)), sg.Input(key="sm_inputId")],
	[sg.Text("Title", size=(6,1)), sg.Input(key="sm_inputTitle")],
	[sg.Text("Chart format")],
	[
		sg.Radio("Original (Old)", group_id="sm_format", enable_events=True, key="sm_formatOld"), 
		sg.Radio("Original (New)", group_id="sm_format", enable_events=True, key="sm_formatNew", default=True), 
		sg.Radio("Psych Engine", group_id="sm_format", enable_events=True, key="sm_formatPsych"), 
	],
	[
		sg.Radio("Kade Engine", group_id="sm_format", enable_events=True, key="sm_formatKade"), 
		sg.Radio("Kade Engine (ModCore)", group_id="sm_format", enable_events=True, key="sm_formatKadeCore"), 
	],
]

sm_layout = [[
	sg.Column(col1_layout),
	sg.Column(col2_layout),
]]


def sm_eventlistener(event: str, values, window): 

	if event == "sm_autoPopulate" or event == "sm_inputFileSimfile":

		infile = values["sm_inputFileSimfile"]
		override = event.startswith("autoPopulate")

		if os.path.isfile(infile):

			infile_name, infile_ext = os.path.splitext(infile)
			infile_dirname = os.path.dirname(infile_name)
			chart_notes = [""]
			chart_notes_index = [-1]
			sm_chart = None

			with open(infile, "r") as chartfile:
				sm_chart = parse_sm(chartfile)
				
			index_temp = -1
			for notes in sm_chart.notes:
				index_temp += 1
				if (notes.metadata['stepstype'] != "dance-single"):
					continue
				chart_notes.append(f"{notes.metadata['stepstype']} {notes.metadata['description']} {notes.metadata['difficulty']} {notes.metadata['meter']}")
				chart_notes_index.append(index_temp)

			window["sm_comboEasyChart"].Update(values=chart_notes)
			window["sm_comboMediumChart"].Update(values=chart_notes)
			window["sm_comboHardChart"].Update(values=chart_notes)

			if values["sm_inputId"] == "" or override:
				window["sm_inputId"].Update(value=sm_chart.title.lower().replace(' ', '-'))
			
			if values["sm_inputTitle"] == "" or override:
				window["sm_inputTitle"].Update(value=sm_chart.title)

				# print(chart_simfile)

			# if values["sm_inputFileSimfile"] == "" or override:
			# 	infile_easy = infile_name + "-easy" + FNF_EXT
			# 	if os.path.isfile(infile_easy):
			# 		window["sm_inputFileSimfile"].Update(infile_easy)


	# if values["sm_inputCharter"] == "":
	# 	window["sm_inputCharter"].Update("fnf-to-sm")

	elif event == "sm_go":
		
		infile = values["sm_inputFileSimfile"]
		
		if infile != "" and os.path.isfile(infile):

			chart_notes = [""]
			chart_notes_index = [-1]
			sm_chart = None

			with open(infile, "r") as chartfile:
				sm_chart = parse_sm(chartfile)

			index_temp = -1
			for notes in sm_chart.notes:
				index_temp += 1
				if (notes.metadata['stepstype'] != "dance-single"):
					continue
				chart_notes.append(f"{notes.metadata['stepstype']} {notes.metadata['description']} {notes.metadata['difficulty']} {notes.metadata['meter']}")
				chart_notes_index.append(index_temp)

			easy_index = chart_notes_index[chart_notes.index(values["sm_comboEasyChart"])]
			medium_index = chart_notes_index[chart_notes.index(values["sm_comboMediumChart"])]
			hard_index = chart_notes_index[chart_notes.index(values["sm_comboHardChart"])]

			sm_chart.title = values["sm_inputId"]

		if values["sm_inputFolderOutput"] == "":
			output_folder = os.getcwd()
		else:
			output_folder = values["sm_inputFolderOutput"]

		window["sm_go"].Update(disabled=True)
		window["progressBar"].UpdateBar(0, 1)
		window["textProgress"].Update("Converting .sm to FNF .json...")

		song_title = values["sm_inputTitle"]
		song_id = values["sm_inputId"]

		if values['sm_formatOld']: format = 'old'
		elif values['sm_formatNew']: format = 'new'
		elif values['sm_formatPsych']: format = 'psych'
		elif values['sm_formatKade']: format = 'kade'
		elif values['sm_formatKadeCore']: format = 'kadecore'

		if format == 'old':
			sm_chart.title = 'Tutorial'
			os.makedirs(os.path.join(output_folder, 'data', 'tutorial'), exist_ok=True)
			os.makedirs(os.path.join(output_folder, 'songs', 'tutorial'), exist_ok=True)
			path_easy = os.path.join(output_folder, 'data', 'tutorial', 'tutorial-easy.json')
			path_medium = os.path.join(output_folder, 'data', 'tutorial', 'tutorial.json')
			path_hard = os.path.join(output_folder, 'data', 'tutorial', 'tutorial-hard.json')
			path_song = os.path.join(output_folder, 'songs', 'tutorial', 'Inst.ogg')
		if format == 'new':
			sm_chart.title = 'Tutorial'
			os.makedirs(os.path.join(output_folder, 'data', 'tutorial'), exist_ok=True)
			os.makedirs(os.path.join(output_folder, 'music'), exist_ok=True)
			path_easy = os.path.join(output_folder, 'data', 'tutorial', 'tutorial-easy.json')
			path_medium = os.path.join(output_folder, 'data', 'tutorial', 'tutorial.json')
			path_hard = os.path.join(output_folder, 'data', 'tutorial', 'tutorial-hard.json')
			path_song = os.path.join(output_folder, 'music', 'Tutorial-Inst.ogg')
		elif format == 'kade':
			sm_chart.title = 'Tutorial'
			os.makedirs(os.path.join(output_folder, 'data', 'songs', 'tutorial'), exist_ok=True)
			os.makedirs(os.path.join(output_folder, 'songs', 'tutorial'), exist_ok=True)
			path_easy = os.path.join(output_folder, 'data', 'songs', 'tutorial', 'tutorial-easy.json')
			path_medium = os.path.join(output_folder, 'data', 'songs', 'tutorial', 'tutorial.json')
			path_hard = os.path.join(output_folder, 'data', 'songs', 'tutorial', 'tutorial-hard.json')
			path_song = os.path.join(output_folder, 'songs', 'tutorial', 'Inst.ogg')
			with open(os.path.join(output_folder, 'data', 'songs', 'tutorial', 'modchart.lua'), 'w') as outfile:
				outfile.write('-- sinkhole')
		elif format == 'kadecore':
			os.makedirs(os.path.join(output_folder, song_title, 'data', 'songs', song_id), exist_ok=True)
			os.makedirs(os.path.join(output_folder, song_title, 'songs', song_id), exist_ok=True)
			os.makedirs(os.path.join(output_folder, song_title, '_append', 'data'), exist_ok=True)
			path_easy = os.path.join(output_folder, song_title, 'data', 'songs', song_id, song_id + '-easy.json')
			path_medium = os.path.join(output_folder, song_title, 'data', 'songs', song_id, song_id + '.json')
			path_hard = os.path.join(output_folder, song_title, 'data', 'songs', song_id, song_id + '-hard.json')
			path_song = os.path.join(output_folder, song_title, 'songs', song_id, 'Inst.ogg')
			with open(os.path.join(output_folder, song_title, '_polymod_meta.json'), 'w') as outfile:
				pack_json = {
					"title": song_title,
					"description": "Converted with fnf-to-sm",
					"author": "fnf-to-sm",
					"api_version": "0.1.0",
					"mod_version": "1.0.0",
					"license": "[PLACEHOLDER] All rights reserved"
				}
				outfile.write(json.dumps(pack_json))
			with open(os.path.join(output_folder, song_title, 'data', 'songs', song_id, '_meta.json'), 'w') as outfile:
				song_meta_json = {
					"title": song_title,
					"offset": "Converted with fnf-to-sm",
				}
				outfile.write(json.dumps(song_meta_json))
			with open(os.path.join(output_folder, song_title, '_append', 'data', 'freeplaySonglist.txt'), 'w') as outfile:
				outfile.write(f'{song_id}:gf:0')

		elif format == 'psych':
			os.makedirs(os.path.join(output_folder, song_title, 'data', song_id), exist_ok=True)
			os.makedirs(os.path.join(output_folder, song_title, 'songs', song_id), exist_ok=True)
			os.makedirs(os.path.join(output_folder, song_title, 'weeks'), exist_ok=True)
			os.makedirs(os.path.join(output_folder, song_title, 'images', 'storymenu'), exist_ok=True)
			path_easy = os.path.join(output_folder, song_title, 'data', song_id, song_id + '-easy.json')
			path_medium = os.path.join(output_folder, song_title, 'data', song_id, song_id + '.json')
			path_hard = os.path.join(output_folder, song_title, 'data', song_id, song_id + '-hard.json')
			path_song = os.path.join(output_folder, song_title, 'songs', song_id, 'Inst.ogg')

			with open(os.path.join(output_folder, song_title, 'weeks', song_id + '.json'), 'w') as outfile:
				week_json = {
					"storyName": "fnf-to-sm",
					"difficulties": "Easy, Normal, Hard",
					"hideFreeplay": False,
					"weekBackground": "stage",
					"weekBefore": "tutorial",
					"freeplayColor": [146, 113, 253],
					"startUnlocked": True,
					"hideStoryMode": False,
					"songs": [[song_id, "bf", [146, 113, 253]]],
					"weekCharacters": ["", "bf", "gf"],
					"hiddenUntilUnlocked": False,
					"weekName": "fnf-to-sm"
				}
				outfile.write(json.dumps(week_json))
			with open(os.path.join(output_folder, song_title, 'pack.json'), 'w') as outfile:
				pack_json = {
					"name": sm_chart.title,
					"description": "Converted with fnf-to-sm",
					"restart": False,
					"color": [170, 0, 255]
				}
				outfile.write(json.dumps(pack_json))
			shutil.copyfile(os.path.join(os.getcwd(), 'blank.png'), os.path.join(output_folder, song_title, 'images', 'storymenu', song_id + '.png'))

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

		shutil.copyfile(os.path.join(infile, '..', sm_chart.metadata['music']), path_song)

		window["textProgress"].Update("All done!")
		window["progressBar"].UpdateBar(1, 1)
		window["sm_go"].Update(disabled=False)

	else:

		return False
	
	return True