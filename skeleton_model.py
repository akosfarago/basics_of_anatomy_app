import vtk
import os
import math

# Path to your OBJ
model_path = os.path.join("models", "male_human_skeleton.obj")


# Function to load OBJ as separate vtkPolyData objects per group
def load_obj_groups(filename):
    actors = []
    actor_name_map = {}  # map actor -> bone_name

    current_vertices = []
    current_faces = []
    current_group_name = None

    actors_list = []

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    global_vertices = []

    for line in lines:
        line = line.strip()
        if line.startswith("v "):
            global_vertices.append([float(p) for p in line.split()[1:]])
        elif line.startswith("g "):
            # Save previous group if it had faces
            if current_group_name and current_faces:
                actors_list.append((current_group_name, current_vertices, current_faces))

            # Get new group name and clean it
            group_name = line[2:].strip()
            group_name = group_name.replace("_", " ")

            # Remove everything after the first dot (e.g. ".003", ".059", ".male human skeleton")
            if "." in group_name:
                group_name = group_name.split(".", 1)[0].strip()

            # (Optional) Remove known trailing suffixes like "male human skeleton"
            suffixes_to_remove = ["male human skeleton", "female human skeleton"]
            for suffix in suffixes_to_remove:
                if suffix.lower() in group_name.lower():
                    group_name = group_name.lower().replace(suffix.lower(), "").strip()

            current_group_name = group_name

            # Start new group
            current_group_name = group_name
            current_vertices = []
            current_faces = []
            vertex_map = {}
        elif line.startswith("f "):
            face = []
            for p in line[2:].split():
                idx = int(p.split("/")[0]) - 1
                if idx not in vertex_map:
                    vertex_map[idx] = len(current_vertices)
                    current_vertices.append(global_vertices[idx])
                face.append(vertex_map[idx])
            current_faces.append(face)

    if current_group_name and current_faces:
        actors_list.append((current_group_name, current_vertices, current_faces))

    vtk_actors = []
    for name, verts, faces in actors_list:
        points = vtk.vtkPoints()
        for v in verts:
            points.InsertNextPoint(v)

        polys = vtk.vtkCellArray()
        for f in faces:
            polys.InsertNextCell(len(f))
            for idx in f:
                polys.InsertCellPoint(idx)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(polys)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.SetPickable(True)
        actor.GetProperty().SetColor(1, 1, 1)
        actor.GetProperty().BackfaceCullingOn()

        vtk_actors.append(actor)
        actor_name_map[actor] = name

    return vtk_actors, actor_name_map


# --- Create renderer, window, interactor ---
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(1920, 980)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Disable rotation, zoom, pan
interactor_style = vtk.vtkInteractorStyleUser()
interactor.SetInteractorStyle(interactor_style)

# --- Load OBJ and create actors ---
actors, actor_name_map = load_obj_groups(model_path)
for a in actors:
    renderer.AddActor(a)

renderer.ResetCamera()

# Now store original camera position and focal
original_camera_pos = list(renderer.GetActiveCamera().GetPosition())
original_camera_focal = list(renderer.GetActiveCamera().GetFocalPoint())

camera = renderer.GetActiveCamera()

pre_zoom_camera_state = None  # Stores camera state before zoom-in

# Save initial camera state
initial_camera_state = {
    "position": camera.GetPosition(),
    "focal_point": camera.GetFocalPoint(),
    "view_up": camera.GetViewUp(),
    "view_angle": camera.GetViewAngle(),
}

# --- Picker ---
picker = vtk.vtkCellPicker()
picker.SetTolerance(0.0005)

# --- Text display ---
text_actor = vtk.vtkTextActor()
text_actor.GetTextProperty().SetFontSize(24)
text_actor.GetTextProperty().SetColor(1, 1, 0)
text_actor.SetPosition(20, 20)
renderer.AddActor2D(text_actor)

# --- Hint / Help Bar ---

# --- Rotation state ---
rotation_enabled = False  # New toggle


def update_hints():
    """Update hint text based on rotation state."""
    state = "Enabled" if rotation_enabled else "Disabled"
    hint_actor.SetInput(f"""
  Controls:
• Hover bone → highlight name
• Click bone → zoom & details
• Click empty space → exit zoom
• Press R → enable rotation ({state})
• Press F → reset camera
• Press Q → quit
""")
    render_window.Render()


# --- Hint / Help Bar ---
hint_actor = vtk.vtkTextActor()
hint_actor.GetTextProperty().SetFontSize(20)
hint_actor.GetTextProperty().SetColor(0.8, 0.8, 0.8)
hint_actor.GetTextProperty().SetJustificationToLeft()
hint_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
hint_actor.SetPosition(0.02, 0.7)  # 2% from left, 70% up from bottom
renderer.AddActor2D(hint_actor)

# Initialize hint text properly
update_hints()


def rotate_camera(cam, axis, angle_deg):
    """Rotate camera around focal point along given axis ('x' or 'y') by angle in degrees."""
    angle_rad = math.radians(angle_deg)
    pos = list(cam.GetPosition())
    focal = list(cam.GetFocalPoint())

    # Vector from focal to camera
    vec = [pos[i] - focal[i] for i in range(3)]

    # Rotation matrices
    if axis == 'y':  # left/right
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        x = vec[0] * cos_a + vec[2] * sin_a
        z = -vec[0] * sin_a + vec[2] * cos_a
        vec[0], vec[2] = x, z
    elif axis == 'x':  # up/down
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        y = vec[1] * cos_a - vec[2] * sin_a
        z = vec[1] * sin_a + vec[2] * cos_a
        vec[1], vec[2] = y, z

    # New camera position
    new_pos = [focal[i] + vec[i] for i in range(3)]
    cam.SetPosition(new_pos)
    cam.SetFocalPoint(focal)
    renderer.ResetCameraClippingRange()
    render_window.Render()


# --- Keyboard events ---
def on_key_press(obj, event):
    global rotation_enabled, camera
    key = interactor.GetKeySym().lower()

    if key == 'r':
        rotation_enabled = not rotation_enabled
        print(f"Rotation Enabled: {rotation_enabled}")
        if rotation_enabled:
            interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        else:
            interactor.SetInteractorStyle(vtk.vtkInteractorStyleUser())  # Reset to non-rotation mode
        update_hints()
    elif key.lower() == 'f':
        # Only reset if not zooming / zoomed into a bone
        if not bone_zoom_state:
            camera.SetPosition(initial_camera_state["position"])
            camera.SetFocalPoint(initial_camera_state["focal_point"])
            camera.SetViewUp(initial_camera_state["view_up"])
            camera.SetViewAngle(initial_camera_state["view_angle"])
            renderer.ResetCameraClippingRange()
            render_window.Render()
        else:
            print("Cannot reset camera while zoomed in. Click empty space to exit zoom first.")

    elif key == 'q':
        interactor.GetRenderWindow().Finalize()
        interactor.TerminateApp()


# --- Hover callback ---
previous_actor = None


def on_mouse_move(obj, event):
    global previous_actor
    x, y = interactor.GetEventPosition()
    picker.Pick(x, y, 0, renderer)
    picked_actor = picker.GetActor()

    # Reset previous highlight
    if previous_actor and previous_actor != picked_actor:
        previous_actor.GetProperty().SetColor(1, 1, 1)

    if picked_actor and picked_actor in actor_name_map:
        bone_name = actor_name_map[picked_actor]
        text_actor.SetInput(f"Hovered: {bone_name}")
        picked_actor.GetProperty().SetColor(1, 1, 0)
        previous_actor = picked_actor
    else:
        text_actor.SetInput("")
        previous_actor = None

    render_window.Render()


# --- Camera animation setup ---
bone_zoom_state = False  # True if currently zoomed in on a bone
target_actor = None
animation_steps = 60  # number of frames for smooth zoom
current_step = 0
start_pos = [0, 0, 0]
start_focal = [0, 0, 0]
end_pos = [0, 0, 0]
end_focal = [0, 0, 0]


def get_actor_center(actor):
    """Compute center of the actor's polydata"""
    bounds = actor.GetMapper().GetInput().GetBounds()
    center = [(bounds[0] + bounds[1]) / 2,
              (bounds[2] + bounds[3]) / 2,
              (bounds[4] + bounds[5]) / 2]
    return center


# --- Global timer id ---
timer_id = None


def start_zoom_animation(actor=None):
    global bone_zoom_state, target_actor, current_step, timer_id
    global start_pos, start_focal, end_pos, end_focal, pre_zoom_camera_state

    cam = renderer.GetActiveCamera()

    if not bone_zoom_state and actor:
        # Save camera state BEFORE zoom-in
        pre_zoom_camera_state = {
            "position": cam.GetPosition(),
            "focal_point": cam.GetFocalPoint(),
            "view_up": cam.GetViewUp(),
            "view_angle": cam.GetViewAngle(),
        }

        # Zoom in
        start_pos = list(cam.GetPosition())
        start_focal = list(cam.GetFocalPoint())
        end_focal = get_actor_center(actor)
        direction = [start_pos[i] - start_focal[i] for i in range(3)]
        mag = sum(d * d for d in direction) ** 0.5
        scale = 0.3 * mag
        end_pos = [end_focal[i] + direction[i] / mag * scale for i in range(3)]

        bone_zoom_state = True
        target_actor = actor

    elif bone_zoom_state:
        # Zoom OUT → restore pre-zoom camera state
        start_pos = list(cam.GetPosition())
        start_focal = list(cam.GetFocalPoint())

        if pre_zoom_camera_state:
            end_pos = list(pre_zoom_camera_state["position"])
            end_focal = list(pre_zoom_camera_state["focal_point"])
            cam.SetViewUp(pre_zoom_camera_state["view_up"])
            cam.SetViewAngle(pre_zoom_camera_state["view_angle"])
        else:
            end_pos = original_camera_pos.copy()
            end_focal = original_camera_focal.copy()

        bone_zoom_state = False
        target_actor = None

    # ✅ Reset animation step and start timer
    current_step = 0
    if timer_id is None:
        timer_id = interactor.CreateRepeatingTimer(16)


def animate_camera(obj, event):
    global current_step, timer_id
    cam = renderer.GetActiveCamera()
    if current_step >= animation_steps:
        if timer_id is not None:
            interactor.DestroyTimer(timer_id)  # use stored timer id
            timer_id = None
        return

    t = (current_step + 1) / animation_steps
    new_pos = [start_pos[i] + t * (end_pos[i] - start_pos[i]) for i in range(3)]
    new_focal = [start_focal[i] + t * (end_focal[i] - start_focal[i]) for i in range(3)]
    cam.SetPosition(new_pos)
    cam.SetFocalPoint(new_focal)
    renderer.ResetCameraClippingRange()
    render_window.Render()
    current_step += 1


# --- Override click callback ---
def on_left_button_press(obj, event):
    x, y = interactor.GetEventPosition()
    picker.Pick(x, y, 0, renderer)
    picked_actor = picker.GetActor()
    if picked_actor and picked_actor in actor_name_map:
        bone_name = actor_name_map[picked_actor]
        print(f"Clicked on bone: {bone_name}")
        start_zoom_animation(picked_actor)
    elif bone_zoom_state:
        # Clicked empty space while zoomed in → zoom out
        start_zoom_animation(None)


interactor.AddObserver("LeftButtonPressEvent", on_left_button_press)
interactor.AddObserver("TimerEvent", animate_camera)
interactor.AddObserver("MouseMoveEvent", on_mouse_move)
interactor.AddObserver("KeyPressEvent", on_key_press)

# --- Start ---
renderer.SetBackground(0.1, 0.1, 0.1)
render_window.Render()
interactor.Start()
