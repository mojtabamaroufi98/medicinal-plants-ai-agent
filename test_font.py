from kivy.app import App
from kivy.uix.label import Label


class TestApp(App):

    def build(self):

        return Label(
            text="سلام گیاهان دارویی",
            font_name="assets/IranNastaliq.ttf",
            font_size=40,
            halign="center",
        )


TestApp().run()