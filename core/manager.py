
from core.handlers import *
from common.utils import Singleton

class ModelException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class ModelManager(metaclass=Singleton):
    """
    Proxy class allowing model management and containing logic to select and 
    apply handling models to claims.
    """

    def __init__(self):
        self._models = {}
        self._default_model = None

    def __len__(self):
        return len(self._models)

    def add(self, model):
        if not issubclass(model.__class__, AbstractClaimHandler) and not isinstance(model, AbstractClaimHandler):
            raise ModelException("Model should be a subclass of %s" % AbstractClaimHandler)
        if self._models.get(model.__class__):
            raise ModelException("Model %s was already added" % model.__class__)
        self._models[model.__class__] = model

    def set_default(self, model_cl):
        if not self._models.get(model_cl):
            raise ModelException("Can't set model %s before it is added" % model_cl)
        self._default_model = self._models[model_cl]

    def process_claims(self, claims):
        return [self._default_model.classify_claim(c) for c in claims]
