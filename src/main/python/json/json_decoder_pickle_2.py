import pickle

class CustomUnpickler(pickle.Unpickler):

    def find_class(self, module, name):
        try:
            return super().find_class(__name__, name)
        except AttributeError:
            print("error")
            return super().find_class(module, name)

pickle_data = CustomUnpickler(open('item_data.pkl', 'rb')).load()
print(pickle_data)
