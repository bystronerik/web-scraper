import json

races = list()
with open("races.txt", "r", encoding="utf8") as f:
    for line in f.readlines():
        race = {}
        print(line.strip())
        race['value'] = line.strip()
        race['other-values'] = []
        races.append(race)
f.close()

f = open("races.json", "w+", encoding="utf8")
json.dump(races, f, ensure_ascii=False)
f.close()
