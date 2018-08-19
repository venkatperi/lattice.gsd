import pygame

BG_COLOR = (20, 20, 20)
FONT_NAME = "font/RobotoMono-Regular.ttf"
FONT_SIZE = 12
TEXT_COLOR = (200, 200, 200)


class ImageViewer(object):
    def __init__(self, width, height, runner, border=40,
                 caption="ImageViewer", autoStop=False):

        pygame.init()
        self.width = width
        self.height = height
        self.runner = runner
        self.border = border
        self.screen = pygame.display.set_mode(
            (width + (2 * border), height + (2 * border)),
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.frame_count = 0
        self.done = False
        self.autoStop = autoStop

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

            self.screen.fill(BG_COLOR)
            # self.screen.fill(BG_COLOR, (0, 0, self.width, self.border))
            # self.screen.fill(BG_COLOR, (0, self.height + self.border, self.width, self.border))

            # Convert to a surface and splat onto screen offset by border width and height
            surface = pygame.surfarray.make_surface(self.runner.lattice.to_rgb_image())
            self.screen.blit(surface, (self.border, self.border))

            # Display and update frame counter
            self.text("{0:,}".format(self.runner.lattice.generation))
            self.text("R:{0}, B:{1}".format(
                self.runner.lattice.counts[0],
                self.runner.lattice.counts[2]),
                bottom=True)

            pygame.display.flip()
            self.clock.tick(60)
