from Dependices import *

pygame.init()

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(APP_NAME)

label_font = pygame.font.Font('fonts/Roboto-Bold.ttf', 32)
medium_text = pygame.font.Font('fonts/Roboto-Bold.ttf', 24)

beats = 8
instruments = 6
bpm = 239

active_len = 0
active_beat = 0

timer = pygame.time.Clock()

boxes_list = []
active_list = [True for _ in range(instruments)]
clicked_list = [[False for _ in range(beats)] for _ in range(instruments)]
playing = True
run = True
beat_changed = True

idx = 100

save_menu = False
load_menu = False

file = open('saved_beats.txt', 'r')
saved_beats = list(file)
pygame.mixer.set_num_channels(instruments * 5)

# loading sounds
hi_hat = mixer.Sound('sounds/hi hat.WAV')
snare = mixer.Sound('sounds/snare.WAV')
kick = mixer.Sound('sounds/kick.WAV')
crash = mixer.Sound('sounds/crash.wav')
clap = mixer.Sound('sounds/clap.wav')
floor_tom = mixer.Sound('sounds/tom.WAV')

sound_and_sound_name_list = [
    [hi_hat, 'Hi Hat'],
    [snare, 'Snare'],
    [kick, 'Base Drum'],
    [crash, 'Crash'],
    [clap, 'Clap'],
    [floor_tom, 'Floor Tom']
]

beat_name = ''
typing = False


def play_notes():
    for i, clicked in enumerate(clicked_list):
        if clicked[active_beat] and active_list[i] == 1:
            sound = sound_and_sound_name_list[i][0]
            sound.play()


def draw_sound_name_and_separators(actives):
    # Drawing separators
    pygame.draw.rect(screen, Colors.GRAY, [0, 0, 200, Constants.HEIGHT - 200], 5)  # left separator
    pygame.draw.rect(screen, Colors.GRAY, [0, Constants.HEIGHT - 200, Constants.WIDTH, 200], 5)  # bottom separator

    for i in range(instruments):
        start_pos = (0, (i * 100) + 100)
        end_pos = (200, (i * 100) + 100)

        pygame.draw.line(
            screen,
            WHITE,
            start_pos,
            end_pos,
            3
        )

    # Drawing sound name
    for idx, sound_and_sound_name in enumerate(sound_and_sound_name_list):
        color = WHITE if actives[idx] == 1 else GRAY
        sound_name = sound_and_sound_name[1]
        pos = (30, 30 + idx * 100)

        text = label_font.render(sound_name, True, color)
        screen.blit(text, pos)


def draw_grid(clicks, beat, actives):
    resultList = []

    draw_sound_name_and_separators(actives)

    for i in range(beats):
        for j in range(instruments):
            if not clicks[j][i]:
                color = Colors.GRAY
            else:
                color = GREEN if actives[j] else DARK_GRAY

            start_x = i * (Constants.WIDTH - 200) // beats + 200
            end_x = ((Constants.WIDTH - 200) // beats)

            start_y = (j * 100)
            end_y = ((Constants.HEIGHT - 200) / instruments)

            rectCoordinates = [
                start_x,
                start_y,
                end_x,
                end_y
            ]

            resultList.append((
                pygame.draw.rect(screen, color, [start_x + 5, start_y + 5, end_x - 10, end_y - 10], 0, 3),
                (i, j))
            )

            pygame.draw.rect(screen, GOLD, rectCoordinates, 5, 5)

            pygame.draw.rect(screen, BLACK, rectCoordinates, 2, 5)

        # Drawing active beat rect
        pygame.draw.rect(
            screen, BLUE,
            [beat * ((WIDTH - 200) // beats) + 200, 2, ((WIDTH - 200) // beats), instruments * 100 - 2],
            5,
            3
        )

    return resultList


def draw_play_pause_button():
    text = 'PAUSE' if playing else 'PLAY'
    play_pause = pygame.draw.rect(screen, GRAY, [50, HEIGHT - 135, 200, 60], 0, 5)
    play_text = label_font.render(text, True, WHITE)

    if playing:
        screen.blit(play_text, (play_text.get_width() - 3, HEIGHT - 125))
    else:
        screen.blit(play_text, (play_text.get_width() + 25, HEIGHT - 125))

    return play_pause


def draw_bpm_controller():
    pygame.draw.rect(
        screen,
        GRAY,
        [300, HEIGHT - 150, 200, 100],
        5,
        5
    )
    bpm_text = medium_text.render('Beats Per Minute', True, WHITE)
    screen.blit(bpm_text, (308, HEIGHT - 142))

    bpm_int = label_font.render(f'{bpm}', True, WHITE)
    screen.blit(bpm_int, (370, HEIGHT - 100))

    bpm_add_rect = pygame.draw.rect(screen, GRAY, [510, HEIGHT - 150, 45, 45], 0, 7)
    bpm_add_text = medium_text.render('+5', True, WHITE)

    bpm_sub_rect = pygame.draw.rect(screen, GRAY, [510, HEIGHT - 100, 45, 45], 0, 7)
    bpm_sub_text = medium_text.render('-5', True, WHITE)

    screen.blit(bpm_add_text, (520, HEIGHT - 140))
    screen.blit(bpm_sub_text, (520, HEIGHT - 90))

    return bpm_add_rect, bpm_sub_rect


def draw_beats_controller():
    beats_rect = pygame.draw.rect(
        screen,
        GRAY,
        [600, HEIGHT - 150, 200, 100],
        5,
        5
    )
    beats_text = medium_text.render('Beats In Loop', True, WHITE)
    screen.blit(beats_text, (627, HEIGHT - 142))

    beats_int = label_font.render(f'{beats}', True, WHITE)
    screen.blit(beats_int, (688, HEIGHT - 100))

    beats_add_rect = pygame.draw.rect(screen, GRAY, [810, HEIGHT - 150, 45, 45], 0, 7)
    beats_add_text = medium_text.render('+1', True, WHITE)

    beats_sub_rect = pygame.draw.rect(screen, GRAY, [810, HEIGHT - 100, 45, 45], 0, 7)
    beats_sub_text = medium_text.render('-1', True, WHITE)

    screen.blit(beats_add_text, (820, HEIGHT - 140))
    screen.blit(beats_sub_text, (820, HEIGHT - 90))

    return beats_add_rect, beats_sub_rect


def draw_save_and_load_button():
    save_rect = pygame.draw.rect(screen, GRAY, [900, HEIGHT - 150, 200, 48], 0, 5)
    save_text = label_font.render('Save Beat', True, WHITE)
    screen.blit(save_text, (930, HEIGHT - 145))

    load_rect = pygame.draw.rect(screen, GRAY, [900, HEIGHT - 95, 200, 48], 0, 5)
    load_text = label_font.render('Load Beat', True, WHITE)
    screen.blit(load_text, (930, HEIGHT - 90))

    return save_rect, load_rect


def draw_clear_board():
    clear_board_rec = pygame.draw.rect(screen, GRAY, [1150, HEIGHT - 135, 200, 60], 0, 5)
    clear_board_text = label_font.render('Clear Board', True, WHITE)
    screen.blit(clear_board_text, (1168, HEIGHT - 126))

    return clear_board_rec


def draw_save_menu(beat_name, typing):
    pygame.draw.rect(screen, BLACK, [0, 0, WIDTH, HEIGHT], 0, 0)

    menu_text = label_font.render('SAVE MENU: Enter a Name for Current Beat', True, WHITE)
    screen.blit(menu_text, (400, 40))

    saving_button = pygame.draw.rect(screen, GRAY, [WIDTH // 2 - 200, HEIGHT * 0.75, 400, 100], 0, 5)
    saving_txt = label_font.render('Save beat', True, WHITE)

    screen.blit(saving_txt, (WIDTH // 2 - 70, HEIGHT * 0.75 + 30))

    exit_btn = pygame.draw.rect(screen, GRAY, [WIDTH - 170, HEIGHT - 76, 100, 60], 0, 5)
    exit_text = label_font.render('Close', True, WHITE)
    screen.blit(exit_text, (WIDTH - 160, HEIGHT - 65))

    if typing:
        pygame.draw.rect(screen, DARK_GRAY, [445, 200, 600, 200], 0, 5)

    entry_rect = pygame.draw.rect(screen, GRAY, [445, 200, 600, 200], 5, 5)
    entry_text = label_font.render(f'{beat_name}', True, WHITE)
    screen.blit(entry_text, (475, 250))

    return exit_btn, saving_button, entry_rect


def draw_load_menu(idx):
    loaded_clicked = []
    loaded_beat = 0
    loaded_bpm = 0
    pygame.draw.rect(screen, BLACK, [0, 0, WIDTH, HEIGHT], 0, 0)

    menu_text = label_font.render('LOAD MENU: Select a Beat To Load', True, WHITE)
    screen.blit(menu_text, (400, 40))

    loading_btn = pygame.draw.rect(screen, GRAY, [WIDTH // 2 - 100, HEIGHT * 0.9, 200, 50], 0, 5)
    loading_txt = label_font.render('Load beat', True, WHITE)

    screen.blit(loading_txt, (WIDTH // 2 - 70, HEIGHT * 0.87 + 30))

    # Check there is a diff between this WIDTH // 2 - 400 and this (WIDTH // 2) - 400
    delete_btn = pygame.draw.rect(screen, GRAY, [(WIDTH // 2) - 500, HEIGHT * 0.9, 200, 50], 0, 5)
    delete_txt = label_font.render('Delete Beat', True, WHITE)
    screen.blit(delete_txt, ((WIDTH // 2) - 485, HEIGHT * 0.87 + 30))

    exit_btn = pygame.draw.rect(screen, GRAY, [WIDTH - 170, HEIGHT - 76, 100, 60], 0, 5)
    exit_text = label_font.render('Close', True, WHITE)
    screen.blit(exit_text, (WIDTH - 160, HEIGHT - 65))

    loaded_rect = pygame.draw.rect(screen, GRAY, [180, 90, 1000, 600], 5, 5)

    if 0 <= idx < len(saved_beats):
        pygame.draw.rect(screen, LIGHT_GRAY, [190, 100 + idx * 50, 980, 30], 0, 100)

    for beat in range(len(saved_beats)):
        if len(saved_beats[beat]) == 1:
            continue
        if beat < 10:
            beat_clicked = []
            row_text = medium_text.render(f'{beat + 1}', True, WHITE)
            screen.blit(row_text, (200, 100 + beat * 50))
            name_index_start = saved_beats[beat].index('name: ') + 6
            name_index_end = saved_beats[beat].index(', beats:')

            name_text = medium_text.render(f'{saved_beats[beat][name_index_start:name_index_end]}', True, WHITE)
            screen.blit(name_text, (240, 100 + beat * 50))
        if 0 <= idx < len(saved_beats) and beat == idx:
            beat_index_end = saved_beats[beat].index(', bpm: ')
            loaded_beat = int(saved_beats[beat][name_index_end + 8 : beat_index_end])
            bpm_index_end = saved_beats[beat].index(', selected: ')
            loaded_bpm = int(saved_beats[beat][beat_index_end + 6 : bpm_index_end])
            loaded_clicks_string =  saved_beats[beat][bpm_index_end + 14 : -3]
            loded_clicks_rows = list(loaded_clicks_string.split('], ['))

            for row in range(len(loded_clicks_rows)):
                loded_clicks_row = (loded_clicks_rows[row].split(', '))

                for item in range(len(loded_clicks_row)):
                    if loded_clicks_row[item] == 'True' or loded_clicks_row[item] == 'False':
                        loded_clicks_row[item] = True if (loded_clicks_row[item] == 'True') else False

                beat_clicked.append(loded_clicks_row)
                loaded_clicked = beat_clicked

    loaded_info = [loaded_beat, loaded_bpm, loaded_clicked]

    return exit_btn, loading_btn, delete_btn, loaded_rect, loaded_clicked, loaded_info


while run:
    timer.tick(Constants.FPS)
    screen.fill(Colors.BLACK)

    play_pause_button = draw_play_pause_button()

    bpm_add_rect, bpm_sub_rect = draw_bpm_controller()
    beats_add_rect, beats_sub_rect = draw_beats_controller()

    boxes_list = draw_grid(clicked_list, active_beat, active_list)

    # instruments rects
    instruments_rects = []

    for i in range(instruments):
        rect = pygame.rect.Rect((0, i * 100), (200, 100))
        instruments_rects.append(rect)

    save_rect, load_rect = draw_save_and_load_button()
    clear_board_rec = draw_clear_board()

    if save_menu:
        exit_rect, saving_button, entry_rect = draw_save_menu(beat_name, typing)
    elif load_menu:
        exit_rect, loading_button, delete_btn, loaded_rect, loaded_clicked, loaded_info = draw_load_menu(idx)

    if beat_changed:
        play_notes()
        beat_changed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not save_menu and not load_menu:
            for box in boxes_list:
                rect = box[0]

                if rect.collidepoint(event.pos):
                    i, j = box[1]

                    clicked_list[j][i] = not clicked_list[j][i]
        elif event.type == pygame.MOUSEBUTTONUP and not save_menu and not load_menu:
            if play_pause_button.collidepoint(event.pos):
                playing = not playing
            elif bpm_add_rect.collidepoint(event.pos):
                bpm += 5
            elif bpm_sub_rect.collidepoint(event.pos):
                bpm -= 5
            elif beats_add_rect.collidepoint(event.pos):
                beats += 1

                for clicked in clicked_list:
                    clicked.append(False)

            elif beats_sub_rect.collidepoint(event.pos):
                beats -= 1

                for clicked in clicked_list:
                    if len(clicked) > 2:
                        clicked.pop(-1)
                    else:
                        beats += 1
                        break
            elif clear_board_rec.collidepoint(event.pos):
                clicked_list = [[False for _ in range(beats)] for _ in range(instruments)]
            elif save_rect.collidepoint(event.pos):
                save_menu = True
            elif load_rect.collidepoint(event.pos):
                load_menu = True

            for index, instrument in enumerate(instruments_rects):
                if instrument.collidepoint(event.pos):
                    active_list[index] = not active_list[index]
        elif event.type == pygame.MOUSEBUTTONUP:
            if exit_rect.collidepoint(event.pos):
                save_menu = False
                load_menu = False
                playing = True
                beat_name = ''
                typing = False
            elif load_menu and loaded_rect.collidepoint(event.pos):
                idx = (event.pos[1] - 100) // 50

            elif save_menu and entry_rect.collidepoint(event.pos):
                typing = not typing
            elif save_menu and saving_button.collidepoint(event.pos):
                with open('saved_beats.txt', 'w') as file:
                    saved_beats.append(f'\nname: {beat_name}, beats: {beats}, bpm: {bpm}, selected: {clicked_list}')

                    for i in range(len(saved_beats)):
                        file.write(str(saved_beats[i]))
                save_menu = False
                typing = False
                beat_name = ''
            elif load_menu and delete_btn.collidepoint(event.pos):
                if 0 <= idx < len(saved_beats):
                    saved_beats.pop(idx)
            elif load_menu and loading_button.collidepoint(event.pos):
                if 0 <= idx < len(saved_beats):
                    beats = loaded_info[0]
                    bpm = loaded_info[1]
                    clicked_list = loaded_info[2]
                    index = 100
                    load_menu = False
        elif event.type == pygame.TEXTINPUT and typing:
            beat_name += event.text
        elif event.type == pygame.KEYDOWN and not save_menu and not load_menu:
            if event.key == pygame.K_SPACE:
                playing = not playing
            elif event.key == pygame.K_s:
                save_menu = True
            elif event.key == pygame.K_l:
                load_menu = True
        elif event.type == pygame.KEYDOWN and save_menu:
            if event.key == pygame.K_BACKSPACE and len(beat_name) > 0 and typing:
                beat_name = beat_name[:-1]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if save_menu or load_menu:
                    save_menu = False
                    load_menu = False
                    playing = True
                    beat_name = ''
                    typing = False
                else:
                    run = False


    beat_length = (FPS * 60) // bpm

    if playing:
        if active_len < beat_length:
            active_len += 1
        else:
            active_len = 0

            if active_beat < beats - 1:
                active_beat += 1
            else:
                active_beat = 0

            beat_changed = True
    pygame.display.flip()
pygame.quit()
