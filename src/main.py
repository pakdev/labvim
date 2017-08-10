import math
import atexit

from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.properties import DictProperty
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.app import App


class KeyboardMonitor(object):
    def __init__(self, root, callback):
        self._keymap = root.keymap
        self._callback = callback

        root.bind(pressed_keys=self._on_pressed_keys)
        root.bind(keymap=self._update_keymap)

    def _on_pressed_keys(self, sender, pressed_keys):
        for pressed_key in pressed_keys:
            for action, keys in self._keymap.items():
                if pressed_key[1] in keys:
                    self._callback(action)

    def _update_keymap(self, sender, new_keymap):
        self._keymap = new_keymap


class Main(ScatterLayout):
    pressed_keys = ListProperty([])

    # TODO: Allow custom keymaps in the future...
    keymap = DictProperty(
        {
            'left': ['h'],
            'right': ['l'],
            'up': ['k'],
            'down': ['j'],
            'insert': ['i'],
            'select': ['enter'],
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
    cols = NumericProperty(0)

    cell_width = BoundedNumericProperty(100, min=100, max=500)
    cell_height = BoundedNumericProperty(100, min=100, max=500)

    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)

        available_height = Window.height
        available_width = Window.width

        self.rows = math.floor(available_height / self.cell_height)
        self.cols = math.floor(available_width / self.cell_width)

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
        super(GridLine, self).__init__(**kwargs)

        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)
            Line(points=[x1, y1, x2, y2])


class Cursor(Widget):
    main = ObjectProperty(None)
    is_active = BooleanProperty(True)
    width = NumericProperty(100)
    height = NumericProperty(100)
    position_x = NumericProperty(0)
    position_y = NumericProperty(0)
    thickness = BoundedNumericProperty(2, min=1, max=5)

    def __init__(self, **kwargs):
        super(Cursor, self).__init__(**kwargs)
        self._keyboard_monitor = None

        if self.is_active:
            with self.canvas:
                Color((1, 1, 0, 0.7))
                Line(rectangle=(self.position_x * self.width,
                                self.position_y * self.height,
                                self.width,
                                self.height),
                     width=self.thickness)

    def on_main(self, sender, main):
        self._keyboard_monitor = KeyboardMonitor(main, self._on_action)

    def _on_action(self, action):
        if self.is_active:
            if action == 'left':
                self.position_x -= 1
            if action == 'right':
                self.position_x += 1
            if action == 'up':
                self.position_y += 1
            if action == 'down':
                self.position_y -= 1


class Drawer(GridLayout):
    main = ObjectProperty(None)
    visible = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(Drawer, self).__init__(**kwargs)
        self._keyboard_monitor = None

    def on_main(self, sender, main):
        self._keyboard_monitor = KeyboardMonitor(main, self._on_action)

    def _on_action(self, action):
        if action == 'insert':
            # Add blocks to drop
            self.add_widget(DrawerOption('../images/math.png'))
            self.add_widget(DrawerOption('../images/science.png'))

            self.visible = True
        elif action == 'select':
            self.clear_widgets()


class DrawerOption(AnchorLayout):
    def __init__(self, image_path, **kwargs):
        super(DrawerOption, self).__init__(**kwargs)
        self.anchor_x = 'center'
        self.anchor_y = 'center'

        self.add_widget(Image(source=image_path))


class LabVIMApp(App):
    def build(self):
        main = Main()
        atexit.register(main.cleanup)
        return main


if __name__ == '__main__':
    LabVIMApp().run()
