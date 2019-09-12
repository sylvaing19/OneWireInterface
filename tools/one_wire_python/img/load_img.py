from os.path import dirname, abspath, join

def img(img_name):
    img_dir = dirname(abspath(__file__))
    return join(img_dir, img_name)
