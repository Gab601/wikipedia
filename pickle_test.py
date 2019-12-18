import pprint, pickle

try:
    pkl_file = open('data.pkl', 'rb')
    data1 = pickle.load(pkl_file)
    pprint.pprint(data1[3])
    pkl_file.close()
except:
    print("file not found")
