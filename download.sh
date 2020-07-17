#!/bin/bash
DATE=$1 #20200711
TYPE=$2
if [ -z "$2" ]
then
  TYPE="P"
else
  TYPE=$2
fi

#E-mini Nasdaq-100
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=${DATE}&reportType=${TYPE}&productId=146" -O data/EminiNasdaq100-${DATE}.xls
#E-mini S&P 500
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=${DATE}&reportType=${TYPE}&productId=133" -O data/EminiSP500-${DATE}.xls
#Crude Oil
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=${DATE}&reportType=${TYPE}&productId=425" -O data/Crude-${DATE}.xls
#Silver
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=${DATE}&reportType=${TYPE}&productId=458" -O data/Silver-${DATE}.xls && python options.py --product silver --input data/Silver-${DATE}.xls --date ${DATE}
#Gold
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=${DATE}&reportType=${TYPE}&productId=437" -O data/Gold-${DATE}.xls && python options.py --product gold --input data/Gold-${DATE}.xls --date ${DATE}
#Bitcoin
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=${DATE}&reportType=${TYPE}&productId=8478" -O data/Bitcoin-${DATE}.xls

python option_report.py --date ${DATE} --product gold --price 1804 --exercise ${DATE} 
python option_report.py --date ${DATE} --product silver --price 1945 --exercise ${DATE} 
