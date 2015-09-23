from flask import (
    Blueprint,
    render_template,
    flash,
    request,
    abort,
    current_app,
    redirect,
    url_for
)

import requests

from organisations_demo.frontend.forms import SearchForm

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        search_term = form.data['search_term'].strip().lower()
        try:
            return redirect(url_for('frontend.search', q=search_term))
        except Exception as e:
            message = "There was a problem searching for: %s" % search_term
            flash(message)
            abort(500)
    return render_template('index.html', form=form)


@frontend.route('/search')
def search():
    name = request.args['q'].strip()
    organisations = current_app.db.premises.find({'entry.name':
        {'$regex': name, '$options': 'i'}})
    if not organisations:
        abort(404)
    return render_template('search.html', organisations=organisations)

@frontend.route('/company/<company_number>')
def company(company_number):
    co_house_api_key = current_app.config['COMPANIES_HOUSE_API_KEY']
    headers = {'Authorization': 'Basic '+co_house_api_key}
    url = 'https://api.companieshouse.gov.uk/company/%s' % company_number
    res = requests.get(url, headers=headers)
    current_app.logger.info(res.json())
    return render_template('company.html', company=res.json())
