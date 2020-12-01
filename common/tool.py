import time


# 获取当前时间
def get_now():
    now = int(time.time())
    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    time_array = time.localtime(now)
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    print(other_style_time)
    return other_style_time
