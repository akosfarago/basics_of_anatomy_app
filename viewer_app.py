import vtk
from model.obj_loader import ObjLoader
from camera.camera_controller import CameraController
from ui.picker_handler import PickerHandler
from ui.text_overlays import TextOverlayManager


class SkeletonViewerApp:
    def __init__(self, obj_path):
        # Core renderer setup
        self.renderer = vtk.vtkRenderer()
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetSize(1920, 980)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)

        # Load model
        loader = ObjLoader(obj_path)
        self.actors, self.actor_map = loader.load_grouped_obj()
        for actor in self.actors:
            self.renderer.AddActor(actor)

        self.renderer.ResetCamera()

        # Setup camera and UI
        self.text_mgr = TextOverlayManager(self.renderer)
        self.camera_ctrl = CameraController(self.renderer.GetActiveCamera(),
                                            self.renderer,
                                            self.interactor,
                                            text_overlay_manager=self.text_mgr)
        self.text_mgr = TextOverlayManager(self.renderer)
        self.picker_handler = PickerHandler(self.interactor,
                                            self.renderer,
                                            self.actor_map,
                                            self.text_mgr,
                                            self.camera_ctrl)

    def run(self):
        self.render_window.Render()
        self.interactor.Start()
