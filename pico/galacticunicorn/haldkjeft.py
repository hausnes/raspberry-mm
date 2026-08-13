import time
from galactic import GalacticUnicorn, Channel
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

# Oppsett
gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

gu.set_brightness(0.5)

# Endre dette tallet for å justere hvor ofte teksten skifter.
# Lavere verdi = raskere bytte, høyere verdi = saktere bytte.
SWITCH_INTERVAL_SECONDS = 1.2
TONE_PULSE_INTERVAL_SECONDS = 0.25

TEXT_1 = "HALD KJEFT!"
TEXT_2 = "MØTE PÅGÅR!"
TEXT_COLOUR = (255, 170, 0)
TEXT_2_COLOUR = (255, 0, 255)  # veldig skrikende magenta/fuchsia for bilde 2
OUTLINE_COLOUR = (0, 0, 0)
BACKGROUND_COLOUR = (12, 8, 20)

# Synth-setup for den taktfastetone som kan slås på/av med knapp A.
tone_channel = gu.synth_channel(0)
tone_channel.configure(
    waveforms=Channel.SQUARE,
    attack=0.010,
    decay=0.020,
    sustain=0,
    release=0.120,
    volume=18000 / 65535,
)

def draw_message(text):
    graphics.set_pen(graphics.create_pen(BACKGROUND_COLOUR[0], BACKGROUND_COLOUR[1], BACKGROUND_COLOUR[2]))
    graphics.clear()

    graphics.set_font("bitmap8")
    text_width = graphics.measure_text(text, 1)
    x = int((width - text_width) / 2)
    y = 2

    graphics.set_pen(graphics.create_pen(OUTLINE_COLOUR[0], OUTLINE_COLOUR[1], OUTLINE_COLOUR[2]))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            graphics.text(text, x + dx, y + dy, -1, 1)

    colour = TEXT_COLOUR if text == TEXT_1 else TEXT_2_COLOUR
    graphics.set_pen(graphics.create_pen(colour[0], colour[1], colour[2]))
    graphics.text(text, x, y, -1, 1)
    gu.update(graphics)


def toggle_tone():
    global tone_enabled, tone_is_on, last_tone_toggle
    tone_enabled = not tone_enabled
    if tone_enabled:
        gu.play_synth()
        tone_channel.frequency(660)  # høyere og mer skrikende tone
        tone_channel.trigger_attack()
        tone_is_on = True
    else:
        tone_channel.trigger_release()
        tone_is_on = False
    last_tone_toggle = time.ticks_ms()


tone_enabled = False
tone_is_on = False
show_text_1 = True
button_was_pressed = False
last_message_switch = time.ticks_ms()
last_tone_toggle = time.ticks_ms()

while True:
    now = time.ticks_ms()

    # Bytt tekst mellom de to valgene med valgt frekvens.
    if now - last_message_switch >= SWITCH_INTERVAL_SECONDS * 1000:
        show_text_1 = not show_text_1
        last_message_switch = now

    if show_text_1:
        draw_message(TEXT_1)
    else:
        draw_message(TEXT_2)

    # Knapp A: slå på/av en taktfast tone som repeteres i en loop.
    if gu.is_pressed(GalacticUnicorn.SWITCH_A):
        if not button_was_pressed:
            toggle_tone()
        button_was_pressed = True
    else:
        button_was_pressed = False

    if tone_enabled and now - last_tone_toggle >= TONE_PULSE_INTERVAL_SECONDS * 1000:
        if tone_is_on:
            tone_channel.trigger_release()
            tone_is_on = False
        else:
            tone_channel.frequency(660)
            tone_channel.trigger_attack()
            tone_is_on = True
        last_tone_toggle = now

    time.sleep(0.01)