from webapp import create_app

app = create_app()

# Set a secret key
app.secret_key = 'webapp_2024_thesis_maria_caill'  # Replace with a random, unique value


if __name__ == '__main__':
    app.run(debug=True)