class CameraAnimator:
    """
    Handles smooth camera animation over time, using a VTK timer.
    Works together with CameraController.
    """

    def __init__(self, renderer, interactor, camera_controller, animation_steps=60):
        self.renderer = renderer
        self.interactor = interactor
        self.camera_controller = camera_controller
        self.camera = renderer.GetActiveCamera()

        # Animation config
        self.animation_steps = animation_steps
        self.current_step = 0
        self.timer_id = None

    def start_animation(self):
        """Start animation timer if not already running."""
        if self.timer_id is None:
            self.current_step = 0
            self.timer_id = self.interactor.CreateRepeatingTimer(16)

    def update_animation(self, obj, event):
        """Called each frame → smoothly updates camera position."""
        if self.current_step >= self.animation_steps:
            # Stop timer
            if self.timer_id is not None:
                self.interactor.DestroyTimer(self.timer_id)
                self.timer_id = None
            return

        t = (self.current_step + 1) / self.animation_steps

        # Manual linear interpolation (like old code)
        new_pos = [
            self.camera_controller.start_pos[i] + t * (self.camera_controller.end_pos[i] - self.camera_controller.start_pos[i])
            for i in range(3)
        ]
        new_focal = [
            self.camera_controller.start_focal[i] + t * (self.camera_controller.end_focal[i] - self.camera_controller.start_focal[i])
            for i in range(3)
        ]

        self.camera.SetPosition(new_pos)
        self.camera.SetFocalPoint(new_focal)
        self.renderer.ResetCameraClippingRange()
        self.renderer.GetRenderWindow().Render()

        self.current_step += 1
