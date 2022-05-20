table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'

tr = {table[i]: i for i in range(58)}

s = [11, 10, 3, 8, 4, 6, 2, 9, 5, 7]

xor = 177451812

add = 100618342136696320



def Decode(x):

    r = sum(tr[x[s[i]]] * 58 ** i for i in range(10))

    return (r - add) ^ xor



def Encode(x):

    x = int(x)
    x = (x ^ xor) + add

    r = list('BV          ')

    for i in range(10):

        r[s[i]] = table[x // 58 ** i % 58]

    return ''. join(r)



# print('Please choose the mode of this application (1 for AV2BV, 2 for BV2AV)')

# mode = input()

# if mode == '1':

#     print('Please input the AV number (number only)')

#     num = int(input())

#     print(Encode(num))

# if mode == '2':

#     print('Please input the BV number (e.g. BV17x411w7KC)')

#     string = input()

#     print(Decode(string))

# if mode != '1' and mode != '2':

#     print('Error!')

# print(Decode('BV17x411w7KC'))

# # print(Decode('BV1Q541167Qg'))

# # print(Decode('BV1mK4y1C7Bz'))

# print(Encode(170001))

# print(Encode(455017605))

# print(Encode(882584971)) 作者：社会易姐QwQ https://www.bilibili.com/read/cv5263184/?from=readlist 出处：bilibili