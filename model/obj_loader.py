# model/obj_loader.py
import vtk
import os


class ObjLoader:
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"OBJ file not found: {path}")
        self.path = path

    def load_grouped_obj(self):
        """
        Loads an OBJ file with 'g' groups.
        Returns: (actors_list, actor_to_name_map)
        """
        current_vertices = []
        current_faces = []
        current_group_name = None
        actors_list = []

        with open(self.path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        global_vertices = []
        vertex_map = {}

        for line in lines:
            line = line.strip()

            if line.startswith("v "):
                global_vertices.append([float(p) for p in line.split()[1:]])

            elif line.startswith("g "):
                # Save previous group if valid
                if current_group_name and current_faces:
                    actors_list.append((current_group_name, current_vertices, current_faces))

                # New group
                group_name = line[2:].strip()
                group_name = group_name.replace("_", " ")

                # Remove everything after first dot
                if "." in group_name:
                    group_name = group_name.split(".", 1)[0].strip()

                # Remove known suffixes
                suffixes_to_remove = ["male human skeleton", "female human skeleton"]
                for suffix in suffixes_to_remove:
                    if suffix.lower() in group_name.lower():
                        group_name = group_name.lower().replace(suffix.lower(), "").strip()

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

        # Final group
        if current_group_name and current_faces:
            actors_list.append((current_group_name, current_vertices, current_faces))

        vtk_actors = []
        actor_to_name_map = {}

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
            actor.SetPickable(True)  # Important for picker/hover
            actor.GetProperty().SetColor(1, 1, 1)
            actor.GetProperty().BackfaceCullingOn()

            vtk_actors.append(actor)
            actor_to_name_map[actor] = name

        return vtk_actors, actor_to_name_map
