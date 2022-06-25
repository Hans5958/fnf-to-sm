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

from io import TextIOWrapper
import re
import json
import math
import os
import subprocess
# import ffmpeg
import threading

SM_EXT = ".sm"
SSC_EXT = ".ssc"
FNF_EXT = ".json"

# stepmania editor's default note precision is 1/192
MEASURE_TICKS = 192
BEAT_TICKS = 48
# fnf step = 1/16 note
STEP_TICKS = 12

NUM_COLUMNS_DOUBLE = 8
NUM_COLUMNS_SINGLE = 4

NOTES_RE = re.compile("^[\\dM][\\dM][\\dM][\\dM]$")

# borrowed from my Sharktooth code
class TempoMarker:
	def __init__(self, bpm, tick_pos, time_pos):
		self.bpm = float(bpm)
		self.tick_pos = tick_pos
		self.time_pos = time_pos

	def getBPM(self):
		return self.bpm

	def getTick(self):
		return self.tick_pos
		
	def getTime(self):
		return self.time_pos
	
	def timeToTick(self, note_time):
		return int(round(self.tick_pos + (float(note_time) - self.time_pos) * MEASURE_TICKS * self.bpm / 240000))
		
	def tickToTime(self, note_tick):
		return self.time_pos + (float(note_tick) - self.tick_pos) / MEASURE_TICKS * 240000 / self.bpm

# compute the maximum note index step per measure
def measure_gcd(num_set, MEASURE_TICKS):
	d = MEASURE_TICKS
	for x in num_set:
		d = math.gcd(d, x)
		if d == 1:
			return d
	return d;

tempomarkers = []

# helper functions for handling global tempomarkers 
def timeToTick(timestamp):
	for i in range(len(tempomarkers)):
		if i == len(tempomarkers) - 1 or tempomarkers[i+1].getTime() > timestamp:
			return tempomarkers[i].timeToTick(timestamp)
	return 0
			
def tickToTime(tick):
	for i in range(len(tempomarkers)):
		if i == len(tempomarkers) - 1 or tempomarkers[i+1].getTick() > tick:
			return tempomarkers[i].tickToTime(tick)
	return 0.0

def tickToBPM(tick):
	for i in range(len(tempomarkers)):
		if i == len(tempomarkers) - 1 or tempomarkers[i+1].getTick() > tick:
			return tempomarkers[i].getBPM()
	return 0.0

def fnf_to_sm(
	chart_jsons, 
	window, 
	song_name, 
	song_artist, 
	song_charter, 
	song_credit, 
	song_subtitle, 
	song_banner_file_name,
	song_bg_file_name,
	initial_steps
):
	
	# for each fnf difficulty
	sm_header = ''
	sm_notes = ''

	steps_to_make = initial_steps
	steps_made = 0

	for chart_json in chart_jsons:

		for mode in chart_json["modes"]:

			steps_to_make += 1

	for chart_json in chart_jsons:

		song_notes = chart_json["song"]["notes"]
		infile = chart_json["infile"]
		num_sections = len(song_notes)
		# build sm header if it doesn't already exist
		if len(sm_header) == 0:
			song_bpm = chart_json["song"]["bpm"]
			
			print("Converting {} to {}.sm".format(infile, song_name))

			# build tempomap
			bpms = "#BPMS:"
			current_bpm = None
			current_tick = 0
			current_time = 0.0
			for i in range(num_sections):
				section = song_notes[i]
									
				if "changeBPM" in section and section["changeBPM"] == True:
					section_bpm = float(section["bpm"])
					if not section_bpm:
						section_bpm = song_bpm
				elif current_bpm == None:
					section_bpm = song_bpm
				else:
					section_bpm = current_bpm
					
				if section_bpm != current_bpm:
					tempomarkers.append(TempoMarker(section_bpm, current_tick, current_time))
					bpms += "{}={},".format(i*4, section_bpm)
					current_bpm = section_bpm


				# each step is 1/16
				section_num_steps = section["lengthInSteps"]
				# default measure length = 192
				section_length = STEP_TICKS * section_num_steps
				time_in_section = 15000.0 * section_num_steps / current_bpm

				current_time += time_in_section
				current_tick += section_length
				
				print(current_time)

			# add semicolon to end of BPM header entry
			bpms = bpms[:-1] + ";\n"

			# write .sm header
			sm_header = "#TITLE:{};\n".format(song_name)
			sm_header += "#SUBTITLE:{};\n".format(song_subtitle)
			sm_header += "#ARTIST:{};\n".format(song_artist)
			sm_header += "#CREDIT:{};\n".format(song_credit)
			sm_header += "#MUSIC:{}.ogg;\n".format(song_name)
			sm_header += "#BANNER:{};\n".format(song_banner_file_name)
			sm_header += "#BACKGROUND:{};\n".format(song_bg_file_name)
			sm_header += bpms

		notes = {}
		notes_merged = {}
		last_note = 0
		last_note_challenge = 0

		# convert note timestamps to ticks
		for i in range(num_sections):
			section = song_notes[i]
			section_notes = section["sectionNotes"]
			for section_note in section_notes:		
				tick = timeToTick(section_note[0])
				if not (0 <= section_note[1] <= 7) or not (isinstance(section_note[1], float) or isinstance(section_note[1], int)) or not (isinstance(section_note[2], float) or isinstance(section_note[2], int)):
					continue
				note = section_note[1]
				note_challenge = section_note[1]
				if section["mustHitSection"]:
					note = (note + 4) % 8
				note = int(note)
				note_challenge = int(note_challenge)
				length = section_note[2]
				
				# Initialize a note for this tick position
				if tick not in notes:
					notes[tick] = [0]*NUM_COLUMNS_DOUBLE
					notes_merged[tick] = [0]*NUM_COLUMNS_DOUBLE

				if length == 0:
					notes[tick][note] = 1
					#print(notes_challenge[tick], note_challenge)
					notes_merged[tick][note_challenge] = 1
				else:
					notes[tick][note] = 2
					notes_merged[tick][note_challenge] = 2
					# 3 is "long note toggle off", so we need to set it after a 2
					long_end = timeToTick(section_note[0] + section_note[2])
					if long_end not in notes:
						notes[long_end] = [0]*NUM_COLUMNS_DOUBLE
					if long_end not in notes_merged:
						notes_merged[long_end] = [0]*NUM_COLUMNS_DOUBLE
					notes[long_end][note] = 3
					notes_merged[long_end][note_challenge] = 3
					if last_note < long_end:
						last_note = long_end
					if last_note_challenge < long_end:
						last_note_challenge = long_end

				if last_note <= tick:
					last_note = tick + 1
				if last_note_challenge <= tick:
					last_note_challenge = tick + 1


		if len(notes) > 0:

			for mode_dict in chart_json["modes"]:

				mode, diff_value = mode_dict

				# write chart & difficulty info
				sm_notes += "\n"
				sm_notes += "#NOTES:\n"
				if mode.startswith("single"):
					sm_notes += "	  dance-single:\n"
				else:
					sm_notes += "	  dance-{}:\n".format(mode)
				if "charter" in chart_json:
					sm_notes += "	  {}:\n".format(chart_json["charter"])
				else:
					sm_notes += "	  {}:\n".format(song_charter)
				if mode == "single-challenge":
					sm_notes += "	  Challenge:\n"
				else:
					sm_notes += "	  {}:\n".format(chart_json["diff"]) # e.g. Challenge:
				sm_notes += "	  {}:\n".format(diff_value)
				sm_notes += "	  :\n" # empty groove radar

				# ensure the last measure has the correct number of lines
				if last_note % MEASURE_TICKS != 0:
					last_note += MEASURE_TICKS - (last_note % MEASURE_TICKS)

				# add notes for each measure
				for measureStart in range(0, last_note, MEASURE_TICKS):
					measureEnd = measureStart + MEASURE_TICKS
					valid_indexes = set()
					for i in range(measureStart, measureEnd):
						if i in notes:
							valid_indexes.add(i - measureStart)

					noteStep = measure_gcd(valid_indexes, MEASURE_TICKS)

					if mode == "single":
						for i in range(measureStart, measureEnd, noteStep):
							if i not in notes:
								sm_notes += '0'*NUM_COLUMNS_SINGLE + '\n'
							else:
								i2 = 0
								for digit in notes[i]:
									if i2 < 4:
										i2 += 1
										continue
									sm_notes += str(digit)
								sm_notes += '\n'
					elif mode == "double" or mode == "couple" or mode == "routine":
						for i in range(measureStart, measureEnd, noteStep):
							if i not in notes:
								sm_notes += '0'*NUM_COLUMNS_DOUBLE + '\n'
							else:
								for digit in notes[i]:
									sm_notes += str(digit)
								sm_notes += '\n'
					elif mode == "single-challenge" or mode == 'single-mixed':
						for i in range(measureStart, measureEnd, noteStep):
							if i not in notes_merged:
								sm_notes += '0'*NUM_COLUMNS_SINGLE + '\n'
							else:
								i2 = 0
								for digit in notes_merged[i]:
									if i2 < 4:
										i2 += 1
										sm_notes += str(digit)
								sm_notes += '\n'

					if measureStart + MEASURE_TICKS == last_note:
						sm_notes += ";\n"
					else:
						sm_notes += ',\n'

				steps_made += 1
				window['progressBar'].UpdateBar(steps_made, steps_to_make)

	# output simfile
	return sm_header + sm_notes

def merge_tracks(
	inst_track, 
	voices_track, 
	output_folder, 
	song_name, 
	song_folder_name,
	window,
	callback
):
	os.makedirs(os.path.join(output_folder, song_folder_name), exist_ok=True)
	print(f"ffmpeg -y -i \"{inst_track}\" -i \"{voices_track}\" -filter_complex amix=inputs=2:duration=longest \"{os.path.join(output_folder, song_folder_name, song_name)}.ogg\"")

	def run_in_thread(callback):
		ffmpeg_subprocess = subprocess.Popen(f"ffmpeg -y -i \"{inst_track}\" -i \"{voices_track}\" -filter_complex amix=inputs=2:duration=longest \"{os.path.join(output_folder, song_folder_name, song_name)}.ogg\"")
		ffmpeg_subprocess.wait()
		callback(window)
		return

	thread = threading.Thread(target=run_in_thread, args=(callback,))
	thread.start()
	return thread
	# ffmpeg.input(inst_track).input(voices_track).filter('amix', inputs=2, duration='longest').output(f"{os.path.join(output_folder, song_name, song_name)}.ogg").run()

# parse the BPMS out of a simfile
def parse_sm_bpms(bpm_string):
	sm_bpms = bpm_string.split(",")
	bpm_re = re.compile("(.+)=(.+)")
	for sm_bpm in sm_bpms:
		re_match = bpm_re.match(sm_bpm)
		if re_match != None and re_match.start() == 0:
			current_tick = int(round(float(re_match.group(1)) * BEAT_TICKS))
			current_bpm = float(re_match.group(2))
			current_time = tickToTime(current_tick)
			tempomarkers.append(TempoMarker(current_bpm, current_tick, current_time))

def parse_sm(chartfile: TextIOWrapper):
	metadata = {}
	title = ""
	offset = 0
	notes = []
	line = "\n"
	while len(line) > 0:
		line = chartfile.readline()

		while line.strip() != "#NOTES:":
			tag_re = re.compile("#([A-Z]+):(.*?)\\s*?;?$")
			re_match = tag_re.match(line.strip())
			if re_match is not None:
				metadata[re_match[1].lower()] = re_match[2]
			line = chartfile.readline()

		# TODO support SSC
		if line.strip() == "#NOTES:":
			notes.append({
				'type': chartfile.readline().strip()[:-1],
				'author': chartfile.readline().strip()[:-1],
				'diff': chartfile.readline().strip()[:-1],
				'diffNum': chartfile.readline().strip()[:-1],
				'groove': chartfile.readline().strip()[:-1],
				'data': []
			})
			
			line = chartfile.readline().strip()
			while line[0] != ";":
				notes[-1]['data'].append(line)
				line = chartfile.readline().strip()
			line = chartfile.readline()

	print(metadata)

	title = metadata['title']
	offset = float(metadata['offset']) * 1000 if 'OFFSET' in metadata else 0
	parse_sm_bpms(metadata['bpms'])

	return {
		'title': title,
		'offset': offset,
		'tempomarkers': tempomarkers,
		'metadata': metadata,
		'notes': notes
	}

def sm_notes_to_fnf_notes(
	chartfile,
	offset,
	chosen_index
): 
	section_number = 0
	fnf_notes = []
	tracked_holds = {} # for tracking hold notes, need to add tails later
	measure_notes = []

	for line in chartfile['notes'][chosen_index]['data']:

		if line[0] not in (",",";"):
			if NOTES_RE.match(line.strip()) != None:
				measure_notes.append(line)
			continue			
		
		# for ticks-to-time, ticks don't have to be integer :)
		ticks_per_row = float(MEASURE_TICKS) / len(measure_notes)
		
		fnf_section = {}
		fnf_section["lengthInSteps"] = 16
		fnf_section["bpm"] = tickToBPM(section_number * MEASURE_TICKS)
		if len(fnf_notes) > 0:
			fnf_section["changeBPM"] = fnf_section["bpm"] != fnf_notes[-1]["bpm"]
		else:
			fnf_section["changeBPM"] = False
		fnf_section["mustHitSection"] = True
		fnf_section["typeOfSection"] = 0
		
		section_notes = []
		for i in range(len(measure_notes)):
			notes_row = measure_notes[i]
			for j in range(len(notes_row)):
				if notes_row[j] in ("1","2","4"):
					note = [tickToTime(MEASURE_TICKS * section_number + i * ticks_per_row) - offset, j, 0]
					section_notes.append(note)
					if notes_row[j] in ("2","4"):
						tracked_holds[j] = note
				# hold tails
				elif notes_row[j] == "3":
					if j in tracked_holds:
						note = tracked_holds[j]
						del tracked_holds[j]
						note[2] = tickToTime(MEASURE_TICKS * section_number + i * ticks_per_row) - offset - note[0]
		
		fnf_section["sectionNotes"] = section_notes
		
		section_number += 1
		fnf_notes.append(fnf_section)

		measure_notes = []
			
	return fnf_notes
			

def sm_to_fnf(
	chart_simfile, 
	easy_index: int, 
	medium_index: int, 
	hard_index: int,
):
	title = chart_simfile['title']
	offset = chart_simfile['offset']
	tempomarkers = chart_simfile['tempomarkers']

	# assemble the fnf json
	chart_json = {}
	chart_json["song"] = {}
	chart_json["song"]["song"] = title
	# chart_json["song"]["song"] = "Tutorial"
	chart_json["song"]["bpm"] = tempomarkers[0].getBPM()
	chart_json["song"]["sections"] = 0
	chart_json["song"]["needsVoices"] = False
	chart_json["song"]["player1"] = "bf"
	chart_json["song"]["player2"] = "gf"
	chart_json["song"]["sectionLengths"] = []
	chart_json["song"]["events"] = []
	chart_json["song"]["speed"] = 2.0
	chart_json["generatedBy"] = 'fnf-to-sm'

	ret_list = []

	if easy_index > -1:
		chart_json["song"]["notes"] = sm_notes_to_fnf_notes(chart_simfile, offset, easy_index)
		ret_list.append(json.dumps(chart_json))
	else:
		ret_list.append(None)

	if medium_index > -1:
		chart_json["song"]["notes"] = sm_notes_to_fnf_notes(chart_simfile, offset, medium_index)
		ret_list.append(json.dumps(chart_json))
	else:
		ret_list.append(None)

	if hard_index > -1:
		chart_json["song"]["notes"] = sm_notes_to_fnf_notes(chart_simfile, offset, hard_index)
		ret_list.append(json.dumps(chart_json))
	else:
		ret_list.append(None)

	return ret_list

# def usage():
# 	print("FNF SM converter")
# 	print("Usage: {} [chart_file]".format(sys.argv[0]))
# 	print("where [chart_file] is a .json FNF chart or a .sm simfile")
# 	sys.exit(1)