import re

text = open("../src/jacll_parser.py", 'r').read()

out = ''
rules = {}

for rule in re.findall(r'\"\"\"([^"]*)\"\"\"', text):
    [name, patterns] = re.split(r'\:', rule)[:2]
    name = name.strip()
    lines = re.split(r'\|', patterns)
    lines = [re.match(r'[^\%]*', y).group(0) for y in [x.strip() if x.strip() != '' else 'ε' for x in lines]]
    if name not in rules:
        rules[name] = lines
    else:
        rules[name] += lines

prod = 1

out += 'NT = { ' + ', '.join(set(filter(lambda x: x != None and x != 'ε',
                                        [x if x not in rules.keys() else None 
                                         for line in rules.values() 
                                         for elem in line 
                                         for x in re.findall(r'\w+', elem)]))) + ' }\n\n\n'
out += 'T = { ' + ', '.join(rules.keys()) + ' }\n\n\n'

for left in rules:
    prods = iter(rules[left])
    out += f'p{str(prod)}: {left} : {next(prods)}\n'
    prod += 1
    for right in prods:
        out += f'p{str(prod)}: {" "*len(left)} | {right}\n'
        prod += 1

outfile = open("BNF.md",'w', encoding='utf-8')

outfile.write(out)

