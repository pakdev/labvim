import math
import atexit

from kivy.uix.scatterlayout import ScatterLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ObjectProperty
from kivy.properties import DictProperty
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.app import App


class Main(ScatterLayout):
    Window.clearcolor = (.25, .25, .25, 1)

    left = BooleanProperty(False)
    right = BooleanProperty(False)
    up = BooleanProperty(False)
    down = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')

        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_key_down)

    def cleanup(self):
        self._keyboard.release()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        handled = False

        if text == 'h':
            self.left = True
            handled = True
        if text == 'j':
            self.down = True
            handled = True
        if text == 'k':
            self.up = True
            handled = True
        if text == 'l':
            self.right = True
            handled = True

        return handled


class Grid(Widget):
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


class Cursor(Widget):
    main = ObjectProperty(None)
    position = DictProperty({'x': 0, 'y': 0})
    thickness = BoundedNumericProperty(2, min=1, max=5)

    def __init__(self, **kwargs):
        super(Cursor, self).__init__(**kwargs)

    def on_main(self, sender, value):
        value.bind(left=self.on_left)
        value.bind(right=self.on_right)
        value.bind(up=self.on_up)
        value.bind(down=self.on_down)

    def on_left(self, sender, value):
        print('left')
        if self.position.x > 0:
            self.position.x -= 1

    def on_right(self, sender, event):
        print('right')
        self.position.x += 1

    def on_up(self, sender, event):
        print('up')
        self.position.y += 1

    def on_down(self, sender, event):
        print('down')
        self.position.y -= 1


class LabVIMApp(App):
    def build(self):
        main = Main()
        atexit.register(main.cleanup)
        return main


if __name__ == '__main__':
    LabVIMApp().run()