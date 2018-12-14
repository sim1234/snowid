class Context:
    """Object passed between scenes using start and stop methods"""

    def __init__(self, last_scene):
        self.last_scene = last_scene
