import pickle
import pandas as pd


movies_dict = pickle.load(open('movie_dict.pkl','rb'))

movies = pd.DataFrame(movies_dict)

print(movies.head())
print(movies.columns)