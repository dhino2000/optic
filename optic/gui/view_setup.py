def setViewSize(q_view, width_min=None, width_max=None, height_min=None, height_max=None):
    if width_min:
        q_view.setMinimumWidth(width_min)
    if width_max:
        q_view.setMaximumWidth(width_max)
    if height_min:
        q_view.setMinimumHeight(height_min)
    if height_max:
        q_view.setMaximumHeight(height_max)