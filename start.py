import threading
from utils import eye_tracking
from utils import kb_mouse


# 开启眼动监测线程
thread_1 = threading.Thread(target=eye_tracking.monitor, args=[2560, 1600]) #传入屏幕分辨率
thread_1.start()

# 开启键鼠监测线程
thread_2 = threading.Thread(target=kb_mouse.monitor)
thread_2.start()

# 等待线程结束
thread_1.join()
thread_2.join()
