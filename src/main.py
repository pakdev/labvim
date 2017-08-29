import math
import atexit
from enum import Enum

from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import BoundedNumericProperty
from kivy.properties import ReferenceListProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.properties import DictProperty
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.app import App


class State(Enum):
    EDITING = 1
    INSERTING = 2


CURRENT_STATE = State.EDITING


class KeyboardMonitor(object):
    def __init__(self, root, callback):
        self._keymap = root.keymap
        self._callback = callback

        root.bind(pressed_keys=self._on_pressed_keys)
        root.bind(keymap=self._update_keymap)

    def _on_pressed_keys(self, sender, pressed_keys):
        for pressed_key in pressed_keys:
            for state, actions in self._keymap.items():
                if state == CURRENT_STATE:
                    for action, keys in actions.items():
                        if pressed_key[1] in keys:
                            self._callback(action)

    def _update_keymap(self, sender, new_keymap):
        self._keymap = new_keymap


class Main(FloatLayout):
    pressed_keys = ListProperty([])
    keymap = DictProperty(
        {
            State.EDITING: {
                'left': ['h', 'left'],
                'right': ['l', 'right'],
                'up': ['k', 'up'],
                'down': ['j', 'down'],
                'insert': ['i'],
                'home': ['gg'],
                'quit': ['ZZ']
            },
            State.INSERTING: {
                'left': ['h'],
                'right': ['l'],
                'up': ['k'],
                'down': ['j'],
                'select': ['enter']
            }
        })

    # Set the background to gray
    Window.clearcolor = (0.25, 0.25, 0.25, 1)

    def __init__(self, **kwargs):
        super(Main, self).__init__()

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            pass

        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

    def cleanup(self):
        self._keyboard.release()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.pressed_keys.append(keycode)
        return True

    def _on_key_up(self, keyboard, keycode):
        self.pressed_keys = list(filter(lambda x: x != keycode, self.pressed_keys))
        return True


class Grid(ScatterLayout):
    rows = NumericProperty(0)
    cols = NumericProperty(0)

    cell_width = BoundedNumericProperty(100, min=100, max=500)
    cell_height = BoundedNumericProperty(100, min=100, max=500)

    def __init__(self, **kwargs):
        super(Grid, self).__init__()

        available_height = Window.height
        available_width = Window.width

        self.rows = int(math.floor(available_height / self.cell_height))
        self.cols = int(math.floor(available_width / self.cell_width))

        for i in range(self.rows + 1):
            y = i * self.cell_height
            grid_line = GridLine(0, y, self.cols * self.cell_width, y)
            self.add_widget(grid_line)

        for i in range(self.cols + 1):
            x = i * self.cell_width
            grid_line = GridLine(x, 0, x, self.rows * self.cell_height)
            self.add_widget(grid_line)


class GridLine(Widget):
    def __init__(self, x1, y1, x2, y2, **kwargs):
        super(GridLine, self).__init__()

        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)
            Line(points=[x1, y1, x2, y2])


class Cursor(Widget):
    main = ObjectProperty(None)

    color = ListProperty([1, 1, 0, 0.7])

    is_active = BooleanProperty(True)
    is_visible = BooleanProperty(True)

    thickness = BoundedNumericProperty(2, min=1, max=5)
    grid_pos_x = NumericProperty(0)
    grid_pos_y = NumericProperty(0)
    grid_pos_min_x = NumericProperty(None)
    grid_pos_max_x = NumericProperty(None)
    grid_pos_min_y = NumericProperty(None)
    grid_pos_max_y = NumericProperty(None)

    grid_pos = ReferenceListProperty(grid_pos_x, grid_pos_y)
    grid_pos_bounds = ReferenceListProperty(grid_pos_min_x, grid_pos_max_x, grid_pos_min_y, grid_pos_max_y)

    def __init__(self, **kwargs):
        super(Cursor, self).__init__()
        self._keyboard_monitor = None

        if self.is_active:
            self._draw()

    def on_main(self, sender, main):
        self._keyboard_monitor = KeyboardMonitor(main, self._on_action)

    def on_is_visible(self, sender, value):
        self._draw()

    def on_grid_pos(self, sender, value):
        self._draw()

    def _on_action(self, action):
        if self.is_active:
            if action == 'left' and (self.grid_pos_min_x is None or self.grid_pos_x > self.grid_pos_min_x):
                self.grid_pos_x -= 1
            if action == 'right' and (self.grid_pos_max_x is None or self.grid_pos_x < self.grid_pos_max_x):
                self.grid_pos_x += 1
            if action == 'up' and (self.grid_pos_max_x is None or self.grid_pos_y < self.grid_pos_max_y):
                self.grid_pos_y += 1
            if action == 'down' and (self.grid_pos_min_y is None or self.grid_pos_y > self.grid_pos_min_y):
                self.grid_pos_y -= 1
            if action == 'home':
                self.grid_pos_x = 0
                self.grid_pos_y = 0

    def _draw(self):
        if self.is_visible:
            self.canvas.clear()
            with self.canvas:
                Color(*self.color)
                Line(rectangle=(self.grid_pos_x * self.width,
                                self.grid_pos_y * self.height,
                                self.width,
                                self.height),
                     width=self.thickness)
        else:
            self.canvas.clear()


class Drawer(GridLayout):
    main = ObjectProperty(None)
    is_visible = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(Drawer, self).__init__()

        self._keyboard_monitor = None
        self._options = [
            DrawerOption(name='Math', source='../images/math.png'),
            DrawerOption(name='Science', source='../images/science.png')
        ]

    def on_main(self, sender, main):
        self._keyboard_monitor = KeyboardMonitor(main, self._on_action)

    def _on_action(self, action):
        global CURRENT_STATE
        if action == 'insert':
            CURRENT_STATE = State.INSERTING
            [self.add_widget(option) for option in self._options]
            self.is_visible = True

        elif action == 'select':
            CURRENT_STATE = State.EDITING
            [self.remove_widget(option) for option in self._options]
            self.is_visible = False


class DrawerOption(AnchorLayout):
    name = StringProperty('')
    image_source = StringProperty('')

    def __init__(self, **kwargs):
        super(DrawerOption, self).__init__()
        self.name = kwargs.get('name', '')
        self.image_source = kwargs.get('source', '')


class VipyrApp(App):
    def build(self):
        main = Main(rows=2, cols=1)
        atexit.register(main.cleanup)
        return main


if __name__ == '__main__':
    VipyrApp().run()
