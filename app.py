import json
import math
from time import time

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

# database path
# PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
# DATABASE = os.path.join(PROJECT_ROOT, 'data', 'se.db')

# deal with config.ini file
# with app.app_context():
#     app.iniconfig = FlaskIni()
#     app.iniconfig.read('/modules/config.ini')

# SQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/se.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

global rid_list  # global value: result rid list
global sort_type  # global value:  sort type


@app.route('/', methods=['GET'])
def index():
    """
    init index page, with four random recipes every time refresh
    :return:
    """
    re = Recipes().find_rand_recipes(4)
    return render_template('home.html', re=re)


@app.route('/about', methods=['GET'])
def about():
    """
    route to about page
    :return:
    """
    return render_template('about.html')


@app.route('/recipe/<rid>', methods=['GET'])
def recipe(rid):
    """
    route to the recipe page with the specific id
    :param rid:
    :return:
    """
    knn = K_nearest().find_knn(rid)
    model = Recipes()
    re = model.find_by_id(rid)
    res = model.find_by_ids(knn)
    return render_template('recipe.html', re=re, res=res)


@app.route('/recipes', methods=['GET'])
def recipes():
    """
    basic search page
    :return:
    """
    return render_template('recipes.html')


@app.route('/results', methods=['POST'])
def results():
    """
    search for results according to different conditions
    :return:
    """
    # get global value
    global rid_list
    global sort_type

    # get request data
    data = json.loads(request.form.get('data'))
    is_title = data['is_title']
    is_advance = data['is_advance']
    keys = data['keys']
    ingredients = data['ingredients']
    time_left = data['time_left']
    time_right = data['time_right']

    # print(is_title, is_advance, keys, ingredients, time_left, time_right)  # check

    begin_time = time()

    if is_title is True:
        rs = Index_name().result_by_tfidf(keys)
        if is_advance and len(ingredients.strip()) != 0:
            rs_ing = Index_ingredient().result_by_bm25(ingredients)
            rs = [i for i in rs if i in rs_ing]
            # rs = list(set(rs).intersection(set(rs_ing)))

    else:
        if len(keys.strip()) != 0:
            rs = Index_name_desc_ing().result_by_bm25(keys)
            if is_advance and len(ingredients.strip()) != 0:
                rs_ing = Index_ingredient().result_by_bm25(ingredients)
                rs = [i for i in rs if i in rs_ing]
                # rs = list(set(rs).intersection(set(rs_ing)))
        else:
            rs = Index_ingredient().result_by_bm25(ingredients)

    end_time = time()
    run_time = end_time - begin_time  # query time

    # get the recipes from database
    if len(rs) == 0:
        return render_template('results.html', res=None)
    else:
        model = Recipes()
        if is_advance and len(time_left.strip()) != 0 and len(time_right.strip()) != 0:
            if time_left > time_right:  # if the time limit is wrong
                return render_template('results.html', res=None)
            # have both limit
            res = model.find_by_ids_limited(rs, int(time_left), int(time_right))
        elif is_advance and len(time_left.strip()) != 0 and len(time_right.strip()) == 0:
            # have left limit
            res = model.find_by_ids_limited(rs, int(time_left), None)
        elif is_advance and len(time_left.strip()) == 0 and len(time_right.strip()) != 0:
            # have right limit
            res = model.find_by_ids_limited(rs, None, int(time_right))
        else:
            # no limit
            res = model.find_by_ids(rs)

        # reset global value rid_list
        list_res = []
        for re in res:
            list_res.append(re.to_json())
        rid_list = []
        for re in list_res:
            rid_list.append(re['id'])

        # reset global value sort_type
        sort_type = 0

        count = res.count()
        res = res.paginate(per_page=5, page=1)
        max_page = math.ceil(count / 5)
        return render_template('results.html', res=res, count=count, run_time=run_time, max_page=max_page, cur_page=1)


@app.route('/pagination', methods=['POST'])
def pagination():
    """
    ajax from pagination operation
    :return:
    """
    # get global value
    global rid_list
    global sort_type

    if 'stype' in request.form:
        sort_type = int(request.form['stype'])

    cur_page = int(request.form['page'])
    res = Recipes().get_sort_list(rid_list, sort_type)

    # update global list
    list_res = []
    for re in res:
        list_res.append(re.to_json())
    rid_list = []
    for re in list_res:
        rid_list.append(re['id'])

    count = res.count()
    res = res.paginate(per_page=5, page=cur_page)
    max_page = math.ceil(count / 5)

    return render_template('pagination.html', res=res, max_page=max_page, cur_page=cur_page)


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    """
    autocomplete function, add by yefei
    :return:
    """
    keys = request.form['keys']
    rs = Recipes().find_by_name_fuzzy(keys)

    list_rs = []
    for r in rs:
        list_rs.append(r.to_json())

    res = []
    for rs in list_rs:
        res.append(rs['name'])

    return jsonify(res)


@app.template_filter('big_number')
def big_number(number):
    """
    custom filter for big number, 1000 -> 1,000
    :param number:
    :return:
    """
    return format(format(number, ','))


if __name__ == '__main__':
    # from controller.search import *
    # app.register_blueprint(search)

    from dbmodel.index_ingredient import Index_ingredient
    from dbmodel.index_name import Index_name
    from dbmodel.index_name_desc_ing import Index_name_desc_ing
    from dbmodel.recipes import Recipes
    from dbmodel.k_nearest import K_nearest

    app.run(debug=True)
