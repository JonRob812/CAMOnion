
class CNCCalc:
    @staticmethod
    def rpm(dia, sfpm):
        return int((int(sfpm) * 3.82) / float(dia))

    @staticmethod
    def feedrate(rpm, feed, flutes):
        return round(float(rpm) * (int(flutes) * float(feed)), 2)
