# MLX-mallit Apple Siliconille (8GB & 64GB) – Kattava Opas

Tämä opas on päivitetty vastaamaan uusimpia MLX-optimoituja tekoälymalleja Apple Silicon -laitteille (M1/M2/M3/M4). Opas kattaa tekstin generoinnin, koodiavustuksen sekä konenäön (Vision/OCR).

Miksi MLX?

MLX on Applen oma koneoppimiskirjasto, joka mahdollistaa mallien ajamisen suoraan Macin GPU:lla ja jaetulla muistilla. Se on usein 2–3x nopeampi kuin geneeriset ratkaisut (kuten perus-Ollama) ja kuluttaa vähemmän virtaa.

1. Suositukset: 8GB RAM (MacBook Air M1/M2)

8GB keskusmuisti on tiukka, joten mallien on oltava voimakkaasti pakattuja (4-bit) ja kooltaan alle 4 miljardia parametria.

Teksti & Koodi (Text Models)

Nämä mallit mahtuvat muistiin (< 4GB) ja jättävät tilaa käyttöjärjestelmälle.

Malli

Käyttötarkoitus

Nopeus (token/s)

Komento (esim.)

Qwen2.5-1.5B-Instruct-4bit

Paras yleismalli 8GB:lle. Loistava koodauksessa ja logiikassa kokoisekseen.

~80–120

mlx-community/Qwen2.5-1.5B-Instruct-4bit

Llama-3.2-1B-Instruct-4bit

Nopein. Erittäin kevyt, hyvä suomenkieliseen chattiin ja yksinkertaisiin ohjeisiin.

~100–140

mlx-community/Llama-3.2-1B-Instruct-4bit

Llama-3.2-3B-Instruct-4bit

Laadukkain chat. Raskaampi (rajalla 8GB:lle), mutta luonnollisin kieli.

~30–50

mlx-community/Llama-3.2-3B-Instruct-4bit

Konenäkö & OCR (Vision Models)

Kuvien tunnistus ja tekstin luku kuvista.

Malli

Käyttötarkoitus

Muistinkäyttö

Qwen2.5-VL-3B-Instruct-4bit

Paras OCR. Lukee suomea, taulukoita ja käsinkirjoitusta erinomaisesti.

~3 GB

Llama-3.2-11B-Vision

Varoitus: Liian raskas 8GB:lle. Käytä Qwen2.5-VL:ää.

-

2. Suositukset: 64GB RAM (MacBook Pro/Studio)

Isolla muistilla voit ajaa "Desktop-luokan" malleja, jotka kilpailevat GPT-4:n kanssa tietyissä tehtävissä.

Teksti & Koodi (Pro)

Malli

Käyttötarkoitus

Huomiot

Qwen2.5-32B-Instruct-4bit

Koodauksen kuningas. Erinomainen päättelykyky. Vastaa GPT-4-tasoa monessa kooditehtävässä.

Vie n. 18-20 GB

Llama-3.3-70B-Instruct-4bit

Paras yleismalli. Valtava tietomäärä, erittäin hyvä suomi.

Vie n. 40 GB (Toimii 64GB koneella hyvin)

Qwen2.5-Coder-14B-Instruct-4bit

Koodi-spesifi. Erityisen hyvä Python/JS-koodauksessa, kevyt 32B:hen verrattuna.

Vie n. 9 GB

Konenäkö (Pro)

Malli

Käyttötarkoitus

Qwen2.5-VL-7B-Instruct-4bit

Tarkempi kuin 3B-versio, ymmärtää monimutkaisia kaavioita paremmin.

3. Asennus ja Käyttö (CLI)

Paras tapa käyttää MLX-malleja on virallinen mlx-lm kirjasto.

1. Perusasennus

Avaa terminaali ja asenna työkalut:

# Asenna MLX-LM ja tarvittavat kirjastot
pip install -U mlx-lm openai pillow

# (Valinnainen) Asenna llm-työkalu ja mlx-laajennus
brew install llm
llm install llm-mlx


2. Pika-ajo (Chat)

Kokeile mallia lataamatta sitä pysyvästi (lataa välimuistiin):

# 8GB koneelle (Qwen 2.5 1.5B)
python -m mlx_lm.generate --model mlx-community/Qwen2.5-1.5B-Instruct-4bit --prompt "Koodaa Pythonilla matopeli."

# 64GB koneelle (Qwen 2.5 32B)
python -m mlx_lm.generate --model mlx-community/Qwen2.5-32B-Instruct-4bit --prompt "Selitä kvanttifysiikan alkeet suomeksi."


3. Serverin pystytys (API)

Tämä tekee koneestasi paikallisen "OpenAI API" -palvelimen. Hyödyllinen koodieditoreille (Cursor, VS Code Continue) tai omille skripteille.

# Käynnistä serveri (esim. Qwen 2.5 VL 3B) porttiin 8080
mlx_lm.server --model mlx-community/Qwen2.5-VL-3B-Instruct-4bit --port 8080


4. Konenäkö ja OCR (Python-scripti)

Kun serveri on käynnissä (ks. kohta 3), voit käyttää tätä Python-koodia kuvien lukemiseen (OCR). Tämä toimii erityisen hyvin Qwen2.5-VL -mallilla.

Tallenna nimellä ocr_test.py:

import base64
from openai import OpenAI

# Yhdistä paikalliseen MLX-serveriin
client = OpenAI(base_url="http://localhost:8080/v1", api_key="mlx")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Vaihda tähän oma kuvatiedostosi
image_path = "lasku.jpg"
base64_image = encode_image(image_path)

response = client.chat.completions.create(
    model="default", # MLX-serveri käyttää ladattua mallia
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Lue tämä kuva ja muuta siinä oleva taulukko Markdown-muotoon."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
            ],
        }
    ],
    max_tokens=800,
)

print(response.choices[0].message.content)


5. Vaihtoehtoiset Työkalut

Jos komentorivi (CLI) tuntuu hankalalta, tässä graafiset vaihtoehdot:

LM Studio:

Lataa sovellus (lmstudio.ai).

Hae hakusanalla "MLX".

Toimii "drag & drop" -periaatteella. Tukee nykyään MLX:ää natiivisti (Technical Preview / Beta).

Ollama:

Helpoin asentaa (brew install ollama), mutta ei käytä MLX:ää.

M1-koneilla Ollama on hieman hitaampi kuin puhdas MLX, koska se käyttää llama.cpp:tä (Metal-kiihdytetty, mutta MLX on optimoidumpi Applen muistinhallinnalle).

Hugging Face CLI:

Jos haluat ladata mallit manuaalisesti: pip install huggingface_hub, sitten huggingface-cli download mlx-community/Qwen2.5-1.5B-Instruct-4bit.

Yhteenveto

8GB kone: Pysy malleissa, joiden nimessä on 1B, 1.5B tai 3B ja pääte -4bit.

Koodaus: Valitse Qwen 2.5 (tai Coder-versio).

Suomi-chat: Llama 3.2 tai Qwen 2.5.

Kuvat (OCR): Qwen2.5-VL-3B.
