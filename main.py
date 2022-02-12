"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

from email.mime import audio
import os
from time import sleep
from playsound import playsound
import pyaudio
import threading
import wave
import speech_recognition as sr

# Listen continuously to audio output


def listen_audio(audio_file):
    global frames
    wf = wave.open(audio_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        wf.writeframes(data)
    wf.close()


# recognize speech from recorded audio data and print it to the console
def recognise_speech(audio_file):
    r = sr.Recognizer()
    text = ""
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
        try:
            text = r.recognize_google(audio, language="ro-RO")

            # print("Google Speech Recognition thinks you said " + r.recognize_google(audio,language="ro-RO"))

        except sr.UnknownValueError:
            pass

    return text


def get_size_of_file(filename):
    statinfo = os.stat(filename)
    return statinfo.st_size

# Play danger_alarm.wav to the speaker when a word is recognized


def sound_notification():
    playsound('danger_alarm.wav')


# Calculate the intersection of previous_text and current_text
def get_new_text(prev_text, current_text):
    new_text = ""
    pos = -1
    # get word list from previous text
    prev_text_list = prev_text.split()
    # get word list from current text
    current_text_list = current_text.split()

    global alarmed

    for current_word in current_text_list:
        if current_word in ["Ștefan", "Ștefane"] and alarmed is False:
            alarmed = True
            sound_thread = threading.Thread(target=sound_notification)
            sound_thread.start()

    for i in range(0, len(prev_text_list)):
        for j in range(0, len(current_text_list)):
            if prev_text_list[i] == current_text_list[j]:
                pos = max(pos, j)

    for i in range(pos+1, len(current_text_list)):
        new_text += ' ' + current_text_list[i]

    return new_text


def message_notification():
    from tkinter import messagebox
    # get the text for the last 30 seconds from last_30_words
    text = ""
    for i in range(0, len(last_30_words)):
        text += last_30_words[i] + " "

    messagebox.showinfo(title="Atenție!!!", message=text, icon="warning")


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 1
WAVE_OUTPUT_FILENAME_0 = "output_0.wav"
WAVE_OUTPUT_FILENAME_1 = "output_1.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

alarmed = False
listen_state = False

x = threading.Thread(target=listen_audio, args=(WAVE_OUTPUT_FILENAME_0,))
x.start()
x.join()

listen_state = True

prev_text = ""

last_30_words = []

while True:
    if listen_state is True:
        listening_file = WAVE_OUTPUT_FILENAME_1
        processing_file = WAVE_OUTPUT_FILENAME_0
    else:
        listening_file = WAVE_OUTPUT_FILENAME_0
        processing_file = WAVE_OUTPUT_FILENAME_1
    x = threading.Thread(target=listen_audio, args=(listening_file,))
    x.start()
    text = recognise_speech(processing_file)
    # print(text)
    new_text = get_new_text(prev_text, text)
    # Make a list of words from the new text
    new_text_list = new_text.split()

    # Concatenate the new_text_list to the last_30_words list
    last_30_words = last_30_words + new_text_list

    # remove elements from the beginning until the list has 30 words or less
    while len(last_30_words) > 30:
        last_30_words.pop(0)

    if alarmed is True:
        message_notification()

    print(get_new_text(prev_text, text))
    prev_text = text
    x.join()
    listen_state = not listen_state
