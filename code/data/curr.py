with open('shit_list.txt', 'w+') as f:
    curr =f.read().replace('\n', '\\n')
    f.write(curr)


list = None
with open('shit_list.txt', 'r') as f:
    list = f.readlines()
    print(list)


print(len(list))
