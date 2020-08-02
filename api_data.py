import requests



def create_ticker(ticker):
    ticker = ticker + ':US'

    return ticker


def set_request(ticker, api_key):
    api_key = '84dc8a2756260d474e62d4de82f9e2cef24d58f2'
    header = {'x-qfs-api-key': api_key}
    ticker = 'PEP:US'

    period = {'period': 'FY-2:FY'}

    request_body = {
        "data": {
            "sales": f"QFS({ticker},revenue, {period})",
            "eps": f"QFS({ticker},eps_diluted, {period})",
            "equity": f"QFS({ticker},total_equity, {period})",
            "long_term_debt": f"QFS({ticker},lt_debt, {period})",
            "current_liabilities": f"QFS({ticker},total_current_liabilities, {period})",
            "current_assets": f"QFS({ticker},total_current_assets, {period})",
            "total_liabilities": f"QFS({ticker},total_liabilities, {period})",
            "operating_cash_flow": f"QFS({ticker},cf_cfo, {period})",
            "maintenance_capex": f"QFS({ticker},cfi_ppe_net, {period})",
        }
    }

    return request_body, header


def get_data(request_body, header):
    response = requests.post("https://public-api.quickfs.net/v1/data/batch", json=request_body, headers=header).json()
    usage = requests.get('https://public-api.quickfs.net/v1/usage', headers=header).json()

    return response, usage


def save_data(response, ticker):
    filename = ticker.split(':')[0] + '_data.txt'

    with open(filename, 'w') as f:
        f.write(str(response))



if __name__ == '__main__':

    ticker = 'FDX'
    api_key = '84dc8a2756260d474e62d4de82f9e2cef24d58f2'

    create_ticker(ticker)
    request_body, header = set_request(ticker, api_key)
    response, usage = get_data(request_body, header)
    save_data(response,ticker)


    # print(response)
    print(usage)