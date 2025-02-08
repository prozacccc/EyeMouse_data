from pynput import mouse

def on_move(x, y):
    print('Mouse moved to ({0}, {1})'.format(x, y))

def on_click(x, y, button, pressed):
    if pressed:
        print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))

# 监听鼠标移动事件
with mouse.Listener(on_move=on_move) as listener_move:
    # 监听鼠标点击事件
    with mouse.Listener(on_click=on_click) as listener_click:
        # 持续监听鼠标事件
        listener_click.join()
