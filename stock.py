import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

# =====================
# Utility Functions
# =====================
def dividend_growth_length(dividends: pd.Series) -> int:
    """Calculate consecutive years of dividend growth."""
    if dividends.empty:
        return 0
    df = dividends.resample("YE").sum()
    amounts = df.values
    length = 0
    for i in range(1, len(amounts)):
        if amounts[i] > amounts[i - 1]:
            length += 1
        else:
            break
    return length


def score_safety(info, dividends, history, sector_avgs):
    """Score stock safety based on volatility, debt, beta, dividends."""
    monthly_returns = history["Close"].pct_change()
    volatility = monthly_returns.std() * (12**0.5) * 100

    beta = info.get("beta", 1)
    dividend_yield = (info.get("dividendYield") or 0) * 100
    div_growth_years = dividend_growth_length(dividends)
    debt_equity = info.get("debtToEquity") or 0
    sector = info.get("sector")
    sector_de = sector_avgs["DebtToEquity"].get(sector)

    score = 0

    # Volatility
    if volatility < 10:
        score += 1
    elif volatility < 20:
        score += 2
    elif volatility < 30:
        score += 1

    # Debt levels
    if debt_equity > 0:
        if debt_equity < 50:
            score += 2
        elif debt_equity < 150:
            score += 1

    # Compare with sector debt
    if sector_de and debt_equity > 0:
        if debt_equity < 0.7 * sector_de:
            score += 2
        elif debt_equity < sector_de:
            score += 1

    # Beta
    if beta < 1:
        score += 2
    elif beta < 1.3:
        score += 1

    # Dividend Yield
    if dividend_yield >= 3:
        score += 2
    elif dividend_yield >= 1:
        score += 1

    # Dividend growth streak
    if div_growth_years >= 20:
        score += 3
    elif div_growth_years >= 15:
        score += 2
    elif div_growth_years >= 10:
        score += 1

    return round(score * 3, 1)


def score_potential(info, sector_avgs):
    """Score growth/potential based on valuation metrics."""
    price = info.get("regularMarketPrice")
    target_price = info.get("targetMeanPrice")
    trailing_pe = info.get("trailingPE") or 0
    forward_pe = info.get("forwardPE") or 0
    peg_ratio = info.get("pegRatio") or 0
    pb_ratio = info.get("priceToBook") or 0
    sector = info.get("sector")

    upside = 0
    if price and target_price:
        upside = ((target_price - price) / price) * 100

    score = 0

    # Upside potential
    if upside > 30:
        score += 2
    elif upside > 20:
        score += 1

    # Sector-relative valuation
    if sector in sector_avgs["TrailingPE"]:
        sector_trailing = sector_avgs["TrailingPE"].get(sector)
        sector_forward = sector_avgs["ForwardPE"].get(sector)
        sector_pb = sector_avgs["PB"].get(sector)

        if trailing_pe and sector_trailing:
            score += 5 if trailing_pe < 0.8 * sector_trailing else 2 if trailing_pe < sector_trailing else 0

        if forward_pe and sector_forward:
            score += 4 if forward_pe < 0.8 * sector_forward else 2 if forward_pe < sector_forward else 0

        if pb_ratio and sector_pb:
            score += 2 if pb_ratio < 0.7 * sector_pb else 1 if pb_ratio < sector_pb else 0
    else:
        if forward_pe < 20:
            score += 3
        elif trailing_pe < 20:
            score += 2
        elif forward_pe < 30:
            score += 1

    # PEG ratio
    if 0 < peg_ratio < 1.5:
        score += 5
    elif 1.5 <= peg_ratio <= 2:
        score += 3
    elif peg_ratio <= 4:
        score += 1

    return round(score * 6, 1)


def score_analysts(info):
    """Convert analyst recommendations to score."""
    
    symbol = info.get("symbol")
    if symbol.upper() == "BYDDF" or symbol.upper() == "NVO":
        return 7
    
    rec_mean = info.get("recommendationMean")
    if rec_mean:
        if rec_mean <= 1.5:
            return 10
        elif rec_mean <= 2:
            return 7
        elif rec_mean <= 2.5:
            return 4
        else:
            return 1
    return 0


def fetch_stock(symbol):
    """Download stock data safely."""
    try:
        t = yf.Ticker(symbol)
        return {
            "symbol": symbol,
            "info": t.info,
            "dividends": t.dividends,
            "history": t.history(period="1y", interval="5d")
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


# =====================
# Main Dashboard
# =====================
st.set_page_config(page_title="Stock Screener", layout="wide")
st.title("📊 Stock Screener & Ranking")

# Load symbols list
file_path = "C:/Users/nalbe/Desktop/sp500.txt"
with open(file_path, "r") as file:
    stocks = file.read().strip().split()

# Fetch data in parallel
all_data = []
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = {executor.submit(fetch_stock, symbol): symbol for symbol in stocks}
    for future in as_completed(futures):
        result = future.result()
        if result:
            all_data.append(result)

# Build sector averages
sector_data = []
for entry in all_data:
    info = entry["info"]
    if not info:
        continue
    sector = info.get("sector")
    if sector:
        sector_data.append((
            sector,
            info.get("trailingPE"),
            info.get("forwardPE"),
            info.get("priceToBook"),
            info.get("debtToEquity")
        ))

sector_df = pd.DataFrame(sector_data, columns=["Sector", "TrailingPE", "ForwardPE", "PB", "DebtToEquity"])
sector_avgs = (
    sector_df.groupby("Sector")[["TrailingPE", "ForwardPE", "PB", "DebtToEquity"]]
    .mean()
    .to_dict()
)

# Score all stocks
results = []
for entry in all_data:
    info = entry["info"]
    if not info:
        continue
    try:
        name = info.get("longName", entry["symbol"])
        s_score = score_safety(info, entry["dividends"], entry["history"], sector_avgs)
        p_score = score_potential(info, sector_avgs)
        a_score = score_analysts(info)
        total_score = s_score + p_score + a_score

        results.append({
            "Name": name,
            "Safety": s_score,
            "Potential": p_score,
            "Analysts": a_score,
            "Total Score": round(total_score, 1),
            "Sector": info.get("sector", "N/A"),
            "TrailingPE": info.get("trailingPE"),
            "Price": f"{round(info.get("regularMarketPrice")*0.86, 2)} €",
        })
    except Exception as e:
        print(f"Error scoring {entry['symbol']}: {e}")

# Display Data
if results:
    df = pd.DataFrame(results).sort_values(by="Total Score", ascending=False)

    st.subheader("🏆 Ranked Stocks")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Sector Averages")
    st.dataframe(pd.DataFrame(sector_avgs), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 Safety")
        st.table(df.nlargest(5, "Safety")["Name Safety".split()])
    with col2:
        st.subheader("Top 5 Potential")
        st.table(df.nlargest(5, "Potential")["Name Potential".split()])
