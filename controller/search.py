# This part has been moved to app.py

# # @File        : search.py
# # @Description :
# # @Time        : 07 March, 2021
# # @Author      : Cyan
# import json
#
# from flask import Blueprint, render_template, request
#
# from dbmodel.index_ingredient import Index_ingredient
# from dbmodel.index_name import Index_name
# from dbmodel.index_name_desc_ing import Index_name_desc_ing
# from dbmodel.recipes import Recipes
# from dbmodel.k_nearest import K_nearest
#
# search = Blueprint('search', __name__)
#
#
# @search.route('/', methods=['GET'])
# def home():
#     """
#
#     :return:
#     """
#     re = Recipes().find_rand_recipes(4)
#     return render_template('home.html', re=re)
#
#
# @search.route('/about', methods=['GET'])
# def about():
#     """
#
#     :return:
#     """
#     return render_template('about.html', error=True)
#
#
# @search.route('/recipe/<rid>', methods=['GET'])
# def recipe(rid):
#     """
#
#     :param rid:
#     :return:
#     """
#     knn = K_nearest().find_knn(rid)
#     model = Recipes()
#     re = model.find_by_id(rid)
#     res = model.find_by_ids(knn)
#     return render_template('recipe.html', re=re, res=res)
#
#
# @search.route('/recipes', methods=['GET'])
# def recipes():
#     """
#
#     :return:
#     """
#     return render_template('recipes.html')
#
#
# @search.route('/results', methods=['POST'])
# def results():
#     """
#
#     :return:
#     """
#     rs = None
#     res = None
#
#     data = json.loads(request.form.get('data'))
#     is_title = data['is_title']
#     keys = data['keys']
#     ingredients = data['ingredients']
#     time_left = data['time_left']
#     time_right = data['time_right']
#
#     print(is_title, keys, ingredients, time_left, time_right)
#
#     if is_title is True:
#         flag, rs = Index_name().result_by_tfidf(keys)
#         if len(ingredients.strip()) != 0:
#             flag, rs_ing = Index_ingredient().result_by_bm25(ingredients)
#             rs = list(set(rs).intersection(set(rs_ing)))
#
#     else:
#         if len(keys.strip()) != 0:
#             flag, rs = Index_name_desc_ing().result_by_bm25(keys)
#             if len(ingredients.strip()) != 0:
#                 flag, rs_ing = Index_ingredient().result_by_bm25(ingredients)
#                 rs = list(set(rs).intersection(set(rs_ing)))
#         else:
#             flag, rs = Index_ingredient().result_by_bm25(ingredients)
#
#     if len(rs) == 0:
#         return render_template('results.html', res=None)
#     else:
#         model = Recipes()
#         if len(time_left.strip()) != 0 and len(time_right.strip()) != 0:
#             # have both limit
#             res = model.find_by_ids_limited(rs, int(time_left), int(time_right))
#         elif len(time_left.strip()) != 0 and len(time_right.strip()) == 0:
#             # have left limit
#             res = model.find_by_ids_limited(rs, int(time_left), None)
#         elif len(time_left.strip()) == 0 and len(time_right.strip()) != 0:
#             # have right limit
#             res = model.find_by_ids_limited(rs, None, int(time_right))
#         elif len(time_left.strip()) == 0 and len(time_right.strip()) == 0:
#             # no limit
#             res = model.find_by_ids(rs)
#         return render_template('results.html', res=res)
#
#
# # @search.route('/test')
# # def test():
# #     recipe = Recipes()
# #     rs = recipe.search_by_id(4)
# #     return jsonify(result_list(rs))  # jsonify: list to json list
#
#
# # def result_list(result):
# #     li = []
# #     for row in result:
# #         dic = {}
# #         for k, v in row.__dict__.items():
# #             if not k.startswith('_sa_instance_state'):
# #                 dic[k] = v
# #                 li.append(dic)
# #
# #     return li
