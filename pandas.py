import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
dates = pd.date_range("2024-01-01", periods=200)
prices = 100 + np.cumsum(np.random.randn(200))  # random walk

df = pd.DataFrame({"Date": dates, "Price": prices})
df.set_index("Date", inplace=True)

window = 10  # size of sliding window

df["Rolling_Mean"] = df["Price"].rolling(window).mean()
df["Rolling_Std"] = df["Price"].rolling(window).std()
df["Rolling_Slope"] = (
    df["Price"]
    .rolling(window)
    .apply(lambda x: np.polyfit(range(window), x, 1)[0], raw=True)
)


plt.figure(figsize=(12, 6))
plt.plot(df.index, df["Price"], label="Price", alpha=0.6)
plt.plot(df.index, df["Rolling_Mean"], label=f"{window}-Day Mean", linewidth=2)
plt.fill_between(
    df.index,
    df["Rolling_Mean"] - df["Rolling_Std"],
    df["Rolling_Mean"] + df["Rolling_Std"],
    color="orange",
    alpha=0.2,
    label="±1 Std Dev"
)

plt.title("Sliding Window Analysis of Time Series")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(alpha=0.3)
plt.show()

df["Trend"] = np.where(df["Rolling_Slope"] > 0, "Up", "Down")
print(df.tail(10))
