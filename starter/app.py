from sudoku_app import create_app

app = create_app()
CURRENT = app.CURRENT

if __name__ == '__main__':
    app.run(debug=True)