#Mini Project: Word Puzzle
import random 
def display_instructions(filename): #displaying the instruction file in read mode
    mode_read = 'r' 
    instruction_txt_file = open(filename, mode_read)
    instructions = instruction_txt_file.read() 
    print(instructions) 
    instructions = instruction_txt_file.close()
    
def play_game(puzzle, answer): 
    initial_guesses = 5 #number of chances that the user gets
    old_guess = [] 
    while initial_guesses >= 1:
        guess = get_guess(initial_guesses)
        update_puzzle_string(puzzle, answer, guess)
        display_puzzle_string(puzzle) 
        answer = list(answer) 
        check_win = is_word_found(puzzle, answer) 
    
        if guess not in answer:
            initial_guesses = initial_guesses - 1 
        else:
            if guess in old_guess:
                initial_guesses = initial_guesses - 1
            else:
                initial_guesses = initial_guesses
        old_guess = store_previous_guess(guess) 
 
        if check_win == 'Y':
            break
        display_result(check_win, answer)
    
def get_guess(num_guesses): # guess remaining
    guess = input('Guess a letter (' + str(num_guesses) + ' guesses remaining):')
    return guess

def update_puzzle_string(puzzle, answer, guess): #updating the puzzle string after a guess
    for n, x in enumerate(answer):
        if guess == x: 
            puzzle[n] = x 
    return puzzle

def display_puzzle_string(puzzle): #current stae of the puzzle
    answer_so_far = '' 
    for x in puzzle:
        answer_so_far = answer_so_far + " " + x 
        print('The answer so far is', answer_so_far + '.') 
    return puzzle

def is_word_found(puzzle, answer): #is the puzzle = answer
    if puzzle == answer: 
        is_win = 'Y' 
    else:
        is_win = 'N' 
    return is_win

def display_result(check_win, answer): #displaying results
    final_answer = ''
    for x in answer:
        final_answer = final_answer + x 
    if check_win == 'Y':
        print('YEAH! You found the word', final_answer + '!')
    else:
        print('No :(, the correct word was', final_answer + '. Good luck next time!', )
        
def store_previous_guess(guess): #storing previous guesses
    old_guess = []
    for x in guess:
        old_guess.append(x)
    return old_guess

def main(): 
    filename = 'wp_instructions.txt' #instructions file
    display_instructions(filename) #displaying the instruction file
    list_of_words = ['bison', 'coyote', 'rhinoceros', 'bear', 'porcupine', 'mouse']
    answer = random.choice(list_of_words) #randomly choosing the word for the puzzle
    current_puzzle = []
 
    for x in answer: #letter in the word?
        current_puzzle.append(x)
 
    for i, x in enumerate(current_puzzle): #diplay of how the puzzle looks like
        current_puzzle[i] = '_ '
 
    print('The answer so far is', '_ ' * len(answer) + '.') #initial state of puzzle
    play_game(current_puzzle, answer) 
    input('Press enter to end game')
main()

