import json

with open('signals.json') as f:
    lines = []
    df = open("destination_signals.json", "w")
    for line in f:
        d = json.loads(line)
        d['new_field'] = '######'
        lines.append(d)
        print(str(d))
        df.write(str(d) + '\n')
    df.close()
