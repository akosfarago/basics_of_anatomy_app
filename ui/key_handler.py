# ui/key_handler.py
import vtk


class KeyHandler:
    def __init__(self, interactor, camera_controller, text_overlays, bone_zoom_state_getter):
        """
        interactor: vtkRenderWindowInteractor
        camera_controller: CameraController instance
        text_overlays: TextOverlays instance (for updating hints)
        bone_zoom_state_getter: callable that returns True if currently zoomed in on a bone
        """
        self.interactor = interactor
        self.camera_controller = camera_controller
        self.text_overlays = text_overlays
        self.bone_zoom_state_getter = bone_zoom_state_getter
        self.rotation_enabled = False

        interactor.AddObserver("KeyPressEvent", self.on_key_press)

    def on_key_press(self, obj, event):
        key = self.interactor.GetKeySym().lower()

        if key == "r":
            # Toggle rotation
            self.rotation_enabled = not self.rotation_enabled
            if self.rotation_enabled:
                self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
            else:
                self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleUser())
            # Update hint overlay
            self.text_overlays.update_rotation_hint(self.rotation_enabled)
            print(f"Rotation Enabled: {self.rotation_enabled}")

        elif key == "f":
            # Reset camera only if not zoomed in
            if not self.bone_zoom_state_getter():
                self.camera_controller.reset_camera()
                print("Camera reset to initial position.")
            else:
                print("Cannot reset camera while zoomed in. Click empty space to exit zoom first.")

        elif key == "q":
            self.interactor.GetRenderWindow().Finalize()
            self.interactor.TerminateApp()

        elif key == "escape":
            # Stop any ongoing animation
            self.camera_controller.stop_animation()
