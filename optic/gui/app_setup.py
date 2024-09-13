# アプリsetup 
def setupMainWindow(q_window, gui_defaults):
    q_window.setWindowTitle(gui_defaults["TITLE"])
    q_window.setGeometry(gui_defaults["WINDOW_SETTINGS"]["INIT_POSITION_X"], 
                         gui_defaults["WINDOW_SETTINGS"]["INIT_POSITION_Y"], 
                         gui_defaults["WINDOW_SETTINGS"]["WIDTH"], 
                         gui_defaults["WINDOW_SETTINGS"]["HEIGHT"])
    if gui_defaults["WINDOW_SETTINGS"].get("MIN_WIDTH") is not None:
        q_window.setMinimumWidth(gui_defaults["WINDOW_SETTINGS"]["MIN_WIDTH"])
    if gui_defaults["WINDOW_SETTINGS"].get("MIN_HEIGHT") is not None:
        q_window.setMinimumHeight(gui_defaults["WINDOW_SETTINGS"]["MIN_HEIGHT"])
    if gui_defaults["WINDOW_SETTINGS"].get("MAX_WIDTH") is not None:
        q_window.setMaximumWidth(gui_defaults["WINDOW_SETTINGS"]["MAX_WIDTH"])
    if gui_defaults["WINDOW_SETTINGS"].get("MAX_HEIGHT") is not None:
        q_window.setMaximumHeight(gui_defaults["WINDOW_SETTINGS"]["MAX_HEIGHT"])
    