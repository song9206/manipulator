import pygame

pygame.init()
joysticks = []

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Joystick Testing / XBOX360 Controller")
#clock = pygame.time.Clock()
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((255, 255, 255))


# clock = pygame.time.Clock()
keepPlaying = True

def main():

     for i in range(0, pygame.joystick.get_count()):
        # create an Joystick object in our list
        joysticks.append(pygame.joystick.Joystick(i))
        # initialize them all (-1 means loop forever)
        joysticks[-1].init()
      #  # print a statement telling what the name of the controller is
        print "Detected joystick '", joysticks[-1].get_name(), "'"

     while keepPlaying:

        #clock.tick(60)

        for event in pygame.event.get():



main()
pygame.quit()