'''market maker program'''

from transact_cb import *
from stored import *
import numpy as np
import time, json, requests, csv, datetime
import pandas as pd

'''
Trade on candle sticks...so in between really large orders (more likely to be on ask side, so acoommodate)
Find large order on buy/sell side and create bid/asks

Have it cancel an order if you get another one (ie large order pops up ahead of it or large order moves further out)
Have limit to how big spread


'''
class cstick_trader:
	def make_mark(self,product,trade_quant,spread_thresh,order_thresh):
		print (cancel_all())
		profit,open_bids,open_asks,num_orders,start= (0,0,0,0,1)
		today = datetime.date.today().strftime("%B %d, %Y")
		name = today + '_OB_trader.csv'
		p1 = product.split('/')[0]
		p2 = product.split('/')[1]
		prod_string = p1+'-'+p2
		x = cb_balance()
		for i in x:
			if i[0]=='USD':
				starting_usd_balance =float(i[1])
			if i[0] =='BTC':
				starting_btc_balance = float(i[1])
		quant_change = 0
		breaker = 0
		with open(name,'a') as fd:
			writer = csv.writer(fd)
			writer.writerow(['time','bid','ask','usd_change','btc_change'])
		while True:
			if breaker==1:
				break
			zzz=0
			heartbeat=1
			USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
			if USD ==0:
				break
			start_price = float(USD)
			titles = ('time','low','high','open','close','volume')
			init_time = 0
			while True and zzz==0:
				heartbeat=heartbeat+1
				if heartbeat ==10:
					print ('.')
					heartbeat=1
				time.sleep(1)
				USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
				if USD == 0:
					break
				bid = float(bid)
				ask = float(ask)
				USD = float(USD)
				sp = ask - bid
				ob =cb_orderbook()
				level =1
				for i in ob['bids']:
					price,size,orders  = (float(i[0]),float(i[1]),float(i[2]))
					if size >= 4:
						if sp < .02 and level == 1:
							open_bid_price = round(float(price),2)
						else:
							open_bid_price = round(float(price+.01),2)
						break
					elif ask - bid >= spread_thresh:
						open_bid_price = round(float(price),2)
						break
					level += 1
					open_bid_price = round(float(price),2)
				level =1
				for i in ob['asks']:
					price,size,orders  = (float(i[0]),float(i[1]),float(i[2]))
					if size >= 10:
						if sp < .02 and level == 1:
							open_ask_price = round(float(price),2)
						else:
							open_ask_price = round(float(price-.01),2)
						break
					elif price - ask >= spread_thresh:
						open_ask_price = round(float(price),2)
						break
					level += 1
					open_ask_price = round(float(price),2)
				if start == 1:
					change,start = (1,0)
				else:
					change = 0    
				x = cb_balance()
				if x == 'ERROR':
					break
				for i in x:
					if i[0]=='BTC':
						bitcoin = float(i[1]) 

					elif i[0]=='USD':
							USD_balance = float(i[1])
				quant_change = bitcoin - starting_btc_balance

				if ask - bid > 0:
					open_bids, open_asks = (0,0)
					x = cb_open()
					if x =='ERROR':
						break
					for i in x:
						if i['side'] == 'buy':
							open_bids += 1
							bid_price = float(i['price'])
							bid_id = i['id']
						else:
							open_asks += 1
							ask_price = float(i['price'])
							ask_id = i['id']
					open_orders = open_asks + open_bids

					if quant_change <=0:
						if open_bids == 0:
							print ('BID PLACED',cb_trade('buy',trade_quant,open_bid_price,prod_string))
							open_orders += 1
							num_orders += 1
							change = 1
						elif abs(bid - open_bid_price) > order_thresh:
							print ('Modification Cancel:',cancel_order(bid_id))
							print ('BID PLACED',cb_trade('buy',trade_quant,open_bid_price,prod_string))
							open_orders += 1
							num_orders += 1
							change = 1
						elif bid_price < open_bid_price:
							print ('Modification Cancel:',cancel_order(bid_id))
							print ('BID PLACED',cb_trade('buy',trade_quant,open_bid_price,prod_string))
							open_orders += 1
							num_orders += 1
							change = 1
						else:
							pass

					if quant_change >=0:
						if open_asks == 0:
							print ('ASK PLACED',cb_trade('sell',trade_quant,open_ask_price,prod_string))
							open_orders += 1
							num_orders +=1
							change = 1
						elif abs(open_ask_price-ask) > order_thresh:
							print ('Modification Cancel (Ask):',cancel_order(ask_id))
							print ('ASK PLACED',cb_trade('sell',trade_quant,open_ask_price,prod_string))
							open_orders += 1
							num_orders +=1
							change = 1
						elif open_ask_price <ask_price:
							print ('Modification Cancel (Ask):',cancel_order(ask_id))
							print ('ASK PLACED',cb_trade('sell',trade_quant,open_ask_price,prod_string))
							open_orders += 1
							num_orders +=1
							change = 1
						else:
							pass

				timey=datetime.datetime.now().strftime("%I:%M%p%B%d%Y")
				if change > 0:	
					btc_change = bitcoin-starting_btc_balance 
					usd_change = USD_balance-starting_usd_balance
					total_change = usd_change + (btc_change * (bid + ask)/2)

					static_p_balance = USD_balance + bitcoin * start_price
					print ('Open Orders:',open_orders,'Price',USD,
						'Base Profit - USD',usd_change ,
						'Subset Profit - BTC',btc_change ,
						'Adj Profit',total_change,
						'Number of Orders:',num_orders,
						'Quantity Change:',quant_change,'Time: ',timey)

					with open(name,'a') as fd:
						writer = csv.writer(fd)
						writer.writerow([str(timey),str(bid),str(ask),str(usd_change),str(btc_change)])
				if abs(btc_change) > .1 or total_change < -.5:
					breaker=1
					break

mm= cstick_trader()
mm.make_mark('BTC/USD',.01,1,10)
