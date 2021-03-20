import json

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
    return render_template('about.html', error=True)


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
    rs = None
    res = None

    data = json.loads(request.form.get('data'))
    is_title = data['is_title']
    keys = data['keys']
    ingredients = data['ingredients']
    time_left = data['time_left']
    time_right = data['time_right']

    print(is_title, keys, ingredients, time_left, time_right)

    if is_title is True:
        flag, rs = Index_name().result_by_tfidf(keys)
        if len(ingredients.strip()) != 0:
            flag, rs_ing = Index_ingredient().result_by_bm25(ingredients)
            rs = list(set(rs).intersection(set(rs_ing)))

    else:
        if len(keys.strip()) != 0:
            flag, rs = Index_name_desc_ing().result_by_bm25(keys)
            if len(ingredients.strip()) != 0:
                flag, rs_ing = Index_ingredient().result_by_bm25(ingredients)
                rs = list(set(rs).intersection(set(rs_ing)))
        else:
            flag, rs = Index_ingredient().result_by_bm25(ingredients)

    if len(rs) == 0:
        return render_template('results.html', res=None)
    else:
        model = Recipes()
        if len(time_left.strip()) != 0 and len(time_right.strip()) != 0:
            # have both limit
            res = model.find_by_ids_limited(rs, int(time_left), int(time_right))
        elif len(time_left.strip()) != 0 and len(time_right.strip()) == 0:
            # have left limit
            res = model.find_by_ids_limited(rs, int(time_left), None)
        elif len(time_left.strip()) == 0 and len(time_right.strip()) != 0:
            # have right limit
            res = model.find_by_ids_limited(rs, None, int(time_right))
        elif len(time_left.strip()) == 0 and len(time_right.strip()) == 0:
            # no limit
            res = model.find_by_ids(rs)
        return render_template('results.html', res=res)


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


if __name__ == '__main__':
    # from controller.search import *
    # app.register_blueprint(search)

    from dbmodel.index_ingredient import Index_ingredient
    from dbmodel.index_name import Index_name
    from dbmodel.index_name_desc_ing import Index_name_desc_ing
    from dbmodel.recipes import Recipes
    from dbmodel.k_nearest import K_nearest

    app.run(debug=True)
