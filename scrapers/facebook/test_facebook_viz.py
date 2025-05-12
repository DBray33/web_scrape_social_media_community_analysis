import os
import matplotlib.pyplot as plt
import numpy as np

# Create output directory if it doesn't exist
os.makedirs("visualizations/facebook", exist_ok=True)

# Create a simple test plot
plt.figure(figsize=(10, 6))
x = np.arange(10)
y = x**2
plt.plot(x, y, marker='o')
plt.title("Test Visualization")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)

# Save the plot
plt.savefig("visualizations/facebook/test_plot.png")
print("Saved test visualization to visualizations/facebook/test_plot.png")