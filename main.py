from utils_vad import OnnxWrapper, init_jit_model, get_speech_timestamps, save_audio, read_audio, collect_chunks
import soundfile as sf


def get_model(onnx):
	if onnx:
		model = OnnxWrapper('./model/vad.onnx')
	else:
		model = init_jit_model(model_path='./model/vad.jit')

	return model


if __name__ == '__main__':
	model = get_model(True)
	wav = read_audio('save.wav', sampling_rate=16000)
	speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000, visualize_probs=True)
	print(speech_timestamps)
	sf.write("result2.wav", collect_chunks(speech_timestamps, wav), 16000)
	save_audio('result.wav', collect_chunks(speech_timestamps, wav), sampling_rate=16000)
