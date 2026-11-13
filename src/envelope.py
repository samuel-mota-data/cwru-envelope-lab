"""Funções usadas nos ensaios 1 e 2 (CWRU, 12 kHz, lado acionado).

Referência: Smith & Randall (2015), "Rolling element bearing diagnostics using the
Case Western Reserve University data: A benchmark study", MSSP 64-65:100-131.
"""
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from scipy.signal import hilbert, butter, sosfiltfilt, stft

FS = 12_000  # amostras por segundo

# Multiplicadores da frequência do eixo, página oficial "Bearing Information" da CWRU.
# A CWRU lista "Rolling Element" = 4.7135 (DE), que é 2xBSF; BSF = 4.7135 / 2.
MULT = {"BPFO": 3.5848, "BPFI": 5.4152, "BSF": 4.7135 / 2, "FTF": 0.39828}
MULT_FE = {"BPFO": 3.0530, "BPFI": 4.9469, "BSF": 3.9874 / 2, "FTF": 0.3817}  # 6203-2RS, lado do ventilador


def load_channel(path, ch="DE"):
    """Lê o sinal de um acelerômetro (DE = lado acionado, FE = lado do ventilador) e a rotação."""
    m = loadmat(path)
    key = next(k for k in m if k.endswith(f"_{ch}_time"))
    rpm_keys = [k for k in m if k.endswith("RPM")]
    rpm = float(np.ravel(m[rpm_keys[0]])[0]) if rpm_keys else 1797.0
    return np.ravel(m[key]).astype(float), rpm


def load_de(path):
    """Lê o sinal do acelerômetro do lado acionado (_DE_time) e a rotação (RPM)."""
    m = loadmat(path)
    key = next(k for k in m if k.endswith("_DE_time"))
    rpm_keys = [k for k in m if k.endswith("RPM")]
    rpm = float(np.ravel(m[rpm_keys[0]])[0]) if rpm_keys else 1797.0
    return np.ravel(m[key]).astype(float), rpm


def fault_freqs(rpm):
    """Frequências teóricas de falha (Hz) para a rotação dada."""
    fr = rpm / 60
    f = {k: v * fr for k, v in MULT.items()}
    f["2xBSF"] = 2 * f["BSF"]
    return fr, f


def envelope_spectrum(x, band=None, fs=FS):
    """Método 1: envelope (Hilbert) e espectro. Com `band`, filtra antes (passa-banda)."""
    x = x - x.mean()
    if band:
        sos = butter(4, band, btype="bandpass", fs=fs, output="sos")
        x = sosfiltfilt(sos, x)
    e = np.abs(hilbert(x))
    e -= e.mean()
    S = np.abs(np.fft.rfft(e * np.hanning(len(e)))) / len(e)
    return np.fft.rfftfreq(len(e), 1 / fs), S


def cepstrum_prewhiten(x):
    """Método 2: pré-branqueamento por cepstro (Borghesani et al., 2013).
    Mantém a fase e deixa a magnitude do espectro igual a 1: some o que é regular,
    sobra o impulsivo."""
    X = np.fft.fft(x - x.mean())
    return np.real(np.fft.ifft(X / (np.abs(X) + 1e-12)))


def kurtosis_band(x, fs=FS, npers=(16, 32, 64), fmin=500, fmax=5400, min_bw=600):
    """Método 3 (simplificado): faixa de maior curtose espectral via STFT.
    Não faz a separação discreto/aleatório do benchmark original."""
    best = (-1.0, None, None)
    for nper in npers:
        f, _, Z = stft(x, fs=fs, nperseg=nper, noverlap=nper * 3 // 4)
        P = np.abs(Z) ** 2
        sk = (P ** 2).mean(axis=1) / (P.mean(axis=1) ** 2 + 1e-30) - 2
        sk[(f < fmin) | (f > fmax)] = -1
        i = int(np.argmax(sk))
        if sk[i] > best[0]:
            bw = max(fs / nper, min_bw)
            best = (float(sk[i]), max(f[i] - bw / 2, 100), min(f[i] + bw / 2, fs / 2 - 100))
    return best  # (curtose, f_baixa, f_alta)


def peak_rank(f, S, target, tol=0.02, fmax=500):
    """Procura o maior valor a ±tol da frequência alvo e diz em que posição ele fica
    entre os picos locais do espectro (5 Hz a fmax). Posição 1 = maior pico."""
    sel = (f > 5) & (f < fmax)
    fs_, Ss = f[sel], S[sel]
    win = np.abs(fs_ - target) <= tol * target
    pk = Ss[win].max()
    pf = float(fs_[win][np.argmax(Ss[win])])
    loc = (Ss[1:-1] > Ss[:-2]) & (Ss[1:-1] > Ss[2:])
    rank = int(np.sum(Ss[1:-1][loc] > pk)) + 1
    return pf, rank


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
