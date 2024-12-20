import os

from nltk.downloader import download
import json

download('punkt')
download('averaged_perceptron_tagger')
download('universal_tagset')
download('wordnet')

from nltk.corpus.reader import WordNetError
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.tag import pos_tag
from word_forms.word_forms import get_word_forms

lemmatizer = WordNetLemmatizer()

categories = ["game", "sport", "food", "liquid", "location", "feeling", "physical_condition"]


def convert_to_wn_tag(tags):
    converted_tags = []

    if type(tags) is not list:
        tags = [tags]

    for t in tags:
        match t:
            case "NOUN":
                converted_tags.append('n')
            case "ADJ":
                converted_tags.append('a')
            case "VERB":
                converted_tags.append('v')
            case "ADV":
                converted_tags.append('r')
            case "n":
                converted_tags.append('n')
            case "a":
                converted_tags.append('a')
            case "v":
                converted_tags.append('v')
            case "r":
                converted_tags.append('r')
            case _:
                pass

    return tuple(converted_tags)


def get_pos_tags(word):
    wn_tags = []
    forms = get_word_forms(word)

    """
    the wordnet solution from the word_forms library provides pos tag classifications but does not correctly identify
    numbers, determiners/articles or pronouns.
    """

    # use word_forms to get base pos tags
    if len(forms['n']) > 1:
        wn_tags.append("NOUN")
    if len(forms['a']) > 1:
        wn_tags.append("ADJ")
    if len(forms['v']) > 1:
        wn_tags.append("VERB")
    if len(forms['r']) > 1:
        wn_tags.append("ADV")

    # the nltk pos tagger
    tags = [pos_tag((word_tokenize(lemmatizer.lemmatize(word))), tagset='universal')[0][1]]

    # a check is done to see if wordnet provided any results, and it will be preferred to nltk's pos_tag if possible
    if len(tags) < 1 and "NUM" not in tags:
        tags = wn_tags

    return tuple(tags)


# returns all the different word forms - as a noun, verb, adj, adverb
def get_forms(word):
    returned_forms = []
    returned_forms.extend(list(get_word_forms(word)['n']))  # nouns
    returned_forms.extend(list(get_word_forms(word)['a']))  # adjectives
    returned_forms.extend(list(get_word_forms(word)['v']))  # verbs
    returned_forms.extend(list(get_word_forms(word)['r']))  # adverbs

    # convert to a set to remove duplicates and convert back to a list
    return tuple(set(returned_forms))


def get_contexts(word):
    returned_contexts = []
    synsets = wordnet.synsets(word)

    for s in synsets:
        # synsets are formatted as "word.pos.n, accessed as [0], [1], [2]"
        temp = s.name().split(".")

        if temp[0] == word:
            returned_contexts.append(temp[2])

    return tuple(returned_contexts)


# used to traverse a tree of word categories
# go down until it reaches the root hypernym (entity)
def traverse_tree(arr, results=None):
    if results is None:
        results = arr

    for i in arr:
        name = i.name().split(".")
        hypernyms = wordnet.synset(name[0] + '.' + name[1] + '.' + name[2]).hypernyms()

        # add results and continue to traverse down the new branches
        for h in hypernyms:
            results.append(h)

        traverse_tree(hypernyms, results)

    return tuple(set(results))


# this function will retrieve pos tags if necessary, but providing them as in input is much faster
def get_categories(word, pos=None, contexts=None, check_forms=False):
    classifications = []
    forms = [word]

    # if a part of speech tag is not specified, return categories resulting from all relevant tags
    if pos is None:
        tags = convert_to_wn_tag(get_pos_tags(word))
    else:
        tags = convert_to_wn_tag(pos)

    # checking all forms of the word if required (e.g., happy, happiness, etc)
    if check_forms:
        forms = get_forms(word)

    if contexts is None:
        contexts = get_contexts(word)
    elif type(contexts) is not list:
        contexts = [contexts]

    for f in forms:
        for t in tags:
            for c in contexts:
                # in the case that there are no hypernyms, we catch the error and continue
                try:
                    # pos = part of speech
                    hypernyms = traverse_tree(wordnet.synset(f + '.' + t + '.' + c).hypernyms())

                    for i in hypernyms:
                        # this will return the category in the form of 'category.n.0#'
                        # so we split it at the . and return the word (0th element)
                        classifications.append(i.name().split(".")[0])
                except WordNetError:
                    pass

    # filter out irrelevant classifications
    return tuple(set(classifications).intersection(categories))


# a function that searches all possible synsets of the word, just in case a broad search is required
def get_all_categories(word, check_forms=False):
    classifications = []

    # this returns the different contexts, e.g. color.n.01, color.n.02, color.v.01 and so on
    synsets = wordnet.synsets(word)

    for s in synsets:
        temp = s.name().split(".")
        classifications.extend(get_categories(temp[0], temp[1], temp[2], check_forms))

    # once again, list(set()) converts it into a set to remove duplicates and then back into a list
    return tuple(set(classifications))


def init_words():
    vocab_list = open("../data/words.txt", 'r')
    vocabulary = vocab_list.read().splitlines()

    # check if the file exists, if not create an empty new one
    if not (os.path.isfile("data/words.json") and os.access("data/words.json", os.R_OK)):
        with open("../data/words.json", 'w') as j:
            j.write("{}")
            j.close()

    # this is much faster than rewriting the file as we only write items that are missing - this operation will be
    # instant if the file is undamaged thus it is very inexpensive to run each time the program opens
    with open("../data/words.json", "r") as j:
        existing_data = json.load(j)

        # update dictionary
        for v in vocabulary:
            if v not in list(existing_data):
                """
                format:
                <word>
                {
                    pos: str
                    uses: float
                    categories: list
                    all_categories: list
                }
                """

                existing_data.update(
                    {v: {
                        "pos":     get_pos_tags(v),
                        "uses":    0,
                        "ctg":     get_categories(v),
                        "all_ctg": get_all_categories(v)
                    }})

        j.close()

    # write back to json
    with open("../data/words.json", "w") as j:
        # dump to file
        json.dump(existing_data, j, indent=1)
        j.close()


def get_word(word):
    returned_data = {}
    with open("../data/words.json", "r") as j:
        data = json.load(j)

        try:
            returned_data = data[word]

        # in case this word does not exist
        except KeyError:
            pass

        j.close()

    return returned_data


def get_all_words():
    returned_data = {}

    try:
        with open("../data/words.json", "r") as j:
            returned_data = json.load(j)

            j.close()
    except FileNotFoundError:
        pass

    return list(returned_data.keys())


init_words()
