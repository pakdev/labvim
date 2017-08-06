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

    move_left = BooleanProperty(False)
    move_right = BooleanProperty(False)
    move_up = BooleanProperty(False)
    move_down = BooleanProperty(False)

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
        if text == 'h':
            self.move_left = True
        elif text == 'j':
            self.move_down = True
        elif text == 'k':
            self.move_up = True
        elif text == 'l':
            self.move_right = True

        self.move_left, self.move_down, self.move_up, self.move_right = (False, False, False, False)
        return text in ['h', 'j', 'k', 'l']


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
    position_x = NumericProperty(0)
    position_y = NumericProperty(0)
    thickness = BoundedNumericProperty(2, min=1, max=5)

    def __init__(self, **kwargs):
        super(Cursor, self).__init__(**kwargs)

    def on_main(self, sender, value):
        value.bind(move_left=self.on_move_left)
        value.bind(move_right=self.on_move_right)
        value.bind(move_up=self.on_move_up)
        value.bind(move_down=self.on_move_down)

    def on_move_left(self, sender, value):
        if value:
            self.position_x -= 1

    def on_move_right(self, sender, value):
        if value:
            self.position_x += 1

    def on_move_up(self, sender, value):
        if value:
            self.position_y += 1

    def on_move_down(self, sender, value):
        if value:
            self.position_y -= 1


class LabVIMApp(App):
    def build(self):
        main = Main()
        atexit.register(main.cleanup)
        return main


if __name__ == '__main__':
    LabVIMApp().run()