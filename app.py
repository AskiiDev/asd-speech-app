import json

from kivy.config import Config
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.animation import Animation

from img_download import get_image
from vocab_compile import get_word, get_all_words
from speech_engine import say

Config.set('graphics', 'resizable', True)
Builder.load_file("app.kv")
Builder.load_file("vocab_grid.kv")

Window.clearcolor = (0, 0, 0, 1)

BG_ALPHA = 1
SAT = 0.5
BRIGHTNESS = 1


def init_kv():
    with open("vocab_grid.kv", "w") as kv:
        kv.write(""
                 "<VocabGrid>\n"
                 "    padding:dp(5),dp(5),dp(25),dp(5)\n"
                 "")
        context_colour = [1 * BRIGHTNESS, 1 * BRIGHTNESS, 1 * BRIGHTNESS, BG_ALPHA]

        with open("data/words.json", "r") as j:
            data = json.load(j)
            for w in data.keys():
                match (data[w]["pos"][0]):
                    case "NOUN":
                        context_colour = [1 * BRIGHTNESS + SAT, 0 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, BG_ALPHA]
                    case "VERB":
                        context_colour = [1 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, 0 * BRIGHTNESS + SAT, BG_ALPHA]
                    case "CONJ":
                        context_colour = [0 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, 0 * BRIGHTNESS + SAT, BG_ALPHA]
                    case "ADJ":
                        context_colour = [1 * BRIGHTNESS + SAT, 0 * BRIGHTNESS + SAT, 0 * BRIGHTNESS + SAT, BG_ALPHA]
                    case "PRON":
                        context_colour = [0 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, BG_ALPHA]
                    case "DET":
                        context_colour = [0 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, BG_ALPHA]
                    case "ADV":
                        context_colour = [1 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, 0 * BRIGHTNESS + SAT, BG_ALPHA]
                    case "NUM":
                        context_colour = [0.5 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, 1 * BRIGHTNESS + SAT, BG_ALPHA]

                kv.write(""
                         "    Button:\n"
                         f'        text: "{w}"\n'
                         "        width: 150\n"
                         "        height: 150\n"
                         "        size_hint: None, None\n"
                         f"        background_color: {context_colour}\n"
                         "        font_size: 20\n"
                         "        on_press: root.animate(self)\n"
                         "")
        j.close()
    kv.close()


# init_kv()


class Panel(Widget):
    def __init__(self, **kwargs):
        self.pos = [0, 0]
        self.size = [1, 1]
        super(Panel, self).__init__(**kwargs)


class AppLayout(BoxLayout):
    pass


class VocabGrid(GridLayout):
    def animate(self, widget, *args):
        bg = widget.background_color

        say(widget.text)

        animation = Animation(background_color=[2, 2, 2, 1], duration=0.1)
        animation += Animation(background_color=bg, duration=0.1)

        animation.start(widget)


vocab_grid = None


# Main app class
class IAApp(App):
    def on_resize(self, widget, *args):
        global vocab_grid
        vocab_grid.cols = int((Window.size[0] / 190))

    def build(self):
        global vocab_grid

        # the main container for the application
        main_container = AppLayout(orientation="vertical", spacing=2)

        # the top margin of the app
        top_container = AppLayout(orientation="vertical", size_hint=(1, 0.05))

        # the middle container - for the vocab options and side menu
        middle_container = AppLayout(orientation="horizontal", spacing=2, size_hint=(1, 1))

        # the bottom container for the dialogue box
        bottom_container = AppLayout(orientation="horizontal", size_hint=(1, 0.35))

        main_scroll = ScrollView(size_hint=(1, 1), size=(Window.width, Window.height))
        vocab_grid = VocabGrid(cols=int((Window.size[0] / 190)), spacing=20, size_hint_y=None)

        vocab_grid.bind(minimum_height=vocab_grid.setter('height'))

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

        Window.bind(size=self.on_resize)

        return main_container


IAApp().run()
