
import arabic_reshaper
from bidi.algorithm import get_display

from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout

from plyer import filechooser

from persian_input import PersianTextInput

from agent import (
    run_agent,
    identify_plant,
    research_identified_plant
)


# =========================================================
# Colors
# =========================================================

BG_COLOR = (0.97, 0.98, 0.97, 1)
WHITE = (1, 1, 1, 1)

PRIMARY = (0.13, 0.42, 0.25, 1)
PRIMARY_DARK = (0.08, 0.29, 0.17, 1)

TEXT_DARK = (0.10, 0.15, 0.12, 1)
TEXT_GRAY = (0.42, 0.46, 0.43, 1)

BORDER = (0.86, 0.89, 0.87, 1)
LIGHT_GREEN = (0.91, 0.96, 0.92, 1)


# =========================================================
# Persian Text
# =========================================================

def persian_text(text):
    if text is None:
        return ""

    text = str(text)

    reshaped = arabic_reshaper.reshape(text)

    return get_display(reshaped)


# =========================================================
# Persian Label
# =========================================================

class PersianLabel(Label):

    def __init__(self, **kwargs):

        kwargs.setdefault(
            "font_name",
            "assets/Vazir-Medium.ttf"
        )

        kwargs.setdefault(
            "font_size",
            dp(15)
        )

        kwargs.setdefault(
            "color",
            TEXT_DARK
        )

        kwargs.setdefault(
            "halign",
            "right"
        )

        kwargs.setdefault(
            "valign",
            "middle"
        )

        super().__init__(**kwargs)

        self.bind(
            width=self.update_text_size,
            texture_size=self.update_height
        )

    def update_text_size(self, *args):

        self.text_size = (
            self.width,
            None
        )

    def update_height(self, *args):

        self.height = max(
            self.texture_size[1] + dp(6),
            dp(30)
        )


# =========================================================
# Simple Card
# =========================================================

class SimpleCard(BoxLayout):

    def __init__(
        self,
        background=WHITE,
        radius=14,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.card_radius = dp(radius)

        with self.canvas.before:

            self.bg_color_instruction = Color(
                *background
            )

            self.background_instruction = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[
                    (
                        self.card_radius,
                        self.card_radius
                    )
                ]
            )

            self.border_color_instruction = Color(
                *BORDER
            )

            self.border_instruction = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    self.card_radius
                ),
                width=0.8
            )

        self.bind(
            pos=self.update_card,
            size=self.update_card
        )

    def update_card(self, *args):

        self.background_instruction.pos = self.pos

        self.background_instruction.size = self.size

        self.border_instruction.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            self.card_radius
        )


# =========================================================
# Main Button
# =========================================================

class MainButton(Button):

    def __init__(
        self,
        button_color=PRIMARY,
        text_color=WHITE,
        **kwargs
    ):

        kwargs.setdefault(
            "font_name",
            "assets/Vazir-Medium.ttf"
        )

        kwargs.setdefault(
            "font_size",
            dp(14)
        )

        kwargs.setdefault(
            "color",
            text_color
        )

        kwargs.setdefault(
            "background_normal",
            ""
        )

        kwargs.setdefault(
            "background_down",
            ""

        )

        kwargs.setdefault(
            "background_color",
            (0, 0, 0, 0)
        )

        super().__init__(**kwargs)

        self.button_color = button_color

        self.radius = dp(12)

        with self.canvas.before:

            self.button_color_instruction = Color(
                *self.button_color
            )

            self.button_background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[
                    (
                        self.radius,
                        self.radius
                    )
                ]
            )

        self.bind(
            pos=self.update_button,
            size=self.update_button,
            state=self.update_state
        )

    def update_button(self, *args):

        self.button_background.pos = self.pos

        self.button_background.size = self.size

    def update_state(self, *args):

        if self.state == "down":

            self.button_color_instruction.rgba = (
                self.button_color[0] * 0.88,
                self.button_color[1] * 0.88,
                self.button_color[2] * 0.88,
                1
            )

        else:

            self.button_color_instruction.rgba = (
                *self.button_color[:3],
                1
            )


# =========================================================
# Outline Button
# =========================================================

class OutlineButton(MainButton):

    def __init__(self, **kwargs):

        super().__init__(
            button_color=WHITE,
            text_color=PRIMARY,
            **kwargs
        )

        with self.canvas.after:

            self.outline_color_instruction = Color(
                *PRIMARY
            )

            self.outline_instruction = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    self.radius
                ),
                width=1
            )

        self.bind(
            pos=self.update_outline,
            size=self.update_outline
        )

    def update_outline(self, *args):

        self.outline_instruction.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            self.radius
        )


# =========================================================
# Application
# =========================================================

class PlantApp(App):

    def build(self):

        # -------------------------------------------------
        # Main layout
        # -------------------------------------------------

        root = BoxLayout(
            orientation="vertical"
        )

        # -------------------------------------------------
        # Background
        # -------------------------------------------------

        with root.canvas.before:

            self.background_color_instruction = Color(
                *BG_COLOR
            )

            self.background_instruction = RoundedRectangle(
                pos=root.pos,
                size=root.size
            )

        root.bind(
            pos=self.update_background,
            size=self.update_background
        )

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(78),
            padding=[
                dp(20),
                dp(12),
                dp(20),
                dp(4)
            ]
        )

        title = PersianLabel(
            text=persian_text(
                "دستیار گیاهان دارویی"
            ),
            font_size=dp(22),
            bold=True,
            color=PRIMARY_DARK,
            halign="right",
            valign="middle",
            size_hint_y=None,
            height=dp(35)
        )

        header.add_widget(title)

        subtitle = PersianLabel(
            text=persian_text(
                "پژوهش و بررسی اطلاعات گیاهان دارویی"
            ),
            font_size=dp(12),
            color=TEXT_GRAY,
            halign="right",
            valign="middle",
            size_hint_y=None,
            height=dp(25)
        )

        header.add_widget(subtitle)

        root.add_widget(header)

        # -------------------------------------------------
        # Scroll Area
        # -------------------------------------------------

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(3)
        )

        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(14),
            padding=[
                dp(18),
                dp(8),
                dp(18),
                dp(20)
            ]
        )

        content.bind(
            minimum_height=content.setter("height")
        )

        # -------------------------------------------------
        # Intro
        # -------------------------------------------------

        intro = SimpleCard(
            orientation="vertical",
            padding=[
                dp(16),
                dp(12)
            ],
            spacing=dp(3),
            size_hint_y=None,
            height=dp(90),
            background=LIGHT_GREEN
        )

        intro_title = PersianLabel(
            text=persian_text(
                "پژوهشگر هوشمند گیاهان دارویی"
            ),
            font_size=dp(17),
            bold=True,
            color=PRIMARY_DARK,
            size_hint_y=None,
            height=dp(30)
        )

        intro.add_widget(intro_title)

        intro_text = PersianLabel(
            text=persian_text(
                "درباره یک گیاه سؤال بپرسید "
                "یا تصویر آن را برای شناسایی انتخاب کنید."
            ),
            font_size=dp(12),
            color=TEXT_GRAY
        )

        intro.add_widget(intro_text)

        content.add_widget(intro)

        # -------------------------------------------------
        # Question Title
        # -------------------------------------------------

        question_title = PersianLabel(
            text=persian_text(
                "سؤال شما"
            ),
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(28)
        )

        content.add_widget(question_title)

        # -------------------------------------------------
        # Input
        # -------------------------------------------------

        input_card = SimpleCard(
            orientation="vertical",
            padding=dp(8),
            size_hint_y=None,
            height=dp(105),
            background=WHITE
        )

        self.question_input = PersianTextInput(
            hint_text=persian_text(
                "مثلاً: خواص نعناع فلفلی چیست؟"
            ),
            font_name="assets/Vazir-Medium.ttf",
            font_size=dp(15),
            size_hint_y=1
        )

        input_card.add_widget(
            self.question_input
        )

        content.add_widget(
            input_card
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        buttons = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48)
        )

        ask_button = MainButton(
            text=persian_text(
                "پرسیدن سؤال"
            ),
            button_color=PRIMARY,
            size_hint_x=0.5
        )

        ask_button.bind(
            on_press=self.ask_agent
        )

        image_button = OutlineButton(
            text=persian_text(
                "انتخاب عکس"
            ),
            size_hint_x=0.5
        )

        image_button.bind(
            on_press=self.open_file_chooser
        )

        buttons.add_widget(
            ask_button
        )

        buttons.add_widget(
            image_button
        )

        content.add_widget(
            buttons
        )

        # -------------------------------------------------
        # Result Title
        # -------------------------------------------------

        result_title = PersianLabel(
            text=persian_text(
                "نتیجه"
            ),
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(28)
        )

        content.add_widget(
            result_title
        )

        # -------------------------------------------------
        # Result Card
        # -------------------------------------------------

        result_card = SimpleCard(
            orientation="vertical",
            padding=dp(12),
            size_hint_y=None,
            height=dp(360),
            background=WHITE
        )

        self.result_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(3)
        )

        self.result_label = PersianLabel(
            text=persian_text(
                "پاسخ Agent در این قسمت نمایش داده می‌شود."
            ),
            font_size=dp(14),
            color=TEXT_GRAY,
            size_hint_y=None,
            halign="right",
            valign="top"
        )

        self.result_scroll.add_widget(
            self.result_label
        )

        result_card.add_widget(
            self.result_scroll
        )

        content.add_widget(
            result_card
        )

        # -------------------------------------------------
        # Footer
        # -------------------------------------------------

        footer = PersianLabel(
            text=persian_text(
                "این برنامه برای پژوهش و آموزش طراحی شده است."
            ),
            font_size=dp(10),
            color=TEXT_GRAY,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(30)
        )

        content.add_widget(
            footer
        )

        scroll.add_widget(
            content
        )

        root.add_widget(
            scroll
        )

        # -------------------------------------------------
        # Initial result sizing
        # -------------------------------------------------

        Clock.schedule_once(
            self.update_result_label,
            0
        )

        return root

    # =====================================================
    # Background
    # =====================================================

    def update_background(self, instance, *args):

        self.background_instruction.pos = (
            instance.pos
        )

        self.background_instruction.size = (
            instance.size
        )

    # =====================================================
    # Result Label
    # =====================================================

    def update_result_label(self, *args):

        if not hasattr(
            self,
            "result_scroll"
        ):
            return

        width = (
            self.result_scroll.width
            - dp(16)
        )

        if width <= 0:
            return

        self.result_label.text_size = (
            width,
            None
        )

        self.result_label.texture_update()

        self.result_label.height = max(
            self.result_label.texture_size[1]
            + dp(10),
            dp(70)
        )

    def reset_result_scroll(self, dt):

        self.update_result_label()

        if hasattr(
            self,
            "result_scroll"
        ):

            self.result_scroll.scroll_y = 1

    # =====================================================
    # Text Question
    # =====================================================

    def ask_agent(self, instance):

        question = (
            self.question_input.text.strip()
        )

        if not question:

            self.result_label.text = persian_text(
                "لطفاً سؤال خود را وارد کنید."
            )

            self.update_result_label()

            return

        self.result_label.text = persian_text(
            "در حال بررسی سؤال...\n\n"
            "Agent در حال پردازش اطلاعات است."
        )

        self.update_result_label()

        self.result_scroll.scroll_y = 1

        Thread(
            target=self.get_agent_answer,
            args=(question,),
            daemon=True
        ).start()

    def get_agent_answer(
        self,
        question
    ):

        try:

            answer = run_agent(
                question
            )

            Clock.schedule_once(
                lambda dt: self.show_answer(
                    answer
                )
            )

        except Exception as error:

            Clock.schedule_once(
                lambda dt: self.show_error(
                    error
                )
            )

    # =====================================================
    # Show Answer
    # =====================================================

    def show_answer(
        self,
        answer
    ):

        self.result_label.text = persian_text(
            answer
        )

        self.update_result_label()

        Clock.schedule_once(
            self.reset_result_scroll,
            0.1
        )

    # =====================================================
    # Image Picker
    # =====================================================

    def open_file_chooser(
        self,
        instance
    ):

        filechooser.open_file(
            on_selection=self.on_file_selected,
            filters=[
                "*.jpg",
                "*.jpeg",
                "*.png"
            ]
        )

    def on_file_selected(
        self,
        selection
    ):

        if not selection:
            return

        image_path = selection[0]

        self.show_image_result(
            image_path
        )

    # =====================================================
    # Image Processing
    # =====================================================

    def show_image_result(
        self,
        image_path
    ):

        self.result_label.text = persian_text(
            "در حال شناسایی گیاه...\n\n"
            "لطفاً کمی صبر کنید."
        )

        self.update_result_label()

        self.result_scroll.scroll_y = 1

        Thread(
            target=self.identify_selected_image,
            args=(image_path,),
            daemon=True
        ).start()

    def identify_selected_image(
        self,
        image_path
    ):

        try:

            result = identify_plant(
                image_path
            )

            if "error" in result:

                Clock.schedule_once(
                    lambda dt: self.show_error(
                        result["error"]
                    )
                )

                return

            Clock.schedule_once(
                lambda dt: self.show_loading(
                    "گیاه شناسایی شد.\n\n"
                    "در حال بررسی منابع علمی..."
                )
            )

            research = research_identified_plant(
                result
            )

            Clock.schedule_once(
                lambda dt: self.show_answer(
                    research
                )
            )

        except Exception as error:

            Clock.schedule_once(
                lambda dt: self.show_error(
                    error
                )
            )

    # =====================================================
    # Identification Result
    # =====================================================

    def show_identification_result(
        self,
        result
    ):

        if "error" in result:

            self.show_error(
                result["error"]
            )

            return

        best_match = result.get(
            "best_match",
            "Unknown"
        )

        plants = result.get(
            "plants",
            []
        )

        text = (
            "نتیجه شناسایی گیاه\n\n"
            f"نام علمی:\n"
            f"{best_match}\n\n"
            "گزینه‌های شناسایی:\n"
        )

        for index, plant in enumerate(
            plants,
            start=1
        ):

            scientific_name = plant.get(
                "scientific_name",
                "Unknown"
            )

            confidence = plant.get(
                "confidence",
                0
            )

            confidence_percent = (
                confidence * 100
            )

            text += (
                f"\n{index}. "
                f"{scientific_name}\n"
                f"اطمینان: "
                f"{confidence_percent:.2f}%\n"
            )

        text += (
            "\nتوجه:\n"
            "این نتیجه شناسایی خودکار است "
            "و تشخیص قطعی محسوب نمی‌شود."
        )

        self.result_label.text = persian_text(
            text
        )

        self.update_result_label()

        Clock.schedule_once(
            self.reset_result_scroll,
            0.1
        )

    # =====================================================
    # Loading
    # =====================================================

    def show_loading(
        self,
        message
    ):

        self.result_label.text = persian_text(
            message
        )

        self.update_result_label()

        self.result_scroll.scroll_y = 1

    # =====================================================
    # Error
    # =====================================================

    def show_error(
        self,
        error
    ):

        self.result_label.text = persian_text(
            f"خطا در دریافت پاسخ:\n\n"
            f"{error}"
        )

        self.update_result_label()

        Clock.schedule_once(
            self.reset_result_scroll,
            0.1
        )


# =========================================================
# Run
# =========================================================

if __name__ == "__main__":

    PlantApp().run()
