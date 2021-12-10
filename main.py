from urllib.request import urlopen
import json
import argparse
from pprint import pprint
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start_date", help="Start date in format DD.MM.YY", type=lambda s: datetime.strptime(s, '%d.%m.%Y'))
    parser.add_argument("end_date", help="End date in format DD.MM.YY", type=lambda s: datetime.strptime(s, '%d.%m.%Y'))
    args = parser.parse_args()

    start_date = args.start_date
    end_date = args.end_date
    if(start_date > end_date):
        parser.error("start_date must be before end_date")
    coin = "bitcoin"
    coin_history = get_price_history(start_date, end_date, coin)
    price_history = parse_data_history(coin_history, start_date, end_date, "prices")
    longest_bear = get_longest_bear(price_history)
    volume_history = parse_data_history(coin_history, start_date, end_date, "total_volumes")
    optimal_investment_dates = get_optimal_investment(price_history)
    highest_volume = get_highest_volume(volume_history)

    print("Longest bearish trend:", longest_bear[0])
    print("Highest volume:",highest_volume[0], "on", highest_volume[1].strftime("%d.%m.%Y"))
    if(optimal_investment_dates[0] == 0):
        print("Optimal investment dates: do not invest in this period")
    else:
        print("Optimal investment dates: buy on",optimal_investment_dates[0].strftime("%d.%m.%Y"),"and sell on", optimal_investment_dates[1].strftime("%d.%m.%Y"))

def get_highest_volume(volume_history):
    highest_volume = 0
    highest_volume_timestamp = 0
    for timestamp in volume_history:
        if(volume_history[timestamp] > highest_volume):
            highest_volume = volume_history[timestamp]
            highest_volume_timestamp = timestamp
    return([highest_volume, datetime.fromtimestamp(highest_volume_timestamp/1000)])

def get_optimal_investment(price_history):
    sorted_history = sorted(price_history, key=price_history.get)
    largest_profit = 0
    largest_profit_dates = [0,0]
    complete = False
    current_end_price = 0
    current_start_price = 0
    current_time = 0
    current_iteration = 0
    # Loop from largest price down
    for current_end_time in reversed(sorted_history):
        current_end_price = price_history[current_end_time]
        if(current_end_price - price_history[sorted_history[0]] < largest_profit):
            # Not possible to find better deal, break
            break
        # Loop from smallest price up
        for current_start_time in sorted_history:
            current_start_price = price_history[current_start_time]

            if(current_end_price - current_start_price > largest_profit):
                if(current_end_time > current_start_time):
                    # Found start price that is before end price, no reason to continue with current end price
                    largest_profit = current_end_price - current_start_price
                    largest_profit_dates = [datetime.fromtimestamp(current_start_time/1000), datetime.fromtimestamp(current_end_time/1000)]
                    break
            else:
                #Maximum profit is smaller that largest found profit, no reason to continue
                break
    return(largest_profit_dates)
                

def get_longest_bear(price_history):
    previous_price = 0
    longest_bear_start = 0
    longest_bear_end = 0
    longest_bear_length = 0
    current_bear_start = 0
    current_bear_length = 0
    for timestamp in price_history:
        if(price_history[timestamp] < previous_price):
            current_bear_length += 1
        else:
            current_bear_start = timestamp
            current_bear_length = 0
        if(current_bear_length > longest_bear_length):
            longest_bear_length = current_bear_length
            longest_bear_start = current_bear_start
            longest_bear_end = timestamp
        previous_price = price_history[timestamp]
    return([longest_bear_length, datetime.fromtimestamp(longest_bear_start/1000), datetime.fromtimestamp(longest_bear_end/1000)])

def parse_data_history(data, start_date, end_date, data_type):
    datapoints = {}
    previous_value = data[data_type][0]
    expected_timestamp = int(datetime.timestamp(start_date)*1000)
    end_timestamp = int(datetime.timestamp(end_date)*1000)
    # Parse response to inlcude only values closest to midnight utc
    for k in data[data_type]:
        # Timestamp is correct
        if(k[0] == expected_timestamp):
            datapoints[k[0]] = k[1]
            expected_timestamp+=86400000
        elif(k[0] > expected_timestamp):
            # Current value was closer to midnight than previous
            if(abs(k[0]-expected_timestamp)<abs(previous_value[0]-expected_timestamp)):
                datapoints[k[0]] = k[1]
            #Previous value was closer to midnight
            else:
                datapoints[previous_value[0]] = previous_value[1]
            expected_timestamp+=86400000
        if(end_timestamp < expected_timestamp):
            break
        previous_value = k
    return datapoints



def get_price_history(start_date, end_date, coin):
    # 3600 added to end date in order to make sure end date midnight is included
    with urlopen("https://api.coingecko.com/api/v3/coins/" + coin + "/market_chart/range?vs_currency=eur&from=" + str(datetime.timestamp(start_date) - 3600) + "&to=" + str(datetime.timestamp(end_date) + 3600)) as response:
        response_content = response.read()
    response_content.decode('utf-8')
    json_response = json.loads(response_content)
    return json_response

if __name__ == '__main__':
    main()