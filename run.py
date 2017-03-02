import cocos
from cocos.sprite import Sprite
from pyaudio import PyAudio, paInt16
import struct
from object import Object
from block import Block
import config
import time


class VoiceGame(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self):
        super(VoiceGame, self).__init__(255, 255, 255, 255, 800, 600)
        self.init_time = time.time()
        self.NUM_SAMPLES = 1000
        self.LEVEL = 1500

        self.score = 0
        self.txt_score = cocos.text.Label(u'score：0',
                                          font_name="Arial",
                                          font_size=24,
                                          color=(0, 0, 0, 255))
        self.txt_score.position = 400, 440
        self.add(self.txt_score, 99999)

        self.voice_bar = Sprite('block.png', color=(0, 0, 255))
        self.voice_bar.position = 20, 450
        self.voice_bar.scale_y = 0.1
        self.voice_bar.image_anchor = 0, 0
        self.add(self.voice_bar)

        self.object = Object()
        self.add(self.object)

        self.floor = cocos.cocosnode.CocosNode()
        self.add(self.floor)
        pos = 0, 100
        for i in range(100):
            b = Block(pos)
            self.floor.add(b)
            pos = b.x + b.width, b.height

        pa = PyAudio()
        sampling_rate = int(pa.get_device_info_by_index(0)['defaultSampleRate'])
        self.stream = pa.open(format=paInt16, channels=1, rate=sampling_rate, input=True, frames_per_buffer=self.NUM_SAMPLES)

        self.schedule(self.update)

    def on_mouse_press(self, x, y, buttons, modifiers):
        pass

    def collide(self):
        px = self.object.x - self.floor.x
        for b in self.floor.get_children():
            if b.x <= px + self.object.width * 0.8 and px + self.object.width * 0.2 <= b.x + b.width:
                if self.object.y < b.height:
                    self.object.land(b.height)
                    break

    def update(self, dt):
        time_temp = time.time() - self.init_time
        self.init_time = time.time()
        self.score += time_temp / 10
        self.txt_score.element.text = u'score：%d' % self.score
        string_audio_data = self.stream.read(self.NUM_SAMPLES)
        volume = max(struct.unpack('1000h', string_audio_data))
        self.voice_bar.scale_x = volume / 10000.0
        volume -= config.sensitivity
        if volume > 3000:
            self.floor.x -= min((volume / 20.0), 150 * config.run_boost) * dt
            self.score += 1/10
            self.txt_score.element.text = u'score：%d' % self.score
        if volume > 8000:
            self.object.jump((volume - 8000) / 1000 * config.jump_boost)
            self.score += 1/10
            self.txt_score.element.text = u'score：%d' % self.score
        self.collide()

    def reset(self):
        self.floor.x = 0
        self.score = 0
        self.txt_score.element.text = u'score: 0'


cocos.director.director.init(caption="CaoNiMa")
cocos.director.director.run(cocos.scene.Scene(VoiceGame()))
