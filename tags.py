from datetime import datetime
from readxls import time_to_int


def color(c, t="time"):
    try:
        if t == "hour":
            if isinstance(c, str):
                c = int(c)
            if c <= 190:
#                print "color", c, t, "red"
                return "red"
            else:
                return "black"
        else:
            format1 = "%H:%M"
            color1 = "black"
            dt1 = datetime.strptime("11:45", format1)
            dt2 = datetime.strptime("12:30", format1)
            if len(c) > 5 and c[2] == ":":
                for c1 in c.split():
                    dt = datetime.strptime(c1, format1)
                    if dt >= dt1 and dt <= dt2:
#                        print "color", c, t, "blue"
                        color1 = "blue"
            return color1
    except Exception, e:
        pass
        #print "Error: ", e
    return "black"
