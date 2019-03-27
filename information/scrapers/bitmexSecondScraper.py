from bitmex_websocket import BitMEXWebsocket
import logging
from time import sleep

# api_key="rKe5sHImgSw9yMK23cQV7w_r", api_secret="gFh9Mftyxka3VenutEKOSXuowk2yIZ4lkErMh3zzyZYfpRRu"
# Basic use of websocket.
def run():

    # Instantiating the WS will make it connect. Be sure to add your api_key/api_secret.
    ws = BitMEXWebsocket(endpoint="https://www.bitmex.com/api/v1", symbol="XBTUSD", api_key=None, api_secret=None)
    # ws = BitMEXWebsocket().

    print("ws.get_instrument():", ws.get_instrument())

    # Run forever
    while(ws.ws.sock.connected):
        print("Ticker: %s" % ws.get_ticker())
        print("Data:", ws.data)
        # if ws.api_key:
        #     print("Funds: %s" % ws.funds())
        # print("Market Depth: %s" % ws.market_depth())
        # print("Recent Trades: %s\n\n" % ws.recent_trades())
        sleep(10)


if __name__ == "__main__":
    run()