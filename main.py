from urllib.request import urlopen
import json
from pprint import pprint
from datetime import datetime, timezone


def main():
    #with urlopen("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY") as response:
    #    response_content = response.read()
    #response_content.decode('utf-8')
    #json_response = json.loads(response_content)
    start_date = "01/01/2020"
    end_date = "01/08/2021"
    coin = "bitcoin"
    coin_history = get_price_history(start_date, end_date, coin)
    price_history = parse_data_history(coin_history, start_date, end_date, "prices")
    volume_history = parse_data_history(coin_history, start_date, end_date, "total_volumes")
    print(get_longest_bear(price_history))
    print(get_highest_volume(volume_history))

def get_highest_volume(volume_history):
    highest_volume = 0
    highest_volume_timestamp = 0
    for timestamp in volume_history:
        if(volume_history[timestamp] > highest_volume):
            highest_volume = volume_history[timestamp]
            highest_volume_timestamp = timestamp
    return([highest_volume, datetime.fromtimestamp(highest_volume_timestamp/1000)])

def get_optimal_investment(price_history):
    
    for timestamp in price_history:
        continue

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
    expected_timestamp = int(date_to_timestamp(start_date)*1000)
    end_timestamp = int(date_to_timestamp(end_date)*1000)
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

def date_to_timestamp(date):
    dt = date.split("/")
    dt = datetime(int(dt[2]),int(dt[1]),int(dt[0]))
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    return timestamp

def get_price_history(start_date, end_date, coin):
    # 3600 added to end date in order to make sure end date midnight is included
    with urlopen("https://api.coingecko.com/api/v3/coins/" + coin + "/market_chart/range?vs_currency=eur&from=" + str(date_to_timestamp(start_date) - 3600) + "&to=" + str(date_to_timestamp(end_date) + 3600)) as response:
        response_content = response.read()
    response_content.decode('utf-8')
    json_response = json.loads(response_content)
    return json_response

if __name__ == '__main__':
    main()