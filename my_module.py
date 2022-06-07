from nowpipes import analysis


@analysis
def data(**params):
    return dict(a=10, b=20)


@analysis
def analysis1(data, **params):
    calc = data.a + 10
    return calc


@analysis
def analysis2(data, **params):
    calc = data.a + 20
    return calc


@analysis
def multiply(analysis1, analysis2, **params):
    return analysis1 * analysis2
    pass


@analysis
def more(analysis1, analysis2, multiply, **params):
    return dict(
        result1=analysis1,
        result2=analysis2,
        multi=multiply
    )
