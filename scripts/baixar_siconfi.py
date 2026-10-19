"""Baixa DCA (contas anuais) e RGF (3º quadrimestre) de todos os municípios
via API SICONFI/Tesouro (apidatalake.tesouro.gov.br) para um intervalo de anos.

Uso:
    python3 scripts/baixar_siconfi.py --anos 2019 2024 --workers 6

Saída: dados/raw/siconfi/{dca,rgf}/{ano}/{cod_ibge}.json.gz (um arquivo por ente/ano).
Retomável: arquivos já existentes são pulados. Log em dados/raw/siconfi/download.log.
"""
import argparse, gzip, json, logging, os, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados", "raw", "siconfi")
UA = "Mozilla/5.0 (TCC-USP-Esalq; pesquisa academica)"


PAUSA = 0.35  # segundos entre requisições por thread (a API devolve HTTP 429 acima de ~3 req/s)
# Só os anexos usados no modelo são armazenados (o restante é descartado após a chamada).
ANEXOS = {
    "dca": {"DCA-Anexo I-C", "DCA-Anexo I-D"},            # receitas e despesas orçamentárias por natureza
    "rgf": {"RGF-Anexo 01", "RGF-Anexo 02", "RGF-Anexo 05"},  # pessoal, dívida consolidada, caixa e restos a pagar
}


def filtrar(rel, items):
    return [i for i in items if i.get("anexo") in ANEXOS[rel]]


def get_json(url, tries=8):
    for t in range(tries):
        try:
            time.sleep(PAUSA)
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            wait = 15 * (t + 1) if e.code == 429 else 2 ** t
            logging.warning("tentativa %d falhou (%s): HTTP %s; aguardando %ds", t + 1, url, e.code, wait)
            time.sleep(wait)
        except Exception as e:  # noqa: BLE001
            wait = 2 ** t
            logging.warning("tentativa %d falhou (%s): %s; aguardando %ds", t + 1, url, e, wait)
            time.sleep(wait)
    return None


def fetch_all(endpoint, params):
    """Segue a paginação ORDS (hasMore/offset) e devolve a lista completa de items."""
    items, offset = [], 0
    while True:
        p = dict(params, offset=offset) if offset else dict(params)
        url = f"{API}/{endpoint}?" + urllib.parse.urlencode(p)
        d = get_json(url)
        if d is None:
            return None
        items.extend(d.get("items", []))
        if not d.get("hasMore"):
            return items
        offset += d.get("limit", 5000)


def entes_municipais():
    d = get_json(f"{API}/entes")
    return sorted(e["cod_ibge"] for e in d["items"] if e["esfera"] == "M")


def salvar(path, items):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)


def baixar_dca(ano, ente):
    path = os.path.join(ROOT, "dca", str(ano), f"{ente}.json.gz")
    if os.path.exists(path):
        return "skip"
    items = fetch_all("dca", {"an_exercicio": ano, "id_ente": ente})
    if items is None:
        return "erro"
    items = filtrar("dca", items)
    salvar(path, items)
    return "ok" if items else "vazio"


def baixar_rgf(ano, ente):
    path = os.path.join(ROOT, "rgf", str(ano), f"{ente}.json.gz")
    if os.path.exists(path):
        return "skip"
    base = {"an_exercicio": ano, "co_tipo_demonstrativo": "RGF", "co_poder": "E", "id_ente": ente}
    items = fetch_all("rgf", dict(base, in_periodicidade="Q", nr_periodo=3))
    if items is None:
        return "erro"
    if not items:  # municípios pequenos podem publicar RGF semestral (art. 63 LRF)
        items = fetch_all("rgf", dict(base, in_periodicidade="S", nr_periodo=2))
        if items is None:
            return "erro"
    items = filtrar("rgf", items)
    salvar(path, items)
    return "ok" if items else "vazio"


def podar_existentes():
    """Reaplica o filtro de anexos aos arquivos já baixados (uso após mudar ANEXOS)."""
    n = 0
    for rel in ANEXOS:
        base = os.path.join(ROOT, rel)
        if not os.path.isdir(base):
            continue
        for ano in os.listdir(base):
            pasta = os.path.join(base, ano)
            for nome in os.listdir(pasta):
                if not nome.endswith(".json.gz"):
                    continue
                path = os.path.join(pasta, nome)
                with gzip.open(path, "rt", encoding="utf-8") as f:
                    items = json.load(f)
                novo = filtrar(rel, items)
                if len(novo) != len(items):
                    salvar(path, novo); n += 1
    logging.info("podados %d arquivos", n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anos", nargs=2, type=int, default=[2019, 2024])
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--relatorios", nargs="+", default=["dca", "rgf"])
    ap.add_argument("--podar", action="store_true", help="só reaplica o filtro de anexos aos arquivos existentes")
    a = ap.parse_args()
    os.makedirs(ROOT, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(os.path.join(ROOT, "download.log")), logging.StreamHandler(sys.stdout)])
    if a.podar:
        podar_existentes(); return
    entes = entes_municipais()
    logging.info("%d municípios; anos %s; relatórios %s", len(entes), a.anos, a.relatorios)
    tarefas = [(rel, ano, e) for ano in range(a.anos[0], a.anos[1] + 1) for rel in a.relatorios for e in entes]
    fn = {"dca": baixar_dca, "rgf": baixar_rgf}
    cont, t0 = {}, time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(fn[rel], ano, e): (rel, ano, e) for rel, ano, e in tarefas}
        for i, f in enumerate(as_completed(futs), 1):
            rel, ano, e = futs[f]
            try:
                r = f.result()
            except Exception as exc:  # noqa: BLE001
                r = "erro"; logging.error("%s %s %s: %s", rel, ano, e, exc)
            cont[r] = cont.get(r, 0) + 1
            if i % 500 == 0 or i == len(tarefas):
                logging.info("%d/%d (%.0f%%) em %.0f min: %s", i, len(tarefas), 100 * i / len(tarefas), (time.time() - t0) / 60, cont)
    logging.info("FIM %s", cont)


if __name__ == "__main__":
    main()
