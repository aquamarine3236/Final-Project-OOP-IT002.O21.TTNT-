import pygame
import sys
import random

# Set the caption of the game window
pygame.display.set_caption("Mighty Action Game")

# Initialize all imported pygame modules
pygame.init()

# Get the current screen width and height
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Define color constants using RGB values
LIGHT_BLUE = (0, 165, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_RED = (128, 0, 0)
GREEN = (0, 128, 0)
LIGHT_GRAY = (209, 209, 209)
DARK_GRAY = (150, 150, 150)
DARKER_GRAY = (100, 100, 100)

# Set the block size for game elements
BLOCK_SIZE = 64

class Button:
    def __init__(self, rect, text, color, hover_color, click_color, text_color, font, border_radius, border_width):
        # Initialize the button's rectangle (position and size)
        self.rect = pygame.Rect(rect)
        
        # The text displayed on the button
        self.text = text
        
        # Default color of the button
        self.color = color
        
        # Color of the button when the mouse hovers over it
        self.hover_color = hover_color
        
        # Color of the button when it is clicked
        self.click_color = click_color
        
        # Color of the text on the button
        self.text_color = text_color
        
        # Font used for the button's text
        self.font = font
        
        # Border radius for rounded corners (0 means no rounding)
        self.border_radius = border_radius
        
        # Width of the button's border
        self.border_width = border_width
        
        # Flag to check if the button is clicked
        self.clicked = False

    def draw(self, screen):
        # Determine the color of the button based on its state (clicked, hovered, or normal)
        if self.clicked:
            color = self.click_color
        elif self.rect.collidepoint(pygame.mouse.get_pos()):
            color = self.hover_color
        else:
            color = self.color

        # Draw the button rectangle with the determined color and border radius
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)

        # Create a border rectangle slightly larger than the button rectangle
        border_rect = self.rect.inflate(self.border_width * 2, self.border_width * 2)

        # Draw the border around the button
        pygame.draw.rect(screen, self.text_color, border_rect, width=self.border_width, border_radius=self.border_radius)

        # Render the text onto a surface
        text_surface = self.font.render(self.text, True, self.text_color)

        # Get the rectangle of the text surface and center it within the button rectangle
        text_rect = text_surface.get_rect(center=self.rect.center)

        # Blit (copy) the text surface onto the screen at the position of the text rectangle
        screen.blit(text_surface, text_rect)


    def handle_event(self, event):
        # Check if the event is a mouse button down event and if it's the left mouse button (button 1)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if the mouse click happened inside the button's rectangle
            if self.rect.collidepoint(event.pos):
                # Set the clicked attribute to True to indicate that the button is currently clicked
                self.clicked = True

        # Check if the event is a mouse button up event and if it's the left mouse button (button 1)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

            # Check if the button was previously clicked and the mouse click happened inside the button's rectangle
            if self.clicked and self.rect.collidepoint(event.pos):

                # Reset the clicked attribute to False since the button is released
                self.clicked = False

                # Return True to indicate that the button was clicked and released
                return True
            
            # Reset the clicked attribute to False if the mouse click didn't occur within the button's rectangle
            self.clicked = False
            
        # Return False if the event was not related to the button or the button was not clicked and released
        return False


class HealthBar:
    def __init__(self, x, y, width, height, max_health):
        # Create the outer rectangle of the health bar
        self.outer_rect = pygame.Rect(x, y, width, height)
        
        # Create the inner rectangle representing the health level
        self.inner_rect = pygame.Rect(x + 3, y + 3, width - 6, height - 6)
        
        # Store the maximum health value
        self.max_health = max_health
        
        # Initialize the current health to the maximum health
        self.current_health = max_health
        
        # Define colors for the health bar
        self.outer_color = BLACK  # Color of the outer border
        self.inner_background_color = DARK_RED  # Color of the inner background
        self.inner_foreground_color = GREEN  # Color of the filled health portion
        
        # Define the border radius for rounded corners
        self.border_radius = 20

    def update(self, current_health):
        # Update the current health value, ensuring it stays within the bounds of 0 and max_health
        self.current_health = max(0, min(self.max_health, current_health))

    def draw(self, screen):
        # Draw the outer rectangle of the health bar
        pygame.draw.rect(screen, self.outer_color, self.outer_rect, border_radius=self.border_radius)
        
        # Draw the inner background rectangle of the health bar
        pygame.draw.rect(screen, self.inner_background_color, self.inner_rect, border_radius=self.border_radius - 3)

        # Calculate the width of the filled health portion
        filled_width = int(self.inner_rect.width * (self.current_health / self.max_health))
        # Create a filled rectangle representing the current health level
        filled_rect = pygame.Rect(self.inner_rect.x, self.inner_rect.y, filled_width, self.inner_rect.height)
        
        # Draw the filled health portion
        pygame.draw.rect(screen, self.inner_foreground_color, filled_rect, border_radius=self.border_radius - 3)


class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Load the character image and scale it to the specified width and height
        self.image = pygame.transform.scale(pygame.image.load("img_character_mighty.png").convert_alpha(), (width, height))

        # Get the rectangle representing the character's position and size
        self.rect = self.image.get_rect()

        # Set the initial position of the character
        self.rect.x = x
        self.rect.y = y
        
        # Attributes related to movement
        self.speed_x = 0
        self.speed_y = 0
        self.speed = 5
        self.gravity = 0.5
        self.jump_strength = -15
        self.on_ground = False
        self.jump_count = 0
        self.is_space_pressed = False
        
        # Attributes related to health
        self.health = 1000
        self.max_health = 1000
        self.immune_to_damage = False
        self.jump_damage = 1

        # Create a HealthBar object for the character's health representation
        self.health_bar = HealthBar(20, 20, 200, 30, self.max_health)
        
        # Sound effect for jumping
        self.jumping_sound = pygame.mixer.Sound("audio_jumping.mp3")
        self.jumping_sound.set_volume(0.25)

        # Flag to indicate game over condition
        self.is_game_over = False

    def update(self):
        # Handle movement based on keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.move_left()
        elif keys[pygame.K_RIGHT]:
            self.move_right()
        else:
            self.stop_x_movement()

        # Apply gravity and update position
        if self.on_ground:
            self.speed_y = 0
            self.jump_count = 0
        if keys[pygame.K_UP] and not self.is_space_pressed:
            if self.on_ground and self.jump_count < 2:
                self.jumping_sound.play()
                self.speed_y = self.jump_strength
                self.on_ground = False
                self.jump_count += 1
                self.is_space_pressed = True
        if not keys[pygame.K_UP]:
            self.is_space_pressed = False
        self.speed_y += self.gravity
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        # Check if character has fallen off the screen
        if self.rect.y > SCREEN_HEIGHT:
            self.is_game_over = True

    def move_left(self):
        # Move character left
        self.speed_x = -1 * self.speed

    def move_right(self):
        # Move character right
        self.speed_x = 1 * self.speed

    def stop_x_movement(self):
        # Stop horizontal movement
        self.speed_x = 0

    def reset_effects(self):
        # Reset all special effects and attributes
        self.speed = 5
        self.jump_strength = -15
        self.immune_to_damage = False
        self.jump_damage = 1

    def update_health(self, health_change):
        # Update character's health
        self.health += health_change

        # Ensure health stays within bounds
        if self.health > self.max_health:
            self.health = self.max_health
        elif self.health <= 0:
            self.is_game_over = True

        # Update the health bar
        self.health_bar.update(self.health)

class Scale_Block(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, width, height):
        super().__init__()
        # Load the image and scale it to the specified width and height
        self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (width, height))

        # Get the rectangle representing the block's position and size
        self.rect = self.image.get_rect()

        # Set the initial position of the block
        self.rect.x = x
        self.rect.y = y


class Item(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__()
        # Load the image and scale it to the BLOCK_SIZE
        self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (BLOCK_SIZE, BLOCK_SIZE))

        # Get the rectangle representing the item's position and size
        self.rect = self.image.get_rect()

        # Set the initial position of the item
        self.rect.x = x
        self.rect.y = y


class HighJumpItem(Item):
    def __init__(self, x, y):
        # Call the constructor of the parent class (Item)
        super().__init__("img_item_high_jump.png", x, y)

    def apply_effect(self, character):
        # Apply the effect of the high jump item to the character
        # Increase the character's jump strength to achieve a higher jump
        character.jump_strength = -20


class SpeedUpItem(Item):
    def __init__(self, x, y):
        # Call the constructor of the parent class (Item)
        super().__init__("img_item_speed_up.png", x, y)

    def apply_effect(self, character):
        # Apply the effect of the speed-up item to the character
        # Increase the character's speed
        character.speed = 7.5


class MuscleUpItem(Item):
    def __init__(self, x, y):
        # Call the constructor of the parent class (Item)
        super().__init__("img_item_muscle_up.png", x, y)

    def apply_effect(self, character):
        # Apply the effect of the muscle-up item to the character
        # Increase the damage caused by the character's jump
        character.jump_damage = 10


class IronBodyItem(Item):
    def __init__(self, x, y):
        # Call the constructor of the parent class (Item)
        super().__init__("img_item_iron_body.png", x, y)

    def apply_effect(self, character):
        # Apply the effect of the iron body item to the character
        # Make the character immune to damage
        character.immune_to_damage = True


class RecoveryItem(Item):
    def __init__(self, x, y):
        # Call the constructor of the parent class (Item)
        super().__init__("img_item_recovery.png", x, y)

    def apply_effect(self, character):
        # Apply the effect of the recovery item to the character
        # Increase the character's health by 100
        character.update_health(100)


class ConfusionItem(Item):
    def __init__(self, x, y):
        super().__init__("img_item_confusion.png", x, y)

    def apply_effect(self, character):
        character.update_health(-200)

class Question_Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load the image and scale it to the BLOCK_SIZE
        self.image = pygame.transform.scale(pygame.image.load("img_block_question.png").convert_alpha(), (BLOCK_SIZE, BLOCK_SIZE))

        # Get the rectangle representing the block's position and size
        self.rect = self.image.get_rect()

        # Set the initial position of the block
        self.rect.x = x
        self.rect.y = y

        # Initialize the hit state of the block
        self.is_hit = False  # Indicates whether the block has been hit
        
        # Sound effect for when the block is hit
        self.breaking_sound = pygame.mixer.Sound("audio_break.mp3")

    def hit(self):
        # Check if the block has not been hit yet
        if not self.is_hit:

            # List of possible items to spawn from the block
            items = [
                HighJumpItem,
                SpeedUpItem,
                MuscleUpItem,
                IronBodyItem,
                ConfusionItem,
                RecoveryItem
            ]

            # Randomly select an item class from the list
            random_item_class = random.choice(items)

            # Create an instance of the selected item class at the block's position
            item = random_item_class(self.rect.x, self.rect.y)

            # Set the block's hit state to True
            self.is_hit = True  # Mark the block as hit

            # Play the breaking sound effect
            self.breaking_sound.play()

            # Remove the block sprite from the sprite group
            self.kill()  # Remove the block from the sprite group

            # If the spawned item is a power-up item, set the game's timer check flag to True
            if random_item_class in [HighJumpItem, SpeedUpItem, MuscleUpItem, IronBodyItem]:
                game.timer_check = True

            # Return the spawned item
            return item
        
        # If the block has already been hit, return None
        return None


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, movement_range, max_health, speed):
        super().__init__()
        # Load the image and scale it to the BLOCK_SIZE
        self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (BLOCK_SIZE, BLOCK_SIZE))

        # Get the rectangle representing the enemy's position and size
        self.rect = self.image.get_rect()

        # Set the initial position of the enemy
        self.rect.x = x
        self.rect.y = y

        # Store the initial x-position for movement range calculation
        self.initial_x = x

        # Define the movement range of the enemy
        self.movement_range = movement_range

        # Set the speed of the enemy
        self.speed_x = speed * 2

        # Set the maximum health of the enemy
        self.max_health = max_health

        # Set the current health of the enemy to its maximum health initially
        self.current_health = max_health

        # Set the initial movement direction of the enemy (1: right, -1: left)
        self.direction = 1

        # Define a damage multiplier for the enemy's attacks
        self.damage_multiplier = 0.1

        # Flag to indicate whether the enemy has hit the character
        self.has_hit_character = False

    def take_damage(self, damage):
        # Reduce the enemy's health by the specified amount of damage
        self.current_health -= damage

        # If the enemy's health drops to or below zero, remove it from the game
        if self.current_health <= 0:
            self.kill()

    def update(self):
        # Move the enemy horizontally according to its speed and direction
        self.rect.x += self.speed_x * self.direction
        
        # Check if the enemy has reached the edge of its movement range
        if self.rect.x <= self.initial_x - self.movement_range:
            # Change the direction to move right if reached left edge
            self.direction = 1
        elif self.rect.x >= self.initial_x:
            # Change the direction to move left if reached right edge
            self.direction = -1


class TVBanner:
    def __init__(self, image_path, x, y, width, height):
        # Load the image and scale it to the specified width and height
        self.image = pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (width, height))

        # Get the rectangle representing the banner's position and size
        self.rect = self.image.get_rect()

        # Set the initial position of the banner
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        # Draw the banner on the screen
        screen.blit(self.image, self.rect)


class PauseMenu:
    def __init__(self, screen_width, screen_height):
        # Store the screen width and height
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load the font for menu buttons
        self.font = pygame.font.Font("font2.otf", 36)

        # Define the buttons for the pause menu
        self.buttons = [
            Button((screen_width // 2 - 100, screen_height // 2 - 50, 200, 50), "Continue", GREEN, DARK_GRAY, DARKER_GRAY, BLACK, self.font, 10, 2),
            Button((screen_width // 2 - 100, screen_height // 2 + 20, 200, 50), "Exit", DARK_RED, DARK_GRAY, DARKER_GRAY, BLACK, self.font, 10, 2)
        ]

    def draw(self, screen):
        # Draw all buttons on the screen
        for button in self.buttons:
            button.draw(screen)

    def handle_event(self, event):
        # Check if any button is clicked and return the text of the clicked button
        for button in self.buttons:
            if button.handle_event(event):
                return button.text
        return None


class Game:
    def __init__(self):
        # Initialize the game screen and clock
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Create sprite groups for different types of sprites
        self.all_sprites = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        # Create ground layers
        self.create_ground(SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE, "img_block_dirt.png")  # Bottom dirt layer
        self.create_ground(SCREEN_HEIGHT - 2 * BLOCK_SIZE, BLOCK_SIZE, "img_block_dirt.png")  # Middle dirt layer
        self.create_ground(SCREEN_HEIGHT - 3 * BLOCK_SIZE, BLOCK_SIZE, "img_block_grass.png")  # Top grass layer

        # Create initial clouds, obstacles, and enemies
        self.create_initial_clouds()
        self.current_cloud = 0
        self.create_obstacles()
        self.create_enemies()

        # Initialize the main character and add it to the sprite group
        character_initial_x = 100
        character_initial_y = SCREEN_HEIGHT - 7 * BLOCK_SIZE
        self.character = Character(character_initial_x, character_initial_y, BLOCK_SIZE * 2, BLOCK_SIZE * 2)
        self.all_sprites.add(self.character)
        self.camera_x = 0

        # Create and add the castle block to the sprite group
        castle_x = 300 * BLOCK_SIZE
        castle_y = SCREEN_HEIGHT - 9 * BLOCK_SIZE
        self.castle = Scale_Block("img_block_castle.png", castle_x, castle_y, BLOCK_SIZE * 6, BLOCK_SIZE * 6)
        self.all_sprites.add(self.castle)

        # Initialize the character's health bar
        self.character_health_bar = HealthBar(20, 20, 500, 40, self.character.max_health)
        self.character.update_health(0)  # Update character's health bar

        # Timer related variables
        self.timer_check = False
        self.timer_font = pygame.font.Font("font2.otf", 52)
        self.timer_active = False
        self.timer = 0

        # Game over and victory banners along with corresponding sounds
        self.game_over_banner = pygame.image.load("img_banner_game_over.png").convert_alpha()
        self.game_over_banner = pygame.transform.scale(self.game_over_banner, (int(SCREEN_WIDTH * 0.8), int(SCREEN_HEIGHT * 0.4)))
        self.game_over_sound = pygame.mixer.Sound("audio_game_over.mp3")

        self.victory_banner = pygame.image.load("img_banner_game_clear.png").convert_alpha()
        self.victory_banner = pygame.transform.scale(self.victory_banner, (int(SCREEN_WIDTH * 0.8), int(SCREEN_HEIGHT * 0.4)))
        self.victory_sound = pygame.mixer.Sound("audio_winner.mp3")

        # Sounds for different game events
        self.hitting_sound = pygame.mixer.Sound("audio_hitting.mp3")
        self.hitting_sound.set_volume(0.1)
        self.killing_sound = pygame.mixer.Sound("audio_killing.mp3")
        self.buff_sound = pygame.mixer.Sound("audio_power_up.mp3")
        self.debuff_sound = pygame.mixer.Sound("audio_power_down.mp3")
        self.recovery_sound = pygame.mixer.Sound("audio_recovery.mp3")
        self.back_sound = pygame.mixer.Sound("audio_background_music.mp3")
        self.back_sound.set_volume(0.5)
        self.pause_sound = pygame.mixer.Sound("audio_pause.mp3")
        self.continue_sound = pygame.mixer.Sound("audio_continue.mp3")
        self.exit_sound = pygame.mixer.Sound("audio_exit.mp3")

        # Initialize TV banner and pause menu
        self.tv_banner = TVBanner("img_banner_tv.png", SCREEN_WIDTH - 95, 20, 75, 75)
        self.pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.paused = False


    def update_timer(self):
        # Update the timer if it is active and greater than 0
        if self.timer_active and self.timer > 0:
            self.timer -= 1
        elif self.timer == 0:
            # If timer reaches 0, deactivate it and reset character effects
            self.timer_active = False
            self.character.reset_effects()

    def draw_timer(self):
        # Draw the timer on the screen if it's active
        if self.timer_active:
            # Render the timer text
            timer_text = self.timer_font.render(str(int(self.timer / 6) / 10) + "s", True, BLACK)
    
            # Get the rectangle representing the timer text
            timer_rect = timer_text.get_rect()

            # Set the position of the timer text on the screen
            timer_rect.topleft = (30, 80)

            # Draw the timer text on the screen
            self.screen.blit(timer_text, timer_rect)

    def create_obstacles(self):
        # Initialize the x-coordinate for obstacle placement
        i = random.randint(5, 15)

        # Loop until reaching the specified x-coordinate limit
        while i <= 290:
            # Randomly decide whether to create a question block or a brick block
            if random.randint(1, 2) == 2:

                # Create a question block at a random y-coordinate within the specified range
                question_block = Question_Block(i * BLOCK_SIZE, random.randint(SCREEN_HEIGHT//2, SCREEN_HEIGHT - 5 * BLOCK_SIZE))

                # Add the question block to the blocks sprite group and all sprites group
                self.blocks.add(question_block)
                self.all_sprites.add(question_block)
            else:
                # Create a brick block at a random y-coordinate within the specified range
                brick = Scale_Block("img_block_brick.png", i * BLOCK_SIZE, random.randint(SCREEN_HEIGHT//2, SCREEN_HEIGHT - 5 * BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE)
                
                # Add the brick block to the blocks sprite group and all sprites group
                self.blocks.add(brick)
                self.all_sprites.add(brick)
            
            # Move to the next x-coordinate with a random increment
            i += random.randint(5, 15)


    def create_ground(self, y, height, image_path):
        # Loop through each segment of the ground and create blocks for each segment
        for x in range(-6 * BLOCK_SIZE, 50 * BLOCK_SIZE, BLOCK_SIZE):
            ground = Scale_Block(image_path, x, y, BLOCK_SIZE, height)
            # Add the ground block to the blocks sprite group and all sprites group
            self.blocks.add(ground)
            self.all_sprites.add(ground)

        for x in range(55 * BLOCK_SIZE, 100 * BLOCK_SIZE, BLOCK_SIZE):
            ground = Scale_Block(image_path, x, y, BLOCK_SIZE, height)
            self.blocks.add(ground)
            self.all_sprites.add(ground)

        for x in range(105 * BLOCK_SIZE, 150 * BLOCK_SIZE, BLOCK_SIZE):
            ground = Scale_Block(image_path, x, y, BLOCK_SIZE, height)
            self.blocks.add(ground)
            self.all_sprites.add(ground)

        for x in range(155 * BLOCK_SIZE, 200 * BLOCK_SIZE, BLOCK_SIZE):
            ground = Scale_Block(image_path, x, y, BLOCK_SIZE, height)
            self.blocks.add(ground)
            self.all_sprites.add(ground)

        for x in range(205 * BLOCK_SIZE, 250 * BLOCK_SIZE, BLOCK_SIZE):
            ground = Scale_Block(image_path, x, y, BLOCK_SIZE, height)
            self.blocks.add(ground)
            self.all_sprites.add(ground)

        for x in range(255 * BLOCK_SIZE, 400 * BLOCK_SIZE, BLOCK_SIZE):
            ground = Scale_Block(image_path, x, y, BLOCK_SIZE, height)
            self.blocks.add(ground)
            self.all_sprites.add(ground)


    def create_initial_clouds(self):
        # Generate initial clouds at random positions within the upper half of the screen
        for _ in range(7):
            cloud = Scale_Block("img_block_cloud.png", random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT // 3), BLOCK_SIZE, BLOCK_SIZE)
            
            # Add the cloud to the clouds sprite group and all sprites group
            self.clouds.add(cloud)
            self.all_sprites.add(cloud)

    def create_clouds(self):
        # Create additional clouds if the current cloud count is below a certain threshold
        if self.current_cloud < random.randint(10, 15):  
            # Generate a new cloud at a random position within a certain range
            cloud = Scale_Block("img_block_cloud.png", self.camera_x + SCREEN_WIDTH + random.randint(0, int(SCREEN_WIDTH * 0.2)), random.randint(0, SCREEN_HEIGHT // 3), BLOCK_SIZE, BLOCK_SIZE)
            
            # Add the cloud to the clouds sprite group and all sprites group
            self.clouds.add(cloud)
            self.all_sprites.add(cloud)
            
            # Increment the current cloud count
            self.current_cloud += 1


    def create_enemies(self):
        # Define different enemy types along with their images and attributes
        enemy_types = [
            ("img_enemy_mushroom.png", 1),
            ("img_enemy_robot.png", 2),
            ("img_enemy_orc.png", 3)
        ]

        # Loop through x-coordinates to create enemies
        for i in range(9, 275, 17):
            # Randomly select an enemy type
            image_path, number = random.choice(enemy_types)

            # Create an enemy instance with the selected image and attributes
            enemy = Enemy(image_path, i * BLOCK_SIZE, SCREEN_HEIGHT - 4 * BLOCK_SIZE, 100 * number, number, number * 0.75)  
            
            # Add the enemy to the enemies sprite group and all sprites group
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)


    def check_collisions(self):
        # Check for vertical collisions between character and blocks
        hits_vertical = pygame.sprite.spritecollide(self.character, self.blocks, False)
        if hits_vertical:
            for block in hits_vertical:
                # Handle collision when character is moving downwards
                if self.character.speed_y > 0: 
                    self.character.on_ground = True
                    self.character.rect.bottom = block.rect.top
                    self.character.speed_y = 0

                    # Check if the collided block is a question block and not yet hit
                    if isinstance(block, Question_Block) and not block.is_hit:
                        # Hit the block to reveal item
                        item = block.hit()
                        if item:
                            self.items.add(item)  
                            self.all_sprites.add(item)

                            # Trigger character jump if on ground after hitting question block
                            if self.character.on_ground:
                                self.character.speed_y = self.character.jump_strength
                                self.character.on_ground = False

        # Check for horizontal collisions between character and blocks
        hits_horizontal = pygame.sprite.spritecollide(self.character, self.blocks, False)
        if hits_horizontal:
            for block in hits_horizontal:
                # Handle collision when character is moving right
                if self.character.speed_x > 0:  
                    self.character.rect.right = block.rect.left

                # Handle collision when character is moving left
                elif self.character.speed_x < 0:  
                    self.character.rect.left = block.rect.right
       
       # Update character's on_ground state if no vertical collisions detected
        if not hits_vertical:
            self.character.on_ground = False
       
        # Check collision with the castle block to trigger win condition
        if pygame.sprite.collide_rect(self.character, self.castle):
            self.win()

        # Check for collisions between character and enemies
        enemy_hits = pygame.sprite.spritecollide(self.character, self.enemies, False)
        if enemy_hits:
            for enemy in enemy_hits:
                # Handle collision when character is moving downwards and below enemy
                if self.character.speed_y > 0 and self.character.rect.bottom <= enemy.rect.bottom:
                    enemy.take_damage(self.character.jump_damage) 
                    self.character.jumping_sound.play()
                    self.character.speed_y = self.character.jump_strength  
       
                    # Remove enemy if its health drops to zero
                    if enemy.current_health <= 0:
                        self.enemies.remove(enemy)  
                        self.character.jumping_sound.stop()
                        self.killing_sound.play()
                        self.all_sprites.remove(enemy)
       
                # Handle collision when character is hit by enemy horizontally
                elif not enemy.has_hit_character:  
                    if not self.character.immune_to_damage:
                        self.character.health -= enemy.current_health 
                        self.hitting_sound.play() 
                        self.character.speed_y = -2
                        self.character.on_ground = False
                        self.character_health_bar.update(self.character.health)
       
                        # Trigger game over condition if character's health drops to zero
                        if self.character.health <= 0:
                            self.character.is_game_over = True


    def check_item_collisions(self):
        # Check for collisions between character and items
        item_hits = pygame.sprite.spritecollide(self.character, self.items, False)

        # Iterate through each item collided with
        for item in item_hits:
            # Check the type of item and apply its effect accordingly
            if isinstance(item, RecoveryItem) or isinstance(item, ConfusionItem):
                
                # Apply effect and play corresponding sound
                item.apply_effect(self.character)
                if isinstance(item, RecoveryItem):
                    self.recovery_sound.play()
                else:
                    self.debuff_sound.play()
                
                # Remove the item from sprite groups
                item.kill()
            else:
                # If the timer is not active, apply the effect and start the timer
                if not self.timer_active:
                    # Apply effect and play buff sound
                    item.apply_effect(self.character)
                    self.buff_sound.play()
                    
                    # Set the timer duration based on the type of item
                    if isinstance(item, SpeedUpItem) or isinstance(item, HighJumpItem) or isinstance(item, MuscleUpItem) or isinstance(item, IronBodyItem):
                        self.timer = 300
                        self.timer_active = True
                    
                    # Remove the item from sprite groups
                    item.kill()



    def game_over(self):
        # Stop background music and play game over sound
        self.back_sound.stop()
        self.game_over_sound.play()

        # Display game over banner
        banner_rect = self.game_over_banner.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(self.game_over_banner, banner_rect)
        
        pygame.display.flip()  # Update the display
        
        pygame.time.wait(3000)  # Wait for 3 seconds
        
        pygame.quit()  # Quit pygame
        
        sys.exit()  # Exit the program

    def win(self):
        # Stop background music and play victory sound
        self.back_sound.stop()
        self.victory_sound.play()
        
        # Display victory banner
        banner_rect = self.victory_banner.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(self.victory_banner, banner_rect)
        
        pygame.display.flip()  # Update the display
        
        pygame.time.wait(4000)  # Wait for 4 seconds
        
        pygame.quit()  # Quit pygame
        
        sys.exit()  # Exit the program


    def run(self):
        # Play background music
        self.back_sound.play(loops=-1)
        running = True
        while running:
            for event in pygame.event.get():
                # Check for quit event
                if event.type == pygame.QUIT:
                    running = False

                # Check for mouse button click on TV banner to pause the game
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.tv_banner.rect.collidepoint(event.pos):
                        self.paused = True
                        self.pause_sound.stop()
                        self.pause_sound.play()

            # Check if the game is paused
            if self.paused:
                # Handle events in the pause menu
                result = self.pause_menu.handle_event(event)
                if result == "Continue":
                    self.continue_sound.play()
                    self.paused = False
                elif result == "Exit":
                    self.exit_sound.play()
                    pygame.time.wait(1100)
                    pygame.quit()
                    sys.exit()
                else:
                    self.pause_menu.draw(self.screen)
            else:
                # Update all sprites, check collisions, and update timer
                self.all_sprites.update()
                self.check_collisions()
                self.check_item_collisions()
                self.update_timer()

                # Check if the character's game is over
                if self.character.is_game_over:
                    self.game_over()

                # Adjust camera position based on character's position
                if self.character.rect.right > SCREEN_WIDTH * 0.7:
                    self.camera_x = self.character.rect.right - SCREEN_WIDTH * 0.7
                elif self.character.rect.left < SCREEN_WIDTH * 0.3:
                    self.camera_x = self.character.rect.left - SCREEN_WIDTH * 0.3

                # Randomly create clouds
                if random.randint(1, 100) <= 2:
                    self.create_clouds()

                # Fill the screen with light blue color
                self.screen.fill(LIGHT_BLUE)

                # Draw all sprites on the screen with adjusted positions
                for sprite in self.all_sprites:
                    self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))

                # Update and draw character's health bar
                self.character_health_bar.update(self.character.health)
                self.character_health_bar.draw(self.screen)

                # Draw timer
                self.draw_timer()

            # Draw TV banner
            self.tv_banner.draw(self.screen)

            # Update the display
            pygame.display.flip()

            # Control frame rate
            self.clock.tick(60)


# Set up a fullscreen display
start_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load and scale the background image to fit the screen
image = pygame.image.load('img_start_background.png')
image = pygame.transform.scale(image, (start_screen.get_width(), start_screen.get_height()))

# Blit the background image onto the screen at coordinates (0, 0)
start_screen.blit(image, (0, 0))

# Load and play the start sound effect
start_sound = pygame.mixer.Sound('audio_starter.mp3')
start_sound.play()

# Update the display to show the background image and sound effect
pygame.display.flip()

# Define the font for the buttons
font = pygame.font.Font("font1.ttf", 24)

# Create "PLAY" button with specific properties using the Button class
play_button = Button((start_screen.get_width() // 2 - 100, 550, 200, 50), "PLAY", LIGHT_GRAY, DARK_GRAY, DARKER_GRAY, BLACK, font, 20, 4)

# Create "QUIT" button with specific properties using the Button class
quit_button = Button((start_screen.get_width() // 2 - 100, 650, 200, 50), "QUIT", LIGHT_GRAY, DARK_GRAY, DARKER_GRAY, BLACK, font, 20, 4)

# Store the buttons in a list for easy access
buttons = [play_button, quit_button]

while True:
    # Event handling loop
    for event in pygame.event.get():
        # If the event is quitting the game, exit the program
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # If a key is pressed and it's the escape key, exit the program
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        # Check if any button is clicked
        for button in buttons:
            if button.handle_event(event):
                # If the "PLAY" button is clicked, start the game
                if button.text == "PLAY":
                    game = Game()
                    game.run()

                # If the "QUIT" button is clicked, exit the program
                elif button.text == "QUIT":
                    pygame.quit()
                    sys.exit()

    # Redraw the background image and buttons on the start screen
    start_screen.blit(image, (0, 0))
    for button in buttons:
        button.draw(start_screen)

    # Update the display
    pygame.display.flip()
