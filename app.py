
from flask import Flask, render_template
from pandas import DataFrame

from common.utils import Util
from datab.mongo import Mongo

app = Flask("Claim processing")

@app.route('/')
def index():
    dbm = Mongo()
    dbm.init()
    dbm.add_db('test')
    dbm.active_db = 'test'
    claim_temp = {'name': (str, ['Jon','Ola','Kari','Bente']), 'age': (int, (18,75)), 'income_knok': (float, (100,1000)), 'check_needed': (int, (0,1))}
    if not dbm.fill_random('claims', claim_temp, 10):
        print("Failed to fill in database")
    data = dbm.read('claims')
    return render_template("claims.html", date=Util.datetime(), cols=data.columns, rows=[r for _,r in data.iterrows()])
    