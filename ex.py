import pygame

pygame.init()

screen = pygame.display.set_mode((640, 640))

potato_img = pygame.image.load('potato.png').convert()

potato_img = pygame.transform.scale(potato_img,
                                    (potato_img.get_width() * 2,
                                     potato_img.get_height() * 2))

potato_img.set_colorkey((0, 0, 0))

running = True
x = 0
clock = pygame.time.Clock()

delta_time = 0.1

font = pygame.font.Font(None, size=30)
moving = False

sound = pygame.mixer.Sound('clank.wav')

while running:
    screen.fill((255, 255, 255))

    screen.blit(potato_img, (x, 30))

    hitbox = pygame.Rect(x, 30, potato_img.get_width(), potato_img.get_height())

    mpos = pygame.mouse.get_pos()

    target = pygame.Rect(300, 0, 160, 280)
    collision = hitbox.colliderect(target)
    m_collision = target.collidepoint(mpos)
    pygame.draw.rect(screen, (255 * collision, 255 * m_collision, 0), target)

    if moving:
        x += 50 * delta_time

    text = font.render('Hello World!', True, (0, 0, 0))
    screen.blit(text, (300, 100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                moving = True
            if event.key == pygame.K_f:
                sound.play()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                moving = False

    pygame.display.flip()

    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(0.1, delta_time))
    
pygame.quit()