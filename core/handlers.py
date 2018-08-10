
import pandas as pd

class AbstractClaimHandler():

    def classify_claim(self, claim):
        """
        Classify claim according to two classes: 
            - True (accept claim)
            - False (reject claim)
        Input:
            - claim: dataframe
        Output:
            - classification: boolean
        """
        raise NotImplementedError()

class BasicClaimHandler(AbstractClaimHandler):
    """
    Simple age-based claim classification model.
    """

    CLAIM_LIMIT_AGE = 45

    def __init__(self):
        pass

    def classify_claim(self, claim):
        return (claim.age > BasicClaimHandler.CLAIM_LIMIT_AGE)

class ChallengerClaimHandler(AbstractClaimHandler):
    """
    This model estimates claims based on age and income normalized by some border values.
    If the sum of normalized age and income is > 1, the claim is accepted.
     """

    def __init__(self, border_age, border_income):
        self._border_age = border_age
        self._border_income = border_income

    def classify_claim(self, claim):
        return ((claim.age / self._border_age + claim.income / self._border_income) > 1)
