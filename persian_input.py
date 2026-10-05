import arabic_reshaper
from bidi.algorithm import get_display

from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout


class PersianTextInput(FloatLayout):

    def __init__(self, **kwargs):

        font_name = kwargs.pop(
            "font_name",
            "assets/Vazir-Medium.ttf"
        )

        font_size = kwargs.pop(
            "font_size",
            18
        )

        hint_text = kwargs.pop(
            "hint_text",
            ""
        )

        super().__init__(**kwargs)

        # =========================
        # Real TextInput
        # =========================

        self.input = TextInput(
            font_size=font_size,
            multiline=True,

            # Background
            background_color=(1, 1, 1, 1),

            # متن واقعی را مخفی می‌کنیم
            # چون متن RTL را Label نمایش می‌دهد
            foreground_color=(0, 0, 0, 0),

            # Cursor مشکی
            cursor_color=(1, 1, 1, 1),

            padding=[15, 15],

            font_name=font_name
        )

        self.add_widget(self.input)

        # =========================
        # RTL Display
        # =========================

        self.display = Label(
            text="",

            font_name=font_name,
            font_size=font_size,

            halign="right",
            valign="top",

            # متن مشکی
            color=(0, 0, 0, 1),

            text_size=(None, None)
        )

        self.add_widget(self.display)

        # =========================
        # Hint
        # =========================

        self.hint_label = Label(
            text=hint_text,

            font_name=font_name,
            font_size=font_size,

            halign="right",
            valign="top",

            # خاکستری
            color=(0.55, 0.55, 0.55, 1)
        )

        self.add_widget(self.hint_label)

        # =========================
        # Events
        # =========================

        self.input.bind(
            text=self.update_display
        )

        self.input.bind(
            focus=self.update_focus
        )

        self.bind(
            size=self.update_size
        )

        self.update_size()

    # =========================
    # Update Display
    # =========================

    def update_display(self, instance, value):

        if not value:

            self.display.text = ""

            self.hint_label.opacity = 1

            return

        self.hint_label.opacity = 0

        reshaped_text = arabic_reshaper.reshape(
            value
        )

        display_text = get_display(
            reshaped_text
        )

        self.display.text = display_text

        # همیشه نمایش داده شود
        self.display.opacity = 1

        self.update_display_size()

    # =========================
    # Display Size
    # =========================

    def update_display_size(self, *args):

        width = self.width - 30

        self.display.text_size = (
            width,
            None
        )

        self.display.texture_update()

        self.display.height = (
            self.display.texture_size[1]
        )

    # =========================
    # Focus
    # =========================

    def update_focus(self, instance, focused):

        # متن RTL را مخفی نکن
        self.display.opacity = 1

    # =========================
    # Size
    # =========================

    def update_size(self, *args):

        self.input.pos = self.pos
        self.input.size = self.size

        self.display.pos = (
            self.x + 15,
            self.y + 15
        )

        self.display.width = (
            self.width - 30
        )

        self.hint_label.pos = (
            self.x + 15,
            self.y + 15
        )

        self.hint_label.size = (
            self.width - 30,
            self.height - 30
        )

        self.update_display_size()

    # =========================
    # Get Text
    # =========================

    @property
    def text(self):

        return self.input.text

    # =========================
    # Set Text
    # =========================

    @text.setter
    def text(self, value):

        self.input.text = value

    # =========================
    # Focus Property
    # =========================

    @property
    def focus(self):

        return self.input.focus

    @focus.setter
    def focus(self, value):

        self.input.focus = value