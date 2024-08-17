season_name = {1:'Winter', 2:'Frühling', 3:'Sommer', 4:'Herbst'}

def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return 1
    elif month in [3, 4, 5]:
        return 2
    elif month in [6, 7, 8]:
        return 3
    elif month in [9, 10, 11]:
        return 4