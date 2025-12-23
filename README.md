# python_git_linux_finance



## Automation (Daily Report)

A daily report is automatically generated at **8:00 PM** via a Cron job. The report is appended to `daily_logs.txt` and includes:

1.  **Quant A (Single Asset):** Analysis of **BTC-USD** (Bitcoin) including Last Price, Volatility, and Sharpe Ratio.
2.  **Quant B (Portfolio):** Performance of the user's current portfolio (loaded from `portfolio_config.json`), including 24h Performance, Total Value, and Max Drawdown.

**Cron Configuration:**
```bash
# Run daily at 20:00
0 20 * * * /usr/bin/python3 /path/to/project/daily_report.py