from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаём таблицы, если их ещё нет
    app.run(debug=~False)
    
    
