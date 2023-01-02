def xT_barchart(ax, pass_data):
    #pass_df = pd.read_csv('Villarreal_pass_data.csv')
    current_match = pass_data.copy()
    current_match = current_match[(current_match['type_displayName'] == 'Pass') & \
                    (current_match['outcomeType_displayName'] == 'Successful') & (current_match['teamId'] == 32)]
    xT_grid = pd.read_csv('xTgrid.csv')
    xT_rows, xT_cols = xT_grid.shape
    current_match['x1_bin'] = pd.cut(current_match['x'], bins=xT_cols, labels=False)
    current_match['y1_bin'] = pd.cut(current_match['y'], bins=xT_rows, labels=False)
    current_match['x2_bin'] = pd.cut(current_match['endX'], bins=xT_cols, labels=False)
    current_match['y2_bin'] = pd.cut(current_match['endY'], bins=xT_rows, labels=False)
    #func to find the xT value acc to the corresponding row and col
    def func(df, row, col):
        return df.iloc[row, col]
    
    current_match['start_zone_value'] = current_match.apply(lambda x: func(xT_grid, x['y1_bin'], x['x1_bin']), axis=1)
    current_match['end_zone_value'] = current_match.apply(lambda x: func(xT_grid, x['y2_bin'], x['x2_bin']), axis=1)
    current_match['xT'] = current_match['end_zone_value'] - current_match['start_zone_value']
    player_xT = current_match.groupby('name').xT.sum().sort_values().reset_index()
    def player_func(x):
        player_split = x.split(' ') 
        if len(player_split) == 2:
            x = player_split[0][0] + '.' + player_split[1]
        return x
    player_xT['name'] = player_xT['name'].apply(lambda x: player_func(x))
    #plotting
#     fig, ax = plt.subplots(figsize=(12, 10))
    plt.barh(player_xT['name'], player_xT['xT'], color='red', ec='black')
    spines = ['left', 'right', 'bottom', 'top']
    for spine in spines:
        ax.spines[spine].set_visible(False)
    plt.title('xT of Successful Passes', size=20)
    plt.savefig('xT_barchart_twitter_bot.png', dpi=300, bbox_inches='tight')