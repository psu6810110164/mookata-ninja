from kivy.core.audio import SoundLoader
import time

paths = [
    'assets/sounds/slash.mp3',
    'assets/sounds/slash.wav',
    'assets/sounds/bomb.mp3',
    'assets/sounds/bgm.mp3',
]

print('Test Sound Loader')
for p in paths:
    print('-' * 40)
    print('Trying:', p)
    s = None
    try:
        s = SoundLoader.load(p)
    except Exception as e:
        print('Exception loading', p, e)
    print('Loaded ->', s)
    if s:
        try:
            s.volume = 0.8
            s.play()
            # wait a short time to hear it
            time.sleep(min(3, getattr(s, 'length', 1) or 1))
            s.stop()
        except Exception as e:
            print('Error playing', p, e)

print('Done')
