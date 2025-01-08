# Version 1.1
- Designed an efficient data structure (in object.py) for massive stock data and optimised the data query APIs, **significantly improved backtesting speed**.
- Provided a new example strategy (in userStrategy.py), which is more complex and has a much bigger security pool than the double MA Strategy (in doublelines.py), to test the framework performance.
- Optimised the Recorder module, now you can see details of the point if your mouse is near the pnl curves. Here is an example:
<p align="center">
  <img src ="https://github.com/cpu9xx/LiquidQuant-backtest-framework/blob/main/userstrategypnl.png"/, width=500>
</p>

- Log will be automatically generated after backtesting.
- Separated userconfig setting from the workplace, now you can edit backtesting params more comfortably.
- Added more APIs.
- Fixed some bugs.
2024-10-6 UPDATE

# Objective
This backtesting framework is designed for China's A-shares market, leveraging the advantages of Joinquant and Backtrader, based on my use experiences.

Joinquant(www.joinquant.com) is an online powerful backtesting framework that is easy to use. Even beginners can quickly figure out how to develop and share their own strategies with Joinquant. This attracts many users, making it the biggest quant forum in China. However, Joinquant cannot cater to the needs of modern data mining techniques. It does not support deep learning packages like Pytorch and TensorFlow and has serious speed problems while backtesting. This limits the diversity and complexity of strategies and significantly drags the progress of strategy development. To overcome its limitations while leveraging its advantages, I developed a local backtesting framework with well-designed APIs, strong speed performance, and good scalability.

# Instrument
## Datafeed
To use this framework, you should have access to two MySQL databases, named 'stock' and 'index'. The 'stock' database should contain tables, and each table contains time series data for one stock. Ensure the table name is like 'xxxxxx.sz' (Shenzhen Exchange) or 'xxxxxx.sh' (Shanghai Exchange). Similarly, the 'index' database should contain indexes such as CSI 300.

You can construct your MySQL databases easily using https://github.com/cpu9xx/MySQLdb-Initial-and-Update-based-on-Tushare.

## Strategy
Develop your strategy in userStrategy.py. If it is the first time loading data, set the "if_load_data" in "userconfig" dict to False. Once you load, a new pickle file named 'data.pkl' will be created, it is used for save data loading time. Then you can directly load data from 'data.pkl' rather than the database by setting "if_load_data" to True. Run the following to backtest:
```
python run.py
```

After backtesting, the profit and loss curve will be automatically presented like this:
<p align="center">
  <img src ="https://github.com/cpu9xx/LiquidQuant-backtest-framework/blob/main/doubleMApnl.png"/, width=500>
</p>


# Requirements 
- python>=3.8.10
- matplotlib==3.7.1
- pandas==1.4.2
- numpy==1.24.4
- SQLAlchemy==2.0.35

