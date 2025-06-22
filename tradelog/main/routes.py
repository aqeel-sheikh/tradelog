from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from ..models import User, db

main = Blueprint('main', __name__)

@main.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('trading.index'))
    return render_template('main/landing.html')

@main.route('/dashboard')
@login_required
def dashboard():
    from ..models import Trade
    trades = Trade.query.filter_by(user_id=current_user.id).all()
    total_trades = len(trades)
    total_pnl = 0
    for t in trades:
        if t.outcome.lower() == "win":
            total_pnl += t.pnl
        elif t.outcome.lower() == "loss":
            total_pnl -= t.pnl
    wins = [t for t in trades if t.outcome.lower() == "win"]
    win_rate = round((len(wins) / total_trades) * 100, 2) if total_trades else 0
    avg_rr = round(sum([t.rr for t in trades]) / total_trades, 2) if total_trades else 0
    last_trade = max(trades, key=lambda t: t.date_time, default=None)
    return render_template("main/dashboard.html",
        total_trades=total_trades,
        total_pnl=total_pnl,
        win_rate=win_rate,
        avg_rr=avg_rr,
        last_trade=last_trade
    )

@main.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template('main/admin.html', users=users)

# Upgrade user Route
@main.route('/upgrade_user/<int:user_id>', methods=['POST'])
@login_required
def upgrade_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = db.session.get(User, user_id)
    user.is_premium = True
    db.session.commit()
    flash(f"{user.username} upgraded to Premium.")
    return redirect(url_for('main.admin'))