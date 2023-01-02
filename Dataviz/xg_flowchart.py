# importing the necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
from highlight_text import HighlightText

# function to calculate cumulative xG accumlated
def nums_cumulative_sum(nums_list):
    return [sum(nums_list[:i+1]) for i in range(len(nums_list))]


def xG_flowchart(shots_data):
    shot_df = shots_data.copy()
    shot_df['X'] = pd.to_numeric(shot_df['X'])
    shot_df['Y'] = pd.to_numeric(shot_df['Y'])
    shot_df['xG'] = pd.to_numeric(shot_df['xG'])
    shot_df['minute'] = pd.to_numeric(shot_df['minute'])
    shot_df.reset_index(inplace=True, drop=True)
    a_xG = [0]
    h_xG = [0]
    a_min = [0]
    h_min = [0]
    h_result = ['Nil']
    a_result = ['Nil']
    add_xG = 0.000001
    add_min = 100
    hteam = shot_df['h_team'].iloc[0]
    ateam = shot_df['a_team'].iloc[0]

    if hteam == 'Manchester United':
        h_color, a_color = '#FF0000', '#0D19A7'
    else:
        h_color, a_color = '#0D19A7', '#FF0000'

    for x in range(len(shot_df['xG'])):
        if shot_df['h_a'][x] == 'a':
            a_xG.append(shot_df['xG'][x])
            a_min.append(shot_df['minute'][x])
            a_result.append(shot_df['result'][x])
        if shot_df['h_a'][x] == 'h':
            h_xG.append(shot_df['xG'][x])
            h_min.append(shot_df['minute'][x])
            h_result.append(shot_df['result'][x])

    a_xG.append(add_xG)
    h_xG.append(add_xG)
    a_min.append(add_min)
    h_min.append(add_min)
    a_result.append('Nil')
    h_result.append('Nil')
    a_cumulative = nums_cumulative_sum(a_xG)
    h_cumulative = nums_cumulative_sum(h_xG)
    a_combined = list(zip(a_result, a_cumulative))
    h_combined = list(zip(h_result, h_cumulative))
    h_ind = [ind for ind, pair in enumerate(h_combined) if 'Goal' in pair]
    a_ind = [ind for ind, pair in enumerate(a_combined) if 'Goal' in pair]
    # this is used to find the total xG. It just creates a new variable from the last item in the cumulative list
    alast = round(a_cumulative[-1], 2)
    hlast = round(h_cumulative[-1], 2)
    # max of the two teams cumulative xG
    gmax = max(alast, hlast)
    # y coordinate of the text to go inside highlighted title text
    htext = gmax+(gmax*0.4)
    text_1 = gmax+(gmax*0.3)
    text_2 = gmax+(gmax*0.25)
    if 0 <= gmax <= 1:
        text_3 = -0.3
    elif 1 <= gmax <= 2:
        text_3 = -0.6
    elif 2 <= gmax <= 3:
        text_3 = -0.8
    else:
        text_3 = -1
#     text_3 =
    # calculating confidence intervals: -+15%
    home_upper = [(xG+(xG*0.15)) for xG in h_cumulative]
    home_lower = [(xG-(xG*0.15)) for xG in h_cumulative]
    away_upper = [(xG+(xG*0.15)) for xG in a_cumulative]
    away_lower = [(xG-(xG*0.15)) for xG in a_cumulative]
    hupper_last = round(home_upper[-1], 2)
    aupper_last = round(away_upper[-1], 2)
    hlower_last = round(home_lower[-1], 2)
    alower_last = round(away_lower[-1], 2)
    # plotting
    fig, ax = plt.subplots(figsize=(18, 12))
    fig.set_facecolor('#FAFAFA')
    ax.patch.set_facecolor('#FAFAFA')
    spines = ['top', 'right', 'left', 'bottom']
    for spine in spines:
        ax.spines[spine].set_visible(False)
    plt.xticks([0, 15, 30, 45, 60, 75, 90])
    plt.xlabel('Minute', color='black', fontsize=15,
               labelpad=15, fontfamily='serif')
    plt.ylabel('Expected Goals (xG)', color='black',
               fontsize=15, labelpad=15, fontfamily='serif')
    ax.tick_params(axis='both', colors='black')
    ax.grid(linestyle='dashed', lw=0.7, which='major', alpha=1)

    ax.step(x=a_min, y=a_cumulative, color=a_color,
            label=ateam, linewidth=3, where='post', zorder=2)
    ax.step(x=h_min, y=h_cumulative, color=h_color,
            label=hteam, linewidth=3, where='post', zorder=2)
    for i in a_ind:
        ax.scatter(x=a_min[i], y=a_cumulative[i], marker="*",
                   s=500, c='#DBE708', ec='black', zorder=3)
    for i in h_ind:
        ax.scatter(x=h_min[i], y=h_cumulative[i], marker="*",
                   s=500, c='#DBE708', ec='black', zorder=3)
    HighlightText(-8, htext, f'<{hteam}> {len(h_ind)}-{len(a_ind)} <{ateam}>', size=35, fontweight='bold', fontfamily='serif',
                  highlight_textprops=[{'color': f'{h_color}'}, {'color': f'{a_color}'}], ax=ax)
    ax.text(-8, text_1, f'{hteam} {hlast} xG ({hupper_last}xG-{hlower_last}xG)',
            size=20, fontfamily='serif')
    ax.text(-7, text_2, f'{ateam} {alast} xG ({aupper_last}xG-{alower_last}xG)',
            size=20, fontfamily='serif')
    ax.text(-8, text_3, 'Shaded area represents the 90% Confidence Interval of the "true"\n expected goals value for each shot(+/-15%)',
            size=17, fontfamily='serif')
    ax.text(90, -0.4, '@prstrggr', size=17,
            fontweight='bold', fontfamily='serif')
    ax.fill_between(x=h_min, y1=home_upper, y2=home_lower,
                    step='post', color=h_color, alpha=0.1)
    ax.fill_between(x=a_min, y1=away_upper, y2=away_lower,
                    step='post', color=a_color, alpha=0.1)
    plt.savefig('xG_flowchart_twitter_bot.png', dpi=500, bbox_inches='tight')
#     ax.scatter(92, -0.5, marker="*", s=500, c='#DBE708', ec='black')
