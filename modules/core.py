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

	def getBeat(self):
		return self.tick_pos/BEAT_TICKS
	
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

class TempoMarkers(list):
	def __init__(self, text = None): # TODO adjust so parse_sm_bps can be merged
		list.__init__(self)
		if text != None:
			self.parse_sm_bpm(text)

	def timeToTick(self, timestamp: float):
		for i in range(len(self)):
			if i == len(self) - 1 or self[i+1].getTime() > timestamp:
				return self[i].timeToTick(timestamp)
		return 0
				
	def tickToTime(self, tick: float):
		for i in range(len(self)):
			if i == len(self) - 1 or self[i+1].getTick() > tick:
				return self[i].tickToTime(tick)
		return 0.0

	def tickToBPM(self, tick: float):
		for i in range(len(self)):
			if i == len(self) - 1 or self[i+1].getTick() > tick:
				return self[i].getBPM()
		return 0.0

	def get_sm_bpm(self):
		return ','.join(list(map(lambda x: f'{x.getBeat()}={x.getBPM()}', self)))

	# parse the BPMS out of a simfile
	def parse_sm_bpm(self, bpm_string):
		sm_bpms = bpm_string.split(",")
		bpm_re = re.compile("(.+)=(.+)")
		for sm_bpm in sm_bpms:
			re_match = bpm_re.match(sm_bpm)
			if re_match != None and re_match.start() == 0:
				current_tick = int(round(float(re_match.group(1)) * BEAT_TICKS))
				current_bpm = float(re_match.group(2))
				current_time = self.tickToTime(current_tick)
				self.append(TempoMarker(current_bpm, current_tick, current_time))

	def __str__(self) -> str:
		return self.get_sm_bpm()

class StepManiaFile:
	def __init__(self, text = None):
		self.title: str = None
		self.bpms: TempoMarkers = None
		self.metadata = {} 
		self.notes: list[StepManiaNotesSection] = list()
		self.offset: float = 0
		if text != None:
			self.parse(text)

	def parse(self, text: str):
		is_ssc = text.find('NOTEDATA') > -1
		metadata = {}
		notes = []
		tag_re = re.compile("#([A-Z]+):(.*?);$", re.MULTILINE|re.DOTALL)
		re_match = tag_re.findall(text)
		notes_section = None

		for entry in re_match:
			key, value = entry
			if is_ssc:
				if key == 'NOTEDATA':
					notes_section = StepManiaNotesSection()
					notes.append(notes_section)
				elif notes_section:
					if key == 'NOTES':
						notes_section.data = value.split()
					elif key == 'BPMS':
						notes_section.bpms = TempoMarkers(value)
					else:
						notes_section.metadata[key.lower()] = value
				else:
					if (key.lower() == 'bpms'): 
						self.bpms = TempoMarkers(value)
					else:
						metadata[key.lower()] = value
			else: 
				if key == 'NOTES':
					stepstype, description, difficulty, meter, radarvalues, data = list(map(lambda x: x.strip(), value.split(':')))
					notes.append(StepManiaNotesSection(
						metadata={
							stepstype: stepstype, 
							description: description, 
							difficulty: difficulty, 
							meter: meter, 
							radarvalues: radarvalues, 
						},
						data=data.split()
					))
				else:
					if (key.lower() == 'bpms'): 
						self.bpms = TempoMarkers(value)
					else:
						metadata[key.lower()] = value

		print(self)

		self.title = metadata['title']
		self.offset = float(metadata['offset']) * 1000 if 'OFFSET' in metadata else 0
		self.notes = notes
		self.metadata = metadata

	def dumps_sm(self):
		text = ""
		for key in self.metadata:
			key: str
			text += f"#{key.upper()}:{self.metadata[key]};\n"
		if (self.bpms): text += f"#BPMS:{self.bpms}"
		else: text += f"#BPMS:{self.notes[0].bpms}"
		for note in self.notes:
			text += note.dumps_sm()
		return text

	def dumps_ssc(self):
		text = ""
		for key in self.metadata:
			key: str
			text += f"#{key.upper()}:{self.metadata[key]};\n"
		if (self.bpms): text += f"#BPMS:{self.bpms}\n"
		else: text += f"#BPMS:{self.notes[0].bpms}\n"
		for note in self.notes:
			text += note.dumps_ssc()
		return text


class StepManiaNotesSection:
	def __init__(
		self,
		data: list = None,
		bpms: TempoMarkers = None,
		metadata: dict = {}
	):
		self.metadata = dict({
			'stepstype': "dance-single",
			'description': "",
			'difficulty': "Edit",
			'meter': 0,
			'radarvalues': "",
			'credit': ""
		}, **metadata)
		self.data = data if data is not None else list()
		self.bpms = bpms

	def get_bpm_string(self):
		return ','.join(list(map(lambda x: f'{x.getBeat()}={x.getBPM()}', self.bpms)))

	def dumps_sm(self):
		data = '\n'.join(self.data)
		return f"""
		
#NOTES:
	  {self.metadata['stepstype']}:
	  {self.metadata['description'] if self.metadata['description'] else self.metadata['credit']}:
	  {self.metadata['difficulty']}:
	  {self.metadata['meter']}:
	  {self.metadata['radarvalues']}:
{data}
;"""

	def dumps_ssc(self):
		text = "\n#NOTEDATA:;\n"
		for key in self.metadata:
			key: str
			text += f"#{key.upper()}:{self.metadata[key]};\n"
		if (self.bpms): text += f"#BPMS:{self.bpms}\n"
		data = '\n'.join(self.data)
		text += f"#NOTES:\n{data}\n;"
		return text


def fnf_to_sm(chart_jsons, window, metadata, initial_steps, format='sm'):

	new_chartfile = StepManiaFile()
	
	# for each fnf difficulty
	sm_header = ''
	sm_notes = ''

	steps_to_make = initial_steps
	steps_made = 0

	for chart_json in chart_jsons:
		for mode in chart_json["modes"]:
			steps_to_make += 1

	new_chartfile.metadata.update({
		**metadata,
		'music': metadata['name'] + '.ogg'
	})

	for chart_json in chart_jsons:

		song_notes = chart_json["song"]["notes"]
		infile = chart_json["infile"]
		num_sections = len(song_notes)

		print("Converting {} to {}.sm".format(infile, metadata['name']))

		song_bpm = chart_json["song"]["bpm"]

		# build tempomap
		tempomarkers: TempoMarkers = TempoMarkers()
		bpms = []
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
				bpms.append(f"{i*4}={section_bpm}")
				current_bpm = section_bpm

			# each step is 1/16
			section_num_steps = section["lengthInSteps"]
			# default measure length = 192
			section_length = STEP_TICKS * section_num_steps
			time_in_section = 15000.0 * section_num_steps / current_bpm

			current_time += time_in_section
			current_tick += section_length
			
		# convert note timestamps to ticks
		notes = {}
		notes_merged = {}
		last_note = 0
		last_note_challenge = 0

		for i in range(num_sections):
			section = song_notes[i]
			section_notes = section["sectionNotes"]
			for section_note in section_notes:		
				tick = tempomarkers.timeToTick(section_note[0])
				if \
					not (0 <= section_note[1] <= 7) or \
					not (isinstance(section_note[1], float) or \
					isinstance(section_note[1], int)) or \
					not (isinstance(section_note[2], float) or \
					isinstance(section_note[2], int)) \
				:
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
					long_end = tempomarkers.timeToTick(section_note[0] + section_note[2])
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

				notes_section = StepManiaNotesSection()

				# type, author, diff, diff_num, groove

				mode, diff_value = mode_dict

				# write chart & difficulty info
				if mode.startswith("single"):
					notes_section.metadata['stepstype'] = 'dance-single'
				else:
					notes_section.metadata['stepstype'] = 'dance-' + mode

				if 'description' in chart_json:
					notes_section.metadata['description'] = chart_json["description"]

				if "charter" in chart_json:
					notes_section.metadata['credit'] = chart_json["charter"]
				else:
					notes_section.metadata['credit'] = metadata['charter']

				if mode == "single-challenge":
					notes_section.metadata['difficulty'] = 'Challenge'
				else:
					notes_section.metadata['difficulty'] = chart_json["diff"]
				
				notes_section.metadata['meter'] = diff_value
				notes_section.bpms = tempomarkers

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
								notes_section.data.append('0'*NUM_COLUMNS_SINGLE)
							else:
								temp_notes = ""
								i2 = 0
								for digit in notes[i]:
									if i2 < 4:
										i2 += 1
										continue
									temp_notes += str(digit)
								notes_section.data.append(temp_notes)
					elif mode == "double" or mode == "couple" or mode == "routine":
						for i in range(measureStart, measureEnd, noteStep):
							if i not in notes:
								notes_section.data.append('0'*NUM_COLUMNS_DOUBLE)
							else:
								temp_notes = ""
								for digit in notes[i]:
									temp_notes += str(digit)
								notes_section.data.append(temp_notes)
					elif mode == "single-challenge" or mode == 'single-mixed':
						for i in range(measureStart, measureEnd, noteStep):
							if i not in notes_merged:
								notes_section.data.append('0'*NUM_COLUMNS_SINGLE)
							else:
								temp_notes = ""
								i2 = 0
								for digit in notes_merged[i]:
									if i2 < 4:
										i2 += 1
										temp_notes += str(digit)
								notes_section.data.append(temp_notes)

					if measureStart + MEASURE_TICKS != last_note:
						notes_section.data.append(',')

				print(len(notes_section.data))
				new_chartfile.notes.append(notes_section)
				steps_made += 1
				window['progressBar'].UpdateBar(steps_made, steps_to_make)

	# output simfile
	if format == "ssc":
		return new_chartfile.dumps_ssc()
	else:
		return new_chartfile.dumps_sm()

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

def parse_sm(chartfile: TextIOWrapper):
	return StepManiaFile(chartfile.read())

def sm_notes_to_fnf_notes(
	chartfile,
	offset,
	chosen_index
): 
	section_number = -1
	fnf_notes = []
	tracked_holds = {} # for tracking hold notes, need to add tails later
	measure_notes = []
	tempomarkers = chartfile.notes[chosen_index].bpms
	if not tempomarkers:
		tempomarkers = chartfile.bpms

	for line in chartfile.notes[chosen_index].data:

		if line[0] not in (",",";"):
			if NOTES_RE.match(line.strip()) != None:
				measure_notes.append(line)
			continue			

		section_number += 1

		# for ticks-to-time, ticks don't have to be integer :)
		ticks_per_row = float(MEASURE_TICKS) / len(measure_notes)
		
		fnf_section = {}
		fnf_section["lengthInSteps"] = 16
		fnf_section["bpm"] = tempomarkers.tickToBPM(section_number * MEASURE_TICKS)
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
					note = [tempomarkers.tickToTime(MEASURE_TICKS * section_number + i * ticks_per_row) - offset, j, 0]
					section_notes.append(note)
					if notes_row[j] in ("2","4"):
						tracked_holds[j] = note
				# hold tails
				elif notes_row[j] == "3":
					if j in tracked_holds:
						note = tracked_holds[j]
						del tracked_holds[j]
						note[2] = tempomarkers.tickToTime(MEASURE_TICKS * section_number + i * ticks_per_row) - offset - note[0]
		
		fnf_section["sectionNotes"] = section_notes
		
		fnf_notes.append(fnf_section)

		measure_notes = []
			
	return fnf_notes
			

def sm_to_fnf(
	chart_simfile,
	easy_index: int, 
	medium_index: int, 
	hard_index: int,
):
	title = chart_simfile.title
	offset = chart_simfile.offset
	print(chart_simfile)
	print(chart_simfile.notes)

	# assemble the fnf json
	chart_json = {
		"song": {
			"song": title,
			"bpm": chart_simfile.bpms[0].getBPM(),
			"sections": 0,
			"needsVoices": False,
			"player1": "bf",
			"player2": "gf",
			"sectionLengths": [],
			"events": [],	# psych (TODO can be removed?)
			"speed": 2.0
		},
		"generator": "fnf-to-sm"
	}

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