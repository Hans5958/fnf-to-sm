import json
import os
# import ffmpeg
import PySimpleGUI as sg
from core import fnf_to_sm, merge_tracks, SM_EXT, SSC_EXT, FNF_EXT

sg.theme("SystemDefault1")

col1_layout = [
	[sg.Text("Beginner", size=(7,1)), sg.Input(key="legacy_inputFileBeginner"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="legacy_fileBrowseBeginner")],
	[sg.Text("Easy", size=(7,1)), sg.Input(key="legacy_inputFileEasy"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="legacy_fileBrowseEasy")],
	[sg.Text("Medium", size=(7,1)), sg.Input(key="legacy_inputFileMedium", enable_events=True), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="legacy_fileBrowseMedium", enable_events=True)],
	[sg.Text("Hard", size=(7,1)), sg.Input(key="legacy_inputFileHard"), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="legacy_fileBrowseHard")],
	[sg.Text("Challenge", size=(7,1)), sg.Input(key="legacy_inputFileChallenge", disabled=True), sg.FileBrowse(file_types=(("JSON Files", "*.json"),), key="legacy_fileBrowseChallenge", disabled=True)],
	[sg.Text("Inst", size=(7,1)), sg.Input(key="legacy_inputFileInst"), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key="legacy_fileBrowseInst")],
	[sg.Text("Voices", size=(7,1)), sg.Input(key="legacy_inputFileVoices"), sg.FileBrowse(file_types=(("OGG Files", "*.ogg"),), key="legacy_fileBrowseVoices")],
	[sg.Button("Auto-Populate", key="legacy_autoPopulate"), sg.Button("Reset", key="legacy_reset")],
	[sg.Text("Output", size=(7,1)), sg.Input(os.getcwd(), key="legacy_inputFolderOutput"), sg.FolderBrowse(key="legacy_folderBrowse")],
	[
		sg.Text("Chart format"),
		sg.Radio("*.sm", group_id="edit2_format", enable_events=True, key="edit2_formatSm"), 
		sg.Radio("*.ssc", group_id="edit2_format", enable_events=True, key="edit2_formatSsc", default=True), 
	],
	# [sg.Text(size=(40,1), key="output1")],
	# [sg.In(), sg.FileBrowse(file_types=(("JSON Files", "*.json"),))],
	[sg.Button("Go", key="legacy_go"), sg.Button("Exit", key="legacy_exit")],
]

col2_layout = [
	[sg.Text("Title", size=(6,1)), sg.Input(key="legacy_inputTitle")],
	[sg.Text("Subtitle", size=(6,1)), sg.Input(key="legacy_inputSubtitle")],
	[sg.Text("Artist", size=(6,1)), sg.Input(key="legacy_inputArtist")],
	[sg.Text("Charter", size=(6,1)), sg.Input(key="legacy_inputCharter")],
	[sg.Text("Credit", size=(6,1)), sg.Input("fnf-to-sm", key="legacy_inputCredit")],
	[sg.Text("Difficulty Value")],
	[
		sg.Text("SBG", size=(4,1)),
		sg.Input(2, key="legacy_inputDiffSingleBeginner", size=(2,1)), 
		sg.Text("SEZ", size=(4,1)),
		sg.Input(4, key="legacy_inputDiffSingleEasy", size=(2,1)), 
		sg.Text("SMD", size=(4,1)), 
		sg.Input(6, key="legacy_inputDiffSingleMedium", size=(2,1)), 
		sg.Text("SHD", size=(4,1)),
		sg.Input(8, key="legacy_inputDiffSingleHard", size=(2,1)),
		sg.Text("SCH", size=(4,1)), 
		sg.Input(10, key="legacy_inputDiffSingleChallenge", size=(2,1)),
	],
	[
		sg.Text("DBG", size=(4,1)),
		sg.Input(3, key="legacy_inputDiffDoubleBeginner", size=(2,1)), 
		sg.Text("DEZ", size=(4,1)), 
		sg.Input(3, key="legacy_inputDiffDoubleEasy", size=(2,1)), 
		sg.Text("DMD", size=(4,1)), 
		sg.Input(7, key="legacy_inputDiffDoubleMedium", size=(2,1)), 
		sg.Text("DHD", size=(4,1)),
		sg.Input(9, key="legacy_inputDiffDoubleHard", size=(2,1)),
		sg.Text("DCH", size=(4,1)), 
		sg.Input(11, disabled=True, key="legacy_inputDiffDoubleChallenge", size=(2,1)),
	],
	[sg.Text("Derivate mixed Challenge parts from...")],
	[
		sg.Radio("Beginner", group_id="legacy_derivateMixedFrom", enable_events=True, key="legacy_radioDerivateMixedFromBeginner"), 
		sg.Radio("Easy", group_id="legacy_derivateMixedFrom", enable_events=True, key="legacy_radioDerivateMixedFromEasy"), 
		sg.Radio("Medium", group_id="legacy_derivateMixedFrom", enable_events=True, key="legacy_radioDerivateMixedFromMedium"), 
		sg.Radio("Hard", default=True, group_id="legacy_derivateMixedFrom", enable_events=True, key="legacy_radioDerivateMixedFromHard"), 
		sg.Radio("None", group_id="legacy_derivateMixedFrom", enable_events=True, key="legacy_radioDerivateMixedFromNone")
	],
	[sg.Text("Banner File Name", size=(15,1)), sg.Input(key="legacy_inputBannerFileName", size=(35, 1))],
	[sg.Text("BG File Name", size=(15,1)), sg.Input(key="legacy_inputBGFileName", size=(35, 1))],
	[sg.Text("Folder Name", size=(15,1)), sg.Input(key="legacy_inputSongFolderName", size=(35, 1))],
]

legacy_layout = [[
	sg.Column(col1_layout),
	sg.Column(col2_layout),
]]

def legacy_eventlistener(event: str, values, window):

	song_name = values["edit2_inputTitle"]
	song_folder_name = values["edit2_inputSongFolderName"]

	if event.startswith("legacy_radioDerivateMixedFrom"):
		if event == "legacy_radioDerivateMixedFromNone":
			window["legacy_inputFileChallenge"].Update(disabled=False)
			window["legacy_fileBrowseChallenge"].Update(disabled=False)
			window["legacy_inputDiffDoubleChallenge"].Update(disabled=False)
		else:
			window["legacy_inputFileChallenge"].Update(disabled=True)
			window["legacy_fileBrowseChallenge"].Update(disabled=True)		
			window["legacy_inputDiffDoubleChallenge"].Update(disabled=True)		

	elif event == "legacy_autoPopulate" or event == "legacy_inputFileMedium":

		infile = values["legacy_inputFileMedium"]
		override = event.startswith("autoPopulate")

		if os.path.isfile(infile):

			infile_name, infile_ext = os.path.splitext(infile)
			infile_dirname = os.path.dirname(infile_name)

			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				
				if values["legacy_inputTitle"] == "" or override:
					window["legacy_inputTitle"].Update(chart_json["song"]["song"])

				if values["legacy_inputSongFolderName"] == "" or override:
					window["legacy_inputSongFolderName"].Update(chart_json["song"]["song"])

			if values["legacy_inputFileEasy"] == "" or override:
				infile_easy = infile_name + "-easy" + FNF_EXT
				if os.path.isfile(infile_easy):
					window["legacy_inputFileEasy"].Update(infile_easy)

			if values["legacy_inputFileHard"] == "" or override:
				infile_hard = infile_name + "-hard" + FNF_EXT
				if os.path.isfile(infile_hard):
					window["legacy_inputFileHard"].Update(infile_hard)

			if values["legacy_inputFileInst"] == "" or override:
				infile_inst = f'{infile_dirname.replace("data", "songs")}/Inst.ogg'
				if os.path.isfile(infile_inst):
					window["legacy_inputFileInst"].Update(infile_inst)

			if values["legacy_inputFileVoices"] == "" or override:
				infile_voices = f'{infile_dirname.replace("data", "songs")}/Voices.ogg'
				if os.path.isfile(infile_voices):
					window["legacy_inputFileVoices"].Update(infile_voices)

	elif event == "legacy_go":

		chart_jsons = []

		infile = values["legacy_inputFileBeginner"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Beginner"
				chart_json["infile"] = infile
				chart_json["modes"] = (("single", values["legacy_inputDiffSingleBeginner"]), ("double", values["legacy_inputDiffDoubleBeginner"]))
				if values["legacy_radioDerivateMixedFromBeginner"]:
					chart_json["modes"].append(("single-challenge", values["legacy_inputDiffSingleChallenge"]))
				chart_jsons.append(chart_json)

		infile = values["legacy_inputFileEasy"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Easy"
				chart_json["infile"] = infile
				chart_json["modes"] = [("single", values["legacy_inputDiffSingleEasy"]), ("double", values["legacy_inputDiffDoubleEasy"])]
				if values["legacy_radioDerivateMixedFromEasy"]:
					chart_json["modes"].append(("single-challenge", values["legacy_inputDiffSingleChallenge"]))
				chart_jsons.append(chart_json)

		infile = values["legacy_inputFileMedium"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Medium"
				chart_json["infile"] = infile
				chart_json["modes"] = [("single", values["legacy_inputDiffSingleMedium"]), ("double", values["legacy_inputDiffDoubleMedium"])]
				if values["legacy_radioDerivateMixedFromMedium"]:
					chart_json["modes"].append(("single-challenge", values["legacy_inputDiffSingleChallenge"]))
				chart_jsons.append(chart_json)

		infile = values["legacy_inputFileHard"]
		if infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Hard"
				chart_json["infile"] = infile
				chart_json["modes"] = [("single", values["legacy_inputDiffSingleHard"]), ("double", values["legacy_inputDiffDoubleHard"])]
				if values["legacy_radioDerivateMixedFromHard"]:
					chart_json["modes"].append(("single-challenge", values["legacy_inputDiffSingleChallenge"]))
				chart_jsons.append(chart_json)

		infile = values["legacy_inputFileChallenge"]
		if values["legacy_radioDerivateMixedFromNone"] and infile != "" and os.path.isfile(infile):
			with open(infile, "r") as chartfile:
				chart_json = json.loads(chartfile.read().strip("\0"))
				chart_json["diff"] = "Challenge"
				chart_json["infile"] = infile
				chart_json["modes"] = (("single", values["legacy_inputDiffSingleChallenge"]), ("double", values["legacy_inputDiffDoubleChallenge"]))
				chart_jsons.append(chart_json)

		if values['edit2_formatSm']: format = 'sm'
		elif values['edit2_formatSsc']: format = 'ssc'

		if values["legacy_inputFolderOutput"] == "":
			output_folder = os.getcwd()
		else:
			output_folder = values["legacy_inputFolderOutput"]

		window["legacy_go"].Update(disabled=True)
		window["progressBar"].UpdateBar(0, 1)
		window["textProgress"].Update("Converting FNF .json to .sm...")

		if values["legacy_inputFileInst"] != "" and values["legacy_inputFileVoices"] != "":
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
			
		if values["legacy_inputFileInst"] != "" and values["legacy_inputFileVoices"] != "":

			window["textProgress"].Update("Merging tracks...")

			def callback(window):
				window["textProgress"].Update("All done!")
				window["progressBar"].UpdateBar(1, 1)
				window["legacy_go"].Update(disabled=False)

			merge_tracks(
				inst_track=values["legacy_inputFileInst"],
				voices_track=values["legacy_inputFileVoices"],
				song_name=values["legacy_inputTitle"], 
				output_folder=output_folder,
				song_folder_name=values["legacy_inputSongFolderName"],
				callback=callback,
				window=window
			)

		else:

			window["textProgress"].Update("All done!")
			window["progressBar"].UpdateBar(1, 1)
			window["legacy_go"].Update(disabled=False)
	
	else:
		
		return False

	return True