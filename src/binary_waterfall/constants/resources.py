import os

from . import paths

RESOURCE_PATH = os.path.join(paths.PATH, "resources")

# A dict to store icon locations (using SVG vector icons)
ICON_PATHS = {
    "program": os.path.join(RESOURCE_PATH, "icon.png"),
    "button": {
        "play": {
            "base": os.path.join(RESOURCE_PATH, "play.svg"),
            "clicked": os.path.join(RESOURCE_PATH, "playC.svg"),
            "hover": os.path.join(RESOURCE_PATH, "playH.svg")
        },
        "pause": {
            "base": os.path.join(RESOURCE_PATH, "pause.svg"),
            "clicked": os.path.join(RESOURCE_PATH, "pauseC.svg"),
            "hover": os.path.join(RESOURCE_PATH, "pauseH.svg")
        },
        "back": {
            "base": os.path.join(RESOURCE_PATH, "back.svg"),
            "clicked": os.path.join(RESOURCE_PATH, "backC.svg"),
            "hover": os.path.join(RESOURCE_PATH, "backH.svg")
        },
        "forward": {
            "base": os.path.join(RESOURCE_PATH, "forward.svg"),
            "clicked": os.path.join(RESOURCE_PATH, "forwardC.svg"),
            "hover": os.path.join(RESOURCE_PATH, "forwardH.svg")
        },
        "restart": {
            "base": os.path.join(RESOURCE_PATH, "restart.svg"),
            "clicked": os.path.join(RESOURCE_PATH, "restartC.svg"),
            "hover": os.path.join(RESOURCE_PATH, "restartH.svg")
        }
    },
    "volume": {
        "base": os.path.join(RESOURCE_PATH, "volume.svg"),
        "mute": os.path.join(RESOURCE_PATH, "mute.svg")
    },
    "watermark": os.path.join(RESOURCE_PATH, "watermark.png")
}