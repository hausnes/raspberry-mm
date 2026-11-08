# Små hjelpefunksjonar for lyd på Cosmic Unicorn
import time

_diff = time.ticks_diff
_add = time.ticks_add


def frekvens(midi):
    """Gjer om eit MIDI-notenummer (A4 = 69) til frekvens i Hz."""
    return int(440 * 2 ** ((midi - 69) / 12))


class Ko:
    """Ein enkel kø for lydhendingar som skal skje litt fram i tid.

    Bruk: ko.om(no, 50, kanal.trigger_release)  -> køyrer om 50 ms
    """

    def __init__(self):
        self.h = []

    def legg_til(self, naar, fn, *arg):
        self.h.append((naar, fn, arg))

    def om(self, no, ms, fn, *arg):
        self.h.append((_add(no, int(ms)), fn, arg))

    def kjor(self, no):
        if not self.h:
            return
        gjeld = self.h
        self.h = []
        for e in gjeld:
            if _diff(no, e[0]) >= 0:
                e[1](*e[2])
            else:
                self.h.append(e)

    def tom(self):
        self.h = []
