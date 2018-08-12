
import pandas as pd

from flask import Flask, render_template

from common.utils import Util
from datab.mongo import Mongo
from core.manager import ModelManager
from core.handlers import *

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
    mgr = ModelManager()
    mgr.add(BasicClaimHandler())
    mgr.add(ChallengerClaimHandler(20, 300))
    mgr.set_default(BasicClaimHandler)
    data['status'] = pd.Series(mgr.process_claims(data), index=data.index)
    return render_template("claims.html", date=Util.datetime(), cols=data.columns, rows=[r for _,r in data.iterrows()])
