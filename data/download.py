"""Baixa os arquivos usados nos ensaios direto do site da Case Western Reserve University
e confere o SHA-256 de cada um. Uso: python data/download.py
"""
import hashlib
import urllib.request
from pathlib import Path

BASE = "https://engineering.case.edu/sites/default/files/{}.mat"
FILES = {
    # arquivo: (descrição na CWRU, sha256)
    "97":  ("Normal_0 (sem defeito, 0 hp)",            "16bf48babcf1c7ac224bc1a81cd9eafdb27e42d5cf559761907e067e8eeadf3c"),
    "105": ("IR007_0 (pista interna, 0,007\", 0 hp)",  "f80b0ea04fd06b372a0eaec7c056543ea37e4bb4727a5b173d2a5bacd2aa9cab"),
    "118": ("B007_0 (esfera, 0,007\", 0 hp)",          "b00628f8dd8d1d930af77fa465d1e5cdb385fe259489053f91f3680bda7f640e"),
    "130": ("OR007@6_0 (pista externa, 0,007\", 0 hp)","35a095307d0971477049b343a1b5981dde465a58fb7f233ad89b035068c1717d"),
    "185": ("B014_0 (esfera, 0,014\", 0 hp)",          "5bea2c60f177215ba3ec4ae287faf745d7e14aed1a12efe9e37b27c27044bafc"),
    "222": ("B021_0 (esfera, 0,021\", 0 hp)",          "fcc0ee740fa123b1f4683f555458891719efb2857afd9fdee63e8fde0ed14469"),
}

out = Path(__file__).resolve().parent / "raw"
out.mkdir(exist_ok=True)
for name, (desc, sha) in FILES.items():
    dest = out / f"{name}.mat"
    if not dest.exists():
        print(f"baixando {name}.mat · {desc}")
        req = urllib.request.Request(BASE.format(name), headers={"User-Agent": "Mozilla/5.0"})
        dest.write_bytes(urllib.request.urlopen(req).read())
    got = hashlib.sha256(dest.read_bytes()).hexdigest()
    print(f"{name}.mat {'OK' if got == sha else 'ARQUIVO DIFERENTE: ' + got}")
