from ib_insync import *
import webbrowser


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

# --- GRAB SCANNER PARAMATERS AND OUTPUT TO XML. OPEN THIS XML ---
# xml = ib.reqScannerParameters()
#
# path = 'scanner_parameters.xml'
# with open(path, 'w') as f:
#     f.write(xml)
#
# webbrowser.open(path)


# --- CREATE SCAMMER AMD GRAB TICKER NAMES ---
sub = ScannerSubscription(
    instrument='STK',
    locationCode='STK.US.MAJOR',
    scanCode='TOP_PERC_GAIN')

tagValues = [
    TagValue("changePercAbove", "20"),
    TagValue('priceAbove', 0.3),
    TagValue('priceBelow', 80)]

# the tagValues are given as 3rd argument; the 2nd argument must always be an empty list
# (IB has not documented the 2nd argument and it's not clear what it does)
scanData = ib.reqScannerData(sub, [], tagValues)

symbols = [sd.contractDetails.contract.symbol for sd in scanData]
print(symbols)
