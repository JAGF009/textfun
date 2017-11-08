from datetime import datetime, timedelta
from random import random
from functools import partial


class WrapperWithCallback:

    def __init__(self, *args, done=None, done_arg=None, **kwargs):
        if done is None:
            # I dont care about callbacks so well, I do nothing
            self.done_callback = lambda: None
        elif done_arg == 'self':
            # I cant get an instance of myself from outside on defining the class (well i could with a metaclass
            # or something like that
            # but this is easier and the other is not worth my time.
            self.done_callback = partial(done, self)
        else:
            # You just gave me a callback! Nice, I will call that when I'm done, notice that if you keep calling next()
            # I will still give you the render, so stop calling me when you don't want more texts!.
            self.done_callback = done
        self.done_notified = False



class FontWrapper(WrapperWithCallback):
    """A class to do that effect that we love, yes, you love it too!
    Just define me and then call me.render(screen, pos) so i will display myself, NICE!
    If you want a callback when i'm done, then define it as the done argument it has to be a callable tho. if you want
    me to call that function with a reference of myself, then just give me a callback and 'self' as done_arg argument
    That's the easiest way to deque me!"""

    BLOCK = '_'

    def __init__(self, font, text, color=(255, 255, 255), delay_range=(0.05, 0.15),
                 loop=False, awake=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = font
        self.text = text
        self.text_len = len(self.text)
        self.i, self.color, self.loop = 0, color, loop
        self.delay_generator = lambda: timedelta(0, delay_range[0] + random() * (delay_range[1] - delay_range[0]))
        self.delay = self.delay_generator()
        self.now = datetime.now()
        self.last_render = None
        self._aware_orig = self._awake = awake

    def next(self):
        if not self._awake:
            return None
        if datetime.now() - self.now > self.delay or self.last_render is None:
            if self.i < self.text_len:
                # Did I say I notified? well... I didn't because I got reseted, weird stuff happens, I tell you.
                if self.done_notified:
                    self.done_notified = False
                # i is still less than length so i'm not done, keep going!
                self.i += 1
                text_to_render = self.text[:self.i] + self.BLOCK if self.i % 2 else self.text[:self.i]
                self.last_render = self.font.render(text_to_render, 0, self.color)
                self.now = datetime.now()
                self.delay = self.delay_generator()
            elif self.loop:
                # i is equal to text length so i was done last next call, i will notify with done_callback
                # but since i'm gonna loop myself i'm not done again, so dont touch the bool
                self.i = 0
                self.now = datetime.now()
                if not self.done_notified:
                    self.done_callback()
            else:
                # I'm done again, and this time for good, so I am going to notify it and tell myself not to do it
                # again with the bool
                if not self.done_notified:
                    self.done_callback()
                    self.done_notified = True
                    # And btw I dont want the BLOCK to stay there so... lets render the text one last time:
                    self.last_render = self.font.render(self.text, 0, self.color)
        return self.last_render

    def reset(self, new_text=None):
        if new_text is not None:
            self.text = new_text
            self.text_len = len(self.text)
        self.i, self.now, self.last_render = 0, datetime.now(), None
        self._awake = self._aware_orig

    @property
    def awake(self):
        return self._awake

    @awake.setter
    def awake(self, value):
        if not isinstance(value, bool):
            raise TypeError('Expected awake value to be bool got %s' % type(value))
        if value:
            self.now = datetime.now()
        self._awake = value

    def blit(self, screen, pos):
        screen.blit(self.next(), pos)


class MultiLineFontWrapper(WrapperWithCallback):

    def __init__(self, font, text, max_h_len, bias=0, color=(255, 255, 255), loop=False,
                 delay_range=(0.05, 0.15), no_sense=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.v_size = font.get_height() + bias  # 10 less just for this font, it looks cool that way!
        self.loop = loop
        words = text.split()
        texts = []
        buff = []
        buff_ap = buff.append
        for w in words:
            buff_ap(w)
            if sum([len(w) for w in buff]) + len(buff) - 1 > max_h_len:
                texts.append(" ".join(buff[:-1]))
                temp = buff[-1]
                buff.clear()
                buff_ap(temp)
        if buff:
            texts.append(" ".join(buff))

        self.font_wrappers = [FontWrapper(font, t, color=color, awake=False, delay_range=delay_range, loop=no_sense,
                                          done=partial(self._done, i)) \
                              for i, t in enumerate(texts)]

    def _done(self, i):
        try:
            self.font_wrappers[i+1].awake = True
        except IndexError:
            # All of the fw are done, tried to access n, where n = len(self.font_wrappers)
            if not self.done_notified:
                self.done_callback()
                self.done_notified = True
            if self.loop:
                self.reset()

    def blit(self, screen, pos):
        if not self.font_wrappers[0].awake:
            self.font_wrappers[0].awake = True
        for i, fw in enumerate(self.font_wrappers):
            surface = fw.next()
            if surface:
                screen.blit(surface, (pos[0], pos[1] + i * self.v_size))

    def reset(self):
        for fw in self.font_wrappers:
            fw.reset()
        self.done_notified = False


def simplify_mlw(max_h_len, bias, color, done=None, done_arg=None):
    simple = partial(
        MultiLineFontWrapper,
        max_h_len=max_h_len,
        bias=bias,
        color=color,
        done=done,
        done_arg=done_arg
    )
    return simple

