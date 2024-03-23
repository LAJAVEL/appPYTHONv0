from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SECRET_KEY'] = 'LaCleSecrete0'
db = SQLAlchemy(app)

# refresh
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# Flask-Migrate
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_content_preview = db.Column(db.String(255), default='')


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('replies', lazy=True))
    post = db.relationship('Post', backref=db.backref('replies', lazy=True))


@app.route('/')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/forum')
@app.route('/forum/page/<int:page>')
def forum(page=1):
    posts_per_page = 5
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=posts_per_page, error_out=False)
    next_url = url_for('forum', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('forum', page=posts.prev_num) if posts.has_prev else None
    return render_template('forum.html', posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validation simple pour bloquer certains caractères
        if any(char in "<>=+" for char in username + email):
            flash("Les caractères <, >, =, + ne sont pas autorisés.", "danger")
            return render_template('register.html')

        # Génération du mot de passe hashé
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        # Tentative d'ajouter le nouvel utilisateur à la base de données
        try:
            new_user = User(username=username, email=email, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash("Le nom d'utilisateur ou l'email est déjà utilisé.", "danger")

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')  
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        # Utilise '%' autour de la requête pour une recherche partielle
        search = "%{}%".format(query)
        posts = Post.query.filter(Post.title.ilike(search) | Post.content.ilike(search)).all()
    else:
        posts = []

    return render_template('search_results.html', posts=posts, query=query)


@app.route('/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if 'user_id' not in session or session['user_id'] != post.user_id:
        flash('Vous n\'êtes pas autorisé à supprimer ce message.', 'danger')
        return redirect(url_for('index'))
    
    # Garder les 3 premiers mots du message original pour l'affichage
    words = post.content.split()[:3]
    preview = ' '.join(words) + '...'
    post.is_deleted = True
    post.deleted_content_preview = preview
    # Ne pas effacer entièrement le contenu pour conserver le preview
    # post.content = 'Message supprimé par l\'utilisateur.'
    
    db.session.commit()
    flash('Le message a été supprimé.', 'success')
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/reply', methods=['POST'])
def post_reply(post_id):
    # Logique pour traiter la réponse ici
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Vous devez être connecté pour répondre à un post.', 'danger')
            return redirect(url_for('login'))
        
        content = request.form['content']
        reply = Reply(content=content, user_id=session['user_id'], post_id=post.id)
        db.session.add(reply)
        db.session.commit()
        flash('Votre réponse a été publiée.', 'success')
        return redirect(url_for('post_detail', post_id=post.id))
    
    return render_template('post_detail.html', post=post)


@app.route('/post', methods=['GET', 'POST'])
def post():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user_id']

        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('new_post.html')


