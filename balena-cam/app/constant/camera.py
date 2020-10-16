resolution_presets = dict()
resolution_presets["cv2"] = dict()
resolution_presets["cv2"]["default"] = (640, 480)
resolution_presets["cv2"][1280] = (1280, 704)
resolution_presets["cv2"][1920] = (1920, 1088)

# picamera
resolution_presets["picamera"] = dict()
resolution_presets["picamera"]["default"] = (640, 480)
resolution_presets["picamera"][640] = (640, 480)
resolution_presets["picamera"][1280] = (1280, 720)
resolution_presets["picamera"][1920] = (1920, 1088)
