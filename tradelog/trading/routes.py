from flask import Blueprint, render_template, redirect, url_for, request, flash, Response, abort
from flask_login import login_required, current_user
from ..models import db, Trade
from .forms import TradeLogForm
import uuid, requests, os
from datetime import datetime

trading = Blueprint('trading', __name__)

@trading.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = TradeLogForm()
    edit_id = request.args.get('edit_id')
    trades = Trade.query.filter_by(user_id=current_user.id).order_by(Trade.date_time.desc()).all()
    # Ensure date_time is a datetime object for formatting in template
    for trade in trades:
        if trade.date_time and isinstance(trade.date_time, str):
            for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
                try:
                    trade.date_time = datetime.strptime(trade.date_time, fmt)
                    break
                except ValueError:
                    continue
    if request.method == 'POST' and edit_id:
        try:
            trade = db.session.get(Trade, int(edit_id))
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
                return redirect(url_for('trading.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the trade.', 'error')
    if form.validate_on_submit() and not edit_id:
        try:
            if not current_user.is_premium:
                trade_count = Trade.query.filter_by(user_id=current_user.id).count()
                if trade_count >= 10:
                    flash('Free users can only add up to 10 trades. Upgrade to premium for unlimited trades!', 'error')
                    return redirect(url_for('trading.index'))
            new_trade = Trade(
                stock=form.stock.data,
                date_time=form.date_time.data,
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
            return redirect(url_for('trading.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while logging the trade.', 'error')
    if form.errors:
        flash(str(form.errors), 'error')
    return render_template('trading/index.html', trades=trades, form=form)

@trading.app_context_processor
def inject_remain_trades():
    remain = None
    if current_user.is_authenticated and not current_user.is_premium:
        trade_count = Trade.query.filter_by(user_id=current_user.id).count()
        remain = max(0, 10 - trade_count)
    return dict(remain_trades=remain)

@trading.route('/delete/<int:trade_id>', methods=['POST'])
@login_required
def delete_trade(trade_id):
    trade = db.session.get(Trade, trade_id)
    if not trade:
        abort(404)
    db.session.delete(trade)
    db.session.commit()
    flash('Trade deleted successfully!')
    return redirect(url_for('trading.index'))

@trading.route('/export')
@login_required
def export_trades():
    trades = Trade.query.filter_by(user_id=current_user.id).all()
    def generate():
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

@trading.route('/upgrade', methods=['POST'])
@login_required
def upgrade():
    order_id = str(uuid.uuid4())
    payload = {
        'order_id': order_id,
        'order_amount': 199.00,
        'order_currency': 'INR',
        'customer_details': {
            'customer_id': str(current_user.id),
            'customer_name': current_user.username,
            'customer_email': current_user.email,
            'customer_phone': '1234567890'
        },
        'order_note': 'Premium Upgrade for TradeLog',
        'order_meta': {
            'return_url': 'https://tradelog-g2ox.onrender.com/payment_success',
            'notify_url': 'https://tradelog-g2ox.onrender.com/payment_webhook'
        }
    }
    headers = {
        'x-api-version': '2022-01-01',
        'x-client-id': os.environ.get('CLIENT_ID', 'fallback-secret'),
        'x-client-secret': os.environ.get('CLIENT_SECRET', 'fallback-secret'),
        'Content-type': 'application/json'
    }
    res = requests.post('https://api.cashfree.com/pg/orders', json=payload, headers=headers)
    print(res.status_code, res.text)
    data = res.json()
    if res.status_code == 200 and data.get('order_status') == 'ACTIVE' and data.get('payment_link'):
        return redirect(data['payment_link'])
    else:
        flash('Failed to initiate payment. Try again later', 'error')
        return redirect(url_for('trading.index'))

@trading.route('/payment_webhook', methods=['POST'])
def payment_webhook():
    data = request.json
    print("Webhook received:", data)
    try:
        if data.get('order_status') == 'PAID':
            user_id = int(data['customer_details']['customer_id'])
            from ..models import User
            user = db.session.get(User, user_id)
            if user:
                user.is_premium = True
                db.session.commit()
                print(f"User {user_id} upgraded to premium.")
            else:
                print(f"User {user_id} not found.")
        else:
            print("Order status not PAID.")
    except Exception as e:
        print("Webhook error:", e)
    return '', 200

@trading.route('/payment_success')
@login_required
def payment_success():
    from ..models import User
    if not current_user.is_premium:
        current_user.is_premium = True
        db.session.commit()
    flash("You are now a Premium user!", "success")
    return redirect(url_for('trading.index'))
