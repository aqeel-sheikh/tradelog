from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired, NumberRange

class TradeLogForm(FlaskForm):
    stock = StringField('Stock', validators=[DataRequired()])
    date_time = DateTimeField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()] )
    bias = SelectField('Bias', choices=[('Buy'), ('Sell')], validators=[DataRequired()])
    position_size = DecimalField('Position Size', validators=[DataRequired(),NumberRange(min=0)])
    entry_reason = StringField('Entry Reason', validators=[DataRequired()])
    exit_reason = StringField('Exit Reason', validators=[DataRequired()])
    outcome = SelectField('Outcome', choices=[('Win'), ('Loss'), ('Breakeven')], validators=[DataRequired()])
    rr = DecimalField('RR', validators=[DataRequired(), NumberRange(min=0)])
    notes = StringField('Notes')
    emotion = StringField('Mental State/Emotions', validators=[DataRequired()])
    trading_plan = SelectField('Followed Trading Plan', choices=[('Yes'), ('No')], validators=[DataRequired()])
    balance = DecimalField('Initial Balance', validators=[DataRequired(), NumberRange(min=0)])
    pnl = DecimalField('PNL', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Log Trade')