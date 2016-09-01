from app import create_app

app = create_app('rj')

if __name__ == '__main__':
    app.run('10.254.238.20',debug=True)
