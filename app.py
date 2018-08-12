
import pandas as pd

from flask import Flask, render_template

from common.utils import Util
from datab.mongo import Mongo
from core.manager import ModelManager
from core.handlers import *

class AppLogic():
    def __init__(self):
        self.dbm = Mongo()
        self.mgr = ModelManager()
        self.claim_temp = {'name': (str, ['Jon','Ola','Kari','Bente']), 'age': (int, (18,75)), 'income_knok': (float, (100,1000)), 'check_needed': (int, (0,1)), 'status':(str, [''])}

    def configure(self, model):
        self.dbm.init()
        self.dbm.add_db('test')
        self.dbm.active_db = 'test'
        if not self.dbm.fill_random('claims', self.claim_temp, 15):
            raise Exception("Failed to fill in database")

        self.mgr.add(ChallengerClaimHandler(20, 300))
        self.mgr.add(BasicClaimHandler())
        if (model == 'basic'):
            self.mgr.set_default(BasicClaimHandler)
        elif (model == 'challenger'):
            self.mgr.set_default(ChallengerClaimHandler)
        else:
            raise Exception("Unknown model %s" % model)

    def process_todays_claims(self):
        data = self.dbm.read('claims', filt={'status':''}, limit=10)
        if not data.empty:
            data['status'] = ['accepted' if res else 'rejected' for res in self.mgr.process_claims(data)]
            # TODO: need a more efficient way
            for _id, stat in zip(data['_id'], data['status']):
                self.dbm.active_db['claims'].update_many({'_id':_id}, {'$set': {'status':stat}})
        return data

app = Flask("Claim processing")

apl = AppLogic()
apl.configure('basic')

@app.route('/')
def index():
    data = apl.process_todays_claims()
    if not data.empty:
        columns = list(data.columns)
        columns.remove('_id')
        return render_template("claims.html", date=Util.datetime(), cols=columns, rows=[r for _,r in data.iterrows()])
    else:
        return "No new claims found"

if __name__ == '__main__':
    data = apl.process_todays_claims()
