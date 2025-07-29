import sounddevice as sd
import numpy as np
import sys
import time
import shutil
import threading
from queue import Queue, Empty
import soundfile as sf
import signal

SAMPLERATE = 16000
BLOCKSIZE = 1024
N_BANDS = 50  # Fixed at 50 for ~1000px width
F_MIN = 20
F_MAX = 8000
HISTORY_SIZE = 20
AUDIO_FILE = '/tmp/input.wav'

# Frequency band setup with ensured coverage
ratio = (F_MAX / F_MIN) ** (1 / N_BANDS)
f_bounds = [F_MIN * (ratio ** i) for i in range(N_BANDS + 1)]
df = SAMPLERATE / BLOCKSIZE
k_min_list = []
k_max_list = []
for b in range(N_BANDS):
    k_min = int(np.ceil(f_bounds[b] / df))
    k_max = int(np.floor(f_bounds[b + 1] / df))
    if k_min > BLOCKSIZE // 2 - 1:
        k_min = BLOCKSIZE // 2 - 1
    if k_max < 0:
        k_max = 0
    k_min_list.append(max(0, k_min))
    k_max_list.append(min(BLOCKSIZE // 2 - 1, k_max))
for b in range(N_BANDS):
    if k_min_list[b] > k_max_list[b]:
        k_min_list[b] = k_max_list[b] = max(0, min(BLOCKSIZE // 2 - 1, len(k_min_list) - 1))

waveform_queue = Queue(maxsize=10)
history = np.zeros((HISTORY_SIZE, N_BANDS))
audio_buffer = []

# Inverted color mapping: blue to red via green based on amplitude
def amplitude_to_color(amp, max_amp):
    if max_amp == 0:
        return '\033[37m'  # White for zero
    norm = min(amp / max_amp, 1.0)
    if norm <= 0.10:
        return '\033[38;5;45m'  # Light blue (ANSI 256)
    elif norm <= 0.20:
        return '\033[34m'  # Blue
    elif norm <= 0.33:
        return '\033[32m'  # Green
    elif norm <= 0.5:
        return '\033[38;5;120m'  # Light green (ANSI 256)
    elif norm <= 0.66:
        return '\033[33m'  # Yellow
    elif norm <= 0.83:
        return '\033[38;5;208m'  # Orange (ANSI 256)
    else:
        return '\033[31m'  # Red

def signal_handler(sig, frame):
    global running
    running = False
    stream.stop()
    save_audio()

def callback(indata, frames, time_info, status):
    global audio_buffer
    if status:
        print(status, file=sys.stderr)
    # Pad indata with zeros on the left to ensure full band coverage
    pad_size = max(0, BLOCKSIZE - len(indata))
    padded_data = np.pad(indata[:, 0], (pad_size, 0), 'constant')
    audio_buffer.append(padded_data.copy())
    fft_data = np.fft.fft(padded_data[:BLOCKSIZE])
    magnitudes = np.abs(fft_data[:BLOCKSIZE // 2])
    sum_magnitudes = []
    for b in range(N_BANDS):
        k_min = k_min_list[b]
        k_max = k_max_list[b]
        if k_min <= k_max:
            s = np.sum(magnitudes[k_min:k_max + 1])
        else:
            s = 0
        sum_magnitudes.append(s)
    max_s = max(sum_magnitudes) or 1e-6
    amplitudes = [s / max_s for s in sum_magnitudes]
    if len(amplitudes) < N_BANDS:
        amplitudes = [0] * (N_BANDS - len(amplitudes)) + amplitudes
    elif len(amplitudes) > N_BANDS:
        amplitudes = amplitudes[:N_BANDS]
    waveform_queue.put(amplitudes)

def save_audio():
    global audio_buffer
    if audio_buffer:
        audio_data = np.concatenate(audio_buffer)
        sf.write(AUDIO_FILE, audio_data, SAMPLERATE)
        print(f"Saved to {AUDIO_FILE}")
    sys.exit(0)

def print_waterfall(amplitudes):
    global history
    history = np.roll(history, 1, axis=0)
    history[0] = amplitudes
    term_size = shutil.get_terminal_size()
    H = min(HISTORY_SIZE, term_size.lines - 6)
    W = 2 * N_BANDS - 1
    if W + 6 > term_size.columns:
        bands_to_show = (term_size.columns - 6) // 2
        W = 2 * bands_to_show - 1
    else:
        bands_to_show = N_BANDS
    grid = [[' ' for _ in range(W)] for _ in range(H)]
    max_amp = np.max(history) or 1e-6
    for t in range(H):
        for b in range(min(bands_to_show, N_BANDS)):
            c = b * 2
            amp = history[t, b]
            if amp > 0 and t < H and c < W:
                color = amplitude_to_color(amp, max_amp)
                grid[t][c] = f"{color}#\033[0m"
    border = '\033[37m' + ' -' * (W // 2) + '\033[0m'
    rec_str = f'\033[1;{W + 1}H\033[31m@ REC\033[0m'
    instr_str = f'\033[{H + 3};1H\033[37mPress [ENTER] or [SPACE] to stop & save, [r] to redo, [x/q] to quit\033[0m'
    waterfall_str = '\n'.join(''.join(row) for row in grid)
    sys.stdout.write(rec_str + '\n')
    sys.stdout.write(border + '\n')
    sys.stdout.write(waterfall_str + '\n')
    sys.stdout.write(border + '\n')
    sys.stdout.write(instr_str + '\n')
    sys.stdout.flush()

def update_display():
    while running:
        try:
            amplitudes = waveform_queue.get(timeout=0.1)
            print_waterfall(amplitudes)
        except Empty:
            continue

# Global running flag and stream
running = True
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

display_thread = threading.Thread(target=update_display, daemon=True)
display_thread.start()

stream = sd.InputStream(channels=1, samplerate=SAMPLERATE, blocksize=BLOCKSIZE, callback=callback)
stream.start()
try:
    while running:
        time.sleep(0.05)
except KeyboardInterrupt:
    running = False
    stream.stop()
    save_audio()