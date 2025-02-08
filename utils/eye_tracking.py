import sys
import clr
from time import time
from os import makedirs
from os.path import join, dirname, abspath, exists


dlls_folder = join(dirname(abspath(__file__)), "DLLs")
sys.path.append(dlls_folder)
clr.AddReference("tobii_interaction_lib_cs")
import Tobii.InteractionLib as Lib


def event_handler(event: Lib.GazePointData, save_path):
    x = event.x
    y = event.y
    is_valid = event.validity == Lib.Validity.Valid

    if is_valid and x > 0 and y > 0:
        t = time()
        data = "{},{},{}\n".format(t, x, y)
        with open(save_path, "a") as f:
            f.write(data)


def monitor(screen_width=2560, screen_height=1600):
    save_dir = 'data'
    if not exists(save_dir):
        makedirs(save_dir)
    save_path = join(save_dir, "eye_tracking.csv")
    lib = Lib.InteractionLibFactory.CreateInteractionLib(Lib.FieldOfUse.Interactive)
    lib.CoordinateTransformAddOrUpdateDisplayArea(screen_width, screen_height)
    lib.CoordinateTransformSetOriginOffset(0, 0)
    lib.GazePointDataEvent += lambda event: event_handler(event, save_path)
    with open(save_path, "w") as f:
        f.write("time,x,y\n")
    while True:
        lib.WaitAndUpdate()
        print("眼动监测中...")


if __name__ == "__main__":
    monitor()
