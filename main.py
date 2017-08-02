from kivy.uix.scatterlayout import ScatterLayout
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import BoundedNumericProperty
from kivy.graphics import Line
from kivy.app import App


class Controller(ScatterLayout):
    pass


class Grid(Widget):
    grid_width = BoundedNumericProperty(100, min=100, max=500)
    grid_height = BoundedNumericProperty(100, min=100, max=500)

    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)

        for i in [-1, 1, 2]:
            for j in range(int(Window.width / self.grid_width)):
                x = i * j * self.grid_width
                grid_line = GridLine(x, -Window.height, x, Window.height * 2)
                self.add_widget(grid_line)

            for j in range(int(Window.height / self.grid_height)):
                y = i * j * self.grid_height
                grid_line = GridLine(-Window.width, y, Window.width * 2, y)
                self.add_widget(grid_line)


class GridLine(Widget):
    def __init__(self, x1, y1, x2, y2, **kwargs):
        super(GridLine, self).__init__(**kwargs)

        with self.canvas:
            Line(points=[x1, y1, x2, y2])


class LabVIMApp(App):
    def build(self):
        return Controller()


if __name__ == '__main__':
    LabVIMApp().run()
