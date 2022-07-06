# fnf-to-sm

This tool converts Friday Night Funkin' `.json` chart files into StepMania's `.sm` or `.ssc` chart files, and vice versa, including converting the music tracks if found. 

For FNF to SM conversion, it can output double and couple charts, and for singles, it can output both the player-side chart (right-chart, like how it is originally played) and the mixed chart (based on the `mustHitSection` aka. the side the camera positioned)   

For SM to FNF conversion, it can output based on the chosen difficulties to the available formats.  

## Support

### StepMania format

| Format | Source | Target | Notes |
| - | - | - | - |
| .sm (old format) | :heavy_check_mark: | :heavy_check_mark:
| .ssc (new format) | :heavy_check_mark: | :heavy_check_mark: | Experimental

### Friday Night Funkin' format

| Format | Source | Target | Notes |
| - | - | - | - |
| Original (Legacy File System) | :heavy_check_mark: | :heavy_check_mark: | Replaces the `Tutorial` song
| Original (New File System) | :heavy_check_mark: | :heavy_check_mark: | Replaces the `Tutorial` song
| [Psych Engine](https://github.com/ShadowMario/FNF-PsychEngine/) | :heavy_check_mark: | :heavy_check_mark: | As a mod (copy to the `mods` folder)
| [Kade Engine](https://github.com/KadeDev/Kade-Engine) | :heavy_check_mark: | :heavy_check_mark: | Replaces the `Tutorial` song
| [Kade Engine](https://github.com/KadeDev/Kade-Engine) ([ModCore](https://github.com/KadeDev/Kade-Engine/blob/master/example_mods/README.md)) | :heavy_check_mark: | :heavy_check_mark: | As a mod (copy to the `mods` folder)

### Interface

| Interface | Availability | Notes
| - | - | - |
| GUI | :heavy_check_mark:
| CLI | :x: | To be redone

## Usage

1. Have Python 3.10 ready. (3.10 is recommended, but you can try old versions)
2. [Download the repository](https://github.com/Hans5958/fnf-to-sm/archive/refs/heads/main.zip). You can also clone by doing `git clone https://github.com/Hans5958/fnf-to-sm.git`.
3. Install the requirements buy running `pip install -r requirements.txt`.
4. Run `fnf-to-sm.py`.
5. Choose between the modes on the tab.
6. Fill the fields as you wish.
   - You can start filling from the Medium field, since it will autofill the other fields if possible.
   - Inst and Voices is for the music tracks, and can be left empty if not needed.
7. Hit "Go" after all set. The output will be located on the set output folder. 

### Modes

| Modes | Description |
| - | - |
| Edit 2 | The recommended mode to use. Uses the Edit difficulty for the mixes.
| Edit 2 (Advanced) | Similar to Edit 2, but with more controls for the meter (difficulty number) and support for additional difficulties.
| StepMania | Converts StepMania charts to FNF charts.
| Edit | Uses the Edit difficulty for the mixes, except on the Single chart.
| Legacy | Uses the intermediary difficulties for the mixes. With the Easy, Medium, and Hard charts on FNF, the player-side charts are on Beginner, Medium, and Expert, and the mixed charts are on Easy, Hard, and Edit.

(when not mentioned, the mode converts FNF charts to StepMania)

## License

fnf-to-sm is licensed under the terms of the [GNU General Public License v3.0](LICENSE).

This is a fork based on [shockdude/fnf-to-sm](https://github.com/shockdude/fnf-to-sm), which is based on the `chart-to-sm.js` by [Paturages](https://github.com/Paturages).
