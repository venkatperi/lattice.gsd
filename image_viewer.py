import pygame

from MovingAverageWithRate import MovingAverageWithRate

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
        self.fps = MovingAverageWithRate(1000)

        runner.lattice.surface = pygame.surfarray.make_surface(runner.lattice.rgb_image)

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

            self.screen.fill(BG_COLOR)

            self.screen.blit(lattice.surface, (self.border, self.border))

            x, fps = self.fps.add(1)
            self.text("{:#7,} | {:.2f}fps".format(
                lattice.generation, fps))

            total = lattice.x * lattice.y
            ratio = 1 if lattice.counts[2] == 0 else lattice.counts[0] / lattice.counts[2]
            self.text("R:{:,} | B:{:,} | R/B:{:.3f} | Rest:{:.3f}".format(
                lattice.counts[0],
                lattice.counts[2],
                ratio,
                (total - (lattice.counts[0] + lattice.counts[2])) / total),
                bottom=True)

            self.frame_count += 1
            self.clock.tick(self.updateRate)

            pygame.display.flip()
