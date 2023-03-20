import time
from threading import Thread
import pyttsx3
import os



engine = pyttsx3.init()

is_speaking = False

# example: ["I", "like", "ice-cream"] --- "I like ice-cream"
sentence = []


def delay(s):
    global is_speaking
    global engine

    engine.runAndWait()

    engine.stop()
    is_speaking = False


def say(word, self=None):
    global is_speaking
    global sentence
    global engine

    # it doesn't matter if the tts is saying something or not, for a more responsive system words will be added
    # to the sentence immediately upon user input
    sentence.append(str(word))

    if is_speaking:
        return

    is_speaking = True

    engine.say(word)

    Thread(target=delay, args=(0.7,)).start()


def say_sentence():
    global is_speaking
    global sentence
    global engine

    if is_speaking:
        return

    is_speaking = True

    engine.runAndWait()
    print("ok")

    Thread(target=delay, args=((len(sentence)*1),)).start()


def clear_sentence():
    global sentence
    sentence = []


def remove_from_sentence(word=""):
    global sentence

    # if there is no input then remove the last element in the list, else remove the specified word
    sentence.remove(sentence[-1] if word == "" else word)
