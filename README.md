# 🦴 Anatomy Viewer Application

A modular, object-oriented **Python + VTK** application designed for visualizing human anatomy models.  
The project features a **main interactive menu** with multiple modules, including:
- Bone Anatomy Viewer  
- Muscle Anatomy (planned)  
- Settings (language switching)  
- Quit  

All menus and labels support **multiple languages** dynamically (English / Hungarian).

---

## 🧠 Features

### 🎛️ Main Menu
- Built with VTK 2D UI elements (`vtkTextActor`)
- Fully interactive with mouse hover and click detection
- Four main menu points:
  1. **Bone Anatomy** – Opens the `SkeletonViewerApp`
  2. **Muscle Anatomy** – Placeholder for future extension
  3. **Settings** – Allows language switching between English and Hungarian
  4. **Quit** – Exits the application gracefully

### 🦴 Skeleton Viewer
- Displays a **3D skeletal model** using VTK rendering
- Loads `.obj` model files dynamically
- Supports rotation, zoom, and model interaction
- Designed to be replaced or extended with other anatomy modules later

### ⚙️ Settings Menu
- Toggle interface language in real-time (English 🇬🇧 / Magyar 🇭🇺)
- Returns automatically to the main menu after selection
- Uses a centralized translation dictionary (`language/language.py`)

---

## 🗂️ Project Structure

