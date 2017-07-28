import kivy

from kivy.uix.scatterlayout import ScatterLayout
from kivy.app import App


class Controller(ScatterLayout):
    pass


class LabVIMApp(App):
    def build(self):
        return Controller()


if __name__ == '__main__':
    LabVIMApp().run()
