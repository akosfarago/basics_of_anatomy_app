import vtk

from language.language import set_language, t


class SettingsMenu:
    def __init__(self, renderer, render_window, on_exit_callback=None):
        self.renderer = renderer
        self.render_window = render_window
        self.on_exit_callback = on_exit_callback  # called when leaving settings

        # Settings options
        self.settings_items = ["English", "Magyar", t("menu_quit")]
        self.text_actors = []
        self.highlighted = None

        self._build_settings()
        self._setup_interaction()

    def _build_settings(self):
        # Remove previous actors first
        for actor in self.renderer.GetActors2D():
            self.renderer.RemoveActor(actor)
        self.text_actors.clear()

        width, height = self.render_window.GetSize()
        n_items = len(self.settings_items)
        font_size = max(width, height) // 30
        spacing = height // (n_items + 2)
        start_y = height - spacing * 2

        for i, label in enumerate(self.settings_items):
            text_actor = vtk.vtkTextActor()
            text_actor.SetInput(label)
            prop = text_actor.GetTextProperty()
            prop.SetFontSize(font_size)
            prop.BoldOn()
            prop.SetColor(1.0, 1.0, 1.0)
            prop.SetJustificationToCentered()
            text_actor.SetDisplayPosition(width // 2, start_y - i * spacing)
            self.renderer.AddActor2D(text_actor)
            self.text_actors.append(text_actor)

        self.renderer.SetBackground(0.05, 0.05, 0.07)
        self.render_window.Render()

    def _setup_interaction(self):
        # Remove previous observers to prevent duplicates
        self.render_window.GetInteractor().RemoveObservers("LeftButtonPressEvent")
        self.render_window.GetInteractor().AddObserver("LeftButtonPressEvent", self._on_click)
        self.render_window.GetInteractor().AddObserver("MouseMoveEvent", self._on_hover)

    def _pick_text_actor(self, x, y):
        for actor in self.text_actors:
            tprop = actor.GetTextProperty()
            font_size = tprop.GetFontSize()
            text_len = len(actor.GetInput())
            width = font_size * text_len * 0.6
            height = font_size
            pos = actor.GetPosition()
            x_min = pos[0] - width // 2
            x_max = pos[0] + width // 2
            y_min = pos[1] - height // 2
            y_max = pos[1] + height // 2
            if x_min <= x <= x_max and y_min <= y <= y_max:
                return actor
        return None

    def _on_hover(self, obj, event):
        x, y = self.render_window.GetInteractor().GetEventPosition()
        picked = self._pick_text_actor(x, y)
        if picked != self.highlighted:
            for t in self.text_actors:
                t.GetTextProperty().SetColor(1.0, 1.0, 1.0)
            if picked:
                picked.GetTextProperty().SetColor(0.3, 0.8, 1.0)
            self.highlighted = picked
            self.render_window.Render()

    def _on_click(self, obj, event):
        x, y = self.render_window.GetInteractor().GetEventPosition()
        picked = self._pick_text_actor(x, y)
        if picked:
            label = self.settings_items[self.text_actors.index(picked)]
            self.handle_selection(label)
        return

    def handle_selection(self, label):
        print(f"[Menu] Selected: {label}")

        if label == "English":
            set_language("en")
            if self.on_exit_callback:
                self.on_exit_callback()  # go back to main menu
        elif label == "Magyar":
            set_language("hu")
            if self.on_exit_callback:
                self.on_exit_callback()  # go back to main menu
        elif label == t("menu_quit"):
            if self.on_exit_callback:
                self.on_exit_callback()  # go back to main menu




