from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import uuid
from translations import translations
from advanced_chatbot import AdvancedAgricultureBot
from schemes_database import get_all_schemes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'agrisahayak_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='farmer')  # farmer, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    profile = db.relationship('Profile', backref='user', uselist=False)
    documents = db.relationship('Documents', backref='user', uselist=False)
    subscriptions = db.relationship('Subscription', backref='user')
    applications = db.relationship('SchemeApplication', backref='user')

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    full_name = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    state = db.Column(db.String(50))  # Separate state field
    farm_location = db.Column(db.String(200))
    land_area = db.Column(db.Float)
    address = db.Column(db.Text)

class Documents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    aadhaar_number = db.Column(db.String(12))
    pan_number = db.Column(db.String(10))
    ration_card_number = db.Column(db.String(20))
    land_record_number = db.Column(db.String(50))
    aadhaar_file = db.Column(db.String(200))
    pan_file = db.Column(db.String(200))
    ration_file = db.Column(db.String(200))
    land_file = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plan_name = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)

class SchemeApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    farmer_name = db.Column(db.String(100))
    crop = db.Column(db.String(50))
    damage_type = db.Column(db.String(100))
    land_area = db.Column(db.Float)
    scheme_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdminAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    farmer_name = db.Column(db.String(100))
    state = db.Column(db.String(50))
    district = db.Column(db.String(50))
    crop = db.Column(db.String(50))
    land_size = db.Column(db.Float)
    scheme_name = db.Column(db.String(100))
    category = db.Column(db.String(50))  # insurance, financial_support, irrigation, etc.
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)  # When admin processed the application

@app.before_request
def create_tables():
    if not hasattr(app, '_tables_created'):
        db.create_all()
        app._tables_created = True

@app.route('/')
def index():
    lang = session.get('lang', 'en')
    t = translations[lang]
    return render_template('index.html', t=t)

@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash(t['username_exists'])
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash(t['email_exists'])
            return redirect(url_for('register'))
        
        role = request.form.get('role', 'farmer')
        
        user = User(username=username, email=email, name=username, 
                   password=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        
        profile = Profile(user_id=user.id)
        documents = Documents(user_id=user.id)
        db.session.add(profile)
        db.session.add(documents)
        db.session.commit()
        
        flash(t['registration_successful'])
        return redirect(url_for('login'))
    
    return render_template('register.html', t=t)

@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['lang'] = session.get('lang', 'en')
            
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash(t['invalid_credentials'])
    
    return render_template('login.html', t=t)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    # Check if user wants enhanced dashboard
    enhanced = request.args.get('enhanced', 'false') == 'true'
    
    if enhanced:
        return render_template('enhanced_dashboard.html', t=t)
    
    # Original dashboard logic for backward compatibility
    user_documents = Documents.query.filter_by(user_id=session['user_id']).first()
    user_profile = Profile.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        if user_profile:
            user_profile.full_name = request.form['full_name']
            user_profile.mobile = request.form['mobile']
            user_profile.farm_location = request.form['farm_location']
            user_profile.land_area = float(request.form['land_area']) if request.form['land_area'] else None
            user_profile.address = request.form['address']
            db.session.commit()
            flash(t['profile_updated'])
    
    return render_template('dashboard.html', profile=user_profile, documents=user_documents, t=t)

@app.route('/enhanced_dashboard')
def enhanced_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    return render_template('enhanced_dashboard.html', t=t)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    user_profile = Profile.query.filter_by(user_id=session['user_id']).first()
    user_documents = Documents.query.filter_by(user_id=session['user_id']).first()
    
    if request.method == 'POST':
        user_profile.full_name = request.form['full_name']
        user_profile.mobile = request.form['mobile']
        user_profile.state = request.form['state']  # Handle state field
        user_profile.farm_location = request.form['farm_location']
        user_profile.land_area = float(request.form['land_area']) if request.form['land_area'] else None
        user_profile.address = request.form['address']
        db.session.commit()
        flash(t['profile_updated'])
    
    return render_template('profile.html', profile=user_profile, documents=user_documents, t=t)

@app.route('/documents', methods=['GET', 'POST'])
def documents():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    user_documents = Documents.query.filter_by(user_id=session['user_id']).first()
    user_profile = Profile.query.filter_by(user_id=session['user_id']).first()
    
    # Get land size and state from profile
    land_size = 0
    state = "Unknown"
    district = "Unknown"
    
    if user_profile:
        land_size = user_profile.land_area or 0
        state = user_profile.state or "Unknown"  # Use the separate state field
        # Parse district from farm_location
        location_parts = (user_profile.farm_location or "").split(", ")
        if len(location_parts) >= 1:
            district = location_parts[0].strip()
    
    # Also check from latest application for more current data
    latest_application = AdminAlert.query.filter_by(farmer_id=session['user_id']).order_by(AdminAlert.created_at.desc()).first()
    if latest_application:
        if latest_application.state and latest_application.state != "Unknown":
            state = latest_application.state
        if latest_application.district:
            district = latest_application.district
        if latest_application.land_size:
            land_size = latest_application.land_size
    
    if request.method == 'POST':
        if user_documents:
            user_documents.aadhaar_number = request.form['aadhaar_number']
            user_documents.pan_number = request.form['pan_number']
            user_documents.ration_card_number = request.form['ration_card_number']
            user_documents.land_record_number = request.form['land_record_number']
            
            if 'aadhaar_file' in request.files:
                file = request.files['aadhaar_file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    user_documents.aadhaar_file = filename
            
            if 'pan_file' in request.files:
                file = request.files['pan_file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    user_documents.pan_file = filename
            
            if 'ration_file' in request.files:
                file = request.files['ration_file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    user_documents.ration_file = filename
            
            if 'land_file' in request.files:
                file = request.files['land_file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    user_documents.land_file = filename
            
            db.session.commit()
            flash(t['documents_updated'])
    
    return render_template('documents.html', documents=user_documents, t=t, land_size=land_size, state=state, district=district)

@app.route('/admin/farmer_documents/<int:farmer_id>')
def admin_farmer_documents(farmer_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    # Get farmer's documents
    farmer_documents = Documents.query.filter_by(user_id=farmer_id).first()
    farmer_profile = Profile.query.filter_by(user_id=farmer_id).first()
    farmer_user = User.query.get(farmer_id)
    
    # Get land size and state from profile or latest application
    land_size = 0
    state = "Unknown"
    district = "Unknown"
    
    if farmer_profile:
        land_size = farmer_profile.land_area or 0
        state = farmer_profile.state or "Unknown"  # Use the separate state field
        # Parse district from farm_location
        location_parts = (farmer_profile.farm_location or "").split(", ")
        if len(location_parts) >= 1:
            district = location_parts[0].strip()
    
    # Also check from latest application for more current data
    latest_application = AdminAlert.query.filter_by(farmer_id=farmer_id).order_by(AdminAlert.created_at.desc()).first()
    if latest_application:
        if latest_application.state:
            state = latest_application.state
        if latest_application.district:
            district = latest_application.district
        if latest_application.land_size:
            land_size = latest_application.land_size
    
    return render_template('admin_farmer_documents.html', 
                         documents=farmer_documents, 
                         t=t, 
                         land_size=land_size, 
                         state=state, 
                         district=district,
                         farmer_name=farmer_user.username if farmer_user else "Unknown",
                         farmer_id=farmer_id)

from concise_chatbot import ConciseAIChatbot

@app.route('/enhanced_chat', methods=['POST'])
def enhanced_chat():
    if 'user_id' not in session:
        return jsonify({'reply': 'Please login to use chat', 'allow_apply': False})
    
    user_message = request.json.get('message', '').strip()
    user_id = session['user_id']
    lang = session.get('lang', 'en')
    
    if not user_message:
        return jsonify({'reply': translations[lang]['chat_placeholder'], 'allow_apply': False})
    
    # Get farmer profile for enhanced responses
    farmer_profile = None
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        farmer_profile = {
            'name': profile.full_name,
            'state': profile.farm_location,
            'land_size': profile.land_area,
            'crop_type': None,
            'district': None
        }
        
        # Parse state and district from farm_location
        location_parts = (profile.farm_location or "").split(", ")
        if len(location_parts) >= 2:
            farmer_profile['district'] = location_parts[0].strip()
            farmer_profile['state'] = location_parts[1].strip()
    
    # Initialize Concise AI chatbot
    bot = ConciseAIChatbot(language=lang)
    
    # Generate enhanced response
    response = bot.get_response(user_message, farmer_profile)
    
    # Determine if apply button should be shown
    allow_apply = any(keyword in user_message.lower() for keyword in 
                    ['scheme', 'apply', 'insurance', 'loan', 'subsidy', 'equipment'])
    
    # Save chat message
    chat_msg = ChatMessage(user_id=user_id, message=user_message, reply=response)
    db.session.add(chat_msg)
    db.session.commit()
    
    return jsonify({'reply': response, 'allow_apply': allow_apply})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/farmer_profile', methods=['GET', 'POST'])
def farmer_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    if request.method == 'POST':
        # Get form data
        profile_data = {
            'name': request.form.get('name'),
            'state': request.form.get('state'),
            'district': request.form.get('district'),
            'crop_type': request.form.get('crop_type'),
            'land_size': request.form.get('land_size'),
            'irrigation_type': request.form.get('irrigation_type'),
            'annual_income': request.form.get('annual_income'),
            'crop_damage': request.form.get('crop_damage'),
            'need_types': request.form.getlist('need_types')
        }
        
        # Update existing profile
        user_profile = Profile.query.filter_by(user_id=session['user_id']).first()
        if user_profile:
            user_profile.full_name = profile_data['name']
            user_profile.farm_location = f"{profile_data['district']}, {profile_data['state']}"
            user_profile.land_area = float(profile_data['land_size']) if profile_data['land_size'] else None
            user_profile.address = f"Crop: {profile_data['crop_type']}, Irrigation: {profile_data['irrigation_type']}"
            db.session.commit()
            flash(t['profile_updated'])
        
        return redirect(url_for('dashboard'))
    
    return render_template('farmer_profile.html', t=t)

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'reply': 'Please login to use chat', 'allow_apply': False})
    
    user_message = request.json.get('message', '').strip()
    user_id = session['user_id']
    lang = session.get('lang', 'en')
    
    if not user_message:
        return jsonify({'reply': translations[lang]['chat_placeholder'], 'allow_apply': False})
    
    # Get farmer profile if available
    farmer_profile = None
    profile = Profile.query.filter_by(user_id=user_id).first()
    if profile:
        farmer_profile = {
            'name': profile.full_name,
            'state': profile.farm_location,
            'land_size': str(profile.land_area) if profile.land_area else None,
            'crop_type': None,  # Could be enhanced to track from chat
            'irrigation_type': None,
            'annual_income': None,
            'crop_damage': None,
            'need_types': []
        }
    
    # Initialize Concise AI chatbot
    bot = ConciseAIChatbot(language=lang)
    
    # Generate intelligent response
    response = bot.get_response(user_message, farmer_profile)
    
    # Save chat message
    chat_msg = ChatMessage(user_id=user_id, message=user_message, reply=response)
    db.session.add(chat_msg)
    db.session.commit()
    
    # Determine if apply button should be shown
    allow_apply = any(keyword in user_message.lower() for keyword in ['scheme', 'apply', 'insurance', 'loan', 'subsidy'])
    
    return jsonify({'reply': response, 'allow_apply': allow_apply})

@app.route('/apply_scheme', methods=['POST'])
def apply_scheme():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login'})
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    
    # Parse location from profile
    location_parts = (profile.farm_location or "").split(", ")
    district = location_parts[0] if len(location_parts) > 0 else "Unknown"
    state = profile.state if profile.state else "Unknown"  # Use the separate state field
    
    # Create enhanced admin alert
    alert = AdminAlert(
        farmer_id=user_id,
        farmer_name=profile.full_name or user.username,
        state=state,
        district=district,
        crop=request.json.get('crop', 'Unknown'),
        land_size=profile.land_area or 0,
        scheme_name=request.json.get('scheme_name', 'Pradhan Mantri Fasal Bima Yojana (PMFBY)'),
        category=request.json.get('category', 'insurance'),
        status='Pending'
    )
    db.session.add(alert)
    
    # Also create scheme application record
    application = SchemeApplication(
        user_id=user_id,
        farmer_name=profile.full_name or user.username,
        crop=request.json.get('crop', 'Unknown'),
        damage_type=request.json.get('damage', 'Unknown'),
        land_area=profile.land_area or 0,
        scheme_name=request.json.get('scheme_name', 'Pradhan Mantri Fasal Bima Yojana (PMFBY)'),
        status='pending'
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Application submitted successfully'})

@app.route('/subscription')
def subscription():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    user_subscription = Subscription.query.filter_by(user_id=session['user_id']).order_by(Subscription.id.desc()).first()
    return render_template('subscription.html', subscription=user_subscription, t=t)

@app.route('/payment')
def payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    return render_template('payment.html', t=t)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    user_id = session['user_id']
    plan = request.json.get('plan')
    
    if plan == 'premium':
        subscription = Subscription(
            user_id=user_id,
            plan_name='Premium Plan',
            status='active',
            expiry_date=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Premium subscription activated successfully!'})
    
    return jsonify({'success': False})

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    lang = session.get('lang', 'en')
    t = translations[lang]
    
    # Get all alerts with enhanced farmer data
    alerts = db.session.query(
        AdminAlert, User, Profile
    ).join(
        User, AdminAlert.farmer_id == User.id
    ).outerjoin(
        Profile, AdminAlert.farmer_id == Profile.user_id
    ).order_by(AdminAlert.created_at.desc()).all()
    
    # Get documents for each alert
    enhanced_alerts = []
    for alert, user, profile in alerts:
        documents = Documents.query.filter_by(user_id=alert.farmer_id).all()
        enhanced_alerts.append({
            'alert': alert,
            'user': user,
            'profile': profile,
            'documents': documents
        })
    
    return render_template('admin_dashboard.html', alerts=enhanced_alerts, t=t)

@app.route('/update_alert/<int:alert_id>/<string:status>')
def update_alert(alert_id, status):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False})
    
    alert = AdminAlert.query.get(alert_id)
    if alert:
        alert.status = status
        alert.processed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False})

@app.route('/get_schemes')
def get_schemes():
    """API endpoint to get all schemes for frontend"""
    from schemes_database import get_all_schemes
    schemes = get_all_schemes()
    return jsonify(schemes)

@app.route('/set_language/<string:lang>')
def set_language(lang):
    if lang in ['en', 'hi', 'mr']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
