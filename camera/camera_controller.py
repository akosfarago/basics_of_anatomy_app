# camera/camera_controller.py
import math
import vtk
from utils.helpers import get_actor_center


class CameraController:
    def __init__(self, camera, renderer, interactor, text_overlay_manager=None):
        self.camera = camera
        self.renderer = renderer
        self.interactor = interactor
        self.text_overlay = text_overlay_manager  # For updating rotation hints

        # --- Rotation state ---
        self.rotation_enabled = False
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleUser())

        # --- Zoom animation state ---
        self.bone_zoom_state = False
        self.target_actor = None
        self.animation_steps = 60
        self.current_step = 0
        self.start_pos = [0, 0, 0]
        self.start_focal = [0, 0, 0]
        self.end_pos = [0, 0, 0]
        self.end_focal = [0, 0, 0]
        self.timer_id = None
        self.pre_zoom_camera_state = None

        # --- Save initial camera state ---
        self.initial_state = {
            "position": camera.GetPosition(),
            "focal_point": camera.GetFocalPoint(),
            "view_up": camera.GetViewUp(),
            "view_angle": camera.GetViewAngle()
        }

        # Bind key events
        self.interactor.AddObserver("KeyPressEvent", self.on_key_press)

    # --- Rotation toggle ---
    def toggle_rotation(self):
        self.rotation_enabled = not self.rotation_enabled
        if self.rotation_enabled:
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        else:
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleUser())
            self.text_overlay.update_rotation_hint(self.rotation_enabled)

    # --- Reset camera ---
    def reset_camera(self):
        if not self.bone_zoom_state:
            self.camera.SetPosition(self.initial_state["position"])
            self.camera.SetFocalPoint(self.initial_state["focal_point"])
            self.camera.SetViewUp(self.initial_state["view_up"])
            self.camera.SetViewAngle(self.initial_state["view_angle"])
            self.renderer.ResetCameraClippingRange()
            self.renderer.GetRenderWindow().Render()
        else:
            print("Cannot reset while zoomed in. Click empty space first.")

    # --- Rotate camera manually ---
    def rotate_camera(self, axis, angle_deg):
        if not self.rotation_enabled:
            return  # Do nothing if rotation is disabled

        pos = list(self.camera.GetPosition())
        focal = list(self.camera.GetFocalPoint())
        vec = [pos[i] - focal[i] for i in range(3)]

        angle_rad = math.radians(angle_deg)
        if axis == "y":  # left/right
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            x = vec[0] * cos_a + vec[2] * sin_a
            z = -vec[0] * sin_a + vec[2] * cos_a
            vec[0], vec[2] = x, z
        elif axis == "x":  # up/down
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            y = vec[1] * cos_a - vec[2] * sin_a
            z = vec[1] * sin_a + vec[2] * cos_a
            vec[1], vec[2] = y, z

        new_pos = [focal[i] + vec[i] for i in range(3)]
        self.camera.SetPosition(new_pos)
        self.camera.SetFocalPoint(focal)
        self.renderer.ResetCameraClippingRange()
        self.renderer.GetRenderWindow().Render()

    # --- Zoom animation ---
    def start_zoom_animation(self, actor=None):
        cam = self.camera
        if not self.bone_zoom_state and actor:
            self.pre_zoom_camera_state = {
                "position": cam.GetPosition(),
                "focal_point": cam.GetFocalPoint(),
                "view_up": cam.GetViewUp(),
                "view_angle": cam.GetViewAngle(),
            }

            self.start_pos = list(cam.GetPosition())
            self.start_focal = list(cam.GetFocalPoint())
            self.end_focal = get_actor_center(actor)
            direction = [self.start_pos[i] - self.start_focal[i] for i in range(3)]
            mag = sum(d * d for d in direction) ** 0.5
            scale = 0.3 * mag
            self.end_pos = [self.end_focal[i] + direction[i] / mag * scale for i in range(3)]

            self.bone_zoom_state = True
            self.target_actor = actor

        elif self.bone_zoom_state:
            self.start_pos = list(cam.GetPosition())
            self.start_focal = list(cam.GetFocalPoint())
            if self.pre_zoom_camera_state:
                self.end_pos = list(self.pre_zoom_camera_state["position"])
                self.end_focal = list(self.pre_zoom_camera_state["focal_point"])
                cam.SetViewUp(self.pre_zoom_camera_state["view_up"])
                cam.SetViewAngle(self.pre_zoom_camera_state["view_angle"])
            else:
                self.end_pos = list(self.initial_state["position"])
                self.end_focal = list(self.initial_state["focal_point"])
            self.bone_zoom_state = False
            self.target_actor = None

        self.current_step = 0
        if self.timer_id is None:
            self.timer_id = self.interactor.CreateRepeatingTimer(16)
            self.interactor.AddObserver("TimerEvent", self.animate_camera)

    def animate_camera(self, obj, event):
        if self.current_step >= self.animation_steps:
            if self.timer_id is None:
                self.timer_id = self.interactor.CreateRepeatingTimer(16)
                self.interactor.AddObserver("TimerEvent", self.animate_camera)
            return

        t = (self.current_step + 1) / self.animation_steps
        new_pos = [self.start_pos[i] + t * (self.end_pos[i] - self.start_pos[i]) for i in range(3)]
        new_focal = [self.start_focal[i] + t * (self.end_focal[i] - self.start_focal[i]) for i in range(3)]
        self.camera.SetPosition(new_pos)
        self.camera.SetFocalPoint(new_focal)
        self.renderer.ResetCameraClippingRange()
        self.renderer.GetRenderWindow().Render()
        self.current_step += 1

    # --- Keyboard handler ---
    def on_key_press(self, obj, event):
        key = self.interactor.GetKeySym().lower()
        if key == 'r':
            self.toggle_rotation()
        elif key == 'f':
            self.reset_camera()
        elif key == 'q':
            self.interactor.GetRenderWindow().Finalize()
            self.interactor.TerminateApp()
