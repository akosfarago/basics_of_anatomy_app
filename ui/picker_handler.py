# ui/picker_handler.py
import vtk


class PickerHandler:
    def __init__(self, interactor, renderer, actor_name_map, text_overlay_manager, camera_controller):
        self.interactor = interactor
        self.renderer = renderer
        self.actor_name_map = actor_name_map
        self.text_overlay = text_overlay_manager
        self.camera_controller = camera_controller
        self.previous_actor = None

        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.0005)

        # Bind events
        interactor.AddObserver("MouseMoveEvent", self.on_mouse_move)
        interactor.AddObserver("LeftButtonPressEvent", self.on_left_button_press)

    def on_mouse_move(self, obj, event):
        x, y = self.interactor.GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)
        picked_actor = self.picker.GetActor()

        if self.previous_actor and self.previous_actor != picked_actor:
            self.previous_actor.GetProperty().SetColor(1, 1, 1)

        if picked_actor and picked_actor in self.actor_name_map:
            bone_name = self.actor_name_map[picked_actor]
            self.text_overlay.set_hover_text(f"Hovered: {bone_name}")
            picked_actor.GetProperty().SetColor(1, 1, 0)
            self.previous_actor = picked_actor
        else:
            self.text_overlay.set_hover_text("")
            self.previous_actor = None

    def on_left_button_press(self, obj, event):
        x, y = self.interactor.GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)
        picked_actor = self.picker.GetActor()
        if picked_actor and picked_actor in self.actor_name_map:
            self.camera_controller.start_zoom_animation(picked_actor)
        else:
            # Click empty space → zoom out
            if self.camera_controller.bone_zoom_state:
                self.camera_controller.start_zoom_animation(None)
