import pickle

class Item(object):
    def __init__(self, name):
        self.name = name

def main():
    foo = Item('Camera')
    with open('item_data.pkl', 'wb') as f:
        pickle.dump([foo], f, -1)

if __name__=='__main__':
    main()
