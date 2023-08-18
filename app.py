from flask import Flask, render_template, request
import pandas as pd
import numpy as np 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

app = Flask(__name__)

# Load data and fit model
data = pd.read_excel('F:\College\Data Science\SEM4\Machine Learning\Leaning\combined_file.xlsx')
text_data = data['Description'].values.astype('U')
vectorizer = TfidfVectorizer()
text_vectors = vectorizer.fit_transform(text_data)
dense_vectors = text_vectors.toarray()
vector_1 = pd.DataFrame(dense_vectors, index=data.index)
final_data = pd.concat([data, vector_1], axis=1)
X = final_data[list(vector_1.columns)]
X = X.astype(str)
X.columns = X.columns.astype(str)
kmeans = KMeans(n_clusters=2, random_state=0)
kmeans.fit(X)
final_data['cluster'] = kmeans.labels_

# Define function to get recommendations
def recommender(description: str, state: str):
    tfvector = vectorizer.transform(np.array([description]))
    review_class = kmeans.predict(tfvector)[0]
    clean = final_data.loc[(final_data.cluster == review_class) & (final_data.State == state)]
    result = clean[['Title', "Rating", 'State']].sort_values(by="Rating", ascending=False).head(5)
    return result.to_dict('records')

# Define route for homepage
@app.route('/')
def home():
    return render_template('index.html')

# Define route for getting recommendations
@app.route('/recommendations', methods=['POST'])
def recommendations():
    description = request.form['description']
    state = request.form['state']
    recommendations = recommender(description, state)
    
    # Generate HTML code for recommendations
    html = "<h2 style='color:blue;text-align:center;'>Recommendations:</h2>"
    html += "<table style='border-collapse:collapse;width:100%;'>"
    html += "<tr style='background-color:#f2f2f2;'>"
    html += "<th style='padding:10px;border:1px solid #ddd;text-align:left;'>Name</th>"
    html += "<th style='padding:10px;border:1px solid #ddd;text-align:left;'>State</th>"
    html += "<th style='padding:10px;border:1px solid #ddd;text-align:left;'>Rating</th>"
    html += "</tr>"
    for r in recommendations:
        html += "<tr>"
        html += f"<td style='padding:10px;border:1px solid #ddd;'>{r['Title']}</td>"
        html += f"<td style='padding:10px;border:1px solid #ddd;'>{r['State']}</td>"
        html += f"<td style='padding:10px;border:1px solid #ddd;'>{r['Rating']}</td>"
        html += "</tr>"
    html += "</table>"
    
    # Return HTML code as a string
    return html


if __name__ == '__main__':
    app.run(debug=True)
