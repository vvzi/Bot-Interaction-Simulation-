import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Constants
BOX_SIZE = 50  # Size of the simulation box
INTERACTION_RADIUS = 10  # Distance within which bots interact
RUN_AWAY_DISTANCE = 40  # Distance beyond which a shy bot will resume random movement
BOT_SPEED_FACTOR = 1  # Adjusted speed factor for moderate speed
UPDATE_INTERVAL = 0.1  # Delay between updates in seconds
TELEPORT_COOLDOWN = 2.0  # Cooldown period (in seconds) for teleportation from a corner to a random corner
MIN_STEPS_DIRECTION = 10  # Minimum number of steps in a direction before changing to a new random direction

class Bot:
    def __init__(self, bot_id, type):
        self.id = bot_id
        self.type = type  # 'shy' or 'chatty'
        self.position = np.array([random.uniform(0, BOX_SIZE), random.uniform(0, BOX_SIZE)], dtype=np.float64)
        self.velocity = np.array([random.uniform(-1, 1), random.uniform(-1, 1)], dtype=np.float64) * BOT_SPEED_FACTOR
        self.interacting_with = None
        self.interaction_timer = 0
        self.teleport_cooldown_timer = 0
        self.last_interaction_status = None  # Track last interaction status
        self.steps_in_current_direction = 0  # Track steps taken in current direction

    def move(self):
        # Random movement with bounded conditions
        self.position += self.velocity
        self.position = np.clip(self.position, 0, BOX_SIZE)
        
        # Count steps in current direction
        self.steps_in_current_direction += 1
        
        # Ensure bots don't stop at boundaries
        if np.any(self.position == 0) or np.any(self.position == BOX_SIZE):
            if self.teleport_cooldown_timer <= 0 and (self.position[0] == 0 or self.position[0] == BOX_SIZE) and (self.position[1] == 0 or self.position[1] == BOX_SIZE):
                self.teleport_random_corner()
                self.teleport_cooldown_timer = TELEPORT_COOLDOWN
            else:
                self.velocity = self.get_random_direction()
                self.steps_in_current_direction = 0
        
        # Check if minimum steps in current direction reached
        if self.steps_in_current_direction >= MIN_STEPS_DIRECTION:
            self.velocity = self.get_random_direction()
            self.steps_in_current_direction = 0

    def teleport_random_corner(self):
        
       # Teleport the bot to a different random corner of the simulation box.
        
        corners = [
            np.array([0, 0], dtype=np.float64),
            np.array([0, BOX_SIZE], dtype=np.float64),
            np.array([BOX_SIZE, 0], dtype=np.float64),
            np.array([BOX_SIZE, BOX_SIZE], dtype=np.float64)
        ]
        # Remove the current corner from the options
        corners = [corner for corner in corners if not np.array_equal(corner, self.position)]
        new_position = random.choice(corners)
        self.position = new_position
        print(f"Bot {self.id} teleported to {new_position}")

        # Reset velocity to a random direction
        self.velocity = self.get_random_direction()

        self.resume_random_movement()  # Resume random movement after teleportation

    def get_random_direction(self):
        
       # Get a random direction vector.
        
        return np.array([random.uniform(-1, 1), random.uniform(-1, 1)], dtype=np.float64) * BOT_SPEED_FACTOR

    def is_within_interaction_radius(self, other):
        distance = np.linalg.norm(self.position - other.position)
        return distance <= INTERACTION_RADIUS

    def run_away(self, other):
        direction_vector = self.position - other.position
        if np.linalg.norm(direction_vector) > 0:
            self.velocity = direction_vector / np.linalg.norm(direction_vector) * BOT_SPEED_FACTOR
            if self.last_interaction_status != 'run_away':
                print(f"Bot {self.id} starts running away from Bot {other.id}")
                self.last_interaction_status = 'run_away'

    def chase(self, other):
        direction_vector = other.position - self.position
        if np.linalg.norm(direction_vector) > 0:
            self.velocity = direction_vector / np.linalg.norm(direction_vector) * BOT_SPEED_FACTOR
            if self.last_interaction_status != 'chase':
                print(f"Bot {self.id} starts chasing Bot {other.id}")
                self.last_interaction_status = 'chase'

    def resume_random_movement(self):
        self.velocity = self.get_random_direction()

# Initialize bots
bot0 = Bot(0, 'shy')
bot1 = Bot(1, 'chatty')

# Matplotlib initialization
fig, ax = plt.subplots()
ax.set_xlim(0, BOX_SIZE)
ax.set_ylim(0, BOX_SIZE)
ax.set_aspect('equal')
ax.set_title('Bot Interaction Simulation')

# Scatter plot initialization
scatter_bot0 = ax.scatter([bot0.position[0]], [bot0.position[1]], c='blue', label='Shy Bot', edgecolor='black', s=100)
scatter_bot1 = ax.scatter([bot1.position[0]], [bot1.position[1]], c='green', label='Chatty Bot', edgecolor='black', s=100)

# Distance text initialization
distance_text = ax.text(0.5, 0.95, '', transform=ax.transAxes, ha='center')

# Function to update the plot
def update_plot(frame):
    bot0.move()
    bot1.move()

    distance = np.linalg.norm(bot0.position - bot1.position)

    if bot0.is_within_interaction_radius(bot1):
        if bot0.type == 'shy' and bot1.type == 'chatty':
            # Shy bot runs away
            bot0.run_away(bot1)

        if bot1.type == 'chatty' and bot0.type == 'shy':
            # Chatty bot chases shy bot
            bot1.chase(bot0)
    else:
        if bot0.last_interaction_status == 'run_away':
            print(f"Bot {bot0.id} got away from Bot {bot1.id}")
            bot0.last_interaction_status = None
        
        if bot1.last_interaction_status == 'chase':
            print(f"Bot {bot1.id} stopped chasing Bot {bot0.id}")
            bot1.last_interaction_status = None

        if distance >= RUN_AWAY_DISTANCE:
            if bot0.type == 'shy' and bot1.type == 'chatty' and bot0.last_interaction_status != 'run_away':
                bot0.resume_random_movement()

            if bot1.type == 'chatty' and bot0.type == 'shy' and bot1.last_interaction_status != 'chase':
                bot1.resume_random_movement()

    # Update scatter plots
    scatter_bot0.set_offsets([bot0.position[0], bot0.position[1]])
    scatter_bot1.set_offsets([bot1.position[0], bot1.position[1]])
    
    # Update distance text
    distance_text.set_text(f'Distance: {distance:.2f}')
    
    # Decrease teleportation cooldown timer
    bot0.teleport_cooldown_timer = max(bot0.teleport_cooldown_timer - UPDATE_INTERVAL, 0)
    bot1.teleport_cooldown_timer = max(bot1.teleport_cooldown_timer - UPDATE_INTERVAL, 0)
    
    return scatter_bot0, scatter_bot1, distance_text

# Animation
ani = FuncAnimation(fig, update_plot, frames=None, interval=UPDATE_INTERVAL * 1000, blit=True)

# Show plot with separate legend entries for 'Shy Bot' and 'Chatty Bot'
ax.legend()

# Display the plot
plt.show()
