# coding=utf-8
import sqlite3
import sys
import pandas as pd
from flask import Flask, render_template, jsonify, request
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
# 导入关联规则包
from mlxtend.frequent_patterns import association_rules

app = Flask(__name__)
app.config.from_object('config')

login_name = None

order_df = pd.read_csv('./data/GoodsOrder.csv', encoding='utf-8')
type_df = pd.read_csv('./data/GoodsTypes.csv', encoding='utf-8')

order_group = order_df.groupby(by='id')

products = []
for id_, df in order_group:
    products.append(df['Goods'].values.tolist())


# --------------------- html render ---------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/overview')
def overview():
    return render_template('overview.html')


@app.route('/products_apriori')
def products_apriori():
    return render_template('products_apriori.html')


@app.route('/products_manage')
def products_manage():
    return render_template('products_manage.html')


# ------------------ ajax restful api -------------------
@app.route('/check_login')
def check_login():
    """判断用户是否登录"""
    return jsonify({'username': login_name, 'login': login_name is not None})


@app.route('/register/<name>/<password>')
def register(name, password):
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    check_sql = "SELECT * FROM sqlite_master where type='table' and name='user'"
    cursor.execute(check_sql)
    results = cursor.fetchall()
    # 数据库表不存在
    if len(results) == 0:
        # 创建数据库表
        sql = """
                CREATE TABLE user(
                    name CHAR(256), 
                    password CHAR(256)
                );
                """
        cursor.execute(sql)
        conn.commit()
        print('创建数据库表成功！')

    sql = "INSERT INTO user (name, password) VALUES (?,?);"
    cursor.executemany(sql, [(name, password)])
    conn.commit()
    return jsonify({'info': '用户注册成功！', 'status': 'ok'})


@app.route('/login/<name>/<password>')
def login(name, password):
    global login_name
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    check_sql = "SELECT * FROM sqlite_master where type='table' and name='user'"
    cursor.execute(check_sql)
    results = cursor.fetchall()
    # 数据库表不存在
    if len(results) == 0:
        # 创建数据库表
        sql = """
                CREATE TABLE user(
                    name CHAR(256), 
                    password CHAR(256)
                );
                """
        cursor.execute(sql)
        conn.commit()
        print('创建数据库表成功！')

    sql = "select * from user where name='{}' and password='{}'".format(name, password)
    cursor.execute(sql)
    results = cursor.fetchall()

    if len(results) > 0:
        login_name = name
        return jsonify({'info': name + '用户登录成功！', 'status': 'ok'})
    else:
        return jsonify({'info': '当前用户不存在！', 'status': 'error'})


@app.route('/type_vis')
def type_vis():
    """婴儿性别和年龄数据"""
    type_counts = type_df['Types'].value_counts().reset_index()
    type_counts = type_counts.sort_values(by='count')

    # 用户一次购买商品数量分布
    product_len_counts = {}
    for pro in products:
        jian_shu = '{}件'.format(len(pro))
        if jian_shu not in product_len_counts:
            product_len_counts[jian_shu] = 0
        product_len_counts[jian_shu] += 1

    product_len_counts = sorted(product_len_counts.items(), key=lambda x: x[1], reverse=True)

    product_counts = {}
    for pros in products:
        for pro in pros:
            if pro not in product_counts:
                product_counts[pro] = 0
            product_counts[pro] += 1

    product_counts = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)

    return jsonify({
        '类别': [g for g in type_counts['Types'].values],
        '商品个数': type_counts['count'].values.tolist(),
        '购买商品个数': [pc[0] for pc in product_len_counts],
        '购买商品个数人次': [pc[1] for pc in product_len_counts],
        '商品': [pc[0] for pc in product_counts],
        '购买商品的人数': [pc[1] for pc in product_counts],
    })


@app.route('/clac_product_association/<min_support>/<min_threshold>')
def clac_product_association(min_support, min_threshold):
    """计算产品之间的关联规则"""
    te = TransactionEncoder()
    # 进行 one-hot 编码
    te_ary = te.fit(products).transform(products)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    # 利用 Apriori 找出频繁项集
    freq = apriori(df, min_support=float(min_support), use_colnames=True)
    # 计算关联规则
    result = association_rules(freq, metric="confidence", min_threshold=float(min_threshold))
    # 关联结果按照置信度或提升度高进行排序
    result = result.sort_values(by='confidence', ascending=False)
    # 结果保存
    # result.to_csv('./results/product_association_min_support{}_{}.csv'.format(min_support, min_threshold),
    #               encoding='utf8', index=False)

    results = result.to_dict(orient='records')
    for result in results:
        result['antecedents'] = str(result['antecedents'])[10: -1]  # 前因
        result['consequents'] = str(result['consequents'])[10: -1]  # 后果

    return jsonify(results)


@app.route('/calc_association/<item1>/<item2>')
def calc_association(item1, item2):
    """计算某两个产品之间的关联规则"""
    te = TransactionEncoder()
    te_ary = te.fit(products).transform(products)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    freq = apriori(df, min_support=float(0.01), use_colnames=True)
    result = association_rules(freq, metric="confidence", min_threshold=float(0))
    result['antecedents'] = result['antecedents'].apply(lambda x: ', '.join(sorted(list(x))))
    result['consequents'] = result['consequents'].apply(lambda x: ', '.join(sorted(list(x))))
    rule = result[(result['antecedents'] == item1) & (result['consequents'] == item2)]
    print(rule)
    results = rule.to_dict(orient='records')
    return jsonify(results)


@app.route('/query_products')
def query_products():
    """查询最新的产品销售数据"""
    products_str = []
    for pros in products:
        s = ''
        for pro in pros:
            s += '<span style="margin-right:10px; color:#B43104">{}</span>'.format(pro)
        products_str.append(s)
    print(products_str)
    return jsonify(products_str[::-1][:40])


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=50000)
