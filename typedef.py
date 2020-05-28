class FitnessInfo:
    pass

class FailFitnessInfo(FitnessInfo):
    def __init__(self, l_eval, r_eval, op, approach_level):
        self.l_eval = l_eval
        self.r_eval = r_eval
        self.op = op
        self.approach_level = approach_level

class SuccessFitnessInfo(FitnessInfo):
    pass