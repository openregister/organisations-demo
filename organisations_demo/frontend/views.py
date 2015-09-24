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
    company, address = _get_company_details(company_number)
    return render_template('company.html',
                           company=company,
                           address=address)


@frontend.route('/company/<company_number>/licences')
def licences(company_number):
    premises = _get_premises(company_number)
    return render_template('company-licences.html',
                           premises=premises)


def _get_company_details(company_number):
    co_house_api_key = current_app.config['COMPANIES_HOUSE_API_KEY']
    headers = {'Authorization': 'Basic '+co_house_api_key}
    try:
        url = 'https://api.companieshouse.gov.uk/company/%s' % company_number
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        current_app.logger.info(res.json())
        company = res.json()
        url = 'https://api.companieshouse.gov.uk/company/%s/registered-office-address' % company_number
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        address = res.json()
        return (company, address)
    except Exception as e:
        current_app.logger.info(e)
        return abort(500)


def _get_premises(company_number):
    try:
        premises = current_app.db.premises.find_one({'entry.company': company_number})
        current_app.logger.info(premises)
        return premises
    except Exception as e:
        current_app.logger.info(e)
        return abort(500)

