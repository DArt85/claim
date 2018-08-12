
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
        if not self.dbm.fill_random('claims', self.claim_temp, 1000):
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
        data = self.dbm.read('claims', filt={'status':''}, limit=20)        
        data['status'] = ['accepted' if res else 'rejected' for res in self.mgr.process_claims(data)]
        return data

app = Flask("Claim processing")

apl = AppLogic()
apl.configure('basic')

@app.route('/')
def index():
    data = apl.process_todays_claims()
    return render_template("claims.html", date=Util.datetime(), cols=data.columns, rows=[r for _,r in data.iterrows()])
