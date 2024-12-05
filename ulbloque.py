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
        GFP.seek()
        
        #INITIALISATION DE 'WIDTH', 'HEIGHT', 'MAX_MOVES' dans le dictionnaire game
        WIDTH, HEIGHT, MAX_MOVES, EDGE_OF_MAP, HORIZ_BOUNDARY, VERT_BOUNDARY, EMPTY = 0, 0, "", "+", "-", "|", "."
        edge_counter = 0
        for w in whole_file:
            if edge_counter < 2:
                if w != EDGE_OF_MAP:
                    WIDTH += 1
                else:
                    edge_counter += 1
        
        OFFSET, row = 4, 1
        while whole_file[-1 + (2*WIDTH + 4 + row * (3 + WIDTH))] != HORIZ_BOUNDARY :
            row += 1
        HEIGHT = row
            
        for i in range(len(whole_file)-1, -1, -1):
            if whole_file[i] != EDGE_OF_MAP and whole_file[i].isnumeric():
                    MAX_MOVES += str(whole_file[i])

        game['width'], game['height'] = WIDTH, HEIGHT
        game['cars'], game['max_moves'], game['empty_slot'] = [], int(MAX_MOVES[::-1]), []
        GFP.seek()

        #COPIE DU PLAN DE JEU
        truncated_whole_file = whole_file[:len(whole_file)-3]
        game_board = game_board_maker(game.get('width'), game.get('height'))
        pos = 1
        for twf in truncated_whole_file:
            if twf.isalpha():
                fk_y = pos//(game.get('width')+3)
                fk_x = pos%(   (game.get('width')+3)*fk_y + 1   )
                game_board[fk_y][fk_x] = twf #Note à moi-même: bordures comptées.
            pos += 1

        #CONSTRUCTION DE 'cars' DANS LE DICTIONNAIRE game
        temp_car_pieces = {}
        for i in range(1,game.get('height')+1):
            for j in range(1, game.get('width')+1):
                if not game_board[i][j].isalpha():
                    game['empty_slot'].append( (j-1, i-1) ) # -1 car j'itère sur la bordure dans mon programme
                else:
                    if game_board[i][j] not in temp_car_pieces.keys() :
                        temp_car_pieces[f'{game_board[i][j]}'] = []
                    temp_car_pieces[f'{game_board[i][j]}'].append( (j-1, i-1) )
             
        #TROUVER L'ORIGINE DE CHAQUE VOITURE
        greatest_car_value = max(temp_car_pieces.keys())           
        for index in range(ord('A'), ord(greatest_car_value)+1):
            current_car = temp_car_pieces[f'{chr(index)}']
            current_car.sort()

            def orientation_car(var):
                return 'h' if all([var[i][1] == var[0][1] for i in range(len(var))]) else 'v'
            
            if orientation_car(current_car) == 'h':
                current_car_length = current_car[-1][0] - current_car[0][0] + 1  
            else:
                current_car_length = current_car[-1][1] - current_car[0][1] + 1
            game['cars'].append([current_car[0], orientation_car(current_car), current_car_length] )
            #origine de la voiture dans le plan = current_car[0] = temp_car_pieces[lettre_voiture][0]
            
    return game
                

def get_game_str(game: dict, current_move_number: int) -> str:
    game_board = game_board_maker(game.get('width'), game.get('HEIGHT'), game.get('cars')[0][0])
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


def game_board_maker(width, HEIGHT, coordonnees_car_A=None):
    EDGE_OF_MAP, HORIZ_BOUNDARY, VERT_BOUNDARY, EMPTY = "+", "-", "|", "."
    UPPER_LOWER_BOUND = f"{EDGE_OF_MAP}{HORIZ_BOUNDARY*(width-2)}{EDGE_OF_MAP}"
    MIDDLE_ROW = f"{VERT_BOUNDARY}{EMPTY*width}{VERT_BOUNDARY}"

    game_board_template = [list(UPPER_LOWER_BOUND)]
    for i in range(HEIGHT):
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
    file_inserted = argv[0]
    parse_game(file_inserted)

