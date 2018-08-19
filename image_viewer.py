import pygame

BG_COLOR = (20, 20, 20)
FONT_NAME = "font/RobotoMono-Regular.ttf"
FONT_SIZE = 16
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
            (width + (2 * border), height + (2 * border)))
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.frame_count = 0
        self.done = False
        self.autoStop = autoStop

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

            # Clear screen
            self.screen.fill(BG_COLOR)

            # Convert to a surface and splat onto screen offset by border width and height
            surface = pygame.surfarray.make_surface(self.runner.lattice.to_rgb_image())
            self.screen.blit(surface, (self.border, self.border))

            # Display and update frame counter
            txt = "{0:,}".format(self.runner.lattice.generation)
            w, h = self.font.size(txt)
            text = self.font.render(txt, True, TEXT_COLOR, BG_COLOR)

            self.screen.blit(text, (
                (self.width + 2 * self.border - w) / 2,
                (self.border - h) / 2))
            self.frame_count += 1

            pygame.display.flip()
            self.clock.tick(60)
