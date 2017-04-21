'''market maker program'''

from transact_cb import *
from stored import *
import numpy as np
import time, json, requests, csv, datetime
import pandas as pd

'''
Get ma quantity to replace 0 as base quantity
Get orig_price of asset to calculate profit and loss based on total value and totalvalue vs market value (if mkt loses)


'''
class MarketMaker:
 
	def make_mark(self,product,trade_amount,spread_thresh,order_thresh):
		profit = 0
		open_bids = 0 
		open_asks = 0
		num_orders = 0
		today = datetime.date.today().strftime("%B %d, %Y")
		p1 = product.split('/')[0]
		p2 = product.split('/')[1]
		prod_string = p1+'-'+p2
		x = cb_balance()
		for i in x:
			if i[0]==p2:
				starting_usd_balance =float(i[1])
			if i[0] ==p1:
				starting_btc_balance = float(i[1])
		btc_change = 0
		breaker = 0
		while True:
			if breaker==1:
				break
			print (cancel_all())
			zzz=0
			heartbeat=1
			USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
			if USD ==0:
				break
			start_price = float(USD)
			while True and zzz==0:
				heartbeat=heartbeat+1
				ma_quantity = trade_amount - btc_change
				if heartbeat ==10:
					print ('.',spread,'total change:',btc_change)
					heartbeat=1
				time.sleep(1)
				USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
				if USD == 0:
					break
				bid = float(bid)
				ask = float(ask)
				USD = float(USD)
				if trade_amount < 0:
					trade_quant = min(float(a_depth),ma_quantity)
				else:
					trade_quant = min(float(b_depth),ma_quantity)
				spread = max(spread_thresh,ask-bid)
				change = 0
				x = cb_balance()
				if x == 'ERROR':
					break
				for i in cb_balance():
					if i[0]==p1:
						btc_change = float(i[1]) - starting_btc_balance

				if ask - bid > 0:
					open_bids = 0
					open_asks = 0
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

					if btc_change < trade_amount:
						if open_asks > 0:
							print ('MA Cancel:',cancel_order(ask_id))
							change = 1
						if open_bids == 0:
							open_bid_price = round(float(ask - spread),2)
							print ('BID PLACED',cb_trade('buy',trade_quant,open_bid_price,prod_string))
							num_orders += 1
							change = 1
						elif abs(bid-bid_price) >= order_thresh:
							print ('Modification Cancel:',cancel_order(bid_id))
							open_bid_price = ask - round(float(ask - spread),2)
							print ('BID PLACED',cb_trade('buy',trade_quant,open_bid_price,prod_string))
							num_orders += 1
							change = 1

						else:
							pass
					if btc_change > trade_amount:
						if open_bids > 0:
							print ('MA Cancel:',cancel_order(bid_id))
							change = 1
						if open_asks == 0:
							open_ask_price = round(float(bid + spread),2)
							print ('ASK PLACED',cb_trade('sell',trade_quant,open_ask_price,prod_string))
							num_orders +=1
							change = 1
						elif abs(ask-ask_price) >= order_thresh:
							print ('Modification Cancel (Ask):',cancel_order(ask_id))
							open_ask_price = round(float(bid + spread),2)
							print ('ASK PLACED',cb_trade('sell',trade_quant,open_ask_price,prod_string))
							num_orders +=1
							change = 1
						else:
							pass
					

				if change > 0:	
					x = cb_balance()
					if x == 'ERROR':
						break
					for i in x:
						if i[0]==p2:
							USD_balance = float(i[1])
						if i[0] ==p1:
							bitcoin = float(i[1])
					btc_change = bitcoin-starting_btc_balance 
					usd_change = USD_balance-starting_usd_balance
					if btc_change > 0 :
						appaid = usd_change/btc_change
					else:
						appaid	= 0

					open_orders = 0
					x = cb_open()
					if x =='ERROR':
						open_orders = 0
					else: 
						for i in x:
							open_orders += 1
					if open_orders > 1:
						print ('Multiple Orders',cancel_all())
					print ('Open Orders:',open_orders,
						'Avg_Price Paid - USD',appaid,
						'BTC Change',btc_change,
						'Target',trade_amount,
						'Number of Orders:',num_orders)

				if abs(btc_change) >= trade_amount:
					print (cancel_all())
					breaker=1
					break

mm= MarketMaker()
#product,trade_amount,spread_thresh,order_thresh
mm.make_mark('BTC/USD',.1,.01,.1)
