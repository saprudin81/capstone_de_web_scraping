from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/exchange-rate-history/usd-idr-2024')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={'class':'history-rates-data'})
Date = table.find_all('a', attrs={'class':'w'})

row_length = len(Date)

temp = [] #initiating a list 

for i in range(1, row_length):
#insert the scrapping process here
    #Date
    tanggal = table.find_all('a', attrs={'class':'w'})[i].text
    tanggal = tanggal.strip()
    #Kurs Harian
    harga_harian = table.find_all('span', attrs={'class':'w'})[i].text
    # menggabung kolom tanggal dan kurs harian
    temp.append((tanggal,harga_harian)) 

#temp = temp[:-1]

#change into dataframe
data = pd.DataFrame(temp,columns= ('tanggal','harga_harian'))

#insert data wrangling here
data['harga_harian'] = data['harga_harian'].str.replace(',', '')
data['harga_harian'] = data['harga_harian'].str.replace('1 USD = ', '')
data['harga_harian'] = data['harga_harian'].str.replace(' IDR', '')
data['harga_harian'] = data['harga_harian'].astype('int64') 
data['tanggal'] = pd.to_datetime(data['tanggal'])
data.set_index('tanggal', inplace=True)
data['month_name'] = data.index.month_name()

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{data["harga_harian"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = data.plot(figsize = (20,10)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)