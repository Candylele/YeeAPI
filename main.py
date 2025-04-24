# dic = {1:[{1}],2:[{2},{22}],3:[{3},{33},{333}]}
# lis = []
# # [{'id': 1, 'step': [{1}]}, {'id': 2, 'step': [{2}, {22}]}, {'id': 3, 'step': [{3}, {33}, {333}]}]
# for key,value in dic.items():
#     dic2 = {}
#     dic2['id'] = key
#     dic2['step'] = value
#     lis.append(dic2)
# print(lis)

json = {
    'status': 'success',
    'data': {
        'key1': 'value1',
        'key2': 'value2'
    }
}
for key,value in json.items():
    print(key,value)