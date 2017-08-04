from kivy.uix.scatterlayout import ScatterLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import BoundedNumericProperty
from kivy.graphics import Line, Color
from kivy.app import App


class Main(ScatterLayout):
    Window.clearcolor = (.25, .25, .25, 1)


class Grid(Widget):
    grid_width = BoundedNumericProperty(100, min=100, max=500)
    grid_height = BoundedNumericProperty(100, min=100, max=500)

    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)

        for i in range(int(Window.width / self.grid_width) + 1):
            x = i * self.grid_width
            grid_line = GridLine(x, 0, x, Window.height)
            self.add_widget(grid_line)

        for i in range(int(Window.height / self.grid_height) + 1):
            y = i * self.grid_height
            grid_line = GridLine(0, y, Window.width, y)
            self.add_widget(grid_line)


class GridLine(Widget):
    def __init__(self, x1, y1, x2, y2, **kwargs):
        super(GridLine, self).__init__(**kwargs)

        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)
            Line(points=[x1, y1, x2, y2])


class LabVIMApp(App):
    def build(self):
        return Main()


if __name__ == '__main__':
    LabVIMApp().run()
