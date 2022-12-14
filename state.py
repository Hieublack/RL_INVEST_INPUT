import pandas as pd
import math
import numpy as np
import heapq
from scipy.stats.mstats import gmean, hmean
import numba as nb
import random

index_test = np.load('index_test.npy', allow_pickle=True)
PROFIT = np.load('list_profit.npy', allow_pickle=True)
COMPANY = np.load('list_company.npy', allow_pickle=True)
data_arr = np.load('data.npy', allow_pickle=True)


NUMBER_VARIABLE = len(data_arr)
TOP_COMP_PER_QUARTER = 20
NUMBER_QUARTER_HISTORY = 24
ALL_QUARTER = len(index_test) - 1



def get_rank_not_invest():
    list_rank_ko_dau_tu = []
    for j in range(len(index_test)-1, 0, -1):
        # profit_q = PROFIT[index_test[j-1]:index_test[j]]
        COMP = COMPANY[index_test[j-1]:index_test[j]]
        list_rank_ko_dau_tu.append(np.where(COMP == 'NOT_INVEST')[0][0]+1)
    return np.array(list_rank_ko_dau_tu)

LIST_RANK_NOT_INVEST = get_rank_not_invest()

LIST_PROFIT_CT1 = np.zeros(ALL_QUARTER)
LIST_PROFIT_CT2 = np.zeros(ALL_QUARTER)

def save_data():
    np.save('index_test.npy', index_test)
    np.save('data.npy', data_arr)
    np.save('list_rank_profit_not_invest.npy', LIST_RANK_NOT_INVEST)
    np.save('list_company.npy', COMPANY)

# save_data()

@nb.njit()
def get_in4_fomula(result_fomula, list_rank_not_invest_temp):
    list_top_comp = np.array([-1])
    list_rank_not_invest_ct = np.array([-1])
    list_comp_ct = np.array([-1])
    for j in range(len(index_test)-1, 0, -1):
        top2 = heapq.nlargest(2,result_fomula[index_test[j-1]:index_test[j]])         #lấy top 2 giá trị lớn nhất
        if top2[0] == top2[1] or np.max(result_fomula[index_test[j-1]:index_test[j]]) == np.min(result_fomula[index_test[j-1]:index_test[j]]):
            # print('toang cong thuc', top2, np.max(result_fomula[index_test[j-1]:index_test[j]]), np.min(result_fomula[index_test[j-1]:index_test[j]]))
            return np.array([-1]), np.array([-1]), 0, list_comp_ct
        rank_thuc = np.argsort(-result_fomula[index_test[j-1]:index_test[j]]) + 1
        list_comp_ct = np.append(list_comp_ct, index_test[j-1] + np.argmax(result_fomula[index_test[j-1]:index_test[j]]))
        id_not_invest = LIST_RANK_NOT_INVEST[-j] 
        if list_rank_not_invest_ct[0] == -1:
            list_rank_not_invest_ct = np.array([np.where(rank_thuc == id_not_invest)[0][0]+1])
            list_top_comp = rank_thuc[:TOP_COMP_PER_QUARTER]
        else:
            list_rank_not_invest_ct = np.append(list_rank_not_invest_ct, np.where(rank_thuc == id_not_invest)[0][0]+1)
            list_top_comp = np.append(list_top_comp, rank_thuc[:TOP_COMP_PER_QUARTER])
    list_rank_not_invest_temp = list_rank_not_invest_ct
    list_comp_ct = list_comp_ct[1:]
    return list_top_comp, list_rank_not_invest_temp, 1, list_comp_ct

IN4_CT1_INDEX = 0
IN4_CT2_INDEX = ALL_QUARTER*TOP_COMP_PER_QUARTER
HISTORY_AGENT_INDEX= IN4_CT2_INDEX + ALL_QUARTER*TOP_COMP_PER_QUARTER
HISTORY_SYS_BOT_INDEX = HISTORY_AGENT_INDEX + ALL_QUARTER
HISTORY_PROFIT_AGENT = HISTORY_SYS_BOT_INDEX + ALL_QUARTER
ID_NOT_INVEST_CT1 = HISTORY_PROFIT_AGENT + ALL_QUARTER
ID_NOT_INVEST_CT2 = ID_NOT_INVEST_CT1 + 1
CURRENT_QUARTER_INDEX = ID_NOT_INVEST_CT2 + 1
ID_ACTION_INDEX = CURRENT_QUARTER_INDEX + 1
CHECK_END_INDEX = ID_ACTION_INDEX + 1
NUMBER_COMP_INDEX = CHECK_END_INDEX + 1
LEVEL_RATIO_INDEX = NUMBER_COMP_INDEX + 1

P_IN4_CT1 = 0
P_IN4_CT2 = P_IN4_CT1 + TOP_COMP_PER_QUARTER*NUMBER_QUARTER_HISTORY
P_GMEAN_P1 = P_IN4_CT2 + TOP_COMP_PER_QUARTER*NUMBER_QUARTER_HISTORY
P_GMEAN_P2 = P_GMEAN_P1 + 1
P_ID_NOT_INVEST_CT1 = P_GMEAN_P2 + 1
P_ID_NOT_INVEST_CT2 = P_ID_NOT_INVEST_CT1 + 1
P_NUMBER_COMP_INDEX = P_ID_NOT_INVEST_CT2 + 1
P_CURRENT_QUARTER_INDEX = P_NUMBER_COMP_INDEX + 1
P_LEVEL_RATIO_INDEX = P_CURRENT_QUARTER_INDEX + 1

# @nb.njit()
def reset(ALL_IN4_SYS, LIST_ALL_COMP_PER_QUARTER):
    # global LIST_RANK_CT1, LIST_RANK_CT2, LIST_PROFIT_CT2, LIST_RANK_NOT_INVEST_CT1, LIST_RANK_NOT_INVEST_CT2
    '''
    Hàm này trả ra 2 công thức và list top20 comp qua từng quý của công thức và các thông tin cần thiết khác
    '''
    LIST_RANK_CT1 = np.zeros(ALL_QUARTER)
    LIST_RANK_CT2 = np.zeros(ALL_QUARTER)
    # list_fomula = []
    # result_fomula = np.zeros(data_arr.shape[1])
    count_fomula = 0
    while count_fomula < 2:
        result_fomula = create_fomula(data_arr)
        LIST_RANK_NOT_INVEST_TEMP = np.zeros(ALL_QUARTER)
        temp, LIST_RANK_NOT_INVEST_TEMP, check, list_comp_ct = get_in4_fomula(result_fomula, LIST_RANK_NOT_INVEST_TEMP)
        # print('check getin4', len(temp), check, result_fomula[:10], temp[:10])
        # print('TEMP, ', LIST_RANK_NOT_INVEST_TEMP[:10])
        count_fomula += check
        if count_fomula == 1 and check == 1:
            LIST_RANK_CT1 = temp.copy()
            # ALL_IN4_SYS[1] = temp.copy()
            # LIST_RANK_NOT_INVEST_CT1 = LIST_RANK_NOT_INVEST_TEMP.copy()
            ALL_IN4_SYS[1] = LIST_RANK_NOT_INVEST_TEMP.copy() 
            ALL_IN4_SYS[3] = list_comp_ct.copy()
            # list_fomula.append(fomula)
        elif count_fomula == 2 and check == 1:
            LIST_RANK_CT2 = temp.copy()
            # ALL_IN4_SYS[3] = temp.copy()
            # LIST_RANK_NOT_INVEST_CT2 = LIST_RANK_NOT_INVEST_TEMP.copy()
            ALL_IN4_SYS[2] = LIST_RANK_NOT_INVEST_TEMP.copy() 
            ALL_IN4_SYS[4] = list_comp_ct.copy()

            # list_fomula.append(fomula)

    id_not_invest_ct1 = ALL_IN4_SYS[1][0]
    id_not_invest_ct2 = ALL_IN4_SYS[2][0]
    current_quarter = 0
    id_action = 0
    check_end_game = 0
    history_agent = np.zeros(ALL_QUARTER*3)
    number_comp = LIST_ALL_COMP_PER_QUARTER[0]
    level_ratio = 0
    # LIST_RANK_CT1, LIST_PROFIT_CT1 = get_in4_fomula(list_fomula[0])
    # LIST_RANK_CT2, LIST_PROFIT_CT2 = get_in4_fomula(list_fomula[1])
    env_state = np.concatenate((LIST_RANK_CT1, LIST_RANK_CT2, history_agent, np.array([id_not_invest_ct1, id_not_invest_ct2, current_quarter, id_action, check_end_game, number_comp, level_ratio])))
    return env_state, ALL_IN4_SYS

@nb.njit()
def create_fomula(data_arr):
    power = np.random.randint(1, 10)
    operand = np.random.randint(1, 10)
    result_fomula = np.zeros(data_arr.shape[1])
    # ct = []
    for i in range(operand):
        op = np.random.randint(2)
        # ct.append(op)
        numerator = np.random.randint(power, NUMBER_VARIABLE - 1 - power)
        denominator = numerator - power
        numer_var = np.random.randint(1, NUMBER_VARIABLE, numerator)
        result_temp = np.zeros(data_arr.shape[1])+1
        if denominator > 0:
            all_var = np.arange(1,NUMBER_VARIABLE)
            for id in range(len(all_var)):
                if all_var[id] in numer_var:
                    all_var[id] = 0
            all_denom_var = all_var[all_var > 0]
            if len(all_denom_var) < denominator:
                all_denom_var = np.append(all_denom_var, np.random.choice(all_var, denominator - len(all_denom_var)))
            denom_var = np.random.choice(all_denom_var, denominator)
            denom_var = np.append(denom_var, np.zeros(numerator-denominator).astype(np.int64))
            denom_var = denom_var.astype(np.int64)
            # ct.append([list(numer_var), list(denom_var)])
            for idx in range(len(numer_var)):
                num = data_arr[numer_var[idx]]
                denom = data_arr[denom_var[idx]]
                denom_zero = np.where(denom == 0)[0]
                denom[denom_zero] = 1
                num[denom_zero] = 1
                result_temp =  result_temp*(num/denom)
        else:
            denom_var = np.zeros(numerator).astype(np.int64)
            # ct.append([list(numer_var), list(denom_var)])
            for id in range(len(numer_var)):
                num = data_arr[numer_var[id]]
                denom = data_arr[denom_var[id]]
                denom_zero = np.where(denom == 0)[0]
                denom[denom_zero] = 1
                num[denom_zero] = 1
                result_temp =  result_temp*(num/denom)
        if op == 1:
            result_fomula = result_fomula + result_temp
        else:
            result_fomula = result_fomula - result_temp
    return result_fomula

@nb.njit()
def state_to_player(env_state):
    '''
    Hàm này trả ra lịch sử kết quả của 2 công thức trong các quý trước đó
    '''
    id_action = env_state[ID_ACTION_INDEX]
    player_state = np.zeros(2*NUMBER_QUARTER_HISTORY*TOP_COMP_PER_QUARTER + 7)
    player_state[P_ID_NOT_INVEST_CT1] = env_state[ID_NOT_INVEST_CT1]
    player_state[P_ID_NOT_INVEST_CT2] = env_state[ID_NOT_INVEST_CT2]
    if env_state[CURRENT_QUARTER_INDEX] != 0:
        history_ct1 = env_state[max(IN4_CT1_INDEX, TOP_COMP_PER_QUARTER*(env_state[CURRENT_QUARTER_INDEX]-NUMBER_QUARTER_HISTORY)):int(env_state[CURRENT_QUARTER_INDEX]*TOP_COMP_PER_QUARTER)]
        history_ct2 = env_state[max(IN4_CT2_INDEX, TOP_COMP_PER_QUARTER*(env_state[CURRENT_QUARTER_INDEX]-NUMBER_QUARTER_HISTORY)+IN4_CT2_INDEX):int(env_state[CURRENT_QUARTER_INDEX]*TOP_COMP_PER_QUARTER)+IN4_CT2_INDEX]
        len_bonus = int(TOP_COMP_PER_QUARTER * (NUMBER_QUARTER_HISTORY - env_state[CURRENT_QUARTER_INDEX]))
        if len_bonus > 0:
            a = np.zeros(len_bonus)
            history_ct1 = np.append(a, history_ct1)
            history_ct2 = np.append(a, history_ct2)
        player_state[P_IN4_CT1:P_IN4_CT2] = history_ct1
        player_state[P_IN4_CT2:P_GMEAN_P1] = history_ct2
    agent_history = env_state[HISTORY_AGENT_INDEX : HISTORY_AGENT_INDEX+ALL_QUARTER][:int(env_state[CURRENT_QUARTER_INDEX])]
    sys_bot_history = env_state[HISTORY_SYS_BOT_INDEX : HISTORY_SYS_BOT_INDEX+ALL_QUARTER][:int(env_state[CURRENT_QUARTER_INDEX])]
    if env_state[CHECK_END_INDEX] == 1:
        if id_action == 0:
            player_state[P_GMEAN_P1] = np.exp(np.mean(np.log(agent_history)))
            player_state[P_GMEAN_P2] = np.exp(np.mean(np.log(sys_bot_history)))
        else:
            player_state[P_GMEAN_P1] = np.exp(np.mean(np.log(sys_bot_history)))
            player_state[P_GMEAN_P2] = np.exp(np.mean(np.log(agent_history)))
    player_state[P_CURRENT_QUARTER_INDEX] = env_state[CURRENT_QUARTER_INDEX]
    player_state[P_LEVEL_RATIO_INDEX] = env_state[LEVEL_RATIO_INDEX]
    player_state[P_NUMBER_COMP_INDEX] = env_state[NUMBER_COMP_INDEX]
    return player_state

# @nb.njit()
def step(action, env_state, ALL_IN4_SYS, LIST_ALL_COMP_PER_QUARTER):
    # print('action step: ', action, int(env_state[CURRENT_QUARTER_INDEX]), ALL_IN4_SYS)
    # if action == 1:
    #     print(ALL_IN4_SYS[3][int(env_state[CURRENT_QUARTER_INDEX])], COMPANY[int(ALL_IN4_SYS[4][int(env_state[CURRENT_QUARTER_INDEX])])])
    # elif action == 2:
    #     print(ALL_IN4_SYS[4][int(env_state[CURRENT_QUARTER_INDEX])], COMPANY[int(ALL_IN4_SYS[4][int(env_state[CURRENT_QUARTER_INDEX])])])

    id_action = env_state[ID_ACTION_INDEX]
    result_quarter = 0
    if action == 0:
        result_quarter = ALL_IN4_SYS[0][int(env_state[CURRENT_QUARTER_INDEX])]
        # env_state[int(HISTORY_PROFIT_AGENT+env_state[CURRENT_QUARTER_INDEX])] = 1
    elif action == 1:
        result_quarter = env_state[int(env_state[CURRENT_QUARTER_INDEX]*TOP_COMP_PER_QUARTER)]
        # env_state[int(HISTORY_PROFIT_AGENT+env_state[CURRENT_QUARTER_INDEX])] = LIST_PROFIT_CT1[int(env_state[CURRENT_QUARTER_INDEX])]
    else:
        result_quarter = env_state[int(env_state[CURRENT_QUARTER_INDEX]*TOP_COMP_PER_QUARTER+IN4_CT2_INDEX)]
        # env_state[int(HISTORY_PROFIT_AGENT+env_state[CURRENT_QUARTER_INDEX])] = LIST_PROFIT_CT2[int(env_state[CURRENT_QUARTER_INDEX])]
    if result_quarter == 0:
        # print('toang',action,  env_state[int(env_state[CURRENT_QUARTER_INDEX]*TOP_COMP_PER_QUARTER+IN4_CT2_INDEX)], np.min(LIST_RANK_CT2))
        raise Exception('toang action')
    rank_3_action = np.array([LIST_RANK_NOT_INVEST[int(env_state[CURRENT_QUARTER_INDEX])], env_state[int(env_state[CURRENT_QUARTER_INDEX]*TOP_COMP_PER_QUARTER)], env_state[int(env_state[CURRENT_QUARTER_INDEX]*TOP_COMP_PER_QUARTER+IN4_CT2_INDEX)]])
    rank_3_action = np.sort(rank_3_action)
    top_action = np.where(rank_3_action == result_quarter)[0][0] + 1
    # print('quarter', int(env_state[CURRENT_QUARTER_INDEX]),'check', 1/top_action, 'action', action, 'topaction',rank_3_action)
    env_state[int(HISTORY_AGENT_INDEX + ALL_QUARTER*id_action +env_state[CURRENT_QUARTER_INDEX])] = (4-top_action)/3

    if env_state[ID_ACTION_INDEX] == 0 and env_state[CURRENT_QUARTER_INDEX] == ALL_QUARTER-1:
        if action == 0:
            print('Không đầu tư quý này')
        else:
            print('Đầu tư công ty ', COMPANY[int(ALL_IN4_SYS[int(2 + action)][int(env_state[CURRENT_QUARTER_INDEX])])], ALL_IN4_SYS[int(2 + action)][int(env_state[CURRENT_QUARTER_INDEX])])



    if env_state[ID_ACTION_INDEX] == 1:
        env_state[CURRENT_QUARTER_INDEX] += 1  
        #rank giá trị công thức của việc không đầu tư
        if env_state[CURRENT_QUARTER_INDEX] < ALL_QUARTER:
            env_state[ID_NOT_INVEST_CT1] = ALL_IN4_SYS[1][int(env_state[CURRENT_QUARTER_INDEX])]
            env_state[ID_NOT_INVEST_CT2] = ALL_IN4_SYS[2][int(env_state[CURRENT_QUARTER_INDEX])]
        env_state[NUMBER_COMP_INDEX] = LIST_ALL_COMP_PER_QUARTER[int(env_state[CURRENT_QUARTER_INDEX])]
        env_state[ID_ACTION_INDEX] = 0
    else:
        env_state[ID_ACTION_INDEX] = 1

    return env_state

def action_player(env_state, list_player, temp_file, per_file):
    player_state = state_to_player(env_state)
    current_player = int(env_state[ID_ACTION_INDEX])
    played_move,temp_file,per_file = list_player[current_player](player_state, temp_file, per_file)
    if played_move not in [0, 1, 2]:
        raise Exception('Action false')
    return played_move,temp_file, per_file
    
@nb.njit()
def check_winner(env_state):
    agent_history = env_state[HISTORY_AGENT_INDEX : HISTORY_AGENT_INDEX+ALL_QUARTER]
    sys_bot_history = env_state[HISTORY_SYS_BOT_INDEX : HISTORY_SYS_BOT_INDEX+ALL_QUARTER]
    np.exp(np.mean(np.log(sys_bot_history)))
    if np.exp(np.mean(np.log(agent_history))) > np.exp(np.mean(np.log(sys_bot_history))): return 0
    else: return 1

@nb.njit()
def check_victory(player_state):
    if not (player_state[P_GMEAN_P1] == player_state[P_GMEAN_P2] and player_state[P_GMEAN_P2] == 0):
        if player_state[P_GMEAN_P1] > player_state[P_GMEAN_P2]: return 1
        else: return 0
    else: return -1

def one_game(list_player, temp_file, per_file, LIST_RANK_NOT_INVEST, LIST_ALL_COMP_PER_QUARTER):
    ALL_IN4_SYS = np.array([LIST_RANK_NOT_INVEST, np.zeros(ALL_QUARTER), np.zeros(ALL_QUARTER)])
    env_state, ALL_IN4_SYS = reset(ALL_IN4_SYS, LIST_ALL_COMP_PER_QUARTER)
    count_turn = 0
    while count_turn < ALL_QUARTER*2:
        action, temp_file, per_file = action_player(env_state, list_player, temp_file, per_file)
        env_state = step(action, env_state, ALL_IN4_SYS, LIST_ALL_COMP_PER_QUARTER)
        count_turn += 1
    env_state[CHECK_END_INDEX] = 1
    for id_player in range(len(list_player)):
        action, temp_file, per_file = action_player(env_state,list_player,temp_file, per_file)
        env_state[ID_ACTION_INDEX] = (env_state[ID_ACTION_INDEX] + 1)%len(list_player)
    result = check_winner(env_state)
    # print(env_state[HISTORY_AGENT_INDEX:])
    return result, per_file

def normal_main(agent_player, times, per_file):
    global data_arr
    count = np.zeros(2)
    # all_id_fomula = np.arange(len(all_fomula))
    list_player = [agent_player, player_random]
    LIST_RANK_NOT_INVEST = get_rank_not_invest()
    LIST_ALL_COMP_PER_QUARTER = []
    for j in range(len(index_test)-1, 0, -1):
        LIST_ALL_COMP_PER_QUARTER.append(index_test[j] - index_test[j-1])
    LIST_ALL_COMP_PER_QUARTER.append(LIST_ALL_COMP_PER_QUARTER[-1])
    LIST_ALL_COMP_PER_QUARTER = np.array(LIST_ALL_COMP_PER_QUARTER)
    for van in range(times):
        temp_file = [[0],[0]]
        # shuffle = np.random.choice(all_id_fomula, 2, replace=False)
        # list_fomula = all_fomula[shuffle]
        winner, file_per = one_game(list_player, temp_file, per_file, LIST_RANK_NOT_INVEST, LIST_ALL_COMP_PER_QUARTER)
        if winner == 0:
            count[0] += 1
        else:
            count[1] += 1
    return count, file_per

def player_random1(player_state, temp_file, per_file):
    list_action = np.array([0,1,2])
    action = int(np.random.choice(list_action))
    # print('check: ', player_state[P_ID_NOT_INVEST_CT1], player_state[P_ID_NOT_INVEST_CT2])
    check = check_victory(player_state)

    return action, temp_file, per_file

def player_random(player_state, temp_file, per_file):
    list_action = np.array([0,1,2])
    action = int(np.random.choice(list_action))
    # check = check_victory(player_state)
    return action, temp_file, per_file

def player_input(player_state, temp_file, per_file):
    # list_action = np.array([0,1,2])
    print(f'Tổng số công ty trong quý hiện tại: {player_state[P_NUMBER_COMP_INDEX]}')
    print('Xếp hạng giá trị hành động không đầu tư của 2 công thức: ', player_state[P_ID_NOT_INVEST_CT1], player_state[P_ID_NOT_INVEST_CT2])
    print('Xếp hạng lợi nhuận 20 công ty hàng đầu của CT1 tại quý trước: ', player_state[P_IN4_CT2-TOP_COMP_PER_QUARTER : P_IN4_CT2])
    print('Xếp hạng lợi nhuận 20 công ty hàng đầu của CT2 tại quý trước:: ', player_state[P_GMEAN_P1-TOP_COMP_PER_QUARTER : P_GMEAN_P1])
    action = -1
    while action not in [0,1,2]:
        try:
            action = int(input('Nhập action của bạn(0 là ko đầu tư, 1 là theo CT1, 2 là theo CT2): ',) )
        except:
            action = -1
    print(f'Người chơi action {action}')
    # print('check: ', player_state[P_ID_NOT_INVEST_CT1], player_state[P_ID_NOT_INVEST_CT2])
    check = check_victory_level(player_state)
    if check != -1:
        if check == 1:
            print(f'Thắng: {player_state[P_GMEAN_P1]}')
        else:
            print(f'Thua: {player_state[P_GMEAN_P1]}')

    return action, temp_file, per_file


@nb.njit()
def check_winner_level(env_state):
    agent_history = env_state[HISTORY_AGENT_INDEX : HISTORY_AGENT_INDEX+ALL_QUARTER]
    sys_bot_history = env_state[HISTORY_SYS_BOT_INDEX : HISTORY_SYS_BOT_INDEX+ALL_QUARTER]
    np.exp(np.mean(np.log(sys_bot_history)))
    level_ratio = env_state[LEVEL_RATIO_INDEX]
    if np.exp(np.mean(np.log(agent_history))) > level_ratio: return 0
    else: return 1

@nb.njit()
def check_victory_level(player_state):
    if not (player_state[P_GMEAN_P1] == player_state[P_GMEAN_P2] and player_state[P_GMEAN_P2] == 0):
        if player_state[P_GMEAN_P1] > player_state[P_LEVEL_RATIO_INDEX]: return 1
        else: return 0
    else: return -1

def one_game_level(list_player, temp_file, per_file, LIST_RANK_NOT_INVEST, LEVEL, LIST_ALL_COMP_PER_QUARTER):
    ALL_IN4_SYS = np.array([LIST_RANK_NOT_INVEST, np.zeros(ALL_QUARTER), np.zeros(ALL_QUARTER), np.zeros(ALL_QUARTER), np.zeros(ALL_QUARTER)])
    env_state, ALL_IN4_SYS = reset(ALL_IN4_SYS, LIST_ALL_COMP_PER_QUARTER)
    env_state[LEVEL_RATIO_INDEX] = LEVEL
    count_turn = 0
    while count_turn < ALL_QUARTER*2:
        action, temp_file, per_file = action_player(env_state, list_player, temp_file, per_file)
        env_state = step(action, env_state, ALL_IN4_SYS, LIST_ALL_COMP_PER_QUARTER)
        count_turn += 1
    env_state[CHECK_END_INDEX] = 1
    for id_player in range(len(list_player)):
        action, temp_file, per_file = action_player(env_state,list_player,temp_file, per_file)
        env_state[ID_ACTION_INDEX] = (env_state[ID_ACTION_INDEX] + 1)%len(list_player)
    result = check_winner_level(env_state)
    # print(env_state[HISTORY_AGENT_INDEX:])
    return result, per_file

ALL_LEVEL = np.array([0.6, 0.7, 0.8, 0.9])


def normal_main_level1(agent_player, times, per_file):
    global data_arr
    count = np.zeros(2)
    # all_id_fomula = np.arange(len(all_fomula))
    list_player = [agent_player, player_random]
    LIST_RANK_NOT_INVEST = get_rank_not_invest()
    LEVEL = 0.6
    LIST_ALL_COMP_PER_QUARTER = []
    for j in range(len(index_test)-1, 0, -1):
        LIST_ALL_COMP_PER_QUARTER.append(index_test[j] - index_test[j-1])
    LIST_ALL_COMP_PER_QUARTER.append(LIST_ALL_COMP_PER_QUARTER[-1])
    LIST_ALL_COMP_PER_QUARTER = np.array(LIST_ALL_COMP_PER_QUARTER)
    for van in range(times):
        temp_file = [[0],[0]]
        # shuffle = np.random.choice(all_id_fomula, 2, replace=False)
        # list_fomula = all_fomula[shuffle]
        winner, file_per = one_game_level(list_player, temp_file, per_file, LIST_RANK_NOT_INVEST, LEVEL, LIST_ALL_COMP_PER_QUARTER)
        if winner == 0:
            count[0] += 1
        else:
            count[1] += 1
    return count, file_per

def normal_main_level2(agent_player, times, per_file):
    global data_arr
    count = np.zeros(2)
    # all_id_fomula = np.arange(len(all_fomula))
    list_player = [agent_player, player_random]
    LIST_RANK_NOT_INVEST = get_rank_not_invest()
    LEVEL = 0.7
    LIST_ALL_COMP_PER_QUARTER = []
    for j in range(len(index_test)-1, 0, -1):
        LIST_ALL_COMP_PER_QUARTER.append(index_test[j] - index_test[j-1])
    LIST_ALL_COMP_PER_QUARTER.append(LIST_ALL_COMP_PER_QUARTER[-1])
    LIST_ALL_COMP_PER_QUARTER = np.array(LIST_ALL_COMP_PER_QUARTER)
    for van in range(times):
        temp_file = [[0],[0]]
        # shuffle = np.random.choice(all_id_fomula, 2, replace=False)
        # list_fomula = all_fomula[shuffle]
        winner, file_per = one_game_level(list_player, temp_file, per_file, LIST_RANK_NOT_INVEST, LEVEL, LIST_ALL_COMP_PER_QUARTER)
        if winner == 0:
            count[0] += 1
        else:
            count[1] += 1
    return count, file_per

def normal_main_level3(agent_player, times, per_file):
    global data_arr
    count = np.zeros(2)
    # all_id_fomula = np.arange(len(all_fomula))
    list_player = [agent_player, player_random]
    LIST_RANK_NOT_INVEST = get_rank_not_invest()
    LEVEL = 0.8
    LIST_ALL_COMP_PER_QUARTER = []
    for j in range(len(index_test)-1, 0, -1):
        LIST_ALL_COMP_PER_QUARTER.append(index_test[j] - index_test[j-1])
    LIST_ALL_COMP_PER_QUARTER.append(LIST_ALL_COMP_PER_QUARTER[-1])
    LIST_ALL_COMP_PER_QUARTER = np.array(LIST_ALL_COMP_PER_QUARTER)
    for van in range(times):
        temp_file = [[0],[0]]
        # shuffle = np.random.choice(all_id_fomula, 2, replace=False)
        # list_fomula = all_fomula[shuffle]
        winner, file_per = one_game_level(list_player, temp_file, per_file, LIST_RANK_NOT_INVEST, LEVEL, LIST_ALL_COMP_PER_QUARTER)
        if winner == 0:
            count[0] += 1
        else:
            count[1] += 1
    return count, file_per

def normal_main_level4(agent_player, times, per_file):
    global data_arr
    count = np.zeros(2)
    # all_id_fomula = np.arange(len(all_fomula))
    list_player = [agent_player, player_random]
    LIST_RANK_NOT_INVEST = get_rank_not_invest()
    LEVEL = 0.9
    LIST_ALL_COMP_PER_QUARTER = []
    for j in range(len(index_test)-1, 0, -1):
        LIST_ALL_COMP_PER_QUARTER.append(index_test[j] - index_test[j-1])
    LIST_ALL_COMP_PER_QUARTER.append(LIST_ALL_COMP_PER_QUARTER[-1])
    LIST_ALL_COMP_PER_QUARTER = np.array(LIST_ALL_COMP_PER_QUARTER)
    for van in range(times):
        temp_file = [[0],[0]]
        # shuffle = np.random.choice(all_id_fomula, 2, replace=False)
        # list_fomula = all_fomula[shuffle]
        winner, file_per = one_game_level(list_player, temp_file, per_file, LIST_RANK_NOT_INVEST, LEVEL, LIST_ALL_COMP_PER_QUARTER)
        if winner == 0:
            count[0] += 1
        else:
            count[1] += 1
    return count, file_per




