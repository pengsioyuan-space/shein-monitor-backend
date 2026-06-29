
def level(hours, t1, t2):
    if hours >= t2:
        return "严重"
    if hours >= t1:
        return "轻微"
    return "正常"
