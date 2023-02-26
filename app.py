from kivy.config import Config
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image

from functools import partial

from img_download import get_image
from vocab_compile import get_word, get_all_words
from speech_engine import say

Config.set('graphics', 'resizable', True)
Builder.load_file("app.kv")

Window.clearcolor = (0, 0, 0, 1)


class Panel(Widget):
    def __init__(self, **kwargs):
        self.pos = [0, 0]
        self.size = [1, 1]
        super(Panel, self).__init__(**kwargs)


class AppLayout(BoxLayout):
    pass


class VocabGrid(GridLayout):
    pass


# Define the main app class
class IAApp(App):
    def build(self):
        # the main container for the application
        main_container = AppLayout(orientation="vertical", spacing=2)

        # the top margin of the app
        top_container = AppLayout(orientation="vertical", size_hint=(1, 0.05))

        # the middle container - for the vocab options and side menu
        middle_container = AppLayout(orientation="horizontal", spacing=2, size_hint=(1, 1))

        # the bottom container for the dialogue box
        bottom_container = AppLayout(orientation="horizontal", size_hint=(1, 0.35))

        main_scroll = ScrollView(size_hint=(1, 1), size=(Window.width, Window.height))
        vocab_grid = VocabGrid(cols=4, spacing=20, size_hint_y=None)
        vocab_grid.bind(minimum_height=vocab_grid.setter('height'))

        # brightness = 2
        # context_colour = [1 * brightness, 1 * brightness, 1 * brightness, 1]
        for w in get_all_words():
            # match (i[1][0]):
            #    case "NOUN":
            #        context_colour = [1 * brightness, 0 * brightness, 1 * brightness, 1]
            #    case "VERB":
            #        context_colour = [1 * brightness, 1 * brightness, 0 * brightness, 1]
            #    case "CONJ":
            #        context_colour = [0 * brightness, 1 * brightness, 0 * brightness, 1]
            #    case "ADJ":
            #        context_colour = [1 * brightness, 0 * brightness, 0 * brightness, 1]
            #    case "PRON":
            #        context_colour = [0 * brightness, 1 * brightness, 1 * brightness, 1]
            #    case "DET":
            #        context_colour = [0 * brightness, 1 * brightness, 1 * brightness, 1]
            #    case "ADV":
            #        context_colour = [1 * brightness, 1 * brightness, 0 * brightness, 1]
            #    case "NUM":
            #        context_colour = [0.5 * brightness, 1 * brightness, 1 * brightness, 1]

            button = Button(text=w, size_hint_y=None, height=150, background_normal=get_image(w))

            callback = partial(say, w)
            button.bind(on_press=callback)

            vocab_grid.add_widget(button)
        main_scroll.add_widget(vocab_grid)

        # add blank white panels
        top_container.add_widget(Panel(size_hint=(1, 1)))
        middle_container.add_widget(Panel(size_hint=(0.1, 1)))
        middle_container.add_widget(main_scroll)
        bottom_container.add_widget(Panel(size_hint=(1, 1)))

        # add sub containers to main container
        main_container.add_widget(top_container)
        main_container.add_widget(middle_container)
        main_container.add_widget(bottom_container)

        return main_container


IAApp().run()
