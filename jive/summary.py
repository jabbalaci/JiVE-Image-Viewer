def to_save(lst):
    return sum(1 for img in lst if img.to_save)

def to_delete(lst):
    return sum(1 for img in lst if img.to_delete)

def to_wallpaper(lst):
    return sum(1 for img in lst if img.to_wallpaper)