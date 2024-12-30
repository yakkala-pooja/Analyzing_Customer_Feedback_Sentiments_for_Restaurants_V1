# Import the libraries
from flask import Flask, render_template, request
from keras.models import load_model
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import tensorflow as tf
import pickle
global graph
graph = tf.compat.v1.get_default_graph()
ps = PorterStemmer()

# Load the saved model
with open(r'cv.pkl', 'rb') as file:
    cv = pickle.load(file)

app = Flask(__name__, template_folder="templates")


@app.route('/')
def welcome():
    return render_template('home.html', name="Home")


@app.route('/predict', methods=['GET', 'POST'])
def pred():
    if request.method == 'POST':
        review = request.form['message']
        review = re.sub('[^a-zA-Z]', ' ', review)
        review = review.lower()
        review = review.split()
        review = [ps.stem(word) for word in review if not word in set(stopwords.words('en'))]
        review = ' '.join(review)
        review = cv.transform([review]).toarray()
        with graph.as_default():
            model = load_model("zomato_analysis.h5", compile=False)
            y_p = model.predict(review)
        print(y_p)
        if y_p.argmax() == 0:
            output = "Average"
        elif y_p.argmax() == 1:
            output = "Good"
        else:
            output = "Poor"
        return render_template('prediction.html', prediction=output)
    else:
        return render_template('prediction.html')


@app.route('/about')
def about():
    return render_template('project.html')


if __name__ == '__main__':
    app.run(host='localhost', port=9000, debug=True, threaded=False)
