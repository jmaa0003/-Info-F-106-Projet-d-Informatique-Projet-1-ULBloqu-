"""
MABHOUMA
JOSHUA
000569226
"""
from sys import argv

def parse_game(game_file_path: str) -> dict:
    game = {}
    with open(game_file_path, 'r') as GFP:
        #INITIALISATION DES CLĚS DANS LE DICTIONNAIRE game
        whole_file = str(GFP.read())
        

        ###TEST3333
        l = [i for i in whole_file]
        print(l)
        GFP.seek()
        #INITIALISATION DE 'WIDTH', 'LENGTH', 'MAX_MOVES' dans le dictionnaire game
        WIDTH, LENGTH, MAX_MOVES, EDGE_OF_MAP, HORIZ_BOUNDARY, VERT_BOUNDARY, EMPTY = 0, 0, "", "+", "-", "|", "."
        edge_counter = 0
        for w in whole_file:
            if edge_counter < 2:
                if w != EDGE_OF_MAP:
                    WIDTH += 1
                else:
                    edge_counter += 1
        
        OFFSET, row = 4, 1
        while whole_file[((2*WIDTH+OFFSET) + (2+WIDTH) * row)-1] != HORIZ_BOUNDARY :
            row += 1
        LENGTH = row
            
        for i in range(len(whole_file)-1, -1, -1):
            if whole_file[i] != EDGE_OF_MAP and whole_file[i].isnumeric():
                    MAX_MOVES += str(whole_file[i])

        game['width'], game['length'] = WIDTH, LENGTH
        game['cars'], game['max_moves'], game['empty_slot'] = [], int(MAX_MOVES[::-1]), []

        GFP.seek()

        #COPIE DU PLAN DE JEU
        truncated_whole_file = whole_file[:len(whole_file)-4]
        ###TEST3333
        print("w ->", game.get('width'), "l ->", game.get('length'), "TOPG ->", game)
        game_board = game_board_maker(game.get('width'), game.get('length'))

        pos = 0
        for twf in truncated_whole_file:
            if twf.isalpha():
                ligne, colonne = pos//game.get('width'), (pos%game.get('width'))-1 
                game_board[ligne+1][colonne+1] = twf #Note à moi-même: bordures comptées.
            pos += 1

        #CONSTRUCTION DE 'cars' DANS LE DICTIONNAIRE game
        i = 1
        temp_car_pieces = {}
        while i < game.get('length')+1:
            j = 1                              #TODO: si possible, remttre en for ... in range...
            while j < game.get('width')+1:
                if not game_board[i][j].isalpha():
                    game['empty_slot'].append( (i-1, j-1) ) # decrémente car itère sur la bordure dans mon programme
                else:
                    if game_board[i][j] not in temp_car_pieces.keys() :
                        temp_car_pieces[f'{game_board[i][j]}'] = []
                    temp_car_pieces[f'{game_board[i][j]}'] = (j-1, i-1)
                    
                    greatest_car_value = max(temp_car_pieces.keys())
                    
                    #TROUVER L'ORIGINE DE CHAQUE VOITURE
                    for index in range(ord('A'), ord(greatest_car_value)+1):
                        current_car = temp_car_pieces[f'{chr(index)}']
                        current_car.sort()
                        game['cars'].append(current_car[0]) #origine de la voiture dans le plan

                        def orientation_car(var):
                            return 'v' if all([var[i][1] == var[0][1] for i in range(len(var))]) else 'h'
                        
                        game['cars'].append( orientation_car(current_car) )

                        if orientation_car(current_car) == 'h':
                            game['cars'].append (current_car[-1][1] - current_car[0][1] + 1 )
                        else:
                            game['cars'].append(current_car[-1][0] - current_car[0][0] + 1 )
                j += 1
            i += 1
    return game
                


def get_game_str(game: dict, current_move_number: int) -> str:
    game_board = game_board_maker(game.get('width'), game.get('length'), game.get('cars')[0][0])
    MAX_MOVES = game.get('max_moves')
    string_to_print = ""
    if not current_move_number % 10 :
        if MAX_MOVES - current_move_number == 10:
            string_to_print = f"ATTENTION ! {MAX_MOVES - current_move_number} mouvements restants"
        else:   
            string_to_print = f"Il vous reste {MAX_MOVES - current_move_number} mouvements"
    
    for i in range(len(game_board)-1):
        for j in game_board[i]:
            string_to_print += game_board[i][j]
        string_to_print += "\n"
    for last_row in game_board[-1]:
        string_to_print += last_row
    
    return string_to_print


def move_car(game: dict, car_index: int, direction: str) -> bool:
    pass

 
def is_win(game: dict) -> bool:
    pass # return parse_game -> game_board[coordonnees][de la sortie] == chr(65)


def play_game(game: dict) -> int:
    pass


def game_board_maker(width, length, coordonnees_car_A=None):
    EDGE_OF_MAP, HORIZ_BOUNDARY, VERT_BOUNDARY, EMPTY = "+", "-", "|", "."
    UPPER_LOWER_BOUND = f"{EDGE_OF_MAP}{HORIZ_BOUNDARY*(width-2)}{EDGE_OF_MAP}"
    MIDDLE_ROW = f"{VERT_BOUNDARY}{EMPTY*width}{VERT_BOUNDARY}"

    game_board_template = [list(UPPER_LOWER_BOUND)]
    for i in range(length):
        game_board_template.append(list(MIDDLE_ROW))
    game_board_template.append(list(UPPER_LOWER_BOUND))

    if coordonnees_car_A != None:
        game_board_template[coordonnees_car_A[-1]][-1] = EMPTY #dans mon programme (x,y) <=> x-ème colonne, y-ème ligne

    return game_board_template
    
"""
def

def

def

def

def
"""

if __name__ == '__main__':
    file_inserted = argv[1]
    parse_game(file_inserted)
