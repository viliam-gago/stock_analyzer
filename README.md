# Stock Analyzer

App serves for quick evaluation of particular stock from US stock exchanges.

For fundamental analysis of a stock, it is necessary to get historical info, representing decissions and results of particular bussines.
I handled the task using quick.fs.net webpage's API, where is possible to acces required data. This task was a good practice of creating basic API requests and storing
results into convenient .txt format.

The process of stock evaluation uses basic methods of value investing, which I tried to implement in Python algorithm. Use of Pandas library was very convenient in this case.
In the end app offers quick calculation of many stock metrices, like debt ratios, intrinsic value, cashflow growth etc., requiring just the ticker symbol of particular stock. 
This project gave me new insights of Python modules, especially Pandas and served as a great learning experience.


## How to use:
This project was initially created in jupyter notebook format. Thus, the use is not perfectly automatized, but everything works correctly.

- run 'api_data.py' in command line, as an argument, pass the ticker of desired stock 
  -> this creates .csv file in working directory with all the data needed
- run 'stock_analyzer_2.py' as a script: change ticker according to desired stock (calculation will work only if the .txt file for particular stock was created)
- based on further analysis of particular stock, set parameters as required_return, coefficient for maintenance capex calculation, etc.
- running the script induces while loop, where you can look up computed results

## Files:
- api_data.py ... script for downloading data from web
- calculation_f.py ... functions used in computation process
- stock_analyzer_2.py ... main file 
- .txt files ... representing downloaded data for particular stock; required for further analysis of particular stock
