from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# HTML and CSS embedded in a single string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Search</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }

        .container {
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }

        h1 {
            text-align: center;
        }

        form {
            display: flex;
            justify-content: space-between;
        }

        input {
            width: 70%;
            padding: 10px;
        }

        button {
            padding: 10px 15px;
        }

        ul {
            list-style-type: none;
            padding: 0;
        }

        li {
            margin: 15px 0;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 5px;
        }

        img {
            max-width: 100px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Book Search</h1>
        <form action="/search" method="get">
            <input type="text" name="query" placeholder="Search by title or author" required>
            <button type="submit">Search</button>
        </form>
        <ul>
            {% if books %}
                {% for book in books %}
                    <li>
                        <h2>{{ book.title }}</h2>
                        <p><strong>Author:</strong> {{ book.author_name[0] if book.author_name else 'Unknown' }}</p>
                        <p><strong>Published:</strong> {{ book.first_publish_year if 'first_publish_year' in book else 'N/A' }}</p>
                        {% if book.cover_i %}
                            <img src="https://covers.openlibrary.org/b/id/{{ book.cover_i }}-M.jpg" alt="{{ book.title }} cover">
                        {% endif %}
                    </li>
                {% endfor %}
            {% else %}
                <p>No results found.</p>
            {% endif %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        response = requests.get(f"https://openlibrary.org/search.json?q={query}")
        data = response.json()
        books = data.get('docs', [])[:10]  # Get the first 10 results
    else:
        books = []
    return render_template_string(HTML_TEMPLATE, books=books)

if __name__ == '__main__':
    app.run(debug=True)
