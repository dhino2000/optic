# アプリsetup        

def setupMainWindow(q_window, gui_defaults):
    q_window.setWindowTitle(gui_defaults["TITLE"])
    q_window.setGeometry(gui_defaults["INIT_POSITION_X"], gui_defaults["INIT_POSITION_Y"], gui_defaults["WIDTH"], gui_defaults["HEIGHT"])