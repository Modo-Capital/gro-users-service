import requests

url = "https://sandbox-quickbooks.api.intuit.com/v3/company/%3C%3CEnter%20QuickBooks%20AccountId/RealmId%3E%3E/query"

querystring = {"minorversion":"8"}

payload = "Select * from Account STARTPOSITION 1 MAXRESULTS 5\n"
headers = {
    'User-Agent': "{{UserAgent}}",
    'Accept': "application/json",
    'Content-Type': "application/text",
    'Authorization': "Bearer eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..dgT0i4NBZG2HMBsejZ5UAA.h-g_24jMacdF26qSEcmbRglshLe82cRgf40D2P6A1QP6j-fo590Yt1GBKUYNH-bMRsVIs1F9b6bzynDC6urERHLDQ5l2dpcKViajG6LE1NpbzX2X4-A7vFGQ-fSvQxo09e-DJxBHWseVTo0rzx7N1KOaH3wjwfAOHPGrIVq5YWx15d0fzqvcfz9wby9A8lcK8YcERKGHh4WDKQCD4ss9I5wkroJ38g5onratXpUi6so8bwUwPRSyLRWzFHxZnSlp9rFCU-fTfFQ1S4vRuo6o2KLayrUXxrgyZjhzLNeCwH-du5U_7TsRlsWN_dmW-RukjesL3VFqQ5BrgRkBpa1-0sc8rf2MfkEjjDMc9h4jtaHubZXO20VOE2ngjj8uuBoZPC_zj3jE_WdsokrcE5gRHfcvYh7kNBe4YN6sTCipLV7iEal5u6hKNJxmiJmK5ui2h9PNr6HGDA87z-CtIkPQ7fyI8S3mmR2SxpOmHR5FctxvJberECUOkCoFDBIeDH-oUzQm-8-d3vZ3uiDLTdk4CNpQragf5KruPSJJQBlJf3Tm7HjwKqOx0nRkWCEtBYBZoaz5GbMD5tGEgtp_zxpTrIYu9XV2ABubhBfH8m2vN_Djf9L6licsnqtF-kYQchL48X50jgJkHIuETpv0_g69Nh1HCxl0sx-4Y5egF18b7wIJbTrBcIoQ_m3Cpn7BkzSE.yxbHaI0lgQ8gKfy_I9HPIA",
    'Cache-Control': "no-cache",
    'Postman-Token': "2bcb835a-2ad2-e1e6-8256-1d3b2f976afa"
    }

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

print(response.text)