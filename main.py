import math
import atexit

from kivy.uix.scatterlayout import ScatterLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.app import App


class Main(ScatterLayout):
    Window.clearcolor = (.25, .25, .25, 1)

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
        print(keycode)
        print(text)
        print(modifiers)

        # Add logic to handle recognized keys and return True
        return False


class Grid(Widget):
    rows = NumericProperty(0)
    columns = NumericProperty(0)
    offset = NumericProperty(10)

    cell_width = BoundedNumericProperty(100, min=100, max=500)
    cell_height = BoundedNumericProperty(100, min=100, max=500)

    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)

        available_height = Window.height - self.offset
        available_width = Window.width - self.offset

        self.rows = math.floor(available_height / self.cell_height)
        self.columns = math.floor(available_width / self.cell_width)

        for i in range(self.rows + 1):
            y = i * self.cell_height + self.offset
            grid_line = GridLine(self.offset, y, self.columns * self.cell_width + self.offset, y)
            self.add_widget(grid_line)

        for i in range(self.columns + 1):
            x = i * self.cell_width + self.offset
            grid_line = GridLine(x, self.offset, x, self.rows * self.cell_height + self.offset)
            self.add_widget(grid_line)


class GridLine(Widget):
    def __init__(self, x1, y1, x2, y2, **kwargs):
        super(GridLine, self).__init__(**kwargs)

        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)
            Line(points=[x1, y1, x2, y2])


class Cursor(Widget):
    thickness = BoundedNumericProperty(2, min=1, max=5)

    def __init__(self, **kwargs):
        super(Cursor, self).__init__(**kwargs)


class LabVIMApp(App):
    def build(self):
        main = Main()
        atexit.register(main.cleanup)
        return main


if __name__ == '__main__':
    LabVIMApp().run()