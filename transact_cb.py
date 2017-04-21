
import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from datetime import datetime,date,timedelta

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
	def __init__(self, api_key, secret_key, passphrase):
		self.api_key = api_key
		self.secret_key = secret_key
		self.passphrase = passphrase

	def __call__(self, request):
		timestamp = str(time.time())
		message = timestamp + request.method + request.path_url + (request.body or '')
		message = message.encode('ascii')
		hmac_key = base64.b64decode(self.secret_key)
		signature = hmac.new(hmac_key, message, hashlib.sha256)
		signature_b64 = base64.b64encode(signature.digest())
		request.headers.update({
		    'Content-Type': 'Application/JSON',
		    'CB-ACCESS-SIGN': signature_b64,
		    'CB-ACCESS-TIMESTAMP': timestamp,
		    'CB-ACCESS-KEY': self.api_key,
		    'CB-ACCESS-PASSPHRASE': self.passphrase
		})
		return request



def load_key(path):
	f = open(path, "r")
	key = f.readline().strip()
	secret = f.readline().strip()
	API_PASS = f.readline().strip()
	return key, secret, API_PASS

	
api_url = 'https://api.gdax.com/'

def auth():	
	API_KEY,API_SECRET,API_PASS = load_key('coinbase.key')
	API_KEY.encode('utf-8')
	API_PASS.encode('utf-8')
	auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)
	return auth


def cb_trade(otype,quantity,price,product):

	'''otype = buy or sell '''

	order = {
	'size': quantity,
	'price': price,
	'side': otype,
	'product_id': product,
	'post_only': True,
	}
	r = requests.post(api_url + 'orders',data=json.dumps(order),auth=auth())
	x = r.json()
	return x

def cb_trade_agg(otype,quantity,price,product):

	'''otype = buy or sell '''

	order = {
	'size': quantity,
	'price': price,
	'side': otype,
	'product_id': product
	}
	r = requests.post(api_url + 'orders', json=order, auth=auth())
	print (r)
	x = r.json()
	print (x)
	return x

def cancel_all():
	try:
		r = requests.delete(api_url +'orders',auth=auth())
		x = r.json()
	except:
		print ('Cancel Error')
		x = 0
	return x

def cancel_order(id):
	r = requests.delete(api_url +'orders/'+ id,auth=auth())
	x = r.json()
	return x

def cb_open():
	try:
		r = requests.get(api_url + 'orders', auth=auth(),timeout=10)
		x = r.json()
	except:
		print ('CB_OPEN ERROR')
		x = 'ERROR'
	return x


def cb_balance():
	balances = []
	try:
		r = requests.get(api_url + 'accounts', auth=auth(),timeout=10)
		x = r.json()
		for i in x:
			y = (i['currency'],i['balance'])
			balances.append(y)
	except:
		print ('CB_BALANCE ERROR')
		balances = 'ERROR'
	return balances

def cb_history():
	accounts =[]
	history =[]
	try:
		r = requests.get(api_url + 'accounts', auth=auth())
		x = r.json()
		for i in x:
			y =float(i['balance'])
			if y > 0:
				accounts.append(i['id'])
		for i in accounts:
			r = requests.get(api_url + 'accounts/' + i +'/ledger', auth=auth())
			x = r.json()
			for j in x:
				bb =datetime.strptime(j['created_at'][:10], '%Y-%m-%d')
				bbb = timedelta(days=1)
				if datetime.today()-bb < bbb:
					history.append(j.copy())
		return history
	except:
		print ('cbhistory error')
		history = [0]
		return history

def cb_orderbook():
	try:
		r = requests.get(api_url + 'products/BTC-USD/book?level=2', auth=auth())
		x = r.json()
		ob = x
		return ob
	except:
		print ('ob_error')
		ob = 'Error'
		return ob







# def cb_history2():
# 	accounts =[]
# 	history =[]
# 	r = requests.get(api_url + 'fills', auth=auth())
# 	x = r.json()
# 	for i in x:
# 		print (i)
# 		history.append(i)
# 	return history
# num_trades =0
# for i in cb_history():
# 	num_trades += 1
# print (num_trades)
#print (cb_balance())

#print (cb_open())
#print (cb_trade_eth('sell',1,.0195))

#print (cb_trade_eth('sell','1',.0197))
#print (cb_trade_eth('buy','1',.0194))
#print (cb_open())


'''
We need to figure out what confirm looks like
'''