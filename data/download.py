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
    # ensaio 3 (lado acionado, carga 3 hp e 0,021")
    "100": ("Normal_3 (sem defeito, 3 hp)", "88a5990cb541320e91505a1d72139e1993500ffe6e292a451011667f4138ca78"),
    "108": ("IR007_3 (DE)", "d415f0e65128bfa0b118c2051c988fb0dc6ce3e4c8aa45fdc5ad1d0967462e7d"),
    "133": ("OR007@6_3 (DE)", "53f076cb0d905cf46bffaee7736abce8224ffed777deed03c0c863d762a90c71"),
    "209": ("IR021_0 (DE)", "9f723d6d9d2eba714c6dc50f99321dffa73d8b1e4d3605675b2c2251511eff80"),
    "212": ("IR021_3 (DE)", "bfe13761f545a26b217db897a12d27e16fec74306aa86ade8dbdc8ebe587c253"),
    "234": ("OR021@6_0 (DE)", "ebcbdb96612e8085bbdbf81f0e5e8e8a8d1a693d1ec559c4894f7792771aa9b2"),
    "237": ("OR021@6_3 (DE)", "233d1edb2daa963658369119e389e30f02aca551dd7bb028ab33e7ba63edfd20"),
    # ensaio 3 (lado do ventilador, rolamento 6203)
    "270": ("IR021_0 (FE)", "fd7c20f53af7ccaf7ab6b08b885fbe4bf27ce44d9739af2725dc94c8130af953"),
    "273": ("IR021_3 (FE)", "990bd16b90bf70650f102962331b066242792f285612d5081c2ba80053b2e637"),
    "278": ("IR007_0 (FE)", "1ad584953158dcdf4eb1ceba71dee781e5596163aad37a2619b0649213f9e3dd"),
    "281": ("IR007_3 (FE)", "0f1a41d62797039139cf27c6f8b823fe87de44dfb4b2ef03fc6e0ef4d3734992"),
    "294": ("OR007@6_0 (FE)", "6b774ffb83a046a6a4402221c2bc02c84c8e4494ea8457452e366ccc048c7d5e"),
    "297": ("OR007@6_3 (FE)", "858c409a74f0dcbd31af28f79175daf5e494fe194269909c18c579851aaf3c1d"),
    "315": ("OR021@6_0 (FE)", "e1f6acfe79b622a24bf2ed3d092b83342c9a280a0e443df480c7220a49fff392"),
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
