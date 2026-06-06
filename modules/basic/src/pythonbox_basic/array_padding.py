import numpy as np
arr = np.array([4, 7, 2, 4, 3])
arr1 = np.pad(arr, (3, 2), 'constant', constant_values=(0,10000))
print(arr1)

print('------')

arr_1 = np.array([4, 7, 2, 4, 3])
arr2 = np.pad(arr_1, (3), 'constant', constant_values=(0))
print(arr2)


a = np.empty(10)
a.fill(7)
print(a)

b = [1, 2]

print(list(a) + b)
