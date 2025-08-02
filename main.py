import os
import sys
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'votre-cle-secrete-inventaire'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventaire.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)
CORS(app)

# Modèles de base de données
class Categorie(db.Model):
    __tablename__ = 'categories'
    id_categorie = db.Column(db.Integer, primary_key=True)
    nom_categorie = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class Article(db.Model):
    __tablename__ = 'articles'
    id_article = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    id_categorie = db.Column(db.Integer, db.ForeignKey('categories.id_categorie'))
    prix_achat = db.Column(db.Float, default=0.0)
    prix_vente = db.Column(db.Float, default=0.0)
    prix_moyen = db.Column(db.Float, default=0.0)
    stock_min = db.Column(db.Integer, default=0)
    stock_max = db.Column(db.Integer, default=0)
    stock_debut = db.Column(db.Float, default=0.0)
    stock_actuel = db.Column(db.Float, default=0.0)
    stock_reel = db.Column(db.Float, default=0.0)
    unite = db.Column(db.String(20), default='unité')
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)

# Routes principales
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/dashboard')
def dashboard():
    total_articles = Article.query.filter_by(actif=True).count()
    total_categories = Categorie.query.count()
    
    return jsonify({
        'success': True,
        'data': {
            'total_articles': total_articles,
            'total_categories': total_categories,
            'stock_alerts': 0,
            'total_value': 0
        }
    })

@app.route('/api/articles')
def get_articles():
    articles = Article.query.filter_by(actif=True).all()
    articles_data = []
    
    for article in articles:
        articles_data.append({
            'id_article': article.id_article,
            'designation': article.designation,
            'prix_moyen': article.prix_moyen,
            'stock_actuel': article.stock_actuel,
            'unite': article.unite
        })
    
    return jsonify({
        'success': True,
        'data': articles_data
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Ajouter des données d'exemple
        if Categorie.query.count() == 0:
            categories = [
                Categorie(nom_categorie='APERITIF', description='Boissons apéritives'),
                Categorie(nom_categorie='LEGUME', description='Légumes frais'),
                Categorie(nom_categorie='VIANDE', description='Viandes et charcuteries')
            ]
            for cat in categories:
                db.session.add(cat)
            
            articles = [
                Article(designation='BEAUVALLON ROUGE 3/4', id_categorie=1, prix_moyen=76.0, stock_actuel=12, unite='bouteille'),
                Article(designation='BEURRE VEGET', id_categorie=2, prix_moyen=25.0, stock_actuel=5, unite='kg')
            ]
            for art in articles:
                db.session.add(art)
            
            db.session.commit()
    
    print("🚀 Application d'inventaire démarrée sur http://localhost:5000" )
    app.run(host='0.0.0.0', port=5000, debug=True)
