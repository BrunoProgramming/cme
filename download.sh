#!/bin/bash
DATE=$1
TYPE=$2
if [ -z "$2" ]
then
  TYPE="P"
else
  TYPE=$2
fi

#E-mini Nasdaq-100
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=2020${DATE}&reportType=${TYPE}&productId=146" -O EminiNasdaq100-${DATE}.xls
#E-mini S&P 500
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=2020${DATE}&reportType=${TYPE}&productId=133" -O EminiSP500-${DATE}.xls
#Crude Oil
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=2020${DATE}&reportType=${TYPE}&productId=425" -O Crude-${DATE}.xls
#Silver
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=2020${DATE}&reportType=${TYPE}&productId=458" -O Silver-${DATE}.xls
#Gold
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=2020${DATE}&reportType=${TYPE}&productId=437" -O Gold-${DATE}.xls
#Bitcoin
wget "https://www.cmegroup.com/CmeWS/exp/voiProductDetailsViewExport.ctl?media=xls&tradeDate=2020${DATE}&reportType=${TYPE}&productId=8478" -O Bitcoin-${DATE}.xls
