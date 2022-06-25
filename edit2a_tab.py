import json
import os
import shutil
# import ffmpeg
import PySimpleGUI as sg
from core import fnf_to_sm, merge_tracks, SM_EXT, SSC_EXT, FNF_EXT

sg.theme("SystemDefault1")

col1_layout = [
	[sg.Text("Beginner", size=(7,1)), sg.Input(key="edit2a_inputFileBeginner"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit2a_fileBrowseBeginner")],
	[sg.Text("Easy", size=(7,1)), sg.Input(key="edit2a_inputFileEasy"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit2a_fileBrowseEasy")],
	[sg.Text("Medium", size=(7,1)), sg.Input(key="edit2a_inputFileMedium", enable_events=True), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit2a_fileBrowseMedium", enable_events=True)],
	[sg.Text("Hard", size=(7,1)), sg.Input(key="edit2a_inputFileHard"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit2a_fileBrowseHard")],
	[sg.Text("Challenge", size=(7,1)), sg.Input(key="edit2a_inputFileChallenge"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="edit2a_fileBrowseChallenge")],
	[sg.Text("Inst", size=(7,1)), sg.Input(key="edit2a_inputFileInst"), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key="edit2a_fileBrowseInst")],
	[sg.Text("Voices", size=(7,1)), sg.Input(key="edit2a_inputFileVoices"), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key="edit2a_fileBrowseVoices")],
	[sg.Button("Auto-Populate", key="edit2a_autoPopulate"), sg.Button("Reset", key="edit2a_reset")],
	[sg.Text("Output", size=(7,1)), sg.Input(os.getcwd(), key="edit2a_inputFolderOutput"), sg.FolderBrowse(key="folderBrowse")],
	[
		sg.Text("Chart format"),
		sg.Radio("*.sm", group_id="edit2_format", enable_events=True, key="edit2_formatSm"), 
		sg.Radio("*.ssc", group_id="edit2_format", enable_events=True, key="edit2_formatSsc", default=True), 
	],
	# [sg.Text(size=(40,1), key="output1")],
	# [sg.In(), sg.FileBrowse(file_types=(("JSON Files", "*.json"),))],
	[sg.Button("Go", key="edit2a_go"), sg.Button("Exit", key="edit2a_exit")],
]

col2_layout = [
	[sg.Text("Title", size=(6,1)), sg.Input(key="edit2a_inputTitle")],
	[sg.Text("Subtitle", size=(6,1)), sg.Input(key="edit2a_inputSubtitle")],
	[sg.Text("Artist", size=(6,1)), sg.Input(key="edit2a_inputArtist")],
	[sg.Text("Charter", size=(6,1)), sg.Input(key="edit2a_inputCharter")],
	[sg.Text("Credit", size=(6,1)), sg.Input("fnf-to-sm", key="edit2a_inputCredit")],
	[sg.Text("Difficulty Value")],
	[
		sg.Column([
			[sg.Text("")],
			[sg.Text("Single")],
			[sg.Text("Single Mixed")],
			[sg.Text("Double")],
			[sg.Text("Couple")], 
		]),
		sg.Column([
			[sg.Text("BG")],
			[sg.Input(0, key="edit2a_inputDiffSingleBeginner", size=(3,1))],
			[sg.Input(0, key="edit2a_inputDiffSingleMixedBeginner", size=(3,1))],
			[sg.Input(0, key="edit2a_inputDiffDoubleBeginner", size=(3,1))],
			[sg.Input(0, key="edit2a_inputDiffCoupleBeginner", size=(3,1))],
		]),
		sg.Column([
			[sg.Text("EZ")],
			[sg.Input(5, key="edit2a_inputDiffSingleEasy", size=(3,1))],
			[sg.Input(5, key="edit2a_inputDiffSingleMixedEasy", size=(3,1))],
			[sg.Input(5, key="edit2a_inputDiffDoubleEasy", size=(3,1))],
			[sg.Input(5, key="edit2a_inputDiffCoupleEasy", size=(3,1))],
		]),
		sg.Column([
			[sg.Text("MD")],
			[sg.Input(7, key="edit2a_inputDiffSingleMedium", size=(3,1))],
			[sg.Input(7, key="edit2a_inputDiffSingleMixedMedium", size=(3,1))],
			[sg.Input(7, key="edit2a_inputDiffDoubleMedium", size=(3,1))],
			[sg.Input(7, key="edit2a_inputDiffCoupleMedium", size=(3,1))],
		]),
		sg.Column([
			[sg.Text("HD")],
			[sg.Input(9, key="edit2a_inputDiffSingleHard", size=(3,1))],
			[sg.Input(9, key="edit2a_inputDiffSingleMixedHard", size=(3,1))],
			[sg.Input(9, key="edit2a_inputDiffDoubleHard", size=(3,1))],
			[sg.Input(9, key="edit2a_inputDiffCoupleHard", size=(3,1))],
		]),
		sg.Column([
			[sg.Text("CH")],
			[sg.Input(0, key="edit2a_inputDiffSingleChallenge", size=(3,1))],
			[sg.Input(0, key="edit2a_inputDiffSingleMixedChallenge", size=(3,1))],
			[sg.Input(0, key="edit2a_inputDiffDoubleChallenge", size=(3,1))],
			[sg.Input(0, key="edit2a_inputDiffCoupleChallenge", size=(3,1))],
		]),
	],
	[sg.Text("Banner File Name", size=(15,1)), sg.Input(key="edit2a_inputBannerFileName", size=(35, 1))],
	[sg.Text("BG File Name", size=(15,1)), sg.Input(key="edit2a_inputBGFileName", size=(35, 1))],
	[sg.Text("Folder Name", size=(15,1)), sg.Input(key="edit2a_inputSongFolderName", size=(35, 1))],
]

edit2a_layout = [[
	sg.Column(col1_layout),
	sg.Column(col2_layout),
]]

def edit2a_eventlistener(event: str, values, window): 

	song_name = values["edit2a_inputTitle"]
	song_folder_name = values["edit2a_inputSongFolderName"]

	if event == "edit2a_autoPopulate" or event == "edit2a_inputFileMedium":

		infile = values["edit2a_inputFileMedium"]
		override = event.startswith("autoPopulate")

		if os.path.isfile(infile):

			infile_name, infile_ext = os.path.splitext(infile)
			infile_dirname = os.path.dirname(infile_name)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				
				if song_name == "" or override:
					window["edit2a_inputTitle"].Update(chart_json["song"]["song"])

				if song_folder_name == "" or override:
					window["edit2a_inputSongFolderName"].Update(chart_json["song"]["song"])

			if values["edit2a_inputFileEasy"] == "" or override:
				infile_easy = infile_name + "-easy" + FNF_EXT
				if os.path.isfile(infile_easy):
					window["edit2a_inputFileEasy"].Update(infile_easy)

			if values["edit2a_inputFileHard"] == "" or override:
				infile_hard = infile_name + "-hard" + FNF_EXT
				if os.path.isfile(infile_hard):
					window["edit2a_inputFileHard"].Update(infile_hard)

			if values["edit2a_inputFileInst"] == "" or override:
				infile_inst = f'{infile_dirname.replace("data", "songs")}/Inst.ogg'
				if os.path.isfile(infile_inst):
					window["edit2a_inputFileInst"].Update(infile_inst)

			if values["edit2a_inputFileVoices"] == "" or override:
				infile_voices = f'{infile_dirname.replace("data", "songs")}/Voices.ogg'
				if os.path.isfile(infile_voices):
					window["edit2a_inputFileVoices"].Update(infile_voices)

	# if values["edit2a_inputCharter"] == "":
	# 	window["edit2a_inputCharter"].Update("fnf-to-sm")

	elif event == "edit2a_go":

		chart_jsons = []
		
		infile = values["edit2a_inputFileBeginner"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Beginner"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("single", values["edit2a_inputDiffSingleBeginner"]),
					("double", values["edit2a_inputDiffDoubleBeginner"]), 
					("couple", values["edit2a_inputDiffCoupleBeginner"]), 
					# ("routine", values["edit2a_inputDiffCoupleBeginner"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Edit"
				chart_json["infile"] = infile
				chart_json["charter"] = "Beginner Mixed"
				chart_json["modes"] = [("single-mixed", values["edit2a_inputDiffSingleMixedBeginner"])]
				chart_jsons.append(chart_json)

		infile = values["edit2a_inputFileEasy"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Easy"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("single", values["edit2a_inputDiffSingleEasy"]),
					("double", values["edit2a_inputDiffDoubleEasy"]), 
					("couple", values["edit2a_inputDiffCoupleEasy"]), 
					# ("routine", values["edit2a_inputDiffCoupleEasy"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Edit"
				chart_json["infile"] = infile
				chart_json["description"] = "Easy Mixed"
				chart_json["modes"] = [("single-mixed", values["edit2a_inputDiffSingleMixedEasy"])]
				chart_jsons.append(chart_json)

		infile = values["edit2a_inputFileMedium"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Medium"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("single", values["edit2a_inputDiffSingleMedium"]),
					("double", values["edit2a_inputDiffDoubleMedium"]), 
					("couple", values["edit2a_inputDiffCoupleMedium"]), 
					# ("routine", values["edit2a_inputDiffCoupleMedium"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Edit"
				chart_json["infile"] = infile
				chart_json["description"] = "Medium Mixed"
				chart_json["modes"] = [("single-mixed", values["edit2a_inputDiffSingleMixedMedium"])]
				chart_jsons.append(chart_json)

		infile = values["edit2a_inputFileHard"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Hard"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("single", values["edit2a_inputDiffSingleHard"]),
					("double", values["edit2a_inputDiffDoubleHard"]), 
					("couple", values["edit2a_inputDiffCoupleHard"]), 
					# ("routine", values["edit2a_inputDiffCoupleHard"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Edit"
				chart_json["infile"] = infile
				chart_json["description"] = "Hard Mixed"
				chart_json["modes"] = [("single-mixed", values["edit2a_inputDiffSingleMixedHard"])]
				chart_jsons.append(chart_json)

		infile = values["edit2a_inputFileChallenge"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Challenge"
				chart_json["infile"] = infile
				chart_json["modes"] = [
					("single", values["edit2a_inputDiffSingleChallenge"]),
					("double", values["edit2a_inputDiffDoubleChallenge"]), 
					("couple", values["edit2a_inputDiffCoupleChallenge"]), 
					# ("routine", values["edit2a_inputDiffCoupleChallenge"])
				]
				chart_jsons.append(chart_json)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Edit"
				chart_json["infile"] = infile
				chart_json["charter"] = "Challenge Mixed"
				chart_json["modes"] = [("single-mixed", values["edit2a_inputDiffSingleMixedChallenge"])]
				chart_jsons.append(chart_json)

		if values['edit2_formatSm']: format = 'sm'
		elif values['edit2_formatSsc']: format = 'ssc'

		if values["edit2a_inputFolderOutput"] == "":
			output_folder = os.getcwd()
		else:
			output_folder = values["edit2a_inputFolderOutput"]

		window["edit2a_go"].Update(disabled=True)
		window["progressBar"].UpdateBar(0, 1)
		window["textProgress"].Update("Converting FNF .json to .sm...")

		if values["edit2a_inputFileInst"] != "" and values["edit2a_inputFileVoices"] != "":
			initial_steps = 1
		else:
			initial_steps = 0

		chartfile = fnf_to_sm(
			chart_jsons=chart_jsons, 
			window=window,
			metadata={
				'name': song_name,
				'subtitle': values["edit2a_inputSubtitle"],
				'artist': values["edit2a_inputArtist"], 
				'charter': values["edit2a_inputCharter"], 
				'credit': values["edit2a_inputCredit"], 
				'banner': values["edit2a_inputBannerFileName"],
				'background': values["edit2a_inputBGFileName"],
			},
			initial_steps=initial_steps,
			format=format
		)

		os.makedirs(os.path.join(output_folder, song_folder_name), exist_ok=True)
		with open(f"{os.path.join(output_folder, song_folder_name, song_name)}.{format}", "w") as outfile:
			outfile.write(chartfile)

		if values["edit2a_inputFileInst"] != "" and values["edit2a_inputFileVoices"] != "":

			window["textProgress"].Update("Merging tracks...")

			def callback(window):
				window["textProgress"].Update("All done!")
				window["progressBar"].UpdateBar(1, 1)
				window["edit2a_go"].Update(disabled=False)

			merge_tracks(
				inst_track=values["edit2a_inputFileInst"],
				voices_track=values["edit2a_inputFileVoices"],
				song_name=song_name, 
				output_folder=output_folder,
				song_folder_name=song_folder_name,
				callback=callback,
				window=window
			)

		elif values["edit2a_inputFileInst"] != "" or values["edit2a_inputFileVoices"] != "":

			print(values["edit2a_inputFileInst"] + values["edit2a_inputFileVoices"])
			print(os.path.join(output_folder, song_folder_name, song_name))
			shutil.copyfile(values["edit2a_inputFileInst"] + values["edit2a_inputFileVoices"], os.path.join(output_folder, song_folder_name, song_name) + '.ogg')
			window["textProgress"].Update("All done!")
			window["progressBar"].UpdateBar(1, 1)
			window["edit2a_go"].Update(disabled=False)

		else:

			window["textProgress"].Update("All done!")
			window["progressBar"].UpdateBar(1, 1)
			window["edit2a_go"].Update(disabled=False)

	else:

		return False
	
	return True