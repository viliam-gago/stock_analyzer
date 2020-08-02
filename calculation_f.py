import finviz
import numpy_financial as np
import numpy
import pandas as pd
from datetime import datetime
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt


def load_data(ticker):
    file_data = f'{ticker}_data.txt'

    with open(file_data, 'r') as f:
        data_dict = eval(f.read())

    return data_dict


def set_index_years(data_dict):
    year_span = len(data_dict['data']['sales'])
    years = list(range(datetime.now().year - year_span, datetime.now().year))

    return years


# api data -> DataFrame
def create_summary_table(data_dict, years):
    table = pd.DataFrame(data_dict['data'], columns=data_dict['data'].keys(), index=years)

    return table


# cf4o
def add_cf4o(table, maintenance_capex_coef):
    cf4o = table['operating_cash_flow'] + (table['maintenance_capex'] * maintenance_capex_coef)
    cf4o.name = 'cf4o'
    table = table.join(cf4o)

    return table


# debt ratios
def debt_info(table):
    current_ratio = table['current_assets'] / table['current_liabilities']
    debt_to_equity_ratio = table['total_liabilities'] / table['equity']
    debt_ratios = pd.concat([current_ratio, debt_to_equity_ratio], axis=1)
    debt_ratios.columns = ['CURRENT RATIO', 'DEBT TO EQUITY RATIO']

    return debt_ratios


# roic

def av_gr_rates(stat, table, periods):
    average_rates = [((table[stat].iloc[-1] / table[stat].iloc[-n - 1]) ** (1 / n) - 1) * 100 for n in periods]

    return average_rates


def create_growth_table(table):
    periods = [9, 7, 5, 3, 1]
    growth_table = pd.DataFrame({'SALES': av_gr_rates('sales', table, periods),
                                 'EPS': av_gr_rates('eps', table, periods),
                                 'EQUITY': av_gr_rates('equity', table, periods),
                                 'CF4O': av_gr_rates('cf4o', table, periods)},
                                index=[str(number) + 'YR' for number in periods])

    return growth_table


def ROIC_calc(table):
    capital = table['long_term_debt'] + table['equity']
    ROIC = (table['cf4o'] / capital) * 100
    ROIC = ROIC.replace([numpy.inf, -numpy.inf], numpy.nan)
    roic_stats = pd.DataFrame({'ROIC_AVERAGES': [ROIC.iloc[-1], ROIC.mean()]},
                              index=['1 YR AVERAGE', '10 YR AVERAGE'])

    return ROIC, roic_stats


## shares outstanding

def recalc_shs(amount: str):
    if amount[-1] == 'B':
        return float(amount[:-1]) * (10 ** 9)
    elif amount[-1] == 'M':
        return float(amount[:-1]) * (10 ** 6)
    else:
        raise Exception('Unknown number')


def get_shares_out(ticker):
    shs_out_str = finviz.get_stock(ticker)['Shs Outstand']

    shs_out = recalc_shs(shs_out_str)

    return shs_out


def compound(tab, i):
    tab[f'Y{i}'] = tab[f'Y{i - 1}'] * (1 + (tab['GROWTH'])) // 1


def set_cf_if_unfilled(table, est_growth):
    starting_cf = pd.Series([table['cf4o'].iloc[-1]] * len(est_growth))
    return starting_cf


def cf_estimate_table(est_growth, starting_cf):
    cf_over_y = [f'Y{y}' for y in range(1, 11)]

    growth_cf_part = pd.DataFrame({"GROWTH": est_growth, 'Y0': starting_cf})
    yrs_cf_part = pd.DataFrame(0, index=range(5), columns=cf_over_y)
    growth_cf = growth_cf_part.join(yrs_cf_part)
    growth_cf.index = [f'MODEL {i}' for i in range(1, 6)]

    for i in range(1, len(cf_over_y) + 1):
        compound(growth_cf, i)

    growth_cf['TERMINAL VALUE'] = growth_cf['Y10'] * 10

    return growth_cf, growth_cf_part


##intrinsic value & buy price

def extracted_cfs(i, growth_cf):
    return list(growth_cf.loc[i][2:])


def create_final_table(growth_cf_part, growth_cf, shs_out, r_f_rate, req_return):
    final_table = growth_cf_part.copy()
    final_table['INTRINSIC VALUE'] = list(
        map(lambda i: np.npv(r_f_rate, [0] + extracted_cfs(i, growth_cf)), growth_cf.index))
    final_table['BUY PRICE'] = list(
        map(lambda i: np.npv(req_return, [0] + extracted_cfs(i, growth_cf)), growth_cf.index))
    final_table['I.V. / SHARE'] = final_table['INTRINSIC VALUE'] / shs_out
    final_table['B.P. / SHARE'] = final_table['BUY PRICE'] / shs_out

    return final_table


def format_growth_cf(growth_cf):
    growth_cf['GROWTH'] = [f'{value * 100} %' for value in growth_cf['GROWTH']]
    for column in growth_cf.columns[1:]:
        growth_cf[column] = [f'${round(value / 1000000, 2)}' for value in growth_cf[column].values]


def format_final_table(final_table):
    final_table.index = [f'MODEL {i}' for i in range(1, 6)]
    reformf = [[f'${round(value / 1000000, 2)}' for value in row] for row in
               final_table[['Y0', 'INTRINSIC VALUE', 'BUY PRICE']].values]
    final_table[['Y0', 'INTRINSIC VALUE', 'BUY PRICE']] = reformf
    final_table['GROWTH'] = [f'{value * 100} %' for value in final_table['GROWTH']]
    final_table['B.P. / SHARE'] = [f'${round(value, 2)}' for value in final_table['B.P. / SHARE']]


if __name__ == '__main__':
    ticker = 'FB'

    est_growth = pd.Series([10, 12, 14, 16, 18]) / 100
    # starting_cf = [180000000, 280000000, 280000000, 280000000, 280000000]
    starting_cf = []

    req_return = 0.19
    r_f_rate = 0.006
    maintenance_capex_coef = 0.5

    #=======================

    data_dict = load_data(ticker)
    years = set_index_years(data_dict)
    table = create_summary_table(data_dict, years)
    table = add_cf4o(table, maintenance_capex_coef)

    debt_ratios = debt_info(table)

    ROIC, roic_stats = ROIC_calc(table)

    growth_table = create_growth_table(table)

    if not starting_cf:
        starting_cf = set_cf_if_unfilled(table, est_growth)
    cf_models_table, cf_models_part = cf_estimate_table(est_growth, starting_cf)

    shs_out = get_shares_out(ticker)
    final_table = create_final_table(cf_models_part, cf_models_table, shs_out, r_f_rate, req_return)

    format_growth_cf(cf_models_table)
    format_final_table(final_table)

