import requests

# url = "https://rest.coinapi.io/v1/symbols/OKEX"

# payload = {}
# headers = {
#   'Accept': 'text/plain',
#   'X-CoinAPI-Key': 'd8c770aa-418a-4509-8387-c3196f9aa11a'
# }

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)
# # 检查请求是否成功
# if response.status_code == 200:
#     # 将响应内容写入文件
#     with open("response.txt", "w") as file:
#         file.write(response.text)
#     print("响应已成功写入到 response.txt 文件中。")
# else:
#     print(f"请求失败，状态码: {response.status_code}")


url = "https://rest.coinapi.io/v1/orderbooks/OKEX_PERP_DOGE_USDT/history?time_start=2025-01-18T09:05:37.919Z&time_end=2025-01-18T09:06:37.919Z&limit=1000"

payload = {}
headers = {
  'Accept': 'text/plain',
  'X-CoinAPI-Key': 
}

response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)


print(response.text)
# # 检查请求是否成功
if response.status_code == 200:
    # 将响应内容写入文件
    with open("response_orderbook.txt", "w") as file:
        file.write(response.text)
    print("响应已成功写入到 response.txt 文件中。")
else:
    print(f"请求失败，状态码: {response.status_code}")
