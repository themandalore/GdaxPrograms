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
 
 
	def make_mark(self,product,trade_quant,spread_thresh,base_o_thresh):
		print (cancel_all())
		profit = 0
		open_bids = 0 
		open_asks = 0
		#spread_thresh is min spread, order thresh is about 2 times spread if tight
		num_orders = 0
		today = datetime.date.today().strftime("%B %d, %Y")
		name = today + '_MovingAverage.csv'
		p1 = product.split('/')[0]
		p2 = product.split('/')[1]
		prod_string = p1+'-'+p2
		ma_quantity = 0
		ma_level = 2#enter seconds for malevel
		ma_thresh = 999
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
			hist_data = []
			print ('wait' ,ma_level,'...')
			while init_time <= ma_level:
				USD = float(USD)
				hist_data.append(USD)
				time.sleep(1)
				init_time = init_time + 1
				USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
				if USD == 0:
					break
			last_values = hist_data[-ma_level:]
			ma_price = np.sum(last_values)/ma_level
			while True and zzz==0:
				heartbeat=heartbeat+1
				if heartbeat ==10:
					print ('.',spread,ma_quantity)
					heartbeat=1
				time.sleep(1)
				USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
				if USD == 0:
					break
				bid = float(bid)
				ask = float(ask)
				USD = float(USD)
				spread = max(spread_thresh,ask-bid)
				order_thresh = max(base_o_thresh,spread * 10)
				hist_data.append(USD)
				last_values = hist_data[-ma_level:]
				ma_price = np.sum(last_values)/ma_level
				'''Currently ma_quantity is just one of the trade_quant, if volume and trades are high enough, this can increase'''
				if USD - ma_price > ma_thresh:
					ma_quantity = -trade_quant
				elif USD - ma_price < -ma_thresh:
					ma_quantity = trade_quant
				else:
					ma_quantity = 0
					
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

					if quant_change <=ma_quantity:
						if open_bids == 0:
							open_bid_price = round(float(ask - spread),2)
							print ('BID PLACED',cb_trade('buy',trade_quant,open_bid_price,prod_string))
							open_orders += 1
							num_orders += 1
							change = 1
						elif abs(bid-bid_price) > order_thresh:
							print ('Modification Cancel:',cancel_order(bid_id))
							open_bid_price = ask - round(float(ask - spread),2)
							print ('BID PLACED',cb_trade('buy',trade_quant,open_bid_price,prod_string))
							open_orders += 1
							num_orders += 1
							change = 1

						else:
							pass

					if quant_change >=ma_quantity:
						if open_asks == 0:
							open_ask_price = round(float(bid + spread),2)
							print ('ASK PLACED',cb_trade('sell',trade_quant,open_ask_price,prod_string))
							open_orders += 1
							num_orders +=1
							change = 1
						elif abs(ask-ask_price) > order_thresh:
							print ('Modification Cancel (Ask):',cancel_order(ask_id))
							open_ask_price = round(float(bid + spread),2)
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
					print ('Open Orders:',open_orders,
						'Base Profit - USD',usd_change ,
						'Subset Profit - BTC',btc_change ,
						'Adj Profit',total_change,
						'Number of Orders:',num_orders,
						'Quantity Change:',quant_change,
						'Time: ',timey)

				with open(name,'a') as fd:
					writer = csv.writer(fd)
					writer.writerow([str(timey),str(bid),str(ask),str(usd_change),str(btc_change)])
				if abs(btc_change) > .1 or total_change < -.5:
					breaker=1
					break

mm= MarketMaker()
mm.make_mark('BTC/USD',.03,.5,10)