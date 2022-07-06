import json
import os
import shutil
import PySimpleGUI as sg
from modules.core import fnf_to_sm, merge_tracks, SM_EXT, SSC_EXT, FNF_EXT

sg.theme("SystemDefault1")

col1_layout = [
	[sg.Text("Easy", size=(7,1)), sg.Input(key="edit2_inputFileEasy"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit2_fileBrowseEasy")],
	[sg.Text("Medium", size=(7,1)), sg.Input(key="edit2_inputFileMedium", enable_events=True), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit2_fileBrowseMedium", enable_events=True)],
	[sg.Text("Hard", size=(7,1)), sg.Input(key="edit2_inputFileHard"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit2_fileBrowseHard")],
	[sg.Text("Inst", size=(7,1)), sg.Input(key="edit2_inputFileInst"), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key="edit2_fileBrowseInst")],
	[sg.Text("Voices", size=(7,1)), sg.Input(key="edit2_inputFileVoices"), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key="edit2_fileBrowseVoices")],
	[sg.Button("Auto-Populate", key="edit2_autoPopulate"), sg.Button("Reset", key="edit2_reset")],
	[sg.Text("Output", size=(7,1)), sg.Input(os.getcwd(), key="edit2_inputFolderOutput"), sg.FolderBrowse(key="folderBrowse")],
	[
		sg.Text("Chart format"),
		sg.Radio("*.sm", group_id="edit2_format", enable_events=True, key="edit2_formatSm", default=True), 
		sg.Radio("*.ssc", group_id="edit2_format", enable_events=True, key="edit2_formatSsc"), 
	],
	# [sg.Text(size=(40,1), key="output1")],
	# [sg.In(), sg.FileBrowse(file_types=(("JSON Files", "*.json"),))],
	[sg.Button("Go", key="edit2_go"), sg.Button("Exit", key="edit2_exit")],
]

col2_layout = [
	[sg.Text("Title", size=(6,1)), sg.Input(key="edit2_inputTitle")],
	[sg.Text("Subtitle", size=(6,1)), sg.Input(key="edit2_inputSubtitle")],
	[sg.Text("Artist", size=(6,1)), sg.Input(key="edit2_inputArtist")],
	[sg.Text("Charter", size=(6,1)), sg.Input(key="edit2_inputCharter")],
	[sg.Text("Credit", size=(6,1)), sg.Input("fnf-to-sm", key="edit2_inputCredit")],
	[sg.Text("Difficulty Value")],
	[
		sg.Column([
			[sg.Text("")],
			[sg.Text("Single")],
			[sg.Text("Double")],
		]),
		sg.Column([
			[sg.Text("Easy")],
			[sg.Input(5, key="edit2_inputDiffSingleEasy", size=(5,1))],
			[sg.Input(5, key="edit2_inputDiffDoubleEasy", size=(5,1))],
		]),
		sg.Column([
			[sg.Text("Med")],
			[sg.Input(7, key="edit2_inputDiffSingleMedium", size=(5,1))],
			[sg.Input(7, key="edit2_inputDiffDoubleMedium", size=(5,1))],
		]),
		sg.Column([
			[sg.Text("Hard")],
			[sg.Input(9, key="edit2_inputDiffSingleHard", size=(5,1))],
			[sg.Input(9, key="edit2_inputDiffDoubleHard", size=(5,1))],
		]),
	],
	[sg.Text("Banner File Name", size=(15,1)), sg.Input(key="edit2_inputBannerFileName", size=(35, 1))],
	[sg.Text("BG File Name", size=(15,1)), sg.Input(key="edit2_inputBGFileName", size=(35, 1))],
	[sg.Text("Folder Name", size=(15,1)), sg.Input(key="edit2_inputSongFolderName", size=(35, 1))],
]

edit2_layout = [[
	sg.Column(col1_layout),
	sg.Column(col2_layout),
]]

def edit2_eventlistener(event: str, values, window): 

	song_name = values["edit2_inputTitle"]
	song_folder_name = values["edit2_inputSongFolderName"]

	if event == "edit2_autoPopulate" or event == "edit2_inputFileMedium":

		infile = values["edit2_inputFileMedium"]
		override = event.startswith("autoPopulate")

		if os.path.isfile(infile):

			infile_name, infile_ext = os.path.splitext(infile)
			infile_dirname = os.path.dirname(infile_name)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				
				if song_name == "" or override:
					window["edit2_inputTitle"].Update(chart_json["song"]["song"])

				if song_folder_name == "" or override:
					window["edit2_inputSongFolderName"].Update(chart_json["song"]["song"])

			if values["edit2_inputFileEasy"] == "" or override:
				infile_easy = infile_name + "-easy" + FNF_EXT
				if os.path.isfile(infile_easy):
					window["edit2_inputFileEasy"].Update(infile_easy)

			if values["edit2_inputFileHard"] == "" or override:
				infile_hard = infile_name + "-hard" + FNF_EXT
				if os.path.isfile(infile_hard):
					window["edit2_inputFileHard"].Update(infile_hard)

			if values["edit2_inputFileInst"] == "" or override:
				infile_inst = f'{infile_dirname.replace("data", "songs")}/Inst.ogg'
				if os.path.isfile(infile_inst):
					window["edit2_inputFileInst"].Update(infile_inst)

			if values["edit2_inputFileVoices"] == "" or override:
				infile_voices = f'{infile_dirname.replace("data", "songs")}/Voices.ogg'
				if os.path.isfile(infile_voices):
					window["edit2_inputFileVoices"].Update(infile_voices)

	# if values["edit2_inputCharter"] == "":
	# 	window["edit2_inputCharter"].Update("fnf-to-sm")

	elif event == "edit2_go":

		chart_jsons = []
		
		infile = values["edit2_inputFileEasy"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Easy"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("single", values["edit2_inputDiffSingleEasy"]),
					("double", values["edit2_inputDiffDoubleEasy"]), 
					("couple", values["edit2_inputDiffSingleEasy"]), 
					# ("routine", values["edit2_inputDiffSingleEasy"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Edit"
				chart_json["infile"] = infile
				chart_json["description"] = "Easy Mixed"
				chart_json["modes"] = [("single-mixed", values["edit2_inputDiffSingleEasy"])]
				chart_jsons.append(chart_json)

		infile = values["edit2_inputFileMedium"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Medium"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("single", values["edit2_inputDiffSingleMedium"]),
					("double", values["edit2_inputDiffDoubleMedium"]), 
					("couple", values["edit2_inputDiffSingleMedium"]), 
					# ("routine", values["edit2_inputDiffSingleMedium"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Edit"
				chart_json["infile"] = infile
				chart_json["description"] = "Medium Mixed"
				chart_json["modes"] = [("single-mixed", values["edit2_inputDiffSingleMedium"])]
				chart_jsons.append(chart_json)

		infile = values["edit2_inputFileHard"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Hard"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("single", values["edit2_inputDiffSingleHard"]),
					("double", values["edit2_inputDiffDoubleHard"]), 
					("couple", values["edit2_inputDiffSingleHard"]), 
					# ("routine", values["edit2_inputDiffSingleHard"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Edit"
				chart_json["infile"] = infile
				chart_json["description"] = "Hard Mixed"
				chart_json["modes"] = [("single-mixed", values["edit2_inputDiffSingleHard"])]
				chart_jsons.append(chart_json)

		if values['edit2_formatSm']: format = 'sm'
		elif values['edit2_formatSsc']: format = 'ssc'

		if values["edit2_inputFolderOutput"] == "":
			output_folder = os.getcwd()
		else:
			output_folder = values["edit2_inputFolderOutput"]

		window["edit2_go"].Update(disabled=True)
		window["progressBar"].UpdateBar(0, 1)
		window["textProgress"].Update("Converting FNF .json to .sm...")

		if values["edit2_inputFileInst"] != "" and values["edit2_inputFileVoices"] != "":
			initial_steps = 1
		else:
			initial_steps = 0
			
		chartfile = fnf_to_sm(
			chart_jsons=chart_jsons, 
			window=window,
			metadata={
				'name': song_name,
				'subtitle': values["edit2_inputSubtitle"],
				'artist': values["edit2_inputArtist"], 
				'charter': values["edit2_inputCharter"], 
				'credit': values["edit2_inputCredit"], 
				'banner': values["edit2_inputBannerFileName"],
				'background': values["edit2_inputBGFileName"],
			},
			initial_steps=initial_steps,
			format=format
		)

		os.makedirs(os.path.join(output_folder, song_folder_name), exist_ok=True)
		with open(f"{os.path.join(output_folder, song_folder_name, song_name)}.{format}", "w") as outfile:
			outfile.write(chartfile)

		if values["edit2_inputFileInst"] != "" and values["edit2_inputFileVoices"] != "":

			window["textProgress"].Update("Merging tracks...")

			def callback(window):
				window["textProgress"].Update("All done!")
				window["progressBar"].UpdateBar(1, 1)
				window["edit2_go"].Update(disabled=False)

			merge_tracks(
				inst_track=values["edit2_inputFileInst"],
				voices_track=values["edit2_inputFileVoices"],
				song_name=song_name, 
				output_folder=output_folder,
				song_folder_name=song_folder_name,
				callback=callback,
				window=window
			)

		elif values["edit2_inputFileInst"] != "" or values["edit2_inputFileVoices"] != "":

			print(values["edit2_inputFileInst"] + values["edit2_inputFileVoices"])
			print(os.path.join(output_folder, song_folder_name, song_name))
			shutil.copyfile(values["edit2_inputFileInst"] + values["edit2_inputFileVoices"], os.path.join(output_folder, song_folder_name, song_name) + '.ogg')
			window["textProgress"].Update("All done!")
			window["progressBar"].UpdateBar(1, 1)
			window["edit2_go"].Update(disabled=False)

		else:

			window["textProgress"].Update("All done!")
			window["progressBar"].UpdateBar(1, 1)
			window["edit2_go"].Update(disabled=False)

	else:

		return False
	
	return True