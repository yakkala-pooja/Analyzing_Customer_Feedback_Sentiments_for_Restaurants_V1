# Importing Libraries
import numpy as np
import pandas as pd
import re
# Import NLTK libraries
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import CountVectorizer
import pickle
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense

# Importing and Reading the Dataset
dataset = pd.read_csv("DataSet/zomato.csv")
data_review = dataset['reviews_list']

# Printing data_review
# print(data_review)

# Splitting the data into Reviews and Ratings
x = []
y = []
for row in range(0, 51716):
    lst = data_review[row].split("('")
    for i in lst:
        if len(i) > 5:
            if i.find("',") != -1:
                single_rev = i.split("',")
                if len(single_rev[0]) > 2:
                    x.append(single_rev[0])
                if len(single_rev[1]) > 2:
                    y.append(single_rev[1])

# Printing X and Y
# print(x)
# print(y)

# Preprocessing 1
ps = PorterStemmer()

# To store the final rating
rating_final = []
# To store cleaned reviews
review_final = []

# Preprocessing for Ratings
for loop in range(0, 40000):
    data_x = x[loop]
    data_x = re.sub('[a-zA-Z]', " ", data_x)
    data_x = data_x.split()
    data_x = ''.join(data_x)
    data_x = float(data_x)
    if data_x < 2.5:
        rating_final.append("poor")
    elif 2.5 <= data_x <= 3.5:
        rating_final.append("average")
    elif data_x > 3.5:
        rating_final.append("good")
# print(rating_final)

# Preprocessing for Reviews
le = LabelEncoder()
rating_final = le.fit_transform(rating_final)
# print(rating_final)
# Convert rating_final from one dimensional array to two-dimensional array
rating_final = np.array(rating_final)
rating_final = np.expand_dims(rating_final, axis=1)
# print(rating_final)
# Convert the integer encoding to binary values

one = OneHotEncoder()
rates = one.fit_transform(rating_final).toarray()
# print(rates)

# Stemming and removing unnecessary stop words
for loop in range(0, 40000):
    data_y = y[loop]
    data_y = re.sub('[^a-zA-Z]', " ", data_y)
    data_y = data_y.lower()
    data_y = data_y.split()
    data_y = [ps.stem(word) for word in data_y if not word in set(stopwords.words('en'))]
    data_y = ' '.join(data_y)
    review_final.append(data_y)
# print(review_final)

# Bag of words
cv = CountVectorizer(max_features=20000)
x_final = cv.fit_transform(review_final).toarray()

# Saving the 'vectorizer' which will be used as dictionary
pickle.dump(cv, open('cv.pkl', 'wb'))

# Split the data into test and train sets
x_train, x_test, y_train, y_test = train_test_split(x_final, rates, test_size=0.2, random_state=0)

# Model Building
model = Sequential()
model.add(Dense(units=13264, kernel_initializer='random_uniform', activation='relu'))
model.add(Dense(units=2000, kernel_initializer='random_uniform', activation='relu'))
model.add(Dense(units=2000, kernel_initializer='random_uniform', activation='relu'))
model.add(Dense(units=2000, kernel_initializer='random_uniform', activation='relu'))
model.add(Dense(units=3, kernel_initializer='random_uniform', activation='softmax'))
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, batch_size=128, epochs=200)

# Testing the prediction
y_pred = model.predict(x_test)
text = "The food is okay. Average place"
text = re.sub('[^a-zA-Z]', " ", text)
text = text.lower()
text = text.split()
text = [ps.stem(word) for word in text if not word in set(stopwords.words('en'))]
text = ' '.join(text)
y_p = model.predict(cv.transform([text]))
# print(y_p)

# Saving the model
model.save("zomato_analysis.h5")
