# plot graph with three curves. 
# Data from the epoch-log.txt file.

# Survivors: This curve represents the number of survivors over time. 
# Colored green.

# Diversity: This curve represents the diversity over time, scaled by multiplying by 350.
# It is plotted on the secondary (right) Y-axis
# Colored red.

# Genome Length: This curve represents the genome length over time, scaled by multiplying by 2.
# It is also plotted on the secondary (right) Y-axis
# Colored blue.
import matplotlib.pyplot as plt
import numpy as np

def plot_Survivors_GenomeLength_Diversity():
    # Load the data
    data = np.loadtxt('../logs/epoch-log.txt')

    # Scale the data
    x = data[:,0]
    survivors = data[:,1]
    diversity = data[:,2] * 350
    genome_length = data[:,3] * 2

    # Create a new figure
    fig, ax1 = plt.subplots()

    # Plot the survivors on y1
    ax1.plot(x, survivors, 'g-', label='Survivors')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Survivors', color='g')

    # Create a second y axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('Scaled Values', color='r')
    ax2.set_ylim([0, 256])

    # Plot the diversity and genome length on y2
    ax2.plot(x, diversity, 'r-', label='Diversity')
    ax2.plot(x, genome_length, 'b-', label='Genome Length')

    # Add a grid
    ax1.grid(True)

    # Add a legend
    fig.legend(loc="upper left", bbox_to_anchor=(0,1), bbox_transform=ax1.transAxes)

    # Save the figure
    plt.savefig('../images/log.png', dpi=200)

if __name__ == "__main__":
    plot_Survivors_GenomeLength_Diversity()