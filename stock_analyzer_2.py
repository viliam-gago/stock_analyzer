import calculation_f as clc
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

def breakpoint():
    brk = input('Press enter to contiune:')

# You should tune these parameters according to particluar stock. Do not use this as definitive tool for stock
# evaluation - it provides just quick info, thus, further analysis is required.
ticker = 'AAPL'
est_growth = pd.Series([0, 2, 4, 6, 8]) / 100
#starting_cf = [180000000, 280000000, 280000000, 280000000, 280000000]
starting_cf = []

req_return = 0.22
r_f_rate = 0.01
maintenance_capex_coef = 0.5


#   ===== CALCULATION =====
data_dict = clc.load_data(ticker)
years = clc.set_index_years(data_dict)
table = clc.create_summary_table(data_dict, years)
table = clc.add_cf4o(table, maintenance_capex_coef)

debt_ratios = clc.debt_info(table)

ROIC, roic_stats = clc.ROIC_calc(table)
growth_history_table = clc.create_growth_table(table)

#starting CF obtained from free_cashflow_for_owner. This can vary according to capital expenditures estimation,
# where subjectivity is significant.
## Possible to set starting cashflow manually for further computation of various cashflow growth models
if not starting_cf:
    starting_cf = clc.set_cf_if_unfilled(table, est_growth)
cf_models_table, cf_models_part = clc.cf_estimate_table(est_growth, starting_cf)

shs_out = clc.get_shares_out(ticker)
final_table = clc.create_final_table(cf_models_part, cf_models_table, shs_out, r_f_rate, req_return)

clc.format_growth_cf(cf_models_table)
clc.format_final_table(final_table)

# === RESULTS ===
string = """SHOW:
1) Stock fundaments
2) Debt_ratios
3) ROIC averages
4) ROIC year by year
5) Historical growth
6) CashFlow growth models year by year
7) Intrinsic value results
8) Graphical representation - ROIC / Sales, EPS, Equity, CF4O history growth
0) QUIT

"""

while True:
    print('\n')

    inp = int(input(string))

    if inp == 1:
        print(table)
        breakpoint()

    elif inp == 2:
        print(debt_ratios)
        breakpoint()

    elif inp == 3:
        print(roic_stats)
        breakpoint()

    elif inp == 4:
        print(ROIC.to_frame(name='ROIC %'))
        breakpoint()

    elif inp == 5:
        print(growth_history_table.T)
        breakpoint()

    elif inp == 6:
        print(cf_models_table)
        breakpoint()

    elif inp == 7:
        print(final_table)
        breakpoint()

    elif inp == 8:
        figure, axes = plt.subplots(1,2, figsize=(9,5))
        ax = ROIC.plot.bar(title='ROIC', ax=axes[0])
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax.grid(axis='y')

        growth_history_table.plot(title='Fundamentals over years', ax=axes[1])
        plt.show()
        continue

    elif inp == 0:

        break
