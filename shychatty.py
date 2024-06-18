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

# Number of bots
NUM_SHY_BOTS = 1  # Number of shy bots
NUM_CHATTY_BOTS = 1  # Number of chatty bots

class Emotion:
    SHY = 'shy'
    CHATTY = 'chatty'

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
bots = []
for i in range(NUM_SHY_BOTS):
    bots.append(Bot(i, Emotion.SHY))
for i in range(NUM_CHATTY_BOTS):
    bots.append(Bot(NUM_SHY_BOTS + i, Emotion.CHATTY))

# Matplotlib initialization
fig, ax = plt.subplots()
ax.set_xlim(0, BOX_SIZE)
ax.set_ylim(0, BOX_SIZE)
ax.set_aspect('equal')
ax.set_title('Bot Interaction Simulation')

# Scatter plot initialization
colors = {'shy': 'blue', 'chatty': 'green'}
scatters = {
    'shy': ax.scatter([bot.position[0] for bot in bots if bot.type == 'shy'],
                      [bot.position[1] for bot in bots if bot.type == 'shy'],
                      c=colors['shy'], label='Shy Bot', edgecolor='black', s=100),
    'chatty': ax.scatter([bot.position[0] for bot in bots if bot.type == 'chatty'],
                         [bot.position[1] for bot in bots if bot.type == 'chatty'],
                         c=colors['chatty'], label='Chatty Bot', edgecolor='black', s=100)
}

# Distance text initialization
distance_text = ax.text(0.5, 0.95, '', transform=ax.transAxes, ha='center')

# Function to update the plot
def update_plot(frame):
    for bot in bots:
        bot.move()

    # Update scatter plot data
    scatters['shy'].set_offsets([[bot.position[0], bot.position[1]] for bot in bots if bot.type == 'shy'])
    scatters['chatty'].set_offsets([[bot.position[0], bot.position[1]] for bot in bots if bot.type == 'chatty'])
    
    # Calculate and update distances and interactions
    for bot in bots:
        for other_bot in bots:
            if bot.id != other_bot.id:
                distance = np.linalg.norm(bot.position - other_bot.position)
                if bot.is_within_interaction_radius(other_bot):
                    if bot.type == Emotion.SHY and other_bot.type == Emotion.CHATTY:
                        bot.run_away(other_bot)
                    elif bot.type == Emotion.CHATTY and other_bot.type == Emotion.SHY:
                        bot.chase(other_bot)
                else:
                    if bot.last_interaction_status == 'run_away':
                        bot.last_interaction_status = None
                    elif bot.last_interaction_status == 'chase':
                        bot.last_interaction_status = None
                    if distance >= RUN_AWAY_DISTANCE:
                        if bot.type == Emotion.SHY and other_bot.type == Emotion.CHATTY and bot.last_interaction_status != 'run_away':
                            bot.resume_random_movement()
                        elif bot.type == Emotion.CHATTY and other_bot.type == Emotion.SHY and bot.last_interaction_status != 'chase':
                            bot.resume_random_movement()
    
    # Update distance text (It was previously used to show distance between two bots.. will still do it if only 2 bots are present, or else just shows avg of theri distance)
    avg_distance = np.mean([np.linalg.norm(bot.position - other_bot.position) for bot in bots for other_bot in bots if bot.id != other_bot.id])
    distance_text.set_text(f'Average Distance: {avg_distance:.2f}')
    
    # Decrease teleportation cooldown timer for all bots (all bots part is intentional, lol)
    for bot in bots:
        bot.teleport_cooldown_timer = max(bot.teleport_cooldown_timer - UPDATE_INTERVAL, 0)
    
    return list(scatters.values()) + [distance_text]

# Animation
ani = FuncAnimation(fig, update_plot, frames=None, interval=UPDATE_INTERVAL * 1000, blit=True)

# Show plot with separate legend entries for 'Shy Bot' and 'Chatty Bot'
ax.legend()

# Display the plot
plt.show()
