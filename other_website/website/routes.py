from flask import render_template
from . import app

# routing for the home page which takes you to the home page and the URL of the base URL/home
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

# routing for the pricing page which takes you to the home page and the URL of the base URL/pricing
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

# routing for the contact page which takes you to the home page and the URL of the base URL/contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

# routing for the privacy page which takes you to the home page and the URL of the base URL/privacy
@app.route('/privacy')
def privacy():
    return render_template('privacypolicy.html')

# routing for the terms page which takes you to the home page and the URL of the base URL/terms
@app.route('/terms')
def terms():
    return render_template('terms.html')