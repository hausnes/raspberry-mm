from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
import time

gu = GalacticUnicorn()
g = PicoGraphics(DISPLAY)
gu.set_brightness(0.5)

farger = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
while True:
    for f in farger:
        g.set_pen(g.create_pen(*f))
        g.clear()
        gu.update(g)
        time.sleep(2)