# -*- coding: utf-8 -*-

#import sys
import random

class Wordle:
    def __init__(self, word_length, lang, use_weight = False):
        self.word_length = word_length
        self.lang = lang
        self.word_list = self.read_wordlist('word_collections/')
        self.round = 0
        self.game_over = False
        self.use_weight = use_weight
        
        self.green_word = ['_', '_', '_', '_', '_']
        self.yellow_letters_tuple = []
        self.yellow_letters_set = set([])
        self.gray_letters = []
        
        self.letters = ['Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P',
                               'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
                               'Y', 'X', 'C', 'V', 'B', 'N', 'M']
        
    
        
    def read_wordlist(self, path):
        word_list = []
        with open(path + self.lang + '.txt', 'r') as wordfile:
            line = wordfile.readline()
            while line != "":
                if len(line) == (self.word_length + 1):
                    line_upper = line.upper()
                    line_as_list = [*line_upper]
                    line_as_list.pop()
                    word_list.append(line_as_list)
                line = wordfile.readline()
        return word_list
    
    
    def get_start_words(self):
        if self.lang == 'german':
            return ['RITEN', 'RATEN', 'ARSEN', 'STEIN']
        elif self.lang == 'english':
            return ['SALET', 'SLATE', 'CRANE', 'SLANT', 'CRATE', 'CARTE']
        
    
    def show_interface(self, use_word):
        self.round += 1
        if self.round > 500:
            self.game_over = True
            return
        return "Try:" + "".join(use_word).upper() + " > "
        
        
    def read_answer(self, use_word):
        answer = str(input())
        
        if answer == '+++++' or answer == "end" or answer == "End":
            self.game_over = True
            return "Round won!"
        
        elif answer == 'N' or answer == "" or answer == 'WNF':
            return "Calculating new word..."
        
        elif len(answer) != 5:
            return "Invalid input."
        
        answer_list = [*answer]
        
        for pos in range(self.word_length):
            if answer_list[pos] == '+':
                #print('gruen:' + use_word[pos])
                self.green_word[pos] = use_word[pos]
                
            elif answer_list[pos] == '=':
                #print('gelb:' + use_word[pos])
                self.yellow_letters_tuple.append((use_word[pos], pos))
                self.yellow_letters_set.add(use_word[pos])
                
            elif answer_list[pos] == '-':
                #print('grau:' + use_word[pos])
                self.gray_letters.append(use_word[pos])
            elif answer_list[pos] == '?':
                pass
            else:
                return "Invalid Symbol"
        return "Calculating new word..."
                
                
    def letter_value(self, letter):
        if letter == 'E':
            if self.lang == 'german':
                return 17.4
            elif self.lang == 'english':
                return 11.0
        elif letter == 'N':
            if self.lang == 'german':
                return 9.78
            elif self.lang == 'english':
                return 7.2
        elif letter == 'I':
            if self.lang == 'german':
                return 7.55
            elif self.lang == 'english':
                return 8.6
        elif letter == 'S':
            if self.lang == 'german':
                return 7.27
            elif self.lang == 'english':
                return 8.7
        elif letter == 'R':
            if self.lang == 'german':
                return 7.0
            elif self.lang == 'english':
                return 7.3
        elif letter == 'A':
            if self.lang == 'german':
                return 6.51
            elif self.lang == 'english':
                return 7.8
        elif letter == 'T':
            if self.lang == 'german':
                return 6.15
            elif self.lang == 'english':
                return 6.7   
        elif letter == 'D':
            if self.lang == 'german':
                return 5.08
            elif self.lang == 'english':
                return 3.8   
        elif letter == 'H':
            if self.lang == 'german':
                return 4.76
            elif self.lang == 'english':
                return 2.3     
        elif letter == 'U':
            if self.lang == 'german':
                return 4.35
            elif self.lang == 'english':
                return 3.3     
        elif letter == 'L':
            if self.lang == 'german':
                return 3.44
            elif self.lang == 'english':
                return 5.3   
        elif letter == 'C':
            if self.lang == 'german':
                return 3.06
            elif self.lang == 'english':
                return 4.0
        elif letter == 'G':
            if self.lang == 'german':
                return 3.01
            elif self.lang == 'english':
                return 3.0
        elif letter == 'M':
            if self.lang == 'german':
                return 2.53
            elif self.lang == 'english':
                return 2.7
        elif letter == 'O':
            if self.lang == 'german':
                return 2.51
            elif self.lang == 'english':
                return 6.1    
        elif letter == 'B':
            if self.lang == 'german':
                return 1.89
            elif self.lang == 'english':
                return 2.0
        elif letter == 'W':
            if self.lang == 'german':
                return 1.89
            elif self.lang == 'english':
                return 0.91 
        elif letter == 'F':
            if self.lang == 'german':
                return 1.66
            elif self.lang == 'english':
                return 0.0  
        elif letter == 'K':
            if self.lang == 'german':
                return 1.21
            elif self.lang == 'english':
                return 0.97
        elif letter == 'Z':
            if self.lang == 'german':
                return 1.13
            elif self.lang == 'english':
                return 0.44  
        elif letter == 'P':
            if self.lang == 'german':
                return 0.79
            elif self.lang == 'english':
                return 2.8 
        elif letter == 'V':
            if self.lang == 'german':
                return 0.67
            elif self.lang == 'english':
                return 1.0 
        elif letter == 'J':
            if self.lang == 'german':
                return 0.27
            elif self.lang == 'english':
                return 0.21  
        elif letter == 'Y':
            if self.lang == 'german':
                return 0.04
            elif self.lang == 'english':
                return 1.6  
        elif letter == 'X':
            if self.lang == 'german':
                return 0.03
            elif self.lang == 'english':
                return 0.27  
        elif letter == 'Q':
            if self.lang == 'german':
                return 0.02
            elif self.lang == 'english':
                return 0.19
        else:
            return 0.0
        
    
    
    def calc_next_word(self, start = False):
        
        next_word_list = []
        
        if start:
            next_word_list = self.get_start_words()
        else:
            for word in self.word_list:
                    
                word_invalid = False
                debug_word = ''
                if "".join(word) == debug_word:
                    print("YES WORD FOUND!")
                
                for pos in range(self.word_length):
                    
                    if word[pos] in self.gray_letters:
                        
                        if word[pos] in self.green_word and word[pos] in self.yellow_letters_set:
                            count_letter_allowed = self.count_letter(word[pos], self.green_word) + 1
                        
                        elif word[pos] in self.green_word and word[pos] not in self.yellow_letters_set:
                            count_letter_allowed = self.count_letter(word[pos], self.green_word)
                      
                        elif word[pos] not in self.green_word and word[pos] in self.yellow_letters_set:
                            count_letter_allowed = 1
                            
                        else:
                            count_letter_allowed = 0
                            
                        count_letter_word = self.count_letter(word[pos], word)
                        
                        if count_letter_word > count_letter_allowed:
                            if "".join(word) == debug_word:
                                print("I want to use the word " + "".join(word) + " but it has too many grey letters!")
                            word_invalid = True
                            

                #    if word[pos] not in self.green_word and word[pos] not in self.yellow_letters_set and word[pos] in self.gray_letters:
                #        if "".join(word) == debug_word:
                #            print("Ich will das Wort " + "".join(word) + " benutzen, aber es enthält graue Buchstaben!")
                #        word_invalid = True
                        
                    if self.yellow_letters_set:
                        if (all(letter in word for letter in self.yellow_letters_set)):
                            pass
                        else:
                            if "".join(word) == debug_word:
                                print("I want to use the word " + "".join(word) + " but it has NO yellow letters!")
                            word_invalid = True
                            
                    #elif self.yellow_letters_set and word[pos] not in self.yellow_letters_set:
                    #    if "".join(word) == debug_word:
                    #        print("Ich will das Wort " + "".join(word) + " benutzen, aber es hat gelbe Buchstaben NICHT!")
                    #    word_invalid = True
                        
                    if self.green_word[pos] != '_' and word[pos] != self.green_word[pos]:
                        if "".join(word) == debug_word:
                            print("I want to use the word " + "".join(word) + " but the green letters are on the wrong position!")
                        word_invalid = True
                    
                for letter_tuple in self.yellow_letters_tuple:
                    letter, pos = letter_tuple
                    if word[pos] == letter:
                        if "".join(word) == debug_word:
                            print("I want to use the word " + "".join(word) + " but it has yellow letters on incorrect places!")
                        word_invalid = True
                    
                if word_invalid:
                    continue
                
                if not word_invalid:
                    next_word_list.append(word)

        
        if not self.use_weight and len(next_word_list) > 0:
            next_word = next_word_list[random.randint(0, len(next_word_list)-1)]
            return "".join(next_word)
            
        elif self.use_weight and len(next_word_list) > 0:
            weighted_list = self.calc_weight_word(next_word_list)
            next_word = random.choices(next_word_list, weights=weighted_list, k=1)[0]
            return "".join(next_word)
        else:
            return None
        
    def count_letter(self, letter, word):
        count = 0
        for let in word:
            if let == letter:
                count += 1
        return count
        
    
    def calc_weight_word(self, word_array):
        # einbauen doppelte Buchstaben bestrafen
        weights = []
        used_letters = []
        for word in word_array:
            weight = 0.0
            for letter in word:
                if letter not in used_letters:
                    weight += self.letter_value(letter)
                else:
                    weight += (self.letter_value(letter)/5)
                used_letters.append(letter)  
            weights.append(weight)
        return weights
        
        
    def check_game_over(self):
        return self.game_over
    
    
    def welcome_text(self):
        text = "Welcome to Wordle-Solver!\n"
        text += "You can use these symbols as input: + = -\n"
        text += "+ : Use this if the letter is green/at the correct position\n"
        text += "= : WUse this if the letter is yellow/not correct position\n"
        text += "- : Use this if the letter is gray/not in the word"
        return text
    
    def debug_mode(self):
        print(self.green_word)
        print(self.yellow_letters_tuple)
        print(self.gray_letters)
    
        
def main():
    
    solver = Wordle(word_length=5, lang='english', use_weight=True)

    print(solver.welcome_text())
    
    start_round = True
    while(not solver.check_game_over()):
    
        word = solver.calc_next_word(start_round)
        start_round = False
        
        if word == None:
            solver.game_over = True
            print("No word found!")
            solver.debug_mode()
            break
        
        print(solver.show_interface(word))
        print(solver.read_answer(word))
    
    input()


if __name__ == "__main__":
    main()




    

