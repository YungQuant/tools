# Gdax Websocket

from websocket import create_connection as cc
import json, time


class Home():
    def __init__(self, *args, **kwargs):

        super(Home, self).__init__()

        # Establishing a connection to the websocket

        url = 'wss://ws-feed.gdax.com'
        data = cc(url)

        # Sending the server a proper message to get updates on
        # Bitcoin, Ethereum, and Litecoin in Dollars

        msg = {'type': 'subscribe', 'product_ids': ['BTC-USD', 'ETH-USD', 'LTC-USD']}
        data.send(json.dumps(msg))

        # While loop ensures updates are constantly recieved forever

        while True:
            output = json.loads(data.recv())

            # Try Except is used in case certain order flows do not have one of
            # these variables

            try:

                # The 'output' variable contains data on each event, all data is organized
                # into json format making it easy to call the values as shown below

                order_Type = output['type']
                order_Side = output['side']
                order_Ticker = output['product_id']
                order_Price = output['price']
                order_Volume = output['remaining_size']

                print(order_Ticker, order_Type, order_Side,
                      order_Price, order_Volume, sep='\t')
                time.sleep(1)
            except:

                print("GDAX_mo failed!")


Home()