import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from math import pi
import os

def plot_hits_result(values, save_path=None):
    """
    Generates a radar chart of the results for HITS.
    
    Args:
        values (list): A list of exactly 10 numerical values.
    
    Raises:
        ValueError: If the length of values is not 10.
    """
    if len(values) != 10:
        raise ValueError("Values list must contain exactly 10 elements.")
        
    categories = [
            'EC Path Length', 'EO Path Length', 'H. Fixation', 
            'H. Targeting', 'H. S/A Ratio', 'V. Targeting', 
            'V. S/A Ratio', 'V. Efficiency', 'Time', 'Accuracy'
    ]
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Completing the loop for a circular plot.
    values += values[:1]
    
    # Create the radar chart.
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Set transparent background
    fig.patch.set_alpha(0)  # Figure background.
    ax.set_facecolor('none')  # Axis background.
        
    # Define circular regions with different background colors.
    radii = [0, 50, 100]
    colors = ["red", "blue"]

    # Fill each circular layer.
    for i in range(len(radii) - 1):
        theta = np.linspace(0, 2 * np.pi, 100)
        ax.fill_between(theta, radii[i], radii[i+1], color=colors[i], alpha=0.25)
        
    # Plot radar chart values.
    ax.plot(angles, values, color='green', linewidth=2, label="Patient", zorder=3)
    ax.fill(angles, values, color='green', alpha=0.25, zorder=3)
        
    # Configure axis and labels.
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Change category label font size.
    ax.set_thetagrids(np.degrees(angles[:-1]), categories, fontsize=20)

    # Set all category label colors to white.
    for label in ax.get_xticklabels():
        label.set_color("white")  # Change text color to white.

    # Go through labels and adjust alignment based on where it is in the circle.
    for label, angle in zip(ax.get_xticklabels(), angles):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')

    # Set the radial limit (0-100).
    ax.set_ylim(0, 100)
    # Set position of y-labels to be in the middle.
    ax.set_rlabel_position(0 / num_vars)
    # Change the color of the tick labels.
    ax.tick_params(colors='black', axis='y', labelsize=8)
    # Change the color of the circular gridlines.
    ax.grid(color='grey')
    # Change the color of the outermost gridline (the spine).
    ax.spines['polar'].set_color('black')
    # Change the width of the outermost gridline (the spine).
    ax.spines['polar'].set_linewidth(2)
    # Change the background color inside the circle itself.
    ax.set_facecolor('white')
        
    # Add overlay pie chart to indicate different test types.
    sizes = [20, 60, 20]
    labels = ['Cognitive Function', 'Eye Tracking', 'Balance Test']
    ax2 = fig.add_subplot(111, label="pie axes", zorder=-1)
    ax2.pie(sizes, radius=1.305, autopct='%1.1f%%', startangle=108.5, labeldistance=1.05,
            wedgeprops={'edgecolor': 'black', 'linewidth': 2}, colors=['blue', 'red', 'yellow'])
    ax2.set(aspect="equal")
        
    # Draw section dividers.
    for angle in [np.pi / 4 + 0.15, np.pi * 3 / 2 - 0.01, -0.32]:
        ax.plot([angle, angle], [0, 100], color='black', linewidth=2)
        
    # Create and display legend.
    radar_line = mlines.Line2D([0], [0], color='green', label='Patient', linewidth=2)
    red_patch = mpatches.Patch(color='red', label='Concussed Zone', alpha=0.25)
    blue_patch = mpatches.Patch(color='blue', label='Non-Concussed Zone', alpha=0.25)
    handles = [radar_line, red_patch, blue_patch]
    # Add legend for radar plot.
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.38, 0.83), fontsize=16)
    # Add legend for pie plot.
    plt.legend(labels=labels, loc='upper right', bbox_to_anchor=(2.05, 1.10), fontsize=16)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    # Show the plot.
    plt.show()

# Example use:
values = [70, 66, 75, 87, 60, 75, 63, 69, 74, 82]
plot_hits_result(values, save_path=r"C:\Users\richy\Documents\Git\HITS\Results images\hits_result_chart.png")