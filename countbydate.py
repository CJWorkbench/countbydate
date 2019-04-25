def render(wf_module, table):
    col = wf_module.get('column')
    sortby = wf_module.get('sortby')
    groupby = wf_module.get('groupby')

    group_options = [
        "%Y-%m-%dT%H:%M:%SZ",  # Seconds
        "%Y-%m-%dT%H:%MZ",  # Minutes
        "%Y-%m-%dT%H:00Z",  # Hours
        "%Y-%m-%d",  # Days
        "%Y-%m",  # Months
        lambda d: "%d Q%d" % (d.year, d.quarter),  # Quarters
        "%Y",  # Years
    ]

    if not col:
        wf_module.set_error('Please select a column containing dates')
        return table

    if table is None:
        return None

    if col not in table.columns:
        return ('There is no column named %s' % col)

    # integer columns, just... no. Never really want to interpret as seconds since 1970
    if table[col].dtype == 'int64':
        return ('Column %s does not seem to be dates' % col)

    # convert the date column to actual datetimes
    try:
        table[col] = pd.to_datetime(table[col])
    except (ValueError, TypeError):
        return ('Column %s does not seem to be dates' % col)

    if table[col].dtype == 'int64':
        return ('Column %s does not seem to be dates' % col)

    if groupby is 5:  # Group by quarter
        table['groupcol'] = table[col].apply(group_options[groupby])
    else:
        table['groupcol'] = table[col].dt.strftime(group_options[groupby])

    newtab = pd.DataFrame(table.groupby(table['groupcol']).size())

    newtab.reset_index(level=0, inplace=True)  # turn index into a column, or we can't see the column names
    newtab.columns = ['date', 'count']

    if sortby != 1:  # Sort by frequency
        newtab = newtab.sort_values('date')
    else:
        newtab = newtab.sort_values('count')

    return newtab
