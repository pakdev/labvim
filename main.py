import math
import atexit

from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.properties import DictProperty
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.app import App


class KeyboardHelper(object):
    def __init__(self, current_key_mappings):
        self._key_mappings = current_key_mappings

    def update_key_mappings(self, current_key_mappings):
        self._key_mappings = current_key_mappings

    def is_action_triggered(self, action, pressed_keys):
        for pressed_key in pressed_keys:
            for key_mapping in self._key_mappings[action]:
                if key_mapping in pressed_key:
                    return True
        return False


class Main(ScatterLayout):
    pressed_keys = ListProperty([])

    # TODO: Allow custom keymaps in the future...
    key_mappings = DictProperty(
        {
            'left': ['h'],
            'right': ['l'],
            'up': ['k'],
            'down': ['j'],
            'insert': ['i'],
            'quit with saving': ['ZZ']
        })

    # Set the background to gray
    Window.clearcolor = (.25, .25, .25, 1)

    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)

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
        self.pressed_keys.remove(keycode)
        return True


class Grid(FloatLayout):
    rows = NumericProperty(0)
    columns = NumericProperty(0)

    cell_width = BoundedNumericProperty(100, min=100, max=500)
    cell_height = BoundedNumericProperty(100, min=100, max=500)

    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)

        available_height = Window.height
        available_width = Window.width

        self.rows = math.floor(available_height / self.cell_height)
        self.columns = math.floor(available_width / self.cell_width)

        for i in range(self.rows + 1):
            y = i * self.cell_height
            grid_line = GridLine(0, y, self.columns * self.cell_width, y)
            self.add_widget(grid_line)

        for i in range(self.columns + 1):
            x = i * self.cell_width
            grid_line = GridLine(x, 0, x, self.rows * self.cell_height)
            self.add_widget(grid_line)


class GridLine(Widget):
    def __init__(self, x1, y1, x2, y2, **kwargs):
        super(GridLine, self).__init__(**kwargs)

        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)
            Line(points=[x1, y1, x2, y2])


class Drawer(Widget):
    main = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Drawer, self).__init__(**kwargs)


class Cursor(Widget):
    main = ObjectProperty(None)
    position_x = NumericProperty(0)
    position_y = NumericProperty(0)
    thickness = BoundedNumericProperty(2, min=1, max=5)

    def __init__(self, **kwargs):
        super(Cursor, self).__init__(**kwargs)
        self._keyboard_helper = None

    def on_main(self, sender, value):
        value.bind(pressed_keys=self._on_pressed_keys)
        value.bind(key_mappings=self._on_key_mappings)
        self._keyboard_helper = KeyboardHelper(value.key_mappings)

    def _on_pressed_keys(self, sender, value):
        if self._keyboard_helper.is_action_triggered('left', value):
            self.position_x -= 1
        if self._keyboard_helper.is_action_triggered('right', value):
            self.position_x += 1
        if self._keyboard_helper.is_action_triggered('up', value):
            self.position_y += 1
        if self._keyboard_helper.is_action_triggered('down', value):
            self.position_y -= 1

    def _on_key_mappings(self, sender, value):
        self._keyboard_helper.update_key_mappings(value)


class LabVIMApp(App):
    def build(self):
        main = Main()
        atexit.register(main.cleanup)
        return main


if __name__ == '__main__':
    LabVIMApp().run()
