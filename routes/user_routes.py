from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from utils.db_utils import execute_query, commit_changes

bp = Blueprint('user', __name__)

@bp.route('/')
def home():
    data = execute_query("SELECT prs_nbr, prs_name, prs_skill, prs_active, prs_added FROM prs_mstr")
    return render_template('index.html', data=data)

@bp.route('/addprsn')
def addprsn():
    nbr = execute_query("SELECT IFNULL(MAX(prs_nbr) + 1, 101) FROM prs_mstr")[0][0]
    return render_template('addprsn.html', newnbr=int(nbr))

@bp.route('/addprsn_submit', methods=['POST'])
def addprsn_submit():
    prsnbr = request.form.get('txtnbr')
    prsname = request.form.get('txtname')
    prsskill = request.form.get('optskill')
    execute_query(
        "INSERT INTO prs_mstr (prs_nbr, prs_name, prs_skill) VALUES (%s, %s, %s)",
        (prsnbr, prsname, prsskill)
    )
    commit_changes()
    return redirect(url_for('user.vfdataset_page', prs=prsnbr))

@bp.route('/vfdataset_page/<prs>')
def vfdataset_page(prs):
    return render_template('gendataset.html', prs=prs)

@bp.route('/countTodayScan')
def countTodayScan():
    rowcount = execute_query("SELECT COUNT(*) FROM accs_hist WHERE accs_date = CURDATE()")[0][0]
    return jsonify({'rowcount': rowcount})

@bp.route('/loadData', methods=['GET', 'POST'])
def loadData():
    data = execute_query(
        "SELECT a.accs_id, a.accs_prsn, b.prs_name, b.prs_skill, DATE_FORMAT(a.accs_added, '%H:%i:%s') "
        "FROM accs_hist a "
        "LEFT JOIN prs_mstr b ON a.accs_prsn = b.prs_nbr "
        "WHERE a.accs_date = CURDATE() "
        "ORDER BY 1 DESC"
    )
    return jsonify(response=data)
