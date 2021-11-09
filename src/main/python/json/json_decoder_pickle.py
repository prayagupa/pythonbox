import pickle

import json_encoder_pickle

if __name__=='__main__':
    json_encoder_pickle.main()
    with open('item_data.pkl', 'rb') as f:
        items = pickle.load(f)
        print(str(items))

