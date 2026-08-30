python3 -c "import RPi.GPIO as g, time; g.setmode(g.BCM); g.setup(18, g.OUT); g.output(18, True); time.sleep(2); g.cleanup()"
