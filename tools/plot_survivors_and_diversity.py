# The Python script will generate a plot with two curves. 
# Data from the epoch-log.txt file.

# Survivors: This curve represents the number of survivors over time. 
# It is plotted on the primary (left) Y-axis
# Colored green.

# Diversity: This curve represents the diversity over time. It is plotted on the secondary (right) Y-axis
# Colored red.
import matplotlib.pyplot as plt
import numpy as np

def plot_survivors_and_diversity():
    # Load the data
    data = np.loadtxt('../logs/epoch-log.txt')

    # Scale the data
    x = data[:,0]
    survivors = data[:,1]
    diversity = data[:,2]

    # Create a new figure
    fig, ax1 = plt.subplots()

    # Plot the survivors on y1
    ax1.plot(x, survivors, 'g-', label='Survivors')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Survivors', color='g')

    # Create a second y axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('Diversity', color='r')
    ax2.set_ylim([0, 1])

    # Plot the diversity on y2
    ax2.plot(x, diversity, 'r-', label='Diversity')

    # Add a grid
    ax1.grid(True)

    # Add a legend
    fig.legend(loc="upper left", bbox_to_anchor=(0,1), bbox_transform=ax1.transAxes)

    # Save the figure
    plt.savefig('../images/log.png', dpi=200)

if __name__ == "__main__":
    plot_survivors_and_diversity()