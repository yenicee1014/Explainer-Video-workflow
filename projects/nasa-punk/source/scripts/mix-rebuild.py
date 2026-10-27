"""Synthesize an original restrained score and mix measured narration clips."""
import json
from pathlib import Path
import subprocess
import wave

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "rebuild-timeline.json").read_text())
SR = 48000
length = int(np.ceil(data["duration"] * SR))
voice = np.zeros(length, np.float32)
speech_envelope = np.zeros(length, np.float32)
for chapter in data["chapters"]:
    for line in chapter["lines"]:
        with wave.open(str(ROOT / line["path"])) as audio:
            samples = np.frombuffer(audio.readframes(audio.getnframes()), "<i2").astype(np.float32)/32768
        start = round(line["start"] * SR)
        count = min(len(samples), length-start)
        voice[start:start+count] += samples[:count]
        speech_envelope[max(0,start-int(.15*SR)):min(length,start+count+int(.25*SR))] = 1

# Leave the 250-4000 Hz speech band mostly empty rather than merely ducking.
score = np.zeros(length, np.float32)
scale = [110, 130.8128, 164.8138, 146.8324, 98, 123.4708]
for index, start_s in enumerate(np.arange(.4, data["duration"], 3.2)):
    dur = min(4.8, data["duration"]-start_s)
    t = np.arange(int(dur*SR))/SR
    f = scale[(index//4) % len(scale)]
    env = np.minimum(t/.7, 1) * np.minimum((dur-t)/1.7, 1)
    note = (np.sin(2*np.pi*f*t)+.32*np.sin(2*np.pi*2*f*t))*env*.021
    start = round(start_s*SR)
    score[start:start+len(note)] += note.astype(np.float32)
for index, start_s in enumerate(np.arange(1.2, data["duration"]-1, 1.6)):
    t = np.arange(int(.65*SR))/SR
    f = [1760, 2093.005, 2637.02, 2349.318][index%4]
    note = np.sin(2*np.pi*f*t)*np.exp(-t*9)*.008
    start = round(start_s*SR)
    score[start:start+len(note)] += note.astype(np.float32)

rng = np.random.default_rng(1975)
for chapter in data["chapters"][1:]:
    start = round((chapter["start"]+.05)*SR)
    t = np.arange(int(.26*SR))/SR
    noise = rng.normal(0, 1, len(t))
    noise = np.concatenate([[0], np.diff(noise)])
    sound = noise*np.sin(np.pi*t/.26)**2*.006
    score[start:start+len(t)] += sound.astype(np.float32)

# Chapter sound marks follow the visual change rather than driving the narration.
score *= (1-.5*speech_envelope)
fade = np.minimum(np.arange(length)/SR/1.3, 1)
fade *= np.minimum((length-np.arange(length))/SR/3, 1)
mix = (voice*.9+score)*fade
peak = np.max(np.abs(mix))
if peak > .92:
    mix *= .92/peak
stereo = np.stack([mix, mix], axis=1)
target = ROOT / "assets/rebuild-mix.wav"
with wave.open(str(target), "wb") as audio:
    audio.setnchannels(2)
    audio.setsampwidth(2)
    audio.setframerate(SR)
    audio.writeframes(np.round(stereo*32767).astype("<i2").tobytes())
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(target), "-af",
                "loudnorm=I=-16:TP=-1.5:LRA=8", "-c:a", "aac", "-b:a", "192k",
                str(ROOT / "assets/rebuild-mix.m4a")], check=True)
print(f"Original score and narration mixed: {data['duration']:.3f}s.")
