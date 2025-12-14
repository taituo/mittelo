Mittelö: Low-Level Design (LLD) Specification

Versio: 1.4 (Code-Aligned Implementation Spec)
Päiväys: 14.12.2025
Taso: Komponentti- ja kooditaso

Versiohistoria & Muutokset (v1.4)

Komponentit: process_mgr.py korvattu client.py:llä (Network Loop). Lisätty drivers/abstract.py.

Protokolla: Viestityypit vakioitu (TASK_REQ, ASSIGN_ROLE, ACK).

Tila: Orkestraattoriin lisätty StreamWriter-yhteys ja last_seen.

Async: Siirrytty selectors-mallista asyncio.gather -malliin.

Sisällysluettelo

Johdanto ja Filosofia

Esivaatimukset (Prerequisites)

Järjestelmän Komponenttirakenne

Viestintäprotokolla (MCP-over-TCP)

Agent Wrapper -sisäinen logiikka

Orkestraattorin Sisäinen Tila

CLI-Adapterit (Driver Layer)

Käyttötapausskenaariot ja Topologiat

Muistinhallinta ja Käyttöjärjestelmäoptimoinnit

Virheenhallinta ja Watchdog

Tuotanto ja Pilvioptimointi (Cloud Strategy)

1. Johdanto ja Filosofia

Mittelö on tehokas paikallinen agenttiparvi. Se poikkeaa SaaS-pohjaisista ratkaisuista siirtämällä laskennan reunalle (Edge/Localhost) ja on tällä hetkellä yksi kustannustehokkaimmista tavoista ajaa moniagenttijärjestelmiä ilman pilvikuluja.

Ei API-rajoja: Agentit eivät ole HTTP-kutsuja, vaan pitkäkestoisia prosesseja.

Ei Token-kustannuksia: Mallit ajetaan paikallisesti (mmap-muistijaolla).

Digitaalinen Suvereniteetti: Data ei poistu koneelta.

2. Esivaatimukset (Prerequisites)

Jotta järjestelmä voi pyörittää 5–40 agentin parvea, seuraavien ehtojen on täytyttävä.

2.1 Laitteistovaatimukset (Hardware Reference)

Taso

Laitteisto

Agenttikapasiteetti (7B Q4_K_M)

Metal-tuki (GPU/NPU)

Huomiot

Minimum

M1 Air / 8GB RAM

4–6 Agenttia

Rajoitettu

Swap-riski, pidä Colima/Docker < 4GB.

Standard

M2 Pro / 32GB RAM

15–20 Agenttia

Kyllä (MPS)

Mukava kehityskäyttö.

Enterprise

M1/M3 Max / 64GB RAM

30–40 Agenttia

Kyllä (Dual-engine)

Täysi suorituskyky. Ei swapia. Koko parvi muistissa.

2.2 Ohjelmistoympäristö

Python 3.10+: Orkestrointiin (asyncio).

Container Runtime (Valinnainen):

macOS: Colima (VZ + Rosetta) tai Rancher Desktop (k3s).

Linux: Podman tai natiivi Docker.

Local LLM Runtime:

llama.cpp (käännettynä: llama-cli) TAI

Ollama (server-moodissa) TAI

MLX (Apple Silicon natiivi Python-kirjasto).

Mallitiedostot: GGUF-muodossa (esim. Llama-3-8B-Instruct-v0.2.Q4_K_M.gguf).

3. Järjestelmän Komponenttirakenne

Järjestelmä koostuu yhdestä hallintaprosessista (orchestrator) ja $N$ kappaleesta agenttiprosesseja (wrapper).

3.1 Tiedostorakenne

Rakenne on päivitetty eriyttämään verkkoliikenne (client.py) ja malliajuri (drivers/).

src/
├── orchestrator/
│   ├── __init__.py
│   ├── server.py         # Asyncio TCP Server (was hub.py)
│   ├── router.py         # Viestinvälityslogiikka (Star/Mesh)
│   └── state.py          # WorkerRegistry & TaskQueue
├── wrapper/
│   ├── __init__.py
│   ├── agent.py          # Agent Loop (was agent.py)
│   ├── backends.py       # Backend execution logic
│   ├── client.py         # Network Loop (TCP Client)
│   └── drivers/          # CLI-spesifiset ajurit
│       ├── abstract.py   # Base Class (start, chat, stop)
│       ├── tmux.py       # Tmux session wrapper
│       ├── llama_cpp.py  # Llama CLI wrapper implementation
│       └── ollama.py     # Ollama API/CLI wrapper
├── protocol/
│   ├── messages.py       # Pydantic/Dataclass määritelmät
│   └── framer.py         # Newline-delimited JSON parseri
└── utils/


4. Viestintäprotokolla (MCP-over-TCP)

Protokolla on tilaton, tekstipohjainen ja rivinvaihtoon perustuva (Newline Delimited JSON, NDJSON).

4.1 Kuljetuskerros (Transport Layer)

Protokolla: TCP (localhost loopback)

Koodaus: UTF-8

Kehystys (Framing): \n (0x0A) erottaa viestit.

4.2 Viestirakenne

{
  "ver": 1,
  "id": "uuid-v4",
  "type": "ENUM",         // Katso 4.3
  "src": "worker-5002",
  "dst": "orch-5000",
  "payload": {}
}


4.3 Viestityypit (Enum)

Viestityypit on vakioitu tukemaan Request/Response -parigmaa ja kättelyn kuittausta.

Tyyppi

Payload

Kuvaus

HANDSHAKE

{ "driver": "llama", "caps": ["code"] }

Agentti ilmoittautuu.

HANDSHAKE_ACK

{ "status": "ok", "config": {...} }

Orkestraattori hyväksyy liitoksen.

ASSIGN_ROLE

{ "role": "tester", "spec_ref": "..." }

Roolin ja tehtävän jako.

TASK_REQ

{ "prompt": "...", "stop": ["###"] }

Pyyntö suorittaa tehtävä (ent. INFERENCE_REQ).

TASK_RES

{ "text": "def foo()...", "done": true }

Vastaus tehtävään.

HEARTBEAT

{ "load": 0.4, "status": "idle" }

Ping/Pong elossaolon varmistamiseen.

KILL

{ "reason": "timeout" }

Pakotettu sammutuskomento.

ERROR

{ "code": 500, "msg": "Process died" }

Virheilmoitus.

5. Agent Wrapper -sisäinen logiikka

Wrapper toimii siltana TCP-socketin ja CLI-prosessin STDIN/STDOUT välillä.

5.1 Tilakone (State Machine)

INIT: Konfiguraatio, TCP-yhteys client.py:ssä.

SPAWN: AbstractDriver.start() käynnistää aliprosessin.

IDLE: Odottaa TASK_REQ-viestejä.

BUSY: Generoi vastausta (driver.chat()).

COOLDOWN: Puskurien tyhjennys.

5.2 Sentinel Detection

Wrapperin on tunnistettava milloin LLM lopettaa puhumisen.

Llama/OpenCode: Käytetään reverse-prompt flagia (esim. ###END###).

One-shot CLI: Prosessin exit code.

5.3 Concurrency (Asyncio Gather)

Käytetään asyncio-kirjastoa (eikä matalan tason selectoreja) hallitsemaan verkkoa ja ajuria rinnakkain.

# wrapper/client.py pseudokoodi
class AgentClient:
    async def run(self):
        reader, writer = await asyncio.open_connection(...)
        # Käynnistetään rinnakkain
        await asyncio.gather(
            self.network_loop(reader, writer),
            self.driver.start()
        )

    async def network_loop(self, reader, writer):
        while True:
            line = await reader.readline()
            msg = json.loads(line)
            if msg['type'] == 'TASK_REQ':
                # Ajetaan taustalla, jotta Heartbeatit ei blokkaa
                asyncio.create_task(self.handle_task(msg, writer))
            elif msg['type'] == 'KILL':
                await self.driver.stop()
                break


6. Orkestraattorin Sisäinen Tila

Orkestraattori hallitsee parven tilaa ja viestien reititystä. Tilaan on lisätty yhteysolio.

6.1 Worker State

@dataclass
class WorkerState:
    id: str                   # "worker-5001"
    connection: StreamWriter  # Aktiivinen TCP-kirjoitin
    role: str                 # "thinker", "debater"
    status: str               # "idle", "busy"
    last_seen: float          # Timestamp (Heartbeat valvontaan)
    driver: str               # "llama_cpp"


7. CLI-Adapterit (Driver Layer)

Ajurikerros on abstrahoitu AbstractDriver-luokalla, jotta olemassa olevat prototyypit voidaan "plugata" sisään.

7.1 Driver Interface (drivers/abstract.py)

class AbstractDriver(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Käynnistää aliprosessin (esim. llama-cli)."""
        pass

    @abstractmethod
    async def chat(self, content: str, stop_tokens: List[str]) -> AsyncGenerator[str, None]:
        """Lähettää promptin ja streamaa vastauksen."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Sammuttaa prosessin hallitusti (SIGTERM)."""
        pass


7.2 Implementaatiot

LlamaCppDriver: Wrappaa llama-cli -binäärin. Hallitsee reverse-prompt logiikan.

OllamaDriver: Wrappaa ollama run tai REST API:n.

8. Käyttötapausskenaariot ja Topologiat

Tämä osio määrittelee, miten agentit organisoidaan eri tehtäviin.

Skenaario 1: Feature Development (Lineaarinen Putki)

Topologia: Linear Pipeline (A -> B -> C -> D).

Agentit: Thinker -> Worker -> TypeGuard -> Tester -> Reviewer.

Data Flow: Speksi valuu alaspäin. Virheistä palautus Workerille.

Skenaario 2: Refaktorointi (Timantti-väittely)

Topologia: Diamond Debate.

Agentit: Proposer -> (Fast vs. Readable) -> Debaters -> Merger.

Data Flow: Haarautuva väittely, yhdistyminen lopussa.

Skenaario 3: Kilpailuareena (Competitive Arena)

Topologia: Parallel Competition.

Agentit: 3x Coder -> 3x Opponent -> Judges.

Logiikka: Ei kommunikaatiota kilpailijoiden välillä. Paras tulos voittaa.

Skenaario 4: Datan Siivous (Map-Reduce)

Topologia: Map-Reduce Swarm.

Agentit: Mappers -> Reducers -> Guard.

Hyöty: Massiivinen rinnakkaisuus suurille tiedostoille.

Skenaario 5: Compliance Chain (Migraatio/Turva)

Topologia: Strict Chain.

Agentit: Scanner -> Anonymizer -> Validator -> Auditor.

Erikoisuus: "STOP"-komento pysäyttää koko ketjun virheen sattuessa.

Skenaario 6: Hybrid Star-Gossip (Robustius)

Tavoite: Tuotantoympäristön vikasietoisuus.

Topologia: Star (Default) -> Gossip (Fallback).

Logiikka:

Normaalitilassa agentit puhuvat Hubille (Star).

Jos Hub ei vastaa Heartbeatiin (3s timeout), agentit siirtyvät Peer-to-Peer -tilaan.

Tilatieto ja tehtäväjonot synkronoidaan Gossip-protokollalla naapureiden kesken.

Hyöty: Järjestelmä ei kaadu, vaikka Orkestraattori-prosessi kuolisi.

9. Muistinhallinta ja Käyttöjärjestelmäoptimoinnit

9.1 Mmap (Memory Mapping)

Kriittinen 40 agentin ajamisessa.

Mekanismi: Kaikki llama-cli prosessit avaavat saman .gguf-mallitiedoston lipuilla MAP_SHARED.

Tulos: OS lataa 5GB mallin vain kerran fyysiseen RAM-muistiin. Agentit jakavat tämän muistin. Vain KV-Cache (n. 300MB/agentti) on uniikkia.

Laskelma: 5GB (Malli) + 40 * 0.3GB (Context) ≈ 17GB. Tämä mahtuu helposti 32GB tai 64GB koneeseen.

9.2 Prosessieristys

os.setsid() varmistaa, että agentit ovat omassa prosessiryhmässään.

resource.setrlimit nostaa avoimien tiedostokahvojen (file descriptors) rajaa.

10. Virheenhallinta ja Watchdog

10.1 Heartbeat

Agentit lähettävät HEARTBEAT 2s välein. Jos hiljaisuus > 10s, Orkestraattori merkitsee agentin kuolleeksi ja käynnistää uuden (Self-healing).

10.2 Hallusinaatiot

Token-pohjainen laskenta (esim. >50 samaa tokenia) on epäluotettavaa sub-word tokenizereilla.

Parempi algoritmi: Toistuvan rivin tunnistus.

Puskuroi edelliset 3 riviä.

Jos current_line == previous_line toistuu > 5 kertaa, kyseessä on luuppi.

Toimenpide: Lähetä SIGTERM aliprosessille ja raportoi virhe.

10.3 Backpressure

TCP-puskurien täyttymistä valvotaan. Raskaissa datasiirroissa käytetään sovellustason ACK-kuittauksia.

11. Tuotanto ja Pilvioptimointi (Cloud Strategy)

Miten Mittelö-arkkitehtuuri skaalataan paikalliskoneelta (Mac) pilveen (Linux K3s/Podman) "Entry Tier" -hinnoittelulla.

11.1 Local vs. Cloud -erojen harmonisointi

Kehitysympäristö (macOS) käyttää virtualisointia, tuotanto (Linux) natiivia kerneliä.

Komponentti

macOS (Dev)

Linux (Cloud/Prod)

Optimointistrategia

Runtime

Colima / Docker Desktop

Podman / Native Docker

Käytä Linuxissa Podmania (rootless) turvallisuuden vuoksi.

GPU/NPU

Metal (MPS)

CPU (AVX2/AVX512)

Huom: Entry-tason pilvessä ei ole GPU:ta. Optimoi CPU-inferenssiin (GGUF).

Muisti

Unified RAM (Shared)

Discrete RAM

Linuxissa mmap toimii tehokkaammin ilman VM-kerrosta.

Volume

VirtioFS (hidas)

Native FS (nopea)

Pilvessä mallitiedostot luetaan suoraan levyltä (NVMe).

11.2 "Bin Packing" -strategia (Entry Tier Maximization)

Tavoite: Maksimoida agenttien määrä per € ilman GPU-vuokrausta.

Strategia: Shared Model Volume & Slim Images

Host Volume: Lataa malli Host-koneelle /mnt/models. Mounttaa se kontteihin Read-Only (-v /mnt/models:/models:ro).

Slim Image: Kontin koon on oltava < 200 MB. Se sisältää vain Python-runtimen ja Mittelö-koodin. Ei malleja, ei raskaita kirjastoja. Tämä takaa nopean käynnistyksen (< 2s) ja pienen registry-kustannuksen.

Mmap: Koska kaikki kontit lukevat samaa fyysistä inodea hostilta, kernelin Page Cache lataa mallin RAMiin vain kerran.

Kapasiteettilaskelma (Hetzner/AWS Entry Tier - CPU Only):

Instance: 4 vCPU / 16 GB RAM (Hinta n. 15-20€/kk).

Malli: Llama-3-8B-Q4 (5 GB).

Agentin overhead: 300 MB (Context) + 50 MB (Python).

Tulos:

Käyttis + K3s: 2 GB.

Malli (Shared): 5 GB.

Vapaa tila agenteille: 9 GB.

Max agentit: 9 GB / 0.35 GB ≈ 25 agenttia.

Kustannus per agentti: < 1€/kk.

11.3 Hybrid Cloud Deployment

Jos paikallinen CPU ei riitä (esim. hidas token-nopeus), käytetään hybridimallia.

Router Node (Entry Tier VPS): Pyörittää Orkestraattoria ja kevyitä "Router"-agentteja.

Inference Endpoints: Raskaat "Thinker"-agentit käyttävät ulkoista, halpaa API:a (esim. Gemini Flash, Claude Haiku) wrapperin läpi.

Privacy: Sensitiivinen data pysyy "Worker"-agenteilla (paikallinen Llama), vain yleinen logiikka menee pilveen.