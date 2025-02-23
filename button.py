import pygame

class Button():
    def __init__(self, image, x, y):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, surface):
        action = False

        # Get mouse position
        pos = pygame.mouse.get_pos()

        # Check mouseover and click
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                action = True

        surface.blit(self.image, self.rect)

        return action