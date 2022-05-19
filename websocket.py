import json
import numpy as np
import soundfile
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8010/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	# 允许跨域请求的域名列表，例如 ['https://example.org', 'https://www.example.org'] 或者 ['*']。
	allow_origins=["*"],
	# 允许跨域请求的域名正则表达式，例如 'https://.*\.example\.org'。
	# allow_origin_regex
	# 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
	allow_credentials=False,
	# 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
	allow_methods=["*"],
	# 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
	# 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
	allow_headers=["*"],
	# 可以被浏览器访问的响应头, 默认是 []，一般很少指定
	# expose_headers=["*"]
	# 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
	# max_age=1000
)


# @app.get("/")
# async def get():
#     return HTMLResponse(html)

def save_voice(frames):
	import wave
	wf = wave.open("res.wav", 'wb')
	wf.setnchannels(1)
	wf.setsampwidth(2)
	wf.setframerate(16000)
	wf.writeframes(b''.join(frames))
	wf.close()


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()
	frame = []
	while True:
		data = await websocket.receive()
		if data.__contains__('bytes'):
			frame.append(data['bytes'])
		if data.__contains__('text'):
			if data['text'][11] == 'e':
				# res = np.frombuffer(frame, dtype=np.int16).astype(np.float32) / 32768.0
				save_voice(frame)
		message = {"code": 200, "content": "阿豪&*（……&*……%&*￥%……*&"}
		await websocket.send_json(message)


if __name__ == '__main__':
	import uvicorn

	# 官方推荐是用命令后启动 uvicorn main:app --host=127.0.0.1 --port=8010 --reload
	uvicorn.run(app='websocket:app', host="0.0.0.0", port=8030, reload=True, debug=True, ssl_keyfile="./key.pem",
				ssl_certfile="./cert.pem")
