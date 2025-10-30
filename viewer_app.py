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
        self.render_window.FullScreenOn()

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)

        # Load 3D model
        self._load_model(obj_path)

        # Setup camera and UI
        self.text_mgr = TextOverlayManager(self.renderer)
        self.camera_ctrl = CameraController(
            self.renderer.GetActiveCamera(),
            self.renderer,
            self.interactor,
            text_overlay_manager=self.text_mgr
        )
        self.picker_handler = PickerHandler(
            self.interactor,
            self.renderer,
            self.actor_map,
            self.text_mgr,
            self.camera_ctrl
        )

    def _load_model(self, obj_path):
        loader = ObjLoader(obj_path)
        self.actors, self.actor_map = loader.load_grouped_obj()
        for actor in self.actors:
            self.renderer.AddActor(actor)
        self.renderer.ResetCamera()

    def run(self):
        self.render_window.Render()
        self.interactor.Start()
        print("Viewer closed, returning to main menu.")

    def load_viewer(self, obj_path):
        loader = ObjLoader(obj_path)
        actors, actor_map = loader.load_grouped_obj()
        for actor in actors:
            self.renderer.AddActor(actor)
        self.renderer.ResetCamera()

        self.text_mgr = TextOverlayManager(self.renderer)
        self.camera_ctrl = CameraController(self.renderer.GetActiveCamera(),
                                            self.renderer,
                                            self.interactor,
                                            text_overlay_manager=self.text_mgr)
        self.picker_handler = PickerHandler(self.interactor,
                                            self.renderer,
                                            actor_map,
                                            self.text_mgr,
                                            self.camera_ctrl)
