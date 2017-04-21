'''
Data Grabber

Exchanges and data:
GDAX
KRAKEN
OKCOIN
BTCE
POLONIEX
BITFINEX
CRYPTOFACILITIES

'''

import cfRestApiV2 as cfApi
import datetime

apiPath = "https://www.cryptofacilities.com/derivatives"
apiPublicKey = "..." # accessible on your Account page under Settings -> API Keys
apiPrivateKey = "..." # accessible on your Account page under Settings -> API Keys
timeout = 10
checkCertificate = True # when using the test environment, this must be set to "False"   

cfPublic = cfApi.cfApiMethods( apiPath, timeout = timeout, checkCertificate = checkCertificate )    
cfPrivate = cfApi.cfApiMethods( apiPath, apiPublicKey = apiPublicKey, apiPrivateKey = apiPrivateKey, \
    checkCertificate = checkCertificate  )

def APITester():        
    ##### public endpoints #####  
      
    # get instruments    
    result = cfPublic.get_instruments()
    print( "get_instruments:\n", result )

    # get tickers
    result = cfPublic.get_tickers()
    print( "get_tickers:\n", result )
    
    # get order book
    symbol = "f-xbt:usd-sep16"
    result = cfPublic.get_orderbook( symbol )
    print( "get_orderbook:\n", result )
