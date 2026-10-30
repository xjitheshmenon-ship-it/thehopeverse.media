# Raga check for a music take (ragas.md section 8): how much of the tonal energy sits on the raga's notes.
# python tools/raga_check.py take.mp3 --raga Kalyani [--sa D]   or   --notes "S R2 G3 M2 P D2 N3"   or   --raga 29 (any melakarta number)
import argparse, sys
import numpy as np

SEMI = {"S": 0, "R1": 1, "R2": 2, "R3": 3, "G1": 2, "G2": 3, "G3": 4, "M1": 5, "M2": 6, "P": 7,
        "D1": 8, "D2": 9, "D3": 10, "N1": 9, "N2": 10, "N3": 11,
        # Hindustani letters (r g d n komal, M tivra)
        "r": 1, "R": 2, "g": 3, "G": 4, "m": 5, "M": 6, "d": 8, "D": 9, "n": 10, "N": 11}
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# Notes used up AND down (borrowed graces left out). Hindustani names in Hindustani letters.
RAGAS = {
    "Mohanam": "S R2 G3 P D2", "Bhupali": "S R G P D", "Hamsadhwani": "S R2 G3 P N3", "Hindolam": "S G2 M1 D1 N2",
    "Malkauns": "S g m d n", "Shivaranjani": "S R2 G2 P D2", "Abhogi": "S R2 G2 M1 D2", "Madhyamavati": "S R2 M1 P N2",
    "Sriranjani": "S R2 G2 M1 D2 N2", "Revati": "S R1 M1 P N2", "Amritavarshini": "S G3 M2 P N3",
    "Bilahari": "S R2 G3 M1 P D2 N3", "Kambhoji": "S R2 G3 M1 P D2 N2 N3", "Kapi": "S R2 G2 M1 P D2 N2 N3",
    "Reetigowla": "S R2 G2 M1 P D2 N2", "Abheri": "S R2 G2 M1 P D2 N2", "Mukhari": "S R2 G2 M1 P D1 D2 N2",
    "Hamsanandi": "S R1 G3 M2 D2 N3", "Sohini": "S r G M D N", "Marwa": "S r G M D N", "Vasantha": "S R1 G3 M1 D2 N3",
    "Bhairavi_carnatic": "S R2 G2 M1 P D1 D2 N2", "Sindhubhairavi": "S R2 G2 M1 P D1 N2",
    "Yaman": "S R G M P D N", "Bihag": "S R G m M P D N", "Kedar": "S R G m M P D N", "Desh": "S R G m P D n N",
    "Khamaj": "S R G m P D n N", "Kafi": "S R g m P D n", "Bageshree": "S R g m P D n", "Bhimpalasi": "S R g m P D n",
    "Darbari": "S R g m P d n", "Jaunpuri": "S R g m P d n", "Bhairavi": "S r g m P d n", "Bhairav": "S r G m P d N",
    "Ahir Bhairav": "S r G m P D n", "Todi": "S r g M P d N", "Purvi": "S r G m M P d N", "Puriya Dhanashri": "S r G M P d N",
    "Lalit": "S r G m M d N", "Multani": "S r g M P d N", "Madhuvanti": "S R g M P D N", "Jog": "S g G m P n",
    "Chandrakauns": "S g m d N", "Durga": "S R m P D", "Pahadi": "S R G m P D N", "Kirwani": "S R g m P d N",
    "Charukeshi": "S R G m P d n", "Jaijaiwanti": "S R g G m P D n N",
}
MELA = """Kanakangi Ratnangi Ganamurti Vanaspati Manavati Tanarupi Senavati Hanumatodi Dhenuka Natakapriya Kokilapriya Rupavati
Gayakapriya Vakulabharanam Mayamalavagowla Chakravakam Suryakantam Hatakambari Jhankaradhwani Natabhairavi Keeravani Kharaharapriya
Gourimanohari Varunapriya Mararanjani Charukesi Sarasangi Harikambhoji Dheerasankarabharanam Naganandini Yagapriya Ragavardhini
Gangeyabhushani Vagadheeswari Shulini Chalanata Salagam Jalarnavam Jhalavarali Navaneetam Pavani Raghupriya Gavambhodi Bhavapriya
Shubhapantuvarali Shadvidamargini Suvarnangi Divyamani Dhavalambari Namanarayani Kamavardhini Ramapriya Gamanashrama Vishwambari
Shamalangi Shanmukhapriya Simhendramadhyamam Hemavati Dharmavati Neetimati Kantamani Rishabhapriya Latangi Vachaspati Mechakalyani
Chitrambari Sucharitra Jyotiswarupini Dhatuvardhani Nasikabhushani Kosalam Rasikapriya""".split()
ALIAS = {"Todi_carnatic": 8, "Shankarabharanam": 29, "Kalyani": 65, "Pantuvarali": 51, "Mayamalavagowla": 15}


def mela(n):
    """Pitch classes of melakarta n (1-72) by the chakra rule in ragas.md section 2."""
    pairs = [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]
    k = (n - 1) % 36
    (r, g), (d, ni) = pairs[k // 6], pairs[k % 6]
    return {0, SEMI[f"R{r}"], SEMI[f"G{g}"], 5 if n <= 36 else 6, 7, SEMI[f"D{d}"], SEMI[f"N{ni}"]}


def raga_set(name=None, notes=None):
    if notes:
        return {SEMI[t] for t in notes.split()}
    key = {k.lower(): k for k in list(RAGAS) + list(ALIAS) + MELA}.get(name.lower())
    if name.isdigit():
        return mela(int(name))
    if key in RAGAS:
        return {SEMI[t] for t in RAGAS[key].split()}
    if key in ALIAS:
        return mela(ALIAS[key])
    if key in MELA:
        return mela(MELA.index(key) + 1)
    sys.exit(f"unknown raga {name!r}: use --notes, a melakarta number, or one of {', '.join(sorted(RAGAS))}")


def score(profile, allowed, sa):
    """Share of the 12-bin pitch profile, Sa left out (a drone would swamp it), that falls on the raga's notes."""
    rel = np.roll(profile, -sa)
    return rel[sorted(allowed - {0})].sum() / rel[1:].sum(), rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--raga")
    ap.add_argument("--notes")
    ap.add_argument("--sa", help="tonic as a note name (C, C#, D ...); guessed when left out")
    a = ap.parse_args()
    if not (a.raga or a.notes):
        sys.exit("give --raga or --notes")
    allowed = raga_set(a.raga, a.notes)
    import librosa
    y, sr = librosa.load(a.audio, sr=22050, mono=True)
    h = librosa.effects.harmonic(y)
    profile = librosa.feature.chroma_cqt(y=h, sr=sr).sum(1)  # bin 0 = C
    if a.sa:
        sa = NAMES.index(a.sa.upper().replace("DB", "C#").replace("EB", "D#").replace("GB", "F#").replace("AB", "G#").replace("BB", "A#"))
    else:
        sa = max(range(12), key=lambda s: score(profile, allowed, s)[0] + 0.15 * np.roll(profile, -s)[0] / profile.sum())
    share, rel = score(profile, allowed, sa)
    pct = 100 * rel / rel.sum()
    print(f"Sa = {NAMES[sa]}{'' if a.sa else ' (guessed)'}   in-raga share {100 * share:.0f}%   "
          f"{'PASS' if share >= .8 else 'WEAK' if share >= .65 else 'MISSED: melody went outside the raga'}")
    print("notes (% of tonal energy):", "  ".join(f"{NAMES[(sa + i) % 12]}{'' if i in allowed else '*'} {pct[i]:.0f}" for i in range(12)))
    out = [f"{NAMES[(sa + i) % 12]} ({pct[i]:.0f}%)" for i in range(12) if i not in allowed and pct[i] >= 6]
    if out:
        print("strong notes the raga does not allow:", ", ".join(out))


if __name__ == "__main__":
    main()
