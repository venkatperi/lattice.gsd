import pygame

from StreamingMovingAverage import StreamingMovingAverage

BG_COLOR = (20, 20, 20)
FONT_NAME = "font/RobotoMono-Regular.ttf"
FONT_SIZE = 12
TEXT_COLOR = (200, 200, 200)


class ImageViewer(object):
    def __init__(self, width, height, runner, border=50,
                 updateRate=60,
                 caption="ImageViewer",
                 autoStop=False):

        pygame.init()
        self.width = width
        self.height = height
        self.runner = runner
        self.border = border
        self.updateRate = updateRate
        self.screen = pygame.display.set_mode(
            (width + (2 * border), height + (2 * border)),
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.frame_count = 0
        self.done = False
        self.autoStop = autoStop
        self.prevGeneration = 0
        self.average = StreamingMovingAverage(100)

        # clear screen
        self.screen.fill(BG_COLOR)

    def text(self, txt, bottom=False):
        w, h = self.font.size(txt)
        t = self.font.render(txt, True, TEXT_COLOR, BG_COLOR)

        x = (self.width + 2 * self.border - w) / 2
        y = (self.border - h) / 2
        y += self.height + self.border if bottom else 0
        self.screen.blit(t, (x, y))

    def start(self):
        while not self.done:
            if not self.runner.isAlive() and self.autoStop:
                pygame.quit()
                return

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

            lattice = self.runner.lattice
            lattice.lock.acquire()

            diff = lattice.generation - self.prevGeneration
            self.prevGeneration = lattice.generation
            average, gps = self.average.process(diff, pygame.time.get_ticks())

            self.clock.tick(self.updateRate)
            self.screen.fill(BG_COLOR)

            surface = pygame.surfarray.make_surface(lattice.to_rgb_image())
            self.screen.blit(surface, (self.border, self.border))

            self.text("{0:,} ({1:,}/s) {2}fps".format(
                lattice.generation, int(gps), int(self.clock.get_fps())))

            self.text("R:{0:,}, B:{1:,}".format(
                self.runner.lattice.counts[0],
                self.runner.lattice.counts[2]),
                bottom=True)

            lattice.lock.release()
            pygame.display.flip()
