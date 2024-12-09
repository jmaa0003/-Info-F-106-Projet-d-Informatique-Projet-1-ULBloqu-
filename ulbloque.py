"""
MABHOUMA
JOSHUA
000569226
"""
from sys import argv
from getkey import getkey

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
                corrupted_y = pos//(game.get('width')+3)
                corrupted_x = pos%(   (game.get('width')+3)*corrupted_y + 1   )
                game_board[corrupted_y][corrupted_x] = twf #Note à moi-même: bordures comptées.
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
    game_board = game_board_maker(game.get('width'), game.get('height'), game.get('cars')[0][0])
    MAX_MOVES = game.get('max_moves')
    WHITE, SUFFIX = ("white", "\u001b[47m"), "\u001b[0m"
    colours = [("red", "\u001b[41m"),\
               ("green", "\u001b[42m"),\
               ("yellow", "\u001b[43m"),\
               ("blue", "\u001b[44m"),\
               ("magenta", "\u001b[45m"),\
               ("cyan", "\u001b[46m") ]
    
    string_to_print = ""
    if MAX_MOVES - current_move_number < 11:
        string_to_print = f"ATTENTION ! {current_move_number} mouvements effectués sur {MAX_MOVES}\n\n"
    else:   
        string_to_print = f"{current_move_number} mouvements effectués. {MAX_MOVES - current_move_number} restants\n\n"
    
    for car_index, car in enumerate(game.get('cars')):
        car_letter, car_length, car_orientation = chr(ord('A') + car_index), car[2], car[1]
        cyclic = (car_index-1)%(len(colours))
        car_origin_x, car_origin_y = car[0]

        if car_orientation == 'h':
            for x in range(car_length):
                if car_index == 0:
                    game_board[car_origin_y + 1][car_origin_x + x + 1] = WHITE[1] + car_letter + SUFFIX #La voiture blanche est toujours horizontale
                else:
                    game_board[car_origin_y + 1][car_origin_x + x + 1] = colours[cyclic][1] + car_letter + SUFFIX
        else:
            for y in range(car_length):
                game_board[car_origin_y + y + 1][car_origin_x + 1] = colours[cyclic][1] + car_letter + SUFFIX

    for i in range(len(game_board)-1):
        for j in range(len(game_board[i])):
            string_to_print += game_board[i][j]
        string_to_print += "\n"
    for last_row in game_board[-1]:
        string_to_print += last_row
    
    return string_to_print


def move_car(game: dict, car_index: int, direction: str) -> bool:
    UNAVAILABLE_COORDINATES = generate_coordinates(game.get('cars'))
    SELECTED_CAR_ORIENTATION, SELECTED_CAR_LENGTH = game.get('cars')[car_index][1:]
    X, Y = game.get('cars')[car_index][0]
    HORIZONTAL_BOUND_X_COORD, VERTICAL_BOUND_Y_COORD = game.get('width'), game.get("height")
    SELECTED_CAR_LETTER, MOVE_DONE = chr(car_index + ord('A')), False
    message_utilisateur = ""

    if SELECTED_CAR_ORIENTATION == 'h':
        if direction == 'UP':
            if all([  (X+j, Y-1) not in [(X, -1)] + UNAVAILABLE_COORDINATES for j in range(SELECTED_CAR_LENGTH)  ]):
                game['cars'][car_index][0],  MOVE_DONE = (X, Y-1), True

        elif direction == 'DOWN':
            if all([  (X+j, Y+1) not in [(X, VERTICAL_BOUND_Y_COORD)] + UNAVAILABLE_COORDINATES for j in range(SELECTED_CAR_LENGTH)  ]):
                game['cars'][car_index][0], MOVE_DONE = (X, Y+1), True

        elif direction == 'RIGHT':
            if (X+SELECTED_CAR_LENGTH, Y) not in [(HORIZONTAL_BOUND_X_COORD, Y)] + UNAVAILABLE_COORDINATES:
                game['cars'][car_index][0], MOVE_DONE = (X+1, Y), True

        elif direction == 'LEFT':
            if (X-1, Y) not in [(-1, Y)] + UNAVAILABLE_COORDINATES:
                game['cars'][car_index][0], MOVE_DONE = (X-1, Y), True
   
    else:
        if direction == 'UP':
            if (X, Y-1) not in [(X, -1)] + UNAVAILABLE_COORDINATES:
                game['cars'][car_index][0], MOVE_DONE = (X, Y-1), True

        elif direction == 'DOWN':
            if (X, Y+SELECTED_CAR_LENGTH) not in [(X, VERTICAL_BOUND_Y_COORD)] + UNAVAILABLE_COORDINATES:
                game['cars'][car_index][0], MOVE_DONE = (X, Y+1), True

        elif direction == 'RIGHT':
            if all([  (X+1, Y+i) not in [(HORIZONTAL_BOUND_X_COORD, Y)] + UNAVAILABLE_COORDINATES for i in range(SELECTED_CAR_LENGTH)  ]):
                game['cars'][car_index][0], MOVE_DONE = (X+1, Y), True

        elif direction == 'LEFT':
            if all([  (X-1, Y+i) not in [(-1, Y)] + UNAVAILABLE_COORDINATES for i in range(SELECTED_CAR_LENGTH)  ]):
                game['cars'][car_index][0], MOVE_DONE = (X-1, Y), True

    return MOVE_DONE

 
def is_win(game: dict) -> bool:
    CAR_A_X, CAR_A_Y = game.get('cars')[0][0]
    CAR_A_LENGTH, HORIZONTAL_BOUND_X_COORD = game.get('cars')[0][2], game.get('width')
    return (CAR_A_X + CAR_A_LENGTH, CAR_A_Y) == (HORIZONTAL_BOUND_X_COORD, CAR_A_Y) #j'empêche tout abus dans ma fonction 'move_car'


def game_board_maker(WIDTH, HEIGHT, coordonnees_car_A=None) -> list[list]:
    EDGE_OF_MAP, HORIZ_BOUNDARY, VERT_BOUNDARY, EMPTY = "+", "-", "|", "."
    UPPER_LOWER_BOUND = f"{EDGE_OF_MAP}{HORIZ_BOUNDARY*(WIDTH-2)}{EDGE_OF_MAP}"
    MIDDLE_ROW = f"{VERT_BOUNDARY}{EMPTY*WIDTH}{VERT_BOUNDARY}"

    game_board_template = [list(UPPER_LOWER_BOUND)]
    for i in range(HEIGHT):
        game_board_template.append(list(MIDDLE_ROW))
    game_board_template.append(list(UPPER_LOWER_BOUND))

    if coordonnees_car_A:
        game_board_template[coordonnees_car_A[-1]][-1] = EMPTY #dans mon programme (x,y) <=> x-ème colonne, y-ème ligne

    return game_board_template
    

def generate_coordinates(set_of_cars) -> list:
    requested_coordinates = []
    for car in set_of_cars:
        car_orientation, car_length = car[1:]
        x_origin, y_origin = car[0]
        
        if car_orientation == 'h':
            for offset in range(car_length):
               requested_coordinates.append((x_origin + offset, y_origin)) 
        else:
            for offset in range(car_length):
               requested_coordinates.append((x_origin, y_origin + offset))

    return requested_coordinates


def play_game(game: dict) -> int:
    PARKING_EXIT_X, PARKING_EXIT_Y = game.get('width'), game.get('cars')[0][2]
    print('▌│█║▌║▌║ Hé toi ! Oui toi ! Peux-tu m\'aider à sortir ma voiture du parking s\'il te plaît ? ║▌║▌║█│▌')
    print('▌│█║▌║▌║ C\'est la voiture A, blanche. Elle est garée à l\'horizontale. ║▌║▌║█│▌\n')
    
    #DISPLAY
    print(get_game_str(game, game.get('max_moves')))
    print(' --- Appuyez sur Y pour accepter, ESC pour fuir la situation ---\n')


    STARTED_GAME = False
    while not STARTED_GAME:
        user_answer = getkey() 
        if user_answer.isalpha():
            if user_answer.upper() == 'Y':
                STARTED_GAME, MAX_MOVES, CARS_INDEXES = True, game.get('max_moves'), [i for i in range(len(game.get('cars')))]
                game_result, current_moves = None, 0
                print('▌│█║▌║▌║ Merci beaucoup ! Si tu n\'en peux plus, ou que tu dois partir, pas de souci ! Fais-le moi savoir ! ║▌║▌║█│▌')
                print(' --- Durant la partie, appuyez sur ESC pour quitter. ---\n --- Bonne chance ! ---')

                key_pressed = getkey()
                while game_result == None and game.get('cars')[0][0] != (PARKING_EXIT_X-1, PARKING_EXIT_Y) and current_moves < MAX_MOVES: 
                    # TODO : !!! VOIR "Solution Code !!!" dans bloc-notes Samsung
                        
                           #TODO: boucle de deplacement continu
                           # TODO: changer le game_result en cours de pqrtie pour la defaite 
                            
                                #TODO : formation du jeu --> selection de voiture, deplacement + incrémentation current_moves ou non ET finir par game_result = 1 sinon = 0
                        #Remplacement plus adapté de is_win()
                
        elif user_answer == 'ESCAPE':
            game_result = 2

    return game_result


def movement_handler() -> bool:
    index_car_selected = pseudo_car_index
    second_pressed_key = getkey()
    if second_pressed_key in {'DOWN', 'UP', 'LEFT', 'RIGHT'}:
        move_car(game, index_car_selected, second_pressed_key)
    elif second_pressed_key == 'ESCAPE':
        game_result = 2
    elif second_pressed_key.isalpha() and ord(second_pressed_key.upper()) - ord('A') in [i for i in range(len(game.get('cars')))]:

"""
def

def
"""

if __name__ == '__main__':
    #INITIALISATION
    file_inserted = argv[0]
    game = parse_game(file_inserted)
    
    if play_game(game) == 2:
        exit("A̴b̴a̴n̴d̴o̴n̴ ̴d̴e̴ ̴l̴a̴ ̴p̴a̴r̴t̴i̴e̴")
    elif play_game(game) == 1:
    elif play_game(game) == 0:
    
#TODO !!!! : DOCSTRINGS !!!!!!!

