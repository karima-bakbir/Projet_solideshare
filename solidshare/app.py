from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///solidshare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    groups = db.relationship('GroupMember', backref='user', lazy=True)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    members = db.relationship('GroupMember', backref='group', lazy=True)
    requests = db.relationship('HelpRequest', backref='group', lazy=True)

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class HelpRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount_needed = db.Column(db.Float, nullable=False)
    amount_collected = db.Column(db.Float, default=0.0)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    requester = db.relationship('User', backref='help_requests', lazy=True)
    contributions = db.relationship('Contribution', backref='request', lazy=True)
    repayments = db.relationship('Repayment', backref='request', lazy=True)
    
class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    contributor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('help_request.id'), nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    contributor = db.relationship('User', backref='contributions', lazy=True)

class Repayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('help_request.id'), nullable=False)
    repaid_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ThankYouMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('help_request.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Create Group')

class HelpRequestForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
    amount_needed = FloatField('Amount Needed', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Submit Request')

class ContributionForm(FlaskForm):
    amount = FloatField('Contribution Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    is_anonymous = SelectField('Contribution Type', choices=[('False', 'Public'), ('True', 'Anonymous')], default='False')
    submit = SubmitField('Contribute')

class ThankYouForm(FlaskForm):
    message = TextAreaField('Thank You Message', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Send Thanks')

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:  # In production, use hashed passwords
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('register'))
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_groups = Group.query.join(GroupMember).filter(GroupMember.user_id == current_user.id).all()
    user_requests = HelpRequest.query.filter_by(requester_id=current_user.id).all()
    contributions = Contribution.query.filter_by(contributor_id=current_user.id).all()
    return render_template('dashboard.html', groups=user_groups, requests=user_requests, contributions=contributions)

@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(name=form.name.data, description=form.description.data, created_by=current_user.id)
        db.session.add(group)
        db.session.commit()
        member = GroupMember(user_id=current_user.id, group_id=group.id)
        db.session.add(member)
        db.session.commit()
        flash('Group created successfully!')
        return redirect(url_for('dashboard'))
    return render_template('create_group.html', form=form)

@app.route('/group/<int:group_id>')
@login_required
def group_detail(group_id):
    group = Group.query.get_or_404(group_id)
    if not GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first():
        flash('You are not a member of this group')
        return redirect(url_for('dashboard'))
    requests = HelpRequest.query.filter_by(group_id=group_id).all()
    return render_template('group_detail.html', group=group, requests=requests)

@app.route('/group/<int:group_id>/request_help', methods=['GET', 'POST'])
@login_required
def request_help(group_id):
    group = Group.query.get_or_404(group_id)
    if not GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first():
        flash('You are not a member of this group')
        return redirect(url_for('dashboard'))
    form = HelpRequestForm()
    if form.validate_on_submit():
        request = HelpRequest(
            title=form.title.data,
            description=form.description.data,
            amount_needed=form.amount_needed.data,
            group_id=group_id,
            requester_id=current_user.id
        )
        db.session.add(request)
        db.session.commit()
        flash('Help request submitted successfully!')
        socketio.emit('new_request', {'group_id': group_id, 'request_id': request.id}, room=f'group_{group_id}')
        return redirect(url_for('group_detail', group_id=group_id))
    return render_template('request_help.html', form=form, group=group)

@app.route('/request/<int:request_id>')
@login_required
def request_detail(request_id):
    request = HelpRequest.query.get_or_404(request_id)
    if not GroupMember.query.filter_by(user_id=current_user.id, group_id=request.group_id).first():
        flash('You are not authorized to view this request')
        return redirect(url_for('dashboard'))
    contributions = Contribution.query.filter_by(request_id=request_id).all()
    repayments = Repayment.query.filter_by(request_id=request_id).all()
    thank_you_messages = ThankYouMessage.query.filter_by(request_id=request_id).all()
    return render_template('request_detail.html', request=request, contributions=contributions, repayments=repayments, thank_you_messages=thank_you_messages)

@app.route('/request/<int:request_id>/contribute', methods=['GET', 'POST'])
@login_required
def contribute(request_id):
    request = HelpRequest.query.get_or_404(request_id)
    if not GroupMember.query.filter_by(user_id=current_user.id, group_id=request.group_id).first():
        flash('You are not authorized to contribute to this request')
        return redirect(url_for('dashboard'))
    form = ContributionForm()
    if form.validate_on_submit():
        contribution = Contribution(
            amount=form.amount.data,
            contributor_id=current_user.id,
            request_id=request_id,
            is_anonymous=form.is_anonymous.data == 'True'
        )
        db.session.add(contribution)
        request.amount_collected += form.amount.data
        if request.amount_collected >= request.amount_needed:
            request.status = 'completed'
        db.session.commit()
        flash('Contribution added successfully!')
        socketio.emit('new_contribution', {'request_id': request_id, 'amount': form.amount.data}, room=f'group_{request.group_id}')
        return redirect(url_for('request_detail', request_id=request_id))
    return render_template('contribute.html', form=form, request=request)

@app.route('/request/<int:request_id>/thank_you', methods=['GET', 'POST'])
@login_required
def send_thank_you(request_id):
    request = HelpRequest.query.get_or_404(request_id)
    if current_user.id != request.requester_id:
        flash('You can only send thank you messages for your own requests')
        return redirect(url_for('request_detail', request_id=request_id))
    form = ThankYouForm()
    if form.validate_on_submit():
        thank_you = ThankYouMessage(
            message=form.message.data,
            from_user_id=current_user.id,
            to_user_id=request.contributions[0].contributor_id if request.contributions else current_user.id,  # Simplified
            request_id=request_id
        )
        db.session.add(thank_you)
        db.session.commit()
        flash('Thank you message sent!')
        return redirect(url_for('request_detail', request_id=request_id))
    return render_template('thank_you.html', form=form, request=request)

@app.route('/api/group/<int:group_id>/stats')
@login_required
def group_stats(group_id):
    if not GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first():
        return jsonify({'error': 'Unauthorized'}), 403
    total_requests = HelpRequest.query.filter_by(group_id=group_id).count()
    total_contributions = db.session.query(db.func.sum(Contribution.amount)).filter(
        Contribution.request_id.in_(
            db.session.query(HelpRequest.id).filter_by(group_id=group_id)
        )
    ).scalar() or 0
    active_requests = HelpRequest.query.filter_by(group_id=group_id, status='active').count()
    return jsonify({
        'total_requests': total_requests,
        'total_contributions': total_contributions,
        'active_requests': active_requests
    })

@socketio.on('join_group')
def handle_join_group(data):
    group_id = data['group_id']
    join_room(f'group_{group_id}')

@socketio.on('leave_group')
def handle_leave_group(data):
    group_id = data['group_id']
    leave_room(f'group_{group_id}')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
