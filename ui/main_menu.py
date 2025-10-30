import vtk
from viewer_app import SkeletonViewerApp
from language.language import t
from ui.settings_menu_point import SettingsMenu


class MainMenu:
    def __init__(self):
        # Renderer setup
        self.renderer = vtk.vtkRenderer()
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window.FullScreenOn()  # fullscreen

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)

        # Menu items
        self.menu_items = [
            t("menu_skeleton"),
            t("menu_muscle"),
            t("menu_settings"),
            t("menu_quit")
        ]
        self.text_actors = []
        self.highlighted = None

        # Build menu and interaction
        self._build_menu()
        self._setup_interaction()

    def _build_menu(self):
        width, height = self.render_window.GetSize()
        # Fetch translated labels every time
        self.menu_items = [
            t("menu_skeleton"),
            t("menu_muscle"),
            t("menu_settings"),
            t("menu_quit")
        ]

        n_items = len(self.menu_items)
        font_size = max(width, height) // 30
        spacing = height // (n_items + 2)
        start_y = height - spacing * 2

        # Remove existing actors
        for actor in self.text_actors:
            self.renderer.RemoveActor(actor)
        self.text_actors.clear()

        for i, label in enumerate(self.menu_items):
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
        self.interactor.AddObserver("MouseMoveEvent", self._on_hover)
        self.interactor.AddObserver("LeftButtonPressEvent", self._on_click)

    def _pick_text_actor(self, x, y):
        """Adaptive click detection based on font size and display position"""
        for actor in self.text_actors:
            tprop = actor.GetTextProperty()
            font_size = tprop.GetFontSize()
            text_len = len(actor.GetInput())
            width = font_size * text_len * 0.6  # rough estimate
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
        x, y = self.interactor.GetEventPosition()
        picked = self._pick_text_actor(x, y)
        if picked != self.highlighted:
            for t in self.text_actors:
                t.GetTextProperty().SetColor(1.0, 1.0, 1.0)
            if picked:
                picked.GetTextProperty().SetColor(0.3, 0.8, 1.0)
            self.highlighted = picked
            self.render_window.Render()

    def _on_click(self, obj, event):
        x, y = self.interactor.GetEventPosition()
        picked = self._pick_text_actor(x, y)
        if picked:
            label = self.menu_items[self.text_actors.index(picked)]
            self.handle_selection(label)

    def handle_selection(self, label):
        print(f"[Menu] Selected: {label}")
        if label == t("menu_quit"):
            self.interactor.TerminateApp()
        elif label == t("menu_skeleton"):  # <- use translation
            self._launch_skeleton_viewer()
        elif label == t("menu_muscle"):  # <- use translation
            print("Muscle Anatomy viewer not implemented yet.")
        elif label == t("menu_settings"):  # <- use translation
            def back_to_main():
                for actor in self.renderer.GetActors2D():
                    self.renderer.RemoveActor(actor)
                self._build_menu()
                self._setup_interaction()

            SettingsMenu(renderer=self.renderer, render_window=self.render_window, on_exit_callback=back_to_main)

    def _launch_skeleton_viewer(self):
        # Close menu first
        self.interactor.TerminateApp()
        # Launch skeleton viewer in a new window
        viewer = SkeletonViewerApp("models/male_human_skeleton.obj")
        viewer.run()

    def run(self):
        self.render_window.Render()
        self.interactor.Start()
