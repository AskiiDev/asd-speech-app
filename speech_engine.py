import time
from threading import Thread
import pyttsx3

engine = pyttsx3.init()

is_speaking = False

# example: ["I", "like", "ice-cream"] --- "I like ice-cream"
sentence = []


def delay(s):
    global is_speaking
    global engine

    engine.runAndWait()
    is_speaking = False


def say(word, self=None):
    global is_speaking
    global sentence
    global engine

    # it doesn't matter if the tts is saying something or not, for a more responsive system words will be added
    # to the sentence immediately upon user input
    sentence.append(str(word))

    # if it is already saying something, do not attempt to start another phrase
    if is_speaking:
        return

    # now speaking, prevent interruptions
    is_speaking = True

    engine.say(word)

    wait = Thread(target=lambda: delay(0.7), name="TTS")

    wait.start()


def say_sentence():
    global is_speaking
    global sentence
    global engine

    # if it is already saying something, do not attempt to start another phrase
    if is_speaking:
        return

    # now speaking, prevent interruptions
    is_speaking = True

    engine.runAndWait()
    print("ok")

    wait = Thread(target=lambda: delay(len(sentence)*1))
    wait.start()


def clear_sentence():
    global sentence
    sentence = []


def remove_from_sentence(word=""):
    global sentence

    # if there is no input then remove the last element in the list, else remove the specified word
    sentence.remove(sentence[-1] if word == "" else word)

