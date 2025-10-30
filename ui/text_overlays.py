# ui/text_overlays.py
import vtk


class TextOverlayManager:
    def __init__(self, renderer):
        self.renderer = renderer

        # Hover text
        self.hover_actor = vtk.vtkTextActor()
        self.hover_actor.GetTextProperty().SetFontSize(24)
        self.hover_actor.GetTextProperty().SetColor(1, 1, 0)
        self.hover_actor.SetPosition(20, 20)
        renderer.AddActor2D(self.hover_actor)

        # Hint bar
        self.hint_actor = vtk.vtkTextActor()
        self.hint_actor.GetTextProperty().SetFontSize(20)
        self.hint_actor.GetTextProperty().SetColor(0.8, 0.8, 0.8)
        self.hint_actor.GetTextProperty().SetJustificationToLeft()
        self.hint_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        self.hint_actor.SetPosition(0.02, 0.7)
        renderer.AddActor2D(self.hint_actor)

        # Initial state
        self.update_hints(rotation_enabled=False)

    def update_hints(self, rotation_enabled: bool):
        """Update the hint text with the current rotation state."""
        # Clear previous text first
        self.hint_actor.SetInput("")

        state = "Enabled" if rotation_enabled else "Disabled"
        self.hint_actor.SetInput(f"""
      Controls:
    • Hover bone → highlight name
    • Click bone → zoom & details
    • Click empty space → exit zoom
    • Press R → enable rotation (mouse left click and hold) 
    • While being zoomed on bone, rotation must
    • be made by holding on the bone.
    • Press F → reset camera
    • Press Q → quit
    """)
        self.renderer.GetRenderWindow().Render()

    def set_hover_text(self, text: str):
        """Set the text shown on hover."""
        self.hover_actor.SetInput(text)
        self.renderer.GetRenderWindow().Render()

    def update_rotation_hint(self, enabled: bool):
        """Convenience method for KeyHandler to update only the rotation state."""
        self.update_hints(rotation_enabled=enabled)