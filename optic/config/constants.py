# アプリ間で共有する定数
class FileFilters:
    MAT = "mat Files (*.mat);;All Files (*)"
    TIFF = "tiff Files (*.tif *.tiff);;All Files (*)"
    NPY = "npy Files (*.npy);;All Files (*)"

class GUIDefaults:
    ROI_OPACITY = 50
    SELECTED_ROI_OPACITY = 255
    MIN_PLOT_RANGE = 30
    MIN_WINDOW_WIDTH = 600
    MIN_WINDOW_HEIGHT = 400
    MIN_CANVAS_WIDTH = 400
    MIN_CANVAS_HEIGHT = 300

class ProcessingDefaults:
    RESPONSE_THRESHOLD = 30

class Colors:
    F = 'cyan'
    FNEU = 'red'
    SPKS = 'gray'
    EVENT = 'green'