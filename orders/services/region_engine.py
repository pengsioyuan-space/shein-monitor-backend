
def region(shop):
    eu = ['DE','FR','IT','ES','NL']
    us = ['US']
    ca = ['CA']
    if shop in eu: return 'EU'
    if shop in us: return 'US'
    if shop in ca: return 'CA'
    return 'OTHER'
