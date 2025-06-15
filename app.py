from flask import Flask, url_for, render_template, redirect, request, flash
import sqlite3
from forms import TradeLogForm
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '18a1de63b63512e88a94fec66b2c5653'

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock TEXT NOT NULL,
                date_time TEXT NOT NULL,
                bias TEXT NOT NULL,
                position_size DECIMAL(10, 2) NOT NULL,
                entry_reason TEXT NOT NULL,
                exit_reason TEXT NOT NULL,
                outcome TEXT NOT NULL,
                rr DECIMAL(10, 2) NOT NULL,
                notes TEXT,
                emotion TEXT NOT NULL,
                trading_plan TEXT NOT NULL,
                balance DECIMAL(10, 2) NOT NULL,
                pnl DECIMAL(10, 2) NOT NULL
            )
        ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    edit_id = request.args.get('edit_id')
    form = TradeLogForm()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Inline edit POST handling
    if request.method == 'POST' and edit_id:
        # Get data from request.form
        stock = request.form.get('stock')
        date_time = request.form.get('date_time')
        bias = request.form.get('bias')
        position_size = request.form.get('position_size')
        entry_reason = request.form.get('entry_reason')
        exit_reason = request.form.get('exit_reason')
        outcome = request.form.get('outcome')
        rr = request.form.get('rr')
        notes = request.form.get('notes')
        emotion = request.form.get('emotion')
        trading_plan = request.form.get('trading_plan')
        balance = request.form.get('balance')
        pnl = request.form.get('pnl')
        # Update the trade
        cursor.execute(
            '''UPDATE trades SET stock=?, date_time=?, bias=?, position_size=?, entry_reason=?, exit_reason=?,
               outcome=?, rr=?, notes=?, emotion=?, trading_plan=?, balance=?, pnl=?
               WHERE id=?''',
            (
                stock,
                date_time,
                bias,
                float(position_size) if position_size else 0,
                entry_reason,
                exit_reason,
                outcome,
                float(rr) if rr else 0,
                notes,
                emotion,
                trading_plan,
                float(balance) if balance else 0,
                float(pnl) if pnl else 0,
                edit_id
            )
        )
        conn.commit()
        conn.close()
        flash('Trade updated successfully!')
        return redirect(url_for('index'))
    
    # Normal add form handling
    if form.validate_on_submit() and not edit_id:
        cursor.execute(
            '''
            INSERT INTO trades (
                stock, date_time, bias, position_size, entry_reason, exit_reason,
                outcome, rr, notes, emotion, trading_plan, balance, pnl
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                form.stock.data,
                form.date_time.data.strftime('%Y-%m-%dT%H:%M'),
                form.bias.data,
                float(form.position_size.data),
                form.entry_reason.data,
                form.exit_reason.data,
                form.outcome.data,
                float(form.rr.data),
                form.notes.data,
                form.emotion.data,
                form.trading_plan.data,
                float(form.balance.data),
                float(form.pnl.data),
            )
        )
        conn.commit()
        conn.close()
        flash('Trade logged successfully!')
        return redirect(url_for('index'))
    else:
        if form.errors:
            flash(str(form.errors))
        cursor.execute('SELECT * FROM trades ORDER BY date_time DESC')
        trades = cursor.fetchall()
        conn.close()
        return render_template('index.html', trades=trades, form=form)

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM trades WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)