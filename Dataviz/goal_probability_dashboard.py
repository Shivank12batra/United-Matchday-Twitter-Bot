import pandas as pd
import numpy as np
import random
from collections import Counter
import matplotlib.pyplot as plt
from highlight_text import HighlightText

def determine_goals(shots):
    goals = 0
    for shot in shots:
        if random.random() <= shot:
            goals += 1
    return goals

def determine_winner(h_team, a_team):
    h_goals = determine_goals(h_team)
    a_goals = determine_goals(a_team)
    
    if h_goals > a_goals:
        return ('Home Win', h_goals, a_goals)
    
    elif a_goals > h_goals:
        return ('Away Win', h_goals, a_goals)
    
    else:
        return ('Draw', h_goals, a_goals)

def match_simulator(h_team, a_team):
    home_win = 0
    away_win = 0
    draw = 0
    home_goals = []
    away_goals = []
    scoreline = []
    
    for i in range(10000):
        result, home_goal, away_goal = determine_winner(h_team, a_team)
        if result == 'Home Win':
            home_win += 1
        elif result == 'Away Win':
            away_win += 1
        else:
            draw += 1
        home_goals.append(home_goal)
        away_goals.append(away_goal)
        scoreline.append(f'{home_goal}-{away_goal}')
            
    home_win_prct = round((home_win/10000)*100, 2)
    away_win_prct = round((away_win/10000)*100, 2)
    draw_prct = round((draw/10000)*100, 2)
    return (home_win_prct, away_win_prct, draw_prct, home_goals, away_goals, scoreline)

def goal_probability_plot(goals, ax, team_name, team_color):
    goals_count = Counter(goals)
    goals_count = {i: k for i, k in sorted(goals_count.items(), key=lambda x:x[0])}
    goal_number = goals_count.keys()
    goal_number = list(map(str, goal_number))
    count = goals_count.values()
    prob = [(i/sum(count)*100) for i in count]
    
    #Plotting
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.bar(goal_number, prob, color=team_color, ec='black')
    plt.ylabel('Probability', fontweight='bold', fontfamily='serif', fontsize=15)
    ax.set_xticklabels(goal_number, fontweight='bold', fontsize=13)
    m = plt.yticks()[0]
    m = [round(i) for i in m]
    new_m = [f'{i}%' for i in m]
    ax.set_yticklabels(new_m, fontweight='bold', fontsize=13)
    text = [f'{round(x, 2)}%' for x in prob]
    for x, y, txt in zip(goal_number, prob, text):
        plt.text(x, y+0.5, txt, fontweight='bold', ha='center')
    max_num = max(prob)
    if m[1] - m[0] <= 5: 
        x_text = -1
        y_text = max(prob) + 4
    else:
        x_text = -0.6
        y_text = max(prob) + 8
    plt.text(x_text, y_text, f'{team_name} Goal Probability Distribution', fontweight='bold', fontfamily='serif', fontsize=20)

def horizontal_bar(away, draw, home, ax, h_team, a_team, a_color, h_color):
    x = [a_team, 'Draw', h_team]
    p = list((away, draw, home))
    txt = list(map(str, p))
    txt = [f'{i}%' for i in txt]
    ax.set_yticklabels(x, fontweight='bold', fontsize=13)
    plt.barh(x, p, color=[a_color, 'black', h_color], ec='black')
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    m = plt.xticks()[0]
    m = [round(i) for i in m]
    new_m = [f'{i}%' for i in m]
    ax.set_xticklabels(new_m, fontweight='bold', fontsize=12)
    for i, y, t in zip(p, x, txt):
        plt.text(i+0.5, y, t, fontweight='bold')
    plt.text(0, 2.6, 'Result Probability', fontweight='bold', fontfamily='serif', fontsize=18)

def scoreline_probability(scorelines, actual):
    s2 = Counter(scorelines)
    s2 = {i:k for i, k in sorted(s2.items(), key=lambda x: x[1], reverse=True)}
    most_likely = list(s2.keys())[0]
    total = sum(list(s2.values()))
    most_likely_prct = round(s2[most_likely]/total*100, 2)
    if actual == most_likely:
        return (most_likely, most_likely_prct, actual)
    actual_prct = round(s2[actual]/total*100, 2)
    actual_rank = list(s2.keys()).index(actual) + 1
    print(most_likely)
    print(most_likely_prct)
    print(actual)
    print(actual_prct)
    print(actual_rank)
    return (most_likely, most_likely_prct, actual, actual_prct, actual_rank)

def goal_probability_dashboard(shots_data):
    match_df = shots_data.copy()
    match_df.reset_index(inplace=True, drop=True)
    home_df = match_df[match_df['h_a'] == 'h']
    away_df = match_df[match_df['h_a'] == 'a']
    home_shots = home_df['xG'].tolist()
    away_shots = away_df['xG'].tolist()
    # team names
    h_team = match_df['h_team'].unique()[0]
    a_team = match_df['a_team'].unique()[0]
    # cumulative xG calculation
    h_cumxG = round(match_df.loc[match_df['h_a']=='h', 'xG'].sum(), 2)
    a_cumxG = round(match_df.loc[match_df['h_a']=='a', 'xG'].sum(), 2)
    home_goals = match_df['h_goals'].unique()[0]
    away_goals = match_df['a_goals'].unique()[0]
    actual_scoreline = f'{home_goals}-{away_goals}'
    h2, a2, d2, r3, r4, s1 = match_simulator(home_shots, away_shots)
    final = scoreline_probability(s1, actual_scoreline)
    if h_team == 'Manchester United':
        h_color, a_color = '#FF0000', '#0D19A7'
    else:
        h_color, a_color = '#0D19A7', '#FF0000'
    
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')
    fig.set_facecolor('#FDF9F9')
    ax1 = fig.add_axes((0.1, 0.5, 0.9, 0.4))
    goal_probability_plot(r3, ax1, h_team, h_color)
    ax2 = fig.add_axes((0.1, 0.01, 0.9, 0.4))
    goal_probability_plot(r4, ax2, a_team, a_color)
    ax3 = fig.add_axes((0.6, 1, 0.4, 0.3))
    horizontal_bar(a2, d2, h2, ax3, h_team, a_team, a_color, h_color)
    
    ax.text(-0.15, 1.55, 'GAME SHOTS SIMULATION', fontsize=29, fontfamily='serif', c='grey', fontweight='bold')
    HighlightText(-0.15, 1.5, f'<{h_team.upper()}> ({h_cumxG} xG)  \nVS \n<{a_team.upper()}> ({a_cumxG} xG)', size=18, fontweight='bold',
                  fontfamily='serif', highlight_textprops=[{'color':f'{h_color}'}, {'color':f'{a_color}'}], ax=ax)
    HighlightText(-0.15, 1.25, f'Most probable scoreline: <{final[0]} ({final[1]}%)>', size=16, fontweight='bold',
                 fontfamily='serif', highlight_textprops=[{'color':'grey'}], ax=ax)
    if len(final) == 5:
        text = f'(Rank {final[-1]})'
        HighlightText(-0.15, 1.2, f'Actual scoreline: <{final[2]} ({final[3]}%) {text}>', size=16, fontweight='bold', fontfamily='serif', highlight_textprops=[{'color':'grey'}], ax=ax)
    else:
        text = ''
        HighlightText(-0.15, 1.2, f'Actual scoreline: <{final[2]} ({final[1]}%) {text}>', size=16, fontweight='bold', fontfamily='serif', highlight_textprops=[{'color':'grey'}], ax=ax)
    print(final)
    plt.savefig('images/goal_probability_dashboard_twitter_bot.png', dpi=300, bbox_inches='tight')