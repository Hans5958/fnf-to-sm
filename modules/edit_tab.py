import json
import os
import PySimpleGUI as sg
from modules.core import fnf_to_sm, merge_tracks, SM_EXT, SSC_EXT, FNF_EXT

sg.theme("SystemDefault1")

col1_layout = [
	[sg.Text("Easy", size=(7,1)), sg.Input(key="edit_inputFileEasy"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit_fileBrowseEasy")],
	[sg.Text("Medium", size=(7,1)), sg.Input(key="edit_inputFileMedium", enable_events=True), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit_fileBrowseMedium", enable_events=True)],
	[sg.Text("Hard", size=(7,1)), sg.Input(key="edit_inputFileHard"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit_fileBrowseHard")],
	[sg.Text("Inst", size=(7,1)), sg.Input(key="edit_inputFileInst"), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key="edit_fileBrowseInst")],
	[sg.Text("Voices", size=(7,1)), sg.Input(key="edit_inputFileVoices"), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key="edit_fileBrowseVoices")],
	[sg.Button("Auto-Populate", key="edit_autoPopulate"), sg.Button("Reset", key="edit_reset")],
	[sg.Text("Output", size=(7,1)), sg.Input(os.getcwd(), key="edit_inputFolderOutput"), sg.FolderBrowse(key="edit_folderBrowse")],
	[
		sg.Text("Chart format"),
		sg.Radio("*.sm", group_id="edit2_format", enable_events=True, key="edit2_formatSm"), 
		sg.Radio("*.ssc", group_id="edit2_format", enable_events=True, key="edit2_formatSsc", default=True), 
	],
	# [sg.Text(size=(40,1), key="output1")],
	# [sg.In(), sg.FileBrowse(file_types=(("JSON Files", "*.json"),))],
	[sg.Button("Go", key="edit_go"), sg.Button("Exit", key="edit_exit")],
]

col2_layout = [
	[sg.Text("Title", size=(6,1)), sg.Input(key="edit_inputTitle")],
	[sg.Text("Subtitle", size=(6,1)), sg.Input(key="edit_inputSubtitle")],
	[sg.Text("Artist", size=(6,1)), sg.Input(key="edit_inputArtist")],
	[sg.Text("Charter", size=(6,1)), sg.Input(key="edit_inputCharter")],
	[sg.Text("Credit", size=(6,1)), sg.Input("fnf-to-sm", key="edit_inputCredit")],
	[sg.Text("Difficulty Value")],
	[
		sg.Text("SBG", size=(3,1)),
		sg.Input(2, key="edit_inputDiffSingleBeginner", size=(2,1)), 
		sg.Text("SEZ", size=(3,1)),
		sg.Input(4, key="edit_inputDiffSingleEasy", size=(2,1)), 
		sg.Text("SMD", size=(3,1)), 
		sg.Input(6, key="edit_inputDiffSingleMedium", size=(2,1)), 
		sg.Text("SHD", size=(3,1)),
		sg.Input(8, key="edit_inputDiffSingleHard", size=(2,1)),
		sg.Text("SCH", size=(3,1)), 
		sg.Input(10, key="edit_inputDiffSingleChallenge", size=(2,1)),
		sg.Text("SED", size=(3,1)), 
		sg.Input(12, key="edit_inputDiffSingleEdit", size=(2,1)),
	],
	[
		sg.Text("DEZ", size=(3,1)), 
		sg.Input(5, key="edit_inputDiffDoubleEasy", size=(2,1)),
		sg.Text("DMD", size=(3,1)), 
		sg.Input(7, key="edit_inputDiffDoubleMedium", size=(2,1)), 
		sg.Text("DHD", size=(3,1)),
		sg.Input(9, key="edit_inputDiffDoubleHard", size=(2,1)),
		sg.Text("CEZ", size=(3,1)), 
		sg.Input(4, key="edit_inputDiffCoupleEasy", size=(2,1)),
		sg.Text("CMD", size=(3,1)), 
		sg.Input(6, key="edit_inputDiffCoupleMedium", size=(2,1)),
		sg.Text("CHD", size=(3,1)),
		sg.Input(8, key="edit_inputDiffCoupleHard", size=(2,1)), 
	],
	[sg.Text("Banner File Name", size=(15,1)), sg.Input(key="edit_inputBannerFileName", size=(35, 1))],
	[sg.Text("BG File Name", size=(15,1)), sg.Input(key="edit_inputBGFileName", size=(35, 1))],
	[sg.Text("Folder Name", size=(15,1)), sg.Input(key="edit_inputSongFolderName", size=(35, 1))],
]

edit_layout = [[
	sg.Column(col1_layout),
	sg.Column(col2_layout),
]]

def edit_eventlistener(event: str, values, window): 

	song_name = values["edit_inputTitle"]
	song_folder_name = values["edit_inputSongFolderName"]

	if event == "edit_autoPopulate" or event == "edit_inputFileMedium":

		infile = values["edit_inputFileMedium"]
		override = event.startswith("autoPopulate")

		if os.path.isfile(infile):

			infile_name, infile_ext = os.path.splitext(infile)
			infile_dirname = os.path.dirname(infile_name)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				
				if values["edit_inputTitle"] == "" or override:
					window["edit_inputTitle"].Update(chart_json["song"]["song"])

				if values["edit_inputSongFolderName"] == "" or override:
					window["edit_inputSongFolderName"].Update(chart_json["song"]["song"])

			if values["edit_inputFileEasy"] == "" or override:
				infile_easy = infile_name + "-easy" + FNF_EXT
				if os.path.isfile(infile_easy):
					window["edit_inputFileEasy"].Update(infile_easy)

			if values["edit_inputFileHard"] == "" or override:
				infile_hard = infile_name + "-hard" + FNF_EXT
				if os.path.isfile(infile_hard):
					window["edit_inputFileHard"].Update(infile_hard)

			if values["edit_inputFileInst"] == "" or override:
				infile_inst = f'{infile_dirname.replace("data", "songs")}/Inst.ogg'
				if os.path.isfile(infile_inst):
					window["edit_inputFileInst"].Update(infile_inst)

			if values["edit_inputFileVoices"] == "" or override:
				infile_voices = f'{infile_dirname.replace("data", "songs")}/Voices.ogg'
				if os.path.isfile(infile_voices):
					window["edit_inputFileVoices"].Update(infile_voices)

	# if values["edit_inputCharter"] == "":
	# 	window["edit_inputCharter"].Update("fnf-to-sm")

	elif event == "edit_go":

		chart_jsons = []

		infile = values["edit_inputFileEasy"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Easy"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("double", values["edit_inputDiffDoubleEasy"]), 
					("couple", values["edit_inputDiffCoupleEasy"]), 
					("single-mixed", values["edit_inputDiffSingleEasy"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Beginner"
				chart_json["infile"] = infile
				chart_json["modes"] = [("single", values["edit_inputDiffSingleBeginner"])]
				chart_jsons.append(chart_json)

		infile = values["edit_inputFileMedium"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Medium"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("double", values["edit_inputDiffDoubleMedium"]), 
					("couple", values["edit_inputDiffCoupleMedium"]), 
					("single", values["edit_inputDiffSingleMedium"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Hard"
				chart_json["infile"] = infile
				chart_json["modes"] = [("single-mixed", values["edit_inputDiffSingleHard"])]
				chart_jsons.append(chart_json)

		infile = values["edit_inputFileHard"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Hard"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("double", values["edit_inputDiffDoubleHard"]), 
					("couple", values["edit_inputDiffCoupleHard"]), 
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Challenge"
				chart_json["infile"] = infile
				chart_json["modes"] = [("single", values["edit_inputDiffSingleChallenge"])]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Edit"
				chart_json["infile"] = infile
				chart_json["modes"] = [("single-mixed", values["edit_inputDiffSingleEdit"])]
				chart_jsons.append(chart_json)

		if values['edit2_formatSm']: format = 'sm'
		elif values['edit2_formatSsc']: format = 'ssc'

		if values["edit_inputFolderOutput"] == "":
			output_folder = os.getcwd()
		else:
			output_folder = values["edit_inputFolderOutput"]

		window["edit_go"].Update(disabled=True)
		window["progressBar"].UpdateBar(0, 1)
		window["textProgress"].Update("Converting FNF .json to .sm...")

		if values["edit_inputFileInst"] != "" and values["edit_inputFileVoices"] != "":
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

		if values["edit_inputFileInst"] != "" and values["edit_inputFileVoices"] != "":

			window["textProgress"].Update("Merging tracks...")

			def callback(window):
				window["textProgress"].Update("All done!")
				window["progressBar"].UpdateBar(1, 1)
				window["edit_go"].Update(disabled=False)

			merge_tracks(
				inst_track=values["edit_inputFileInst"],
				voices_track=values["edit_inputFileVoices"],
				song_name=values["edit_inputTitle"], 
				output_folder=output_folder,
				song_folder_name=values["edit_inputSongFolderName"],
				callback=callback,
				window=window
			)

		else:

			window["textProgress"].Update("All done!")
			window["progressBar"].UpdateBar(1, 1)
			window["edit_go"].Update(disabled=False)

	else:

		return False
	
	return True