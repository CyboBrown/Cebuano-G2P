from transformers import VitsModel, AutoTokenizer
import torch
import scipy.io.wavfile
import numpy as np

def create_audio(text):
    model = VitsModel.from_pretrained("facebook/mms-tts-ceb")
    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-ceb")
    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        output = model(**inputs).waveform

    output_np = output.numpy()

    output_np = output_np.flatten()

    max_val = np.max(np.abs(output_np))
    if max_val > 0:
        output_np = output_np / max_val

    output_np = (output_np * 32767).astype('int16')

    scipy.io.wavfile.write(f"output2.mpeg", rate=model.config.sampling_rate, data=output_np)

    return 