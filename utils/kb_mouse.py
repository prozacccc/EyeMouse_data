from time import time
from os.path import join, exists
from os import makedirs
from pynput import keyboard, mouse


def monitor():
    save_dir = 'data'
    
    if not exists(save_dir):
        makedirs(save_dir)

    def on_key_press(key):
        print(f"键盘按下: {key}")
        with open(join(save_dir, "KB.csv"), "a") as f:
            f.write("{},{}\n".format(time(), key))

    def on_move(x, y):
        print("鼠标移动到 {0}".format((x, y)))
        with open(join(save_dir, "Move.csv"), "a") as f:
            f.write("{},{},{}\n".format(time(), x, y))

    def on_click(x, y, button, pressed):
        print("{0} {1}".format("鼠标点击" if pressed else "鼠标释放", (x, y)))
        if pressed:
            with open(join(save_dir, "Click.csv"), "a") as f:
                f.write("{},{},{}\n".format(time(), x, y))

    def on_scroll(x, y, dx, dy):
        direction = "down" if dy < 0 else "up"
        print("鼠标滚轮{0}-{1}".format(direction, (x, y)))
        with open(join(save_dir, "Scroll.csv"), "a") as f:
            f.write("{},{},{},{}\n".format(time(), x, y, direction))

    with open(join(save_dir, "KB.csv"), "w") as f:
        f.write("time,key\n")
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    keyboard_listener.start()

    with open(join(save_dir, "Click.csv"), "w") as f:
        f.write("time,x,y,\n")
    with open(join(save_dir, "Move.csv"), "w") as f:
        f.write("time,x,y,\n")
    with open(join(save_dir, "Scroll.csv"), "w") as f:
        f.write("time,x,y,direction\n")
    mouse_listener = mouse.Listener(
        on_move=on_move, on_click=on_click, on_scroll=on_scroll
    )
    mouse_listener.start()

    keyboard_listener.join()
    mouse_listener.join()
