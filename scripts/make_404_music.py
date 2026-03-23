"""
404 스타일 음악 생성기
- 몽환적 신스 패드 + 글리치 요소 + 미니멀 비트
- numpy로 웨이브폼 합성 → WAV 출력
"""

import numpy as np
import wave
import struct
import os

SAMPLE_RATE = 44100
BPM = 85
BEAT = 60 / BPM  # 한 비트 길이(초)
DURATION = int(BEAT * 64)  # 64비트 = 약 45초


def sine_wave(freq, duration, sr=SAMPLE_RATE, amplitude=0.3):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * freq * t)


def saw_wave(freq, duration, sr=SAMPLE_RATE, amplitude=0.15):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return amplitude * (2 * (freq * t % 1) - 1)


def square_wave(freq, duration, sr=SAMPLE_RATE, amplitude=0.1):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return amplitude * np.sign(np.sin(2 * np.pi * freq * t))


def noise(duration, sr=SAMPLE_RATE, amplitude=0.05):
    return amplitude * np.random.randn(int(sr * duration))


def envelope(signal, attack=0.01, decay=0.05, sustain=0.7, release=0.1):
    """ADSR 엔벨로프"""
    n = len(signal)
    sr = SAMPLE_RATE
    env = np.ones(n)

    a_samples = int(attack * sr)
    d_samples = int(decay * sr)
    r_samples = int(release * sr)

    # Attack
    if a_samples > 0:
        env[:a_samples] = np.linspace(0, 1, a_samples)
    # Decay
    if d_samples > 0:
        start = a_samples
        end = min(start + d_samples, n)
        env[start:end] = np.linspace(1, sustain, end - start)
    # Sustain
    env[a_samples + d_samples: n - r_samples] = sustain
    # Release
    if r_samples > 0 and n > r_samples:
        env[-r_samples:] = np.linspace(sustain, 0, r_samples)

    return signal * env


def low_pass_filter(signal, cutoff=2000, sr=SAMPLE_RATE):
    """간단한 1차 로우패스 필터"""
    rc = 1.0 / (2 * np.pi * cutoff)
    dt = 1.0 / sr
    alpha = dt / (rc + dt)
    filtered = np.zeros_like(signal)
    filtered[0] = alpha * signal[0]
    for i in range(1, len(signal)):
        filtered[i] = filtered[i - 1] + alpha * (signal[i] - filtered[i - 1])
    return filtered


def reverb(signal, decay=0.3, delay_ms=80, sr=SAMPLE_RATE):
    """간단한 딜레이 기반 리버브"""
    delay_samples = int(delay_ms * sr / 1000)
    output = signal.copy()
    for i in range(1, 4):
        d = delay_samples * i
        if d < len(signal):
            output[d:] += signal[:-d] * (decay ** i)
    return output


def note_freq(note_name):
    """노트 이름 → 주파수"""
    notes = {
        'C3': 130.81, 'D3': 146.83, 'Eb3': 155.56, 'E3': 164.81,
        'F3': 174.61, 'G3': 196.00, 'Ab3': 207.65, 'A3': 220.00,
        'Bb3': 233.08, 'B3': 246.94,
        'C4': 261.63, 'D4': 293.66, 'Eb4': 311.13, 'E4': 329.63,
        'F4': 349.23, 'G4': 392.00, 'Ab4': 415.30, 'A4': 440.00,
        'Bb4': 466.16, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'Eb5': 622.25, 'E5': 659.25,
        'F5': 698.46, 'G5': 783.99, 'Ab5': 830.61,
        'C2': 65.41, 'D2': 73.42, 'Eb2': 77.78, 'E2': 82.41,
        'F2': 87.31, 'G2': 98.00, 'Ab2': 103.83, 'A2': 110.00,
        'Bb2': 116.54,
    }
    return notes.get(note_name, 440.0)


def make_pad(chord_notes, duration, detune=1.003):
    """몽환적 패드 사운드"""
    signal = np.zeros(int(SAMPLE_RATE * duration))
    for note in chord_notes:
        freq = note_freq(note)
        # 약간의 디튠으로 두께감
        s = sine_wave(freq, duration, amplitude=0.12)
        s += sine_wave(freq * detune, duration, amplitude=0.08)
        s += sine_wave(freq / 2, duration, amplitude=0.05)  # 서브
        signal += s
    signal = low_pass_filter(signal, cutoff=1500)
    signal = envelope(signal, attack=0.8, decay=0.3, sustain=0.6, release=1.0)
    return signal


def make_bass(note, duration):
    """깊은 서브 베이스"""
    freq = note_freq(note)
    s = sine_wave(freq, duration, amplitude=0.35)
    s += saw_wave(freq, duration, amplitude=0.08)
    s = low_pass_filter(s, cutoff=300)
    s = envelope(s, attack=0.01, decay=0.1, sustain=0.8, release=0.05)
    return s


def make_melody_note(note, duration):
    """클린한 신스 멜로디"""
    freq = note_freq(note)
    s = sine_wave(freq, duration, amplitude=0.2)
    s += sine_wave(freq * 2, duration, amplitude=0.05)  # 옥타브 하모닉
    s = envelope(s, attack=0.02, decay=0.1, sustain=0.5, release=0.15)
    return s


def make_kick(duration=0.3):
    """킥 드럼"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # 주파수 스윕 (높은 → 낮은)
    freq_sweep = 150 * np.exp(-t * 20) + 40
    phase = 2 * np.pi * np.cumsum(freq_sweep) / SAMPLE_RATE
    s = 0.4 * np.sin(phase)
    # 짧은 엔벨로프
    env = np.exp(-t * 8)
    return s * env


def make_hihat(duration=0.08):
    """하이햇"""
    s = noise(duration, amplitude=0.15)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    env = np.exp(-t * 40)
    return s * env


def make_glitch(duration=0.05):
    """글리치 사운드 (404 에러 느낌)"""
    s = noise(duration, amplitude=0.1)
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    # 랜덤 주파수 변조
    mod = np.sin(2 * np.pi * np.random.uniform(500, 3000) * t)
    s *= mod
    env = np.exp(-t * 20)
    return s * env


def place_sound(master, sound, position_seconds):
    """마스터 트랙에 사운드 배치"""
    start = int(position_seconds * SAMPLE_RATE)
    end = start + len(sound)
    if end > len(master):
        end = len(master)
        sound = sound[:end - start]
    if start < len(master):
        master[start:end] += sound


def generate_track():
    total_samples = int(SAMPLE_RATE * DURATION)
    master = np.zeros(total_samples)

    print("🎹 패드 코드 생성 중...")
    # 코드 진행: Am - F - C - G (어두우면서 감성적)
    # 404 느낌 → Cm - Ab - Eb - Bb (더 어둡게)
    chord_progression = [
        ['C3', 'Eb3', 'G3', 'Bb3'],   # Cm7
        ['Ab3', 'C4', 'Eb4'],          # Ab
        ['Eb3', 'G3', 'Bb3'],          # Eb
        ['Bb2', 'D3', 'F3', 'Ab3'],    # Bb7 (도미넌트)
    ]

    chord_duration = BEAT * 8  # 8비트(2마디)씩
    for i in range(8):  # 8번 반복 = 64비트
        chord = chord_progression[i % 4]
        pad = make_pad(chord, chord_duration)
        place_sound(master, pad, i * chord_duration)

    print("🎸 베이스 라인 생성 중...")
    bass_pattern = ['C2', 'C2', 'Ab2', 'Ab2', 'Eb2', 'Eb2', 'Bb2', 'Bb2']
    bass_note_dur = BEAT * 4
    for repeat in range(4):
        for i, note in enumerate(bass_pattern):
            pos = repeat * (bass_note_dur * 8) + i * bass_note_dur
            bass = make_bass(note, bass_note_dur * 0.9)
            place_sound(master, bass, pos)

    print("🎵 멜로디 생성 중...")
    # 멜로디: 단순하고 반복적, 몽환적
    melody_phrases = [
        # 프레이즈 1
        [('Eb5', 1.5), ('D5', 0.5), ('C5', 1.0), (None, 1.0),
         ('Eb5', 0.5), ('G5', 1.5), ('F5', 1.0), (None, 0.5)],
        # 프레이즈 2
        [('Ab5', 1.0), ('G5', 0.5), ('Eb5', 1.5), (None, 0.5),
         ('D5', 1.0), ('C5', 1.5), (None, 0.5), ('Bb4', 1.0)],
        # 프레이즈 3 (변형)
        [('C5', 1.0), ('Eb5', 1.0), ('G5', 1.0), (None, 1.0),
         ('F5', 0.5), ('Eb5', 0.5), ('D5', 1.0), (None, 1.5)],
        # 프레이즈 4
        [(None, 2.0), ('Eb5', 0.5), ('D5', 0.5), ('C5', 2.0),
         (None, 1.0), ('Bb4', 1.0)],
    ]

    # 멜로디는 16비트 이후 시작 (인트로 후)
    melody_start = BEAT * 16
    for phrase_idx, phrase in enumerate(melody_phrases):
        pos = melody_start + phrase_idx * BEAT * 8
        note_pos = pos
        for note, dur_beats in phrase:
            dur = dur_beats * BEAT
            if note is not None:
                mel = make_melody_note(note, dur * 0.85)
                place_sound(master, mel, note_pos)
            note_pos += dur

    # 멜로디 두 번째 반복 (살짝 변형)
    melody_start2 = BEAT * 48
    for phrase_idx in range(2):
        phrase = melody_phrases[phrase_idx]
        pos = melody_start2 + phrase_idx * BEAT * 8
        note_pos = pos
        for note, dur_beats in phrase:
            dur = dur_beats * BEAT
            if note is not None:
                mel = make_melody_note(note, dur * 0.85)
                mel *= 0.7  # 살짝 작게
                place_sound(master, mel, note_pos)
            note_pos += dur

    print("🥁 비트 생성 중...")
    # 킥: 매 2비트
    for i in range(32):
        beat_pos = (i * 2) * BEAT
        if beat_pos < DURATION:
            kick = make_kick()
            place_sound(master, kick, beat_pos)

    # 하이햇: 매 비트 (8비트 이후 시작)
    for i in range(56):
        beat_pos = (8 + i) * BEAT
        if beat_pos < DURATION:
            hh = make_hihat()
            # 오프비트 하이햇은 살짝 작게
            if i % 2 == 1:
                hh *= 0.5
            place_sound(master, hh, beat_pos)

    print("💥 글리치 이펙트 추가 중...")
    # 글리치: 랜덤 위치에 배치 (404 에러 느낌)
    np.random.seed(404)  # 시드도 404!
    glitch_positions = np.random.uniform(BEAT * 4, DURATION - 1, size=20)
    for pos in glitch_positions:
        glitch_dur = np.random.uniform(0.02, 0.1)
        g = make_glitch(glitch_dur)
        place_sound(master, g, pos)

    # 특별 글리치 구간 (32비트 근처에 집중)
    for i in range(8):
        pos = BEAT * 30 + np.random.uniform(0, BEAT * 4)
        g = make_glitch(np.random.uniform(0.03, 0.15))
        g *= 1.5  # 더 크게
        place_sound(master, g, pos)

    print("✨ 리버브 & 마스터링...")
    master = reverb(master, decay=0.25, delay_ms=100)

    # 페이드 인/아웃
    fade_in = int(SAMPLE_RATE * 2)
    fade_out = int(SAMPLE_RATE * 3)
    master[:fade_in] *= np.linspace(0, 1, fade_in)
    master[-fade_out:] *= np.linspace(1, 0, fade_out)

    # 노멀라이즈
    peak = np.max(np.abs(master))
    if peak > 0:
        master = master / peak * 0.85

    return master


def save_wav(filename, data, sr=SAMPLE_RATE):
    """WAV 파일 저장"""
    data_int = np.int16(data * 32767)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)  # 모노
        wf.setsampwidth(2)  # 16비트
        wf.setframerate(sr)
        wf.writeframes(data_int.tobytes())


if __name__ == '__main__':
    print("=" * 50)
    print("  🎵 404 Music Generator")
    print("  BPM: 85 | Key: Cm | Duration: ~45s")
    print("=" * 50)

    track = generate_track()

    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "404_music.wav")
    save_wav(output_path, track)

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ 저장 완료: {output_path}")
    print(f"   파일 크기: {file_size:.1f} MB")
    print(f"   재생 시간: ~{DURATION}초")
    print("   → 파일을 더블클릭하거나 미디어 플레이어로 재생하세요!")
