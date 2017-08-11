import csv

with open('Feminism Comments.csv', 'r') as csvfile:
    spamwriter = csv.reader(csvfile, delimiter='\t', encoding='utf8')
    k = 0
    name = ''
    for line in spamwriter:
        if line[0] != name:
            name = line[0]
            k += 1
    print(k)


