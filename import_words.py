file_from = ''
file_to = ''

word_list = []

with open(file_from, 'r') as word_file:
    lines = word_file.readlines()
    for word in lines:
        word = word[:-1]
        if len(word) == 5:
            word_list.append(word)

with open(file_to, 'w') as word_file:
       for word in word_list:
            word_file.write(word + '\n')


