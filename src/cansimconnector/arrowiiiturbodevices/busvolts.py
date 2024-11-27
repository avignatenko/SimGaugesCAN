ELECTRICS_MIN_VOLTS = 5


def electrics_on(volts):
    return volts > ELECTRICS_MIN_VOLTS
