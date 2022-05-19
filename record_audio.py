import numpy as np
import pyaudio
import torch
import wave
import uuid
from tqdm import tqdm
import os
import soundfile as sf

from utils_vad import VADIterator, OnnxWrapper, init_jit_model, get_speech_timestamps, save_audio, read_audio, \
	collect_chunks


def get_model(onnx):
	if onnx:
		model = OnnxWrapper('./model/vad.onnx')
	else:
		model = init_jit_model(model_path='./model/vad.jit')

	return model


model = get_model(True)

vad_iterator = VADIterator(model)

s = input('请输入你计划录音多少秒：')

CHUNK = 16000
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = int(s)
WAVE_OUTPUT_FILENAME = "save_audio/%s.wav" % str(uuid.uuid1()).replace('-', '')

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)

print("开始录音, 请说话......")
if not os.path.exists('save_audio'):
	os.makedirs('save_audio')

frames = []
speech_probs = []

for i in tqdm(range(0, int(RATE / CHUNK * RECORD_SECONDS))):
	data = stream.read(CHUNK)
	data_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
	# speech_dict = vad_iterator(data_chunk, return_seconds=True)
	# print(speech_dict)
	speech_prob = model(torch.tensor(data_chunk), 16000).item()
	print(speech_prob)
	speech_probs.append(speech_prob)
	frames.append(data)

print("录音已结束!")
vad_iterator.reset_states()

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print('文件保存在：%s' % WAVE_OUTPUT_FILENAME)
