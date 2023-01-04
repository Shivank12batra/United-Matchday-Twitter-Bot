# importing the necessary libraries
from mplsoccer import Pitch, VerticalPitch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from highlight_text import HighlightText
from matplotlib.colors import LinearSegmentedColormap

def xT_barchart(ax, pass_data):
    # pass_df = pd.read_csv('Villarreal_pass_data.csv')
    current_match = pass_data.copy()
    current_match = current_match[(current_match['type_displayName'] == 'Pass') &
                                  (current_match['outcomeType_displayName'] == 'Successful') & (current_match['teamId'] == 32)]
    xT_grid = pd.read_csv('./data/xTgrid.csv')
    xT_rows, xT_cols = xT_grid.shape
    current_match['x1_bin'] = pd.cut(
        current_match['x'], bins=xT_cols, labels=False)
    current_match['y1_bin'] = pd.cut(
        current_match['y'], bins=xT_rows, labels=False)
    current_match['x2_bin'] = pd.cut(
        current_match['endX'], bins=xT_cols, labels=False)
    current_match['y2_bin'] = pd.cut(
        current_match['endY'], bins=xT_rows, labels=False)
    # func to find the xT value acc to the corresponding row and col

    def func(df, row, col):
        return df.iloc[row, col]

    current_match['start_zone_value'] = current_match.apply(
        lambda x: func(xT_grid, x['y1_bin'], x['x1_bin']), axis=1)
    current_match['end_zone_value'] = current_match.apply(
        lambda x: func(xT_grid, x['y2_bin'], x['x2_bin']), axis=1)
    current_match['xT'] = current_match['end_zone_value'] - \
        current_match['start_zone_value']
    player_xT = current_match.groupby(
        'name').xT.sum().sort_values().reset_index()

    def player_func(x):
        player_split = x.split(' ')
        if len(player_split) == 2:
            x = player_split[0][0] + '.' + player_split[1]
        return x
    player_xT['name'] = player_xT['name'].apply(lambda x: player_func(x))
    # plotting
#     fig, ax = plt.subplots(figsize=(12, 10))
    plt.barh(player_xT['name'], player_xT['xT'], color='red', ec='black')
    spines = ['left', 'right', 'bottom', 'top']
    for spine in spines:
        ax.spines[spine].set_visible(False)
    plt.title('xT of Successful Passes', size=20)
    plt.savefig('xT_barchart_twitter_bot.png', dpi=300, bbox_inches='tight')


def pass_network(pass_data, pitch, ax):
    df = pass_data.copy()
    man_utd = df[df['teamId'] == 32]
    man_utd['passer'] = man_utd['playerId']
    man_utd['recipient'] = man_utd['passer'].shift(-1)
    passes = man_utd[man_utd['type_displayName'] == 'Pass']
    successful = passes[passes['outcomeType_displayName'] == 'Successful']
    subs = man_utd[man_utd['type_displayName'] == 'SubstitutionOff']
    subs = subs['minute']
    firstSub = subs.min()
    successful = successful[successful['minute'] < firstSub]
    shirt_no = pd.to_numeric(successful['shirtNo'], downcast='integer')
    pas = pd.to_numeric(successful['passer'], downcast='integer')
    rec = pd.to_numeric(successful['recipient'], downcast='integer')
    successful['shirtNo'] = shirt_no
    successful['passer'] = pas
    successful['recipient'] = rec
    player_jersey = successful.groupby(['passer', 'shirtNo'])[
        'x'].mean().reset_index()
    player_mapping = {i: k for i, k in zip(
        player_jersey['passer'], player_jersey['shirtNo'])}

    average_locations = successful.groupby('passer').agg(
        {'x': ['mean'], 'y': ['mean', 'count']})
    average_locations.columns = ['x', 'y', 'count']
    df_copy = average_locations.copy()
    df_copy.reset_index(inplace=True)
    df_copy['shirtNo'] = df_copy['passer'].map(player_mapping)
    pass_between = successful.groupby(
        ['passer', 'recipient']).id.count().reset_index()
    pass_between.rename({'id': 'pass_count'}, axis='columns', inplace=True)
    pass_between = pass_between.merge(
        average_locations, left_on='passer', right_index=True)
    pass_between = pass_between.merge(
        average_locations, left_on='recipient', right_index=True, suffixes=['', '_end'])
    pass_between = pass_between[pass_between['pass_count'] > 3]

    # plotting
    arrows = pitch.arrows(pass_between.x, pass_between.y, pass_between.x_end, pass_between.y_end,
                          ax=ax, width=5, headwidth=3, color='blue', zorder=1, alpha=0.8)
    nodes = pitch.scatter(average_locations.x, average_locations.y,
                          s=1000, color='#FF0000', edgecolors='black', linewidth=5, alpha=1, zorder=2, ax=ax)

    for x in range(len(df_copy['passer'])):
        pitch.annotate(text='{}'.format(df_copy['shirtNo'][x]), xy=(df_copy['x'][x], df_copy['y'][x]),
                       ha='center', va='center', c='white', ax=ax, size=10)

#     ax.set_title('Vs {}'.format(opp_team), fontsize=30, color="#082630",
#                              fontfamily = "Century Gothic", fontweight = "bold", va="center", ha="center", pad=15)
    plt.savefig('pass_network_twitter_bot.png', dpi=300, bbox_inches='tight')


def filter_shotmap(df, result, min_val, max_val, shot_type=None, opp_team='N/A', player_name='N/A'):
    data = df.copy()
    data['X'] = data['X']*100
    data['Y'] = data['Y']*100
    if opp_team != 'N/A':
        opp_team_text = f'Against {opp_team}'
        data = data[(data['h_team'] == opp_team) |
                    (data['a_team'] == opp_team)]
    else:
        opp_team_text = ''
    if player_name != 'N/A':
        name_text = player_name
        data = data[data['player'] == player_name]
    else:
        name_text = 'Manchester United'
        team_h = data[(data['h_team'] == 'Manchester United')
                      & (data['h_a'] == 'h')]
        team_a = data[(data['a_team'] == 'Manchester United')
                      & (data['h_a'] == 'a')]
        data = pd.concat([team_h, team_a])
    if result != 'None':
        if result == 'Goal':
            data = data[data['result'] == result]
        else:
            data = data[data['result'] != 'Goal']
    data = data[(data['xG'] >= min_val) & (data['xG'] <= max_val)]
    if shot_type is not None:
        if len(shot_type) == 1:
            data = data[data['shotType'] == shot_type[0]]
        elif len(shot_type) == 2:
            data = data[(data['shotType'] == shot_type[0]) |
                        (data['shotType'] == shot_type[1])]

    return (data, opp_team_text, name_text)


def plot_shotmap(final_df, opposition, name, pitch, ax, show_title=True):
    #         mycolormap = LinearSegmentedColormap.from_list('my colormap', ['#80ffdb', '#7400b8'], N=100)
    mSize = [0.3] * 4
    mSize = [0.3]
    mSizeS = [10000*i for i in mSize]
    mx = [i for i in range(27, 87, 15)]
    my = [66] * 4
    mSize2 = [i for i in np.arange(0.1, 1.1, 0.2)]
    mSizeS2 = [700*i for i in mSize2]
    mx2 = [65, 60, 54, 47, 39]
    my2 = [55] * 5
    outside_text = ['xG/shot', 'shots', 'xG', 'goals']
    xG_text = round(final_df['xG'].sum(), 2)
    xG_shot = round(final_df['xG'].mean(), 2)
    s_text = final_df.shape[0]
    goal_df = final_df[final_df['result'] == 'Goal']

    if not goal_df.empty:
        g_text = goal_df['result'].value_counts()[0]
    else:
        g_text = 0
    inside_text = [g_text, xG_text, s_text, xG_shot]
    rev_inside_text = inside_text[::-1]

    if show_title:
        plt.title(f'{name} Shotmap {opposition}', fontsize=20,
                  fontfamily='serif', fontweight='bold')
    final_df = final_df.reset_index()
    for x in range(len(final_df['xG'])):
        if final_df['result'].iloc[x] == 'Goal':
            c, alpha, ec = '#18E7E1', 0.4, '#18E7E1'
        else:
            c, alpha, ec = '#F9F7FC', 0.6, '#FF008E'
        if final_df['xG'].iloc[x] > 0.5:
            s = 300
        elif 0.3 <= final_df['xG'].iloc[x] >= 0.5:
            s = 225
        elif 0.1 <= final_df['xG'].iloc[x] >= 0.3:
            s = 150
        else:
            s = 75
        print(c, alpha, ec)
        pitch.scatter(final_df['X'][x], final_df['Y'][x],
                      c=c, alpha=alpha, s=s, ec=ec, zorder=3, ax=ax)

    pitch.scatter(my, mx, s=mSizeS, marker='h', color='white',
                  ec='grey', lw=2, alpha=1, ax=ax)
    pitch.scatter(my2, mx2, s=mSizeS2, color='white',
                  ec='black', lw=1, alpha=1, ax=ax)
    ax.text(mx2[0]+4, my2[0], 'low\nquality\nchance', ha='center',
            va='center', c='black', weight='bold', fontfamily='serif', fontsize=10)
    ax.text(mx2[-1]-6, my2[-1], 'high\nquality\nchance', ha='center',
            va='center', c='black', weight='bold', fontfamily='serif', fontsize=10)

    for i in range(len(rev_inside_text)):
        if i == 3:
            c = '#18E7E1'
        else:
            c = 'black'
        ax.text(mx[i], my[i], rev_inside_text[i], ha='center', va='center', c=c,
                fontfamily='serif', weight='bold', fontsize=15)
        ax.text(mx[i], my[i]-5, outside_text[i], ha='center', va='center', c=c,
                fontfamily='serif', weight='bold', fontsize=15)

    plt.savefig('shotmap_twitter_bot.png', dpi=500, bbox_inches='tight')


def calculate_progressive_pass(df):
    df['beginning'] = np.sqrt(np.square(120-df['x']) + np.square(40-df['y']))
    df['end'] = np.sqrt(np.square(120-df['endX']) + np.square(40-df['endY']))
    df.reset_index(inplace=True, drop=True)
    df['progressive'] = [(df['end'][x]) / (df['beginning'][x])
                         < 0.75 for x in range(len(df['beginning']))]
    df = df[df['progressive'] == True].reset_index(drop=True)

    return df


def passplot(df, metric, criteria, plot_type, pitch, ax, outcome='All',
             opp_team='N/A', passer_name='N/A', receiver_name='N/A', show_title=False):
    data = df.copy()
    data['recipient'] = data['name'].shift(-1)
    if outcome != 'All':
        data = data[(data['type_displayName'] == 'Pass') & (
            data['outcomeType_displayName'] == outcome)]
    else:
        data = data[data['type_displayName'] == 'Pass']
    if opp_team != 'N/A':
        data = data[data['match_id'] == opp_team]
    if passer_name != 'N/A' and receiver_name != 'N/A':
        data = data[(data['name'] == passer_name) & (
            data['recipient'] == receiver_name)]
    elif passer_name != 'N/A':
        data = data[data['name'] == passer_name]
    elif receiver_name != 'N/A':
        data = data[data['recipient'] == receiver_name]
    else:
        data = data[data['teamId'] == 32]
    if metric == 'Progressive Passes':
        data = calculate_progressive_pass(data)
    if criteria == 'Starting Location Of Pass':
        heatmap_x, heatmap_y = 'y', 'x'
    elif criteria == 'Ending Location Of Pass':
        heatmap_x, heatmap_y = 'endY', 'endX'
    data.reset_index(inplace=True, drop=True)
    customcmap = LinearSegmentedColormap.from_list('custom cmap',
                                                   ['#fee5d9', '#fc9e80', '#db2824', '#67000d'])
    # plotting
    if plot_type == 'Passmap':
        for i in range(len(data['x'])):
            if data['outcomeType_displayName'][i] == 'Successful':
                pitch.lines(data['x'][i], data['y'][i], data['endX'][i], data['endY'][i],
                            color='green', alpha_start=0.1, alpha_end=0.5, comet=True, ax=ax)
                pitch.scatter(data['endX'][i], data['endY']
                              [i], color='green', ax=ax)
            if data['outcomeType_displayName'][i] == 'Unsuccessful':
                pitch.lines(data['x'][i], data['y'][i], data['endX'][i], data['endY']
                            [i], color='red', alpha_start=0.1, alpha_end=0.5, comet=True, ax=ax)
                pitch.scatter(data['endX'][i], data['endY']
                              [i], color='red', ax=ax)
    elif plot_type == 'Heatmap':
        kde = sns.kdeplot(
            data[heatmap_x], data[heatmap_y], statistic='count',
            cmap=customcmap, shade=True, shade_lowest=False,
            n_levels=400, lw=0.1, alpha=1, zorder=0, ax=ax
        )
        plt.xlim(0, 100)
        plt.ylim(0, 100)
    if show_title:
        plt.title(f'Manchester United Progressive Passes', size=20)
    plt.savefig('passmap_twitter_bot.png', dpi=300, bbox_inches='tight')


def match_summary_dashboard(pass_data, shots_data):
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.axis('off')
    pitch_1 = Pitch(pitch_type='opta', pitch_color='#edece9', line_color='#082630',
                    constrained_layout=True, tight_layout=True, line_zorder=1, linewidth=4.5, spot_scale=0.006)
    ax1 = fig.add_axes((0.1, 0.55, 0.8, 0.5))
    pitch_1.draw(ax=ax1)
    pass_network(pass_data, pitch_1, ax1)
    pitch_2 = VerticalPitch(pitch_type='opta', half=True, pad_bottom=0.5,
                            goal_type='box', goal_alpha=0.8, pitch_color='white', tight_layout=False)
    ax2 = fig.add_axes((0.1, 0.01, 0.8, 0.55))
    pitch_2.draw(ax=ax2)
    h_team = shots_data['h_team'].unique()[0]
    a_team = shots_data['a_team'].unique()[0]
    h_cumxG = round(shots_data.loc[shots_data['h_a'] == 'h', 'xG'].sum(), 2)
    a_cumxG = round(shots_data.loc[shots_data['h_a'] == 'a', 'xG'].sum(), 2)
    if h_team == 'Manchester United':
        h_color, a_color = '#FF0000', '#0D19A7'
    else:
        h_color, a_color = '#0D19A7', '#FF0000'
    df, opp_name_text, name_text = filter_shotmap(
        shots_data, 'None', 0, 1, opp_team=a_team)
    plot_shotmap(df, opp_name_text, name_text, pitch_2, ax2, show_title=False)
    ax3 = fig.add_axes((0.9, 0.8, 0.4, 0.5))
    xT_barchart(ax3, pass_data)
    pitch_3 = VerticalPitch(pitch_type='opta', pad_bottom=0.5, goal_type='box',
                            goal_alpha=0.8, pitch_color='white', tight_layout=False)
    ax4 = fig.add_axes((0.75, 0.01, 0.6, 0.7))
    pitch_3.draw(ax=ax4)
    passplot(pass_data, 'Progressive Passes', 'Starting Location Of Pass',
             'Passmap', pitch_3, ax4, outcome='Successful', show_title=True)
    ax.text(0.05, 1.55, 'MATCHDAY DASHBOARD', fontsize=45,
            fontfamily='serif', c='grey', fontweight='bold')
    HighlightText(0.05, 1.5, f'<{h_team}>({h_cumxG})\nVS\n<{a_team}>({a_cumxG})', size=35, fontweight='bold',
                  fontfamily='serif', highlight_textprops=[{'color': f'{h_color}'}, {'color': f'{a_color}'}], ax=ax)
    # ax.text(-0.15, 1.55, 'GAME SHOTS SIMULATION', fontsize=29, fontfamily='serif', c='grey', fontweight='bold')
    plt.savefig('images/match_summary_dashboard_twitter_bot.png',
                dpi=300, bbox_inches='tight')
