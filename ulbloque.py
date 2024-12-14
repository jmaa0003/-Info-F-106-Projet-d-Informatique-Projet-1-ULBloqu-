"""
MABHOUMA
JOSHUA
000569226
"""
from sys import argv
from getkey import getkey

def parse_game(game_file_path: str) -> dict:
    """
    Cette fonction prend en paramètre 'game_file_path', un lien vers un fichier de jeu, et renvoie le dictionnaire 'game',
    primordial au bon déroulement de la suite du jeu.
    """
    game = {}
    with open(game_file_path, 'r') as GFP:
        #INITIALISATION DES CLĚS DANS LE DICTIONNAIRE game
        whole_file = str(GFP.read())
        GFP.seek(0)
        
        #INITIALISATION DE 'WIDTH', 'HEIGHT', 'MAX_MOVES' dans le dictionnaire game
        WIDTH, HEIGHT, MAX_MOVES, EDGE_OF_MAP, HORIZ_BOUNDARY, VERT_BOUNDARY, EMPTY = 0, 0, "", "+", "-", "|", "."
        edge_counter = 0
        for w in whole_file:
            if edge_counter < 2:
                if w != EDGE_OF_MAP:
                    WIDTH += 1
                else:
                    edge_counter +=  1
        
        OFFSET, row = 4, 1
        while whole_file[-1 + (2*WIDTH + 4 + row * (3 + WIDTH))] != HORIZ_BOUNDARY :
            row += 1
        HEIGHT = row
            
        for i in range(len(whole_file)-1, -1, -1):
            if whole_file[i] != EDGE_OF_MAP and whole_file[i].isnumeric():
                    MAX_MOVES += str(whole_file[i])

        game['width'], game['height'] = WIDTH, HEIGHT
        game['cars'], game['max_moves'], game['empty_slot'] = [], int(MAX_MOVES[::-1]), []
        GFP.seek(0)

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
    """
    Cette fonction prend en paramètres le dictionnaire 'game' et un entier 'current_move_number', et renvoie l'affichage du parking
    correspondant au dictionnaire susmentionné.
    """
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
        string_to_print = f" --- ATTENTION ! {current_move_number} mouvements effectués sur {MAX_MOVES} ---\n\n"
    else:   
        string_to_print = f" --- {current_move_number} mouvements effectués. {MAX_MOVES - current_move_number} restants ---\n\n"
    
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
    """
    Cette fonction prend en paramètres le dictionnaire 'game', l'entier 'car_index' ainsi que la string 'direction' et
    Tente d'effectuer le mouvement de la voiture [chr(65 + car_index)] dans la direction donnée.
    Si le déplacement n'est pas possible dû à une collision avec une autre voiture ou une bordure, False est renvoyé sinon True
    """
    UNAVAILABLE_COORDINATES = generate_coordinates(game.get('cars'))
    SELECTED_CAR_ORIENTATION, SELECTED_CAR_LENGTH = game.get('cars')[car_index][1:]
    X, Y = game.get('cars')[car_index][0]
    HORIZONTAL_BOUND_X_COORD, VERTICAL_BOUND_Y_COORD = game.get('width'), game.get("height")
    SELECTED_CAR_LETTER, move_has_been_done = chr(car_index + ord('A')), False

    if SELECTED_CAR_ORIENTATION == 'h':
        if direction == 'UP':
            if all([  (X+j, Y-1) not in [(X, -1)] + UNAVAILABLE_COORDINATES for j in range(SELECTED_CAR_LENGTH)  ]):
                game['cars'][car_index][0], move_has_been_done = (X, Y-1), True

        elif direction == 'DOWN':
            if all([  (X+j, Y+1) not in [(X, VERTICAL_BOUND_Y_COORD)] + UNAVAILABLE_COORDINATES for j in range(SELECTED_CAR_LENGTH)  ]):
                game['cars'][car_index][0], move_has_been_done = (X, Y+1), True

        elif direction == 'RIGHT':
            if (X+SELECTED_CAR_LENGTH, Y) not in [(HORIZONTAL_BOUND_X_COORD, Y)] + UNAVAILABLE_COORDINATES:
                game['cars'][car_index][0], move_has_been_done = (X+1, Y), True

        elif direction == 'LEFT':
            if (X-1, Y) not in [(-1, Y)] + UNAVAILABLE_COORDINATES:
                game['cars'][car_index][0], move_has_been_done = (X-1, Y), True
   
    else:
        if direction == 'UP':
            if (X, Y-1) not in [(X, -1)] + UNAVAILABLE_COORDINATES:
                game['cars'][car_index][0], move_has_been_done = (X, Y-1), True

        elif direction == 'DOWN':
            if (X, Y+SELECTED_CAR_LENGTH) not in [(X, VERTICAL_BOUND_Y_COORD)] + UNAVAILABLE_COORDINATES:
                game['cars'][car_index][0], move_has_been_done = (X, Y+1), True

        elif direction == 'RIGHT':
            if all([  (X+1, Y+i) not in [(HORIZONTAL_BOUND_X_COORD, Y)] + UNAVAILABLE_COORDINATES for i in range(SELECTED_CAR_LENGTH)  ]):
                game['cars'][car_index][0], move_has_been_done = (X+1, Y), True

        elif direction == 'LEFT':
            if all([  (X-1, Y+i) not in [(-1, Y)] + UNAVAILABLE_COORDINATES for i in range(SELECTED_CAR_LENGTH)  ]):
                game['cars'][car_index][0], move_has_been_done = (X-1, Y), True

    return move_has_been_done

 
def is_win(game: dict) -> bool:
    """
    Cette fonction prend le dictionnaire 'game' en paramètres et vérifie selon les données dans ce dictionnaire que la partie
    est gagnée. Si oui, renvoie True, sinon False.
    """
    CAR_A_X, CAR_A_Y = game.get('cars')[0][0]
    CAR_A_LENGTH, HORIZONTAL_BOUND_X_COORD = game.get('cars')[0][2], game.get('width')
    return (CAR_A_X + CAR_A_LENGTH, CAR_A_Y) == (HORIZONTAL_BOUND_X_COORD, CAR_A_Y) #j'empêche tout abus dans ma fonction 'move_car'


def game_board_maker(WIDTH: int, HEIGHT: int, coordonnees_car_A=None) -> list[list]:
    """
    Cette fonction crée avec les paramètres entiers WIDTH, HEIGHT une matrice correspondant au parking de jeu.
    Si coordonnees_car_A, un 2-tuple, est mentionné alors la sortie tout à droite de la voiture A est placée. 
    """
    EDGE_OF_MAP, HORIZ_BOUNDARY, VERT_BOUNDARY, EMPTY = "+", "-", "|", "."
    UPPER_LOWER_BOUND = f"{EDGE_OF_MAP}{HORIZ_BOUNDARY*(WIDTH)}{EDGE_OF_MAP}"
    MIDDLE_ROW = f"{VERT_BOUNDARY}{EMPTY*WIDTH}{VERT_BOUNDARY}"

    game_board_template = [list(UPPER_LOWER_BOUND)]
    for i in range(HEIGHT):
        game_board_template.append(list(MIDDLE_ROW))
    game_board_template.append(list(UPPER_LOWER_BOUND))

    if coordonnees_car_A:
        game_board_template[1 + coordonnees_car_A[-1]][-1] = EMPTY #dans mon programme (x,y) <=> x-ème colonne, y-ème ligne

    return game_board_template
    

def generate_coordinates(set_of_cars: list) -> list:
    """
    Cette fonction prend en paramètre une liste de voitures et génère une liste des coordonnées dans le parking où il
    n'est pas possible de se déplacer.
    """
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
    """
    Cette fonction prend en paramètre le dictionnaire 'game' et gère la partie entière de jeu. Elle renvoie:
    - 0 si la voiture A est sortie
    - 1 si elle n'est toujours pas sortie avant le nombre max de mouvement tolérés
    - 2 si l'utilisateur abandonne la partie en appuyant sur ESC
    """
    PARKING_EXIT = (game.get('width'), game.get('cars')[0][0][1])
    MESSAGES = ['▌│█║▌║▌║ Hé toi ! Oui toi ! Peux-tu m\'aider à sortir ma voiture du parking de l\'ULB s\'il te plaît ? ║▌║▌║█│▌',\
                '▌│█║▌║▌║ C\'est la voiture A, blanche. Elle est garée à l\'horizontale. ║▌║▌║█│▌\n',\
                ' --- Appuyez sur Y pour accepter, ESC pour fuir la situation ---\n',\
                '▌│█║▌║▌║ Merci beaucoup ! Si tu n\'en peux plus, ou que tu dois partir, pas de souci ! Fais-le moi savoir ! ║▌║▌║█│▌\n',\
                ' --- Durant la partie, appuyez sur ESC pour quitter. ---\n --- TOUCHES:\
                \n     ⇦⇧⇨⇩ pour déplacer une voiture\n     Clavier pour choisir la voiture à la lettre correspondante ---\n\
                       --- Bonne chance ! ---',\
                ' --- Une voiture doit être choisie avant d\'exécuter un mouvement ---',\
                ' --- Sélection de voiture invalide. Réessayez ---',\
                ' --- Touche invalide ---\n --- RAPPEL:\n     ESC = fuir\nClavier = Selectionner depuis le clavier la voiture à la\
                lettre correspondante\n ⇦⇧⇨⇩ = déplacer une voiture choisie au préalable ---',\
                ' --- Touche invalide ---',\
                ' --- Voiture {} sélectionnée ---']

    print(MESSAGES[0])
    print(MESSAGES[1])
    #DISPLAY
    print(get_game_str(game, 0))
    print(MESSAGES[2])
    
    STARTED_GAME = False
    while not STARTED_GAME:
        user_answer = getkey()
        if user_answer.upper() == 'Y':
            STARTED_GAME, MAX_MOVES, CAR_A_LENGTH, CARS_INDEXES = True, game.get('max_moves'), game.get('cars')[0][2], [i for i in range(len(game.get('cars')))]
            game_result, number_of_moves_done, times_invalid_keys_pressed = None, 0, 0
            print(MESSAGES[3])
            print(MESSAGES[4])
            print(get_game_str(game, number_of_moves_done))
            key_pressed, current_car_index = None, None
            
            while game_result == None and (game.get('cars')[0][0][0] + CAR_A_LENGTH, game.get('cars')[0][0][1]) != PARKING_EXIT \
                                      and number_of_moves_done < MAX_MOVES:
                key_pressed = getkey()
                if is_a_car_letter(key_pressed, CARS_INDEXES):
                    if current_car_index != None:
                        car_already_selected = key_pressed.upper() == chr(65 + current_car_index)
                        if not car_already_selected:
                            print(MESSAGES[9].format(key_pressed.upper())) 
                    else:
                        print(MESSAGES[9].format(key_pressed.upper()))
                    current_car_index = ord(key_pressed.upper()) - ord('A')
                
                elif is_a_move(key_pressed):
                    if current_car_index is None:
                        print(MESSAGES[5])
                    else: 
                        if move_car(game, current_car_index, key_pressed):
                            number_of_moves_done += 1
                        print(get_game_str(game, number_of_moves_done))
                else:    
                    if key_pressed == 'ESCAPE':
                        game_result = 2
                        
                    elif key_pressed.isalpha():
                        print(MESSAGES[6])
                        
                    elif times_invalid_keys_pressed % 5 == 00 and times_invalid_keys_pressed > 0:
                        print(MESSAGES[7])
                        times_invalid_keys_pressed += 1
                        
                    else:
                        print(MESSAGES[8])
                        times_invalid_keys_pressed += 1
            
            if number_of_moves_done == MAX_MOVES:
                front_of_car_A = (game.get('cars')[0][0][0] + CAR_A_LENGTH, game.get('cars')[0][0][1])
                if front_of_car_A != PARKING_EXIT:
                    game_result = 1
                else:
                    game_result = 0
                    
            else:
                game_result = 0
        
        elif user_answer == 'ESCAPE':
            game_result = 2
            STARTED_GAME = not STARTED_GAME

    return game_result


def is_a_car_letter(pseudo_car_letter: str, list_of_cars_indices: list) -> bool:
    """
    Cette fonction prend la string "pseudo_car_letter" et une liste d'indices de voitures et vérifie qu'il s'agit bien\
    d'une lettre de voiture valide. Toute voiture [...] aura pour indice ord([...]) - ord('A')
    Elle renvoie True si c'est le cas, False sinon
    """
    return pseudo_car_letter.isalpha() and len(pseudo_car_letter) == 1 and ord(pseudo_car_letter.upper()) - ord('A')\
           in list_of_cars_indices


def is_a_move(pseudo_move: str) -> bool:
    """
    Cette fonction prend la string "pseudo_move" et vérifie qu'il s'agit bien d'une tentative de mouvement de voiture valide.
    Elle renvoie True si c'est le cas, False sinon
    """
    return pseudo_move in {'DOWN', 'UP', 'LEFT', 'RIGHT'}


if __name__ == '__main__':
    MESSAGES_MAIN = ['▌│█║▌║▌║ OOOooh merci beaucoup ! Tu as réussi à amener ma voiture à la sortie dans les temps.\
                     Je n\'avais pas dis qu\'il manquait d\'essence donc tes mouvements étaient limités. ▌│█║▌║▌║\n▌│█║▌║▌║ Mais tu l\'as fait. Merci vraiment ! ▌│█║▌║▌║\n\
                     _____🚓💨_____',
                     '▌│█║▌║▌║ Sacrebleu ! Non seulement ma voiture est coincée ici, mais en plus il n\'y a plus d\'essence !? Je n\'aurai jamais dû me garer ici.\
                     Merci toutefois pour ton aide j\'en suis reconnaissant...▌│█║▌║▌║\n --- ÉCHEC ---',\
                     'A̴b̴a̴n̴d̴o̴n̴ ̴d̴e̴ ̴l̴a̴ ̴p̴a̴r̴t̴i̴e̴ \n▌│█║▌║▌║ Ah tu t\'en vas ? Dommage... Merci d\'avoir essayé.▌│█║▌║▌║\n --- ÉCHEC ---']
    
    file_inserted = argv[1]
    game = parse_game(file_inserted)
    result_after_game_played = play_game(game)
    if result_after_game_played == 2:
        exit(MESSAGES_MAIN[result_after_game_played])
    else:
        print(MESSAGES_MAIN[result_after_game_played])
        
