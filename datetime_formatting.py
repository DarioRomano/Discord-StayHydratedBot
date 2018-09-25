import datetime


def read_timedelta(args: list):
    keys = ["D", "M", "S", "H"]
    units = {key: 0 for key in keys}
    for arg in args:
        units[arg[-1:].upper()] = int(arg[:-1])
    return datetime.timedelta(days=units["D"], minutes=units["M"]+60*units["H"], seconds=units["S"])


def neat_timedelta(time: datetime.timedelta):
    seconds = time.seconds
    hours = seconds // (60*60)
    minutes = (seconds // 60) - (hours * 60)
    names = {"days": time.days, "hours": hours, "minutes": minutes, "seconds": seconds % 60}
    keys = names.keys()
    ret = ""
    for key in keys:
        if names[key] == 1:
            ret += ("1 %s " % key[:-1])
        elif names[key] > 1:
            ret += ("%i %s " % (names[key], key))
    if ret == "":
        return "0 seconds"
    else:
        return ret.strip()

