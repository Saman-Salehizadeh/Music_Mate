# Music_Mate

Music_Mate is a Python-based tool that converts a musical input into a piano-reduction score and generates a PDF containing playable piano notes.

## Installation

Music_Mate uses two separate Python environments:

* `a2p2`: Python 3.7, used for piano reduction with MidiBERT.
* `a2p`: Python 3.10, used for transcription and the main Music_Mate pipeline.

Create and install the environments with:

```bash
python3.7 -m venv a2p2
. a2p2/bin/activate
pip install -r a2p2-requirements.txt
deactivate

python3.10 -m venv a2p
. a2p/bin/activate
pip install -r a2p-requirements.txt
```

## Model Checkpoint

Download the piano-reduction checkpoint from the following link:

**[Piano-reduction checkpoint](https://drive.google.com/drive/folders/12wJvDAO48q6VPvAXopvN0YzU7PKMHNu-?usp=sharing)**

Place the downloaded checkpoint at:

```text
piano-reduction-with-midibert/MidiBERT/CP/result/finetune/reduction_/model_best.ckpt
```

The checkpoint was trained by the Music_Mate authors using the Music_Mate fork of the piano-reduction project.

## Usage

Activate the main environment:

```bash
. a2p/bin/activate
```

Then run:

```bash
python music_mate.py
```

The program will ask for the input file path and the output PDF path when required.

The pipeline performs the following steps:

1. Converts the input audio to WAV when necessary.
2. Uses **MuScriptor** to transcribe the musical input and extract notes.
3. Converts the transcription to MIDI.
4. Uses the **MidiBERT piano-reduction model** to reduce the orchestral MIDI to playable piano notes.
5. Uses **LilyPond** to engrave the resulting notes and generate the final PDF.

## Piano Reduction

The `piano-reduction-with-midibert` directory is a fork of the following project:

https://github.com/tpmmthomas/piano-reduction-with-midibert

The original project and its authors retain the copyright to their original work.

Music_Mate uses this fork for piano reduction. The `model_best.ckpt` checkpoint provided for Music_Mate was trained by the Music_Mate authors using this fork and is not an original checkpoint from the upstream project.

## Music Transcription

Music_Mate uses **MuScriptor** to transcribe the input audio and extract musical notes.

## Music Engraving

Music_Mate uses **LilyPond** to engrave the reduced piano notes and generate the final PDF score.

## Tested Hardware

The project has been tested on the following hardware configuration:

- **Laptop:** MSI Cyborg 15 A12VF
- **CPU:** Intel Core i7-12650H
- **GPU:** NVIDIA GeForce RTX 4060 Laptop GPU
- **GPU Memory (VRAM):** 8 GB GDDR6
- **System RAM:** 16 GB DDR5
- **Operating System:** Windows 11 Pro with WSL2 running Ubuntu 26.04 LTS

## License and Attribution

Please refer to the original `piano-reduction-with-midibert` repository for the license and attribution requirements of the upstream code.

Music_Mate's own code and separately trained model checkpoint are provided by the Music_Mate authors.
