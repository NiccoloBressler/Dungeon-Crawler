import pygame
from character import Character

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, animation_list, coin_placeholder = False):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type # 0 = coin, 1 = hp potion
        self.frame_index = 0
        self.animation_list = animation_list
        self.image = self.animation_list[self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.coin_placeholder = coin_placeholder

    def update(self, screen_scroll, player, coin_sound, heal_sound):
        # Check if coin placeholder
        if not self.coin_placeholder:
        # Reposition item based on scroll
            self.rect.x += screen_scroll[0]
            self.rect.y += screen_scroll[1]
        # Collision check with player and item
        if pygame.sprite.collide_rect(self, player):
            # Coin
            if self.item_type == 0:
                coin_sound.play()
                player.coins += 1
                self.kill()
            # Potion
            elif self.item_type == 1:
                heal_sound.play()
                player.hp += 20
                if player.hp > 100:
                    player.hp = 100
                self.kill()
        # Animations
        animation_cooldown = 200
        # Update image
        self.image = self.animation_list[self.frame_index]
        # Check if update is needed
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # Reset animation if finished
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)