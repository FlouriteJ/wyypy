import sys,io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
import requests 
import json
	
def getComment(idSong):
	url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_"+ idSong +"/?csrf_token=" 
	params = b'O5/yxckUkfK03FP34r7bgJVnmX5k2/G/l+JCIrgOQwyl+J53UnkgD1kh9z4b6IVTfsjcxGSpGImwZD9kofBZOZTdVyWchjIZes8sb6tnAWuqdC4/j7mOH13VQxx3TDUy'
	encSecKey = '257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c'
	data = { "params": params, "encSecKey": encSecKey } 
	response = requests.post(url, headers=headers, data=data)
	json_text = response.text 
	json_dict = json.loads(json_text) 
	total = json_dict['total']
	content_list = []
	for item in json_dict['hotComments']: 
		content_list.append(item['content'])
	return total,content_list
getComment('503207093')