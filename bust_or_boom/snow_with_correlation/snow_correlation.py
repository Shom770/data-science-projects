from json import load

with open("oni.json") as oni_file:
    oni_values = load(oni_file)
    december_oni_values = {
        key: value[-1] for key, value in oni_values.items() if len(value) == 12
    }
with open("nao_values.json") as nao_file:
    nao_values = load(nao_file)
    december_nao_values = {
        key: value[-1] for key, value in nao_values.items() if len(value) == 12 and int(key) >= 1964
    }

with open("ao_values.json") as ao_file:
    ao_values = load(ao_file)
    december_ao_values = {
        key: value[-1] for key, value in ao_values.items() if len(value) == 12 and int(key) >= 1964
    }

with open("pna_values.json") as pna_file:
    pna_values = load(pna_file)
    december_pna_values = {
        key: value[-1] for key, value in pna_values.items() if len(value) == 12 and int(key) >= 1964
    }

with open("epo_values.json") as epo_file:
    epo_values = load(epo_file)
    december_epo_values = {
        key: value[-1] for key, value in epo_values.items() if len(value) == 12 and int(key) >= 1964
    }


for year, (nao, ao, epo, pna, oni) in enumerate(
    zip(
        december_nao_values.values(),
        december_ao_values.values(),
        december_epo_values.values(),
        december_pna_values.values(),
        december_oni_values.values()
    ),
    start=1964
):
    if nao < 0 and ao < 0 and epo < 0 and pna < 0 and oni < 0:
        print("December", year)
