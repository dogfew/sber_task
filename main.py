import pandas as pd
old_df = pd.read_csv('dannye_3mes.csv', sep=';', encoding='cp1252')
old_df.columns = 'Кредит (актив);Вклад (пассив);Дата погашения;Срок погашения, дней;Ставка, %;[ОТВЕТ] Номер группы;Пример группировки (для первых 20 сделок);'.split(';')
new_df = old_df.groupby(by=['Ставка, %', 'Срок погашения, дней'], as_index=False).sum()
new_df['s'] = new_df['Кредит (актив)'] - new_df['Вклад (пассив)']
r, t, s = new_df['Ставка, %'], new_df['Срок погашения, дней'], new_df['s']
d = {'r': [x for x in r],
     't': [x for x in t],
     's': [x for x in s]}
d = list(zip(d['r'], d['t'], d['s']))


def rwa(t, a, p):
    w_gross = 0.05 * (2 if t < 31 else 1)
    w_net = 0.2 * (2 if t < 31 else 1)
    return (a + p) * w_gross + abs(a - p) * w_net


def main(d):
    dr = 0.15 / 2
    dt = 30 / 2
    c = 0
    groups = dict()
    indexes = []
    for num_1, j in enumerate(d):
        if num_1 in indexes:
            continue
        indexes.append(num_1)
        r0, t0, s0 = j
        sA = s0 if s0 >= 0 else 0
        sP = -s0 if s0 < 0 else 0
        new_df['[ОТВЕТ] Номер группы'][num_1] = c
        for num_2, i in enumerate(d):
            if num_2 in indexes:
                continue
            r1, t1, s1 = i
            if abs(r0 - r1) <= dr and abs(t0 - t1) <= dt:
                sA += s1 if s1 >= 0 else 0
                sP -= s1 if s1 < 0 else 0
                indexes.append(num_2)
                new_df['[ОТВЕТ] Номер группы'][num_2] = c
        groups[c] = (t0, r0, sA, sP)
        c += 1
    s = 0
    for k, v in groups.items():
        t, r, a, p = v
        s += rwa(t, a, p)
    return s, groups


result, groups = main(d)
new_df.to_csv('промежуточный_результат.csv')
for r, t, N in zip(new_df['Ставка, %'], new_df['Срок погашения, дней'],
                   new_df['[ОТВЕТ] Номер группы']):
    indexes = old_df[(old_df['Срок погашения, дней'] == t) & (old_df['Ставка, %'] == r)].index
    for i in indexes:
        old_df['[ОТВЕТ] Номер группы'][i] = N
old_df.to_csv('answer.csv')
print(f"RWA: {result}\nGroups: {groups}")
