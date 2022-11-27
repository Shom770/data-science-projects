from json import load


with open("nao_values.json") as file:
    nao_values = load(file)

winter_nao_values = {key: value[:3] + value[10:] for key, value in nao_values.items()}