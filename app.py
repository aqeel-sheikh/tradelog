from flask import Flask, render_template, redirect, url_for, request, flash, Response, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, Trade, User
from forms import TradeLogForm, RegisterForm, LoginForm
from datetime import datetime
import csv, os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Landing Page
@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('landing.html')

# Index Route
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = TradeLogForm()
    edit_id = request.args.get('edit_id')
    trades = Trade.query.filter_by(user_id=current_user.id).all()
    # Inline edit POST
    if request.method == 'POST' and edit_id:
        try:
            trade = Trade.query.get(int(edit_id))
            if trade and trade.user_id == current_user.id:
                trade.stock = request.form.get('stock')
                trade.date_time = request.form.get('date_time')
                trade.bias = request.form.get('bias')
                trade.position_size = request.form.get('position_size')
                trade.entry_reason = request.form.get('entry_reason')
                trade.exit_reason = request.form.get('exit_reason')
                trade.outcome = request.form.get('outcome')
                trade.rr = request.form.get('rr')
                trade.notes = request.form.get('notes')
                trade.emotion = request.form.get('emotion')
                trade.trading_plan = request.form.get('trading_plan')
                trade.balance = request.form.get('balance')
                trade.pnl = request.form.get('pnl')
                db.session.commit()
                flash('Trade updated successfully!', 'success')
                return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the trade.', 'error')
    # Add new trade with free user limit
    if form.validate_on_submit() and not edit_id:
        try:
            if not current_user.is_premium:
                trade_count = Trade.query.filter_by(user_id=current_user.id).count()
                if trade_count >= 20:
                    flash('Free users can only add up to 20 trades. Upgrade to premium for unlimited trades!', 'error')
                    return redirect(url_for('index'))
            new_trade = Trade(
                stock=form.stock.data,
                date_time=form.date_time.data.strftime('%Y-%m-%dT%H:%M'),
                bias=form.bias.data,
                position_size=form.position_size.data,
                entry_reason=form.entry_reason.data,
                exit_reason=form.exit_reason.data,
                outcome=form.outcome.data,
                rr=form.rr.data,
                notes=form.notes.data,
                emotion=form.emotion.data,
                trading_plan=form.trading_plan.data,
                balance=form.balance.data,
                pnl=form.pnl.data,
                user_id=current_user.id
            )
            db.session.add(new_trade)
            db.session.commit()
            flash('Trade logged successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while logging the trade.', 'error')
    if form.errors:
        flash(str(form.errors), 'error')
    return render_template('index.html', trades=trades, form=form)

# Delete Route
@app.route('/delete/<int:trade_id>')
@login_required
def delete_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)
    db.session.delete(trade)
    db.session.commit()
    flash('Trade deleted successfully!')
    return redirect(url_for('index'))

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your email and password.')
    return render_template('login.html', form=form)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Export Route (Premium)
@app.route('/export')
@login_required
def export_trades():
    trades = Trade.query.filter_by(user_id=current_user.id).all()
    def generate():
        data = []
        header = [
            'stock', 'date_time', 'bias', 'position_size', 'entry_reason', 'exit_reason',
            'outcome', 'rr', 'notes', 'emotion', 'trading_plan', 'balance', 'pnl'
        ]
        yield ','.join(header) + '\n'
        for t in trades:
            row = [
                t.stock,
                t.date_time,
                t.bias,
                str(t.position_size),
                t.entry_reason,
                t.exit_reason,
                t.outcome,
                str(t.rr),
                t.notes or '',
                t.emotion,
                t.trading_plan,
                str(t.balance),
                str(t.pnl)
            ]
            yield ','.join('"{}"'.format(x.replace('"', '""')) if isinstance(x, str) else str(x) for x in row) + '\n'
    return Response(generate(), mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename=trades.csv'
    })

# Admin Route
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template('admin.html', users=users)

# Upgrade user Route
@app.route('/upgrade/<int:user_id>', methods=['POST'])
@login_required
def upgrade_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get(user_id)
    user.is_premium = True
    db.session.commit()
    flash(f"{user.username} upgraded to Premium.")
    return redirect(url_for('admin'))

# Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    trades = Trade.query.filter_by(user_id=current_user.id).all()

    total_trades = len(trades)
    total_pnl = sum([t.pnl for t in trades])
    wins = [t for t in trades if t.outcome.lower() == "win"]
    win_rate = round((len(wins) / total_trades) * 100, 2) if total_trades else 0
    avg_rr = round(sum([t.rr for t in trades]) / total_trades, 2) if total_trades else 0
    last_trade = max(trades, key=lambda t: t.date_time, default=None)

    return render_template("dashboard.html",
        total_trades=total_trades,
        total_pnl=total_pnl,
        win_rate=win_rate,
        avg_rr=avg_rr,
        last_trade=last_trade
    )

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)