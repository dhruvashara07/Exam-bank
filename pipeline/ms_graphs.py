"""Maths mark schemes: graphs printed as calculator SCREENSHOTS are drawn again from the function the question gives
(Dhruv, round 32: 'redraw in the same grid, black and white and clear, the function in the top right corner').

SPECS is data read from the question paper by eye (like ms.MS_RELABEL): the function(s) and the window the question's
own axes show. The drawing: a light grey grid, black axes with arrows and the question's labelled ticks, curves in
black (split where they jump: asymptotes), the function(s) written in the top right corner.
"""
import math

# (question id, mark-scheme row label) -> spec. 'f': [(python expression in x, label as printed)], 'x' / 'y': window,
# 'xt' / 'yt': labelled ticks (as on the question's axes), 'grid': grid step (x, y), 'ylab': y-axis letter.
SPECS = {
    ('0607_2024FM_42_q10', '10(b)(i)'): {'f': [('(3*x-2)/(5-2*x)', 'y = (3x − 2)/(5 − 2x)')], 'x': (-2, 6), 'y': (-10, 10),
                                         'labels': [[('i', 'y'), ('t', ' = '), ('frac', '3x − 2', '5 − 2x')]],
                                         'xt': [-2, 2, 4, 6], 'yt': [-10, -5, 5, 10], 'grid': (1, 2.5)},
    ('0607_2024MJ_42_q03', '3(b)(i)'): {'f': [('2**x - 1/x', 'f(x) = 2ˣ − 1/x')], 'x': (-3, 3), 'y': (-5, 8),
                                        'labels': [[('t', 'f('), ('i', 'x'), ('t', ') = 2'), ('sup', 'x'), ('t', ' − '), ('frac', '1', 'x')]],
                                        'xt': [-3, 3], 'yt': [-5, 8], 'grid': (1, 1)},
    ('0607_2024MJ_42_q03', '3(b)(iv)(a)'): {'f': [('2**x - 1/x', 'f(x) = 2ˣ − 1/x'), ('3 - x', 'g(x) = 3 − x')],
                                            'x': (-3, 3), 'y': (-5, 8), 'xt': [-3, 3], 'yt': [-5, 8], 'grid': (1, 1),
                                            'labels': [[('t', 'f('), ('i', 'x'), ('t', ') = 2'), ('sup', 'x'), ('t', ' − '), ('frac', '1', 'x')],
                                                       [('t', 'g('), ('i', 'x'), ('t', ') = 3 − '), ('i', 'x')]]},
    ('0607_2024MJ_43_q10', '10(f)'): {'f': [('math.sin(math.radians(3*(x+1)))', 'y = sin(3(x + 1))'),
                                            ('1 - 0.01*x', 'y = 1 − 0.01x')],
                                      'x': (0, 180), 'y': (-2, 2), 'xt': [180], 'yt': [-2, 2], 'grid': (30, 0.5),
                                      'labels': [[('i', 'y'), ('t', ' = sin(3('), ('i', 'x'), ('t', ' + 1))')],
                                                 [('i', 'y'), ('t', ' = 1 − 0.01'), ('i', 'x')]]},
    ('0607_2024MJ_61_q13', '13(b)(iii)'): {'f': [('x - 1 + math.sqrt(1 - x)', 'G = x − 1 + √(1 − x)')], 'x': (0, 1),
                                           'y': (0, 0.5), 'xt': [1], 'yt': [0.5], 'grid': (0.1, 0.05), 'ylab': 'G',
                                           'labels': [[('i', 'G'), ('t', ' = '), ('i', 'x'), ('t', ' − 1 + √(1 − '), ('i', 'x'), ('t', ')')]]},
    ('0607_2023MJ_63_q12', '12(c)(iii)'): {'f': [('1.12*2**(-x) - 0.12', 'R = 1.12 × 2⁻ʰ − 0.12')], 'x': (0, 52), 'y': (-0.2, 1.0),
                                           'xt': [8, 16, 24, 32, 40, 48], 'yt': [-0.2, 0.2, 0.4, 0.6, 0.8, 1.0], 'grid': (4, 0.2),
                                           'ylab': 'R', 'xlab': 'h', 'xlow': True,      # (round 34: a blurred screenshot, redrawn from the model)
                                           'labels': [[('i', 'R'), ('t', ' = 1.12 × 2'), ('sup', '–h'), ('t', ' – 0.12')]]},
    ('0607_2020ON_62_q06', '6(a)'): {'f': [], 'label': False, 'vector': True, 'x': (9, 20), 'y': (900, 1100), 'grid': (1, 10),   # the 12
                                     'xt': list(range(9, 21)), 'yt': [950, 1000, 1050, 1100], 'xlab': 't', 'ylab': 'L',  # points
                                     'points': [(9, 960), (10, 959), (11, 960), (12, 960), (13, 960), (14, 959), (15, 960),  # of
                                                (16, 987), (17, 1014), (18, 1041), (19, 1068), (20, 1095)]},   # the question's table
    ('0607_2020ON_43_q08', '8(a)(iii)'): {'f': [('1.5**(-x)', ''), ('x**2', '')], 'label': False, 'dash': False, 'vector': True, 'col': 3,  # faint
                                          'x': (-2, 2), 'y': (0, 4), 'grid': (1, 1), 'xt': [-2, 2], 'yt': [4]},  # (round 37)
    ('0607_2018ON_61_q05', '5(b)(i)'): {'f': [('math.sqrt(x*x - 2.25)', '')], 'label': False, 'x': (-6, 6), 'y': (0, 6),
                                        'grid': (1, 1), 'xt': [-6, 6], 'yt': [6]},     # blurry screenshot (round 37)
    ('0607_2018ON_61_q06', '6(c)'): {'f': [('x*math.cos(math.radians(76))', ''), ('0.139*x', '')], 'label': False,
                                     'dash': False, 'x': (0, 6), 'y': (0, 2), 'grid': (0.5, 0.25),       # z = x cos 76,
                                     'xt': [1, 2, 3, 4, 5, 6], 'yt': [1, 2], 'xlab': 'x', 'ylab': 'z'},  # z = 0.139x (round 37)
    ('0607_2019ON_61_q05', '5(a)(ii)'): {'f': [('12 - 1.8*math.cos(math.radians(x))', 'y = 12 − 1.8 cos t°')],     # (round 35:
                                         'x': (0, 360), 'y': (0, 14), 'grid': (20, 2), 'ylab': 'y', 'xlab': 't',  # a blurred
                                         'xt': [60, 120, 180, 240, 300, 360], 'yt': [2, 4, 6, 8, 10, 12, 14],    # screenshot;
                                         'label': False},   # the question's model; no function label: the printed
                                                            # MS shows none (Dhruv round 36: a label only where the original has one)
    ('0607_2023MJ_32_q11', '11(a)'): {'w': 250.0, 'h': 200.0, 'tree': {         # (round 34: a blurred handwriting-style picture of the
        'first': [('0.80', ['wakes before', '7am']), ('0.20', ['does not', 'wake before', '7am'])],       # completed tree,
        'second': [[('0.92', ['gets to school', 'on time']), ('0.08', ['does not', 'get to school', 'on time'])],     # drawn again
                   [('0.23', ['gets to school', 'on time']), ('0.77', ['does not', 'get to school', 'on time'])]]}},   # like the question's)
}


# The screenshot redraw batch (Dhruv 2026-11-22/24): every blurry calculator screenshot in the M2 + M3 mark schemes drawn
# again from the question's function on the question's own axes (ticks as printed there), no function label unless the
# screenshot prints one. 'kept' (left as printed, docs/ERROR_PATTERNS 264): sketches with no axes in the question.
NO = {'label': False, 'dash': False}
# Pictures left as printed by Dhruv's decision (maths_check.picture_checks flags every other screenshot / faint picture):
# (question id, MS row label or figure suffix) -> why
KEPT = {
    ('0607_2020MJ_31_q11', '11(a)(i)'): 'Venn: Dhruv ok round 37', ('0607_2020MJ_31_q11', '11(b)(i)'): 'Venn: Dhruv ok round 37',
}
HERD = [(1, 20), (2, 36), (3, 64), (4, 116), (5, 208), (6, 374), (7, 674), (8, 1214)]   # 2021 ON 62 (MS 5(b)(i))
SPECS.update({
    # 2021 MJ
    ('0607_2021MJ_31_q12', '12(a)(i)'): dict(NO, f=[('x**3 + 3*x**2', '')], x=(-3, 2), y=(-10, 25), grid=(1, 5), xt=[-3, 2], yt=[-10, 25]),
    ('0607_2021MJ_31_q12', '12(b)'): dict(NO, f=[('x**3 + 3*x**2', ''), ('3*x**2 - 5', '')], x=(-3, 2), y=(-10, 25), grid=(1, 5),
                                          xt=[-3, 2], yt=[-10, 25]),
    ('0607_2021MJ_32_q06', '6(b)(i)'): dict(NO, f=[('2*x**2 - 4*x', '')], x=(-1, 3), y=(-3, 6), grid=(0.5, 1), xt=[-1, 3], yt=[-3, 6]),
    ('0607_2021MJ_33_q11', '11(a)(i)'): dict(NO, f=[('x**2 + 2*x + 1', '')], x=(-3, 2), y=(-1, 10), grid=(1, 1), xt=[-3, 2], yt=[-1, 10]),
    ('0607_2021MJ_33_q11', '11(b)'): dict(NO, f=[('x**2 + 2*x + 1', ''), ('2**x', '')], x=(-3, 2), y=(-1, 10), grid=(1, 1),
                                          xt=[-3, 2], yt=[-1, 10]),
    ('0607_2021MJ_41_q05', '5(f)(i)'): dict(NO, f=[('x**2', '')], x=(-3, 3), y=(-2, 10), grid=(1, 1), xt=[-3, 3], yt=[-2, 10]),
    ('0607_2021MJ_41_q05', '5(f)(iii)'): dict(NO, f=[('x**2', ''), ('3 - x', '')], x=(-3, 3), y=(-2, 10), grid=(1, 1), xt=[-3, 3], yt=[-2, 10]),
    ('0607_2021MJ_41_q11', '11(a)'): dict(NO, f=[('5**x', ''), ('10', '')], x=(-1, 3), y=(-1, 12), grid=(0.5, 1), xt=[-1, 3], yt=[-1, 12]),
    ('0607_2021MJ_42_q04', '4(a)'): dict(f=[('abs(10 - x**2)', '')], dash=False, x=(-5, 5), y=(-15, 15), grid=(1, 5), xt=[-5, 5], yt=[-15, 15],
                                         labels=[[('t', 'f('), ('i', 'x'), ('t', ') = |10 − '), ('i', 'x'), ('sup', '2'), ('t', '|')]]),
    ('0607_2021MJ_42_q13', '13(a)'): dict(f=[('(x**2 + 3)/((1 - x)*(x + 3))', '')], dash=False, x=(-5, 5), y=(-5, 5), grid=(1, 1),
                                          xt=[-5, 5], yt=[-5, 5],
                                          labels=[[('t', 'f('), ('i', 'x'), ('t', ') = '), ('frac', 'x² + 3', '(1 − x)(x + 3)')]]),
    ('0607_2021MJ_43_q09', '9(a)'): dict(NO, f=[('x**x', '')], x=(0, 2.5), y=(0, 10), grid=(0.5, 1), xt=[2.5], yt=[10]),
    ('0607_2021MJ_62_q03', '3(b)'): dict(NO, h=1.0, f=[], x=(0, 12), y=(0, 20), grid=(1, 2), xt=[2, 4, 6, 8, 10, 12], yt=[5, 10, 15, 20],   # h: the picture's height (text under it)
                                         xlab='n', ylab='d²', points=[(1, 1), (2, 2), (3, 4), (4, 5), (5, 8), (6, 9), (7, 10),
                                                                      (8, 13), (9, 16), (10, 17), (11, 18)]),   # d² against n
    ('0607_2021MJ_62_q08', '8(a)'): dict(NO, f=[], x=(0, 25), y=(0, 1), grid=(1, 0.1), xt=[5, 10, 15, 20, 25], yt=[0.5, 1],
                                         xlab='F', ylab='p', points=[(2, 0.99), (4, 0.85), (6, 0.56), (8, 0.26), (10, 0.11), (12, 0.04),
                                                                     (14, 0.02), (16, 0.02), (18, 0.02), (20, 0.02), (22, 0.01)]),
    ('0607_2021MJ_62_q09', '9(c)(i)'): dict(NO, f=[('math.exp(-(x/8)**0.5)', ''), ('math.exp(-(x/8)**1)', ''), ('math.exp(-(x/8)**2.5)', ''),
                                                   ('math.exp(-(x/8)**10)', '')], x=(0, 25), y=(0, 1), grid=(5, 0.25),
                                            xt=[5, 10, 15, 20, 25], yt=[1], xlab='F', ylab='p',
                                            tags=[(20, 0.31, 'a=0.5'), (18, 0.145, 'a=1'), (4.5, 0.81, 'a=2.5'), (9.0, 0.93, 'a=10')]),
    ('0607_2021MJ_63_q04', '4(a)(i)'): dict(NO, f=[('math.cos(math.radians(2*x))', '')], x=(0, 360), y=(-1, 1), grid=(30, 0.5),
                                            xt=[90, 180, 270, 360], yt=[-1, 1]),
    ('0607_2021MJ_63_q06', '6(b)'): dict(NO, f=[('0.4*0.7**x*math.cos(math.radians(200*x)) + 0.6', '')], x=(0, 5), y=(0, 1.2),
                                         grid=(0.5, 0.2), xt=[5], yt=[], xlab='t', ylab='d'),
    ('0607_2021MJ_63_q07', '7(d)'): dict(NO, f=[('1 + 2.4*x**2*(x - 1) - 0.6*x**4', '')], x=(0, 3), y=(-0.5, 1.2),   # a = 2.4,
                                         grid=(0.5, 0.25), xt=[1, 2, 3], yt=[1], xlab='t', ylab='D'),            # b = -0.6 (MS)
    # 2021 ON
    ('0607_2021ON_22_q10', '10(a)'): {'venn': {'sets': 'PQ', 'shade': 'not (P or Q)'}, 'w': 200.0, 'h': 100.0},
    ('0607_2021ON_31_q07', '7(b)(i)'): {'w': 260.0, 'h': 200.0, 'tree': {
        'first': [('16/30', ['Grape']), ('14/30', ['Cherry'])],
        'second': [[('15/29', ['Grape']), ('14/29', ['Cherry'])], [('16/29', ['Grape']), ('13/29', ['Cherry'])]]}},
    ('0607_2021ON_31_q12', '12(a)'): dict(NO, f=[('x**3', '')], x=(-2, 2), y=(-8, 8), grid=(0.5, 2), xt=[-2, 2], yt=[-8, 8]),
    ('0607_2021ON_31_q12', '12(c)'): dict(NO, f=[('x**3', ''), ('2*x', '')], x=(-2, 2), y=(-8, 8), grid=(0.5, 2), xt=[-2, 2], yt=[-8, 8]),
    ('0607_2021ON_32_q11', '11(a)(i)'): dict(NO, f=[('7 - x**2', '')], x=(-3, 3), y=(-3, 10), grid=(1, 1), xt=[-3, 3], yt=[-3, 10]),
    ('0607_2021ON_32_q11', '11(b)(i)'): dict(NO, f=[('7 - x**2', ''), ('6/x**2', '')], x=(-3, 3), y=(-3, 10), grid=(1, 1),
                                             xt=[-3, 3], yt=[-3, 10]),
    ('0607_2021ON_62_q05', '5(b)(ii)'): dict(NO, f=[], x=(0, 8), y=(0, 1400), grid=(0.5, 100), xt=[1, 2, 3, 4, 5, 6, 7, 8],
                                             yt=[200, 400, 600, 800, 1000, 1200, 1400], xlab='n', ylab='P', points=HERD),
    ('0607_2021ON_62_q06', '6(b)(ii)'): dict(NO, f=[('8*(x - 1)**2 + 8*(x - 1) + 20 if x >= 1 else None', '')], x=(0, 8), y=(0, 1400),
                                             grid=(0.5, 100), xt=[1, 2, 3, 4, 5, 6, 7, 8], yt=[200, 400, 600, 800, 1000, 1200, 1400],
                                             xlab='n', ylab='P', points=HERD),      # a = 8, b = 8 (MS 6(b)(i))
    ('0607_2021ON_62_q07', '7(b)'): dict(NO, f=[('36*(x - 1)**1.07 if x >= 1 else None', '')], x=(0, 8), y=(0, 1400),
                                         grid=(0.5, 100), xt=[1, 2, 3, 4, 5, 6, 7, 8], yt=[200, 400, 600, 800, 1000, 1200, 1400],
                                         xlab='n', ylab='P', points=HERD),          # P = 36(n - 1)^1.07 (MS 7(a)(ii))
    # 2022 MJ
    ('0607_2022MJ_21_q11', '11(a)'): {'venn': {'sets': 'PQ', 'shade': 'P or Q'}, 'w': 180.0, 'h': 100.0},
    ('0607_2022MJ_33_q02', '2(f)'): {'bars': [('Sugar', 2000), ('Raisin', 2500), ('Cream', 1500), ('Jam', 1250), ('Iced', 750)],
                                     'y': (0, 3000), 'yt': [0, 500, 1000, 1500, 2000, 2500, 3000], 'grid': (None, 250),
                                     'w': 230.0, 'h': 170.0},
    ('0607_2022MJ_33_q10', '10(a)'): dict(NO, f=[('x**3 + 1/x', '')], x=(-2, 2), y=(-10, 10), grid=(0.5, 2), xt=[-2, 2], yt=[-10, 10]),
    ('0607_2022MJ_33_q10', '10(d)'): dict(NO, f=[('x**3 + 1/x', ''), ('5*x', '')], x=(-2, 2), y=(-10, 10), grid=(0.5, 2),
                                          xt=[-2, 2], yt=[-10, 10]),
    ('0607_2022MJ_33_q11', '11(a)'): {'w': 250.0, 'h': 170.0, 'tree': {
        'first': [('6/10', ['snows']), ('4/10', ['does not', 'snow'])],
        'second': [[('2/5', ['goes for', 'a walk']), ('3/5', ['does not go', 'for a walk'])],
                   [('5/7', ['goes for', 'a walk']), ('2/7', ['does not go', 'for a walk'])]]}},
    ('0607_2022MJ_41_q03', '3(a)'): dict(NO, f=[('2*x + 4 - 1/x**2', '')], x=(-3, 1), y=(-5, 5), grid=(0.5, 1), xt=[-3, 1], yt=[-5, 5]),
    ('0607_2022MJ_42_q04', '4(a)'): dict(NO, f=[('4 - 2*abs(x)', ''), ('0.25*x**2', '')], x=(-4, 4), y=(-4, 4), grid=(1, 1),
                                         xt=[-4, 4], yt=[-4, 4]),
    ('0607_2022MJ_43_q05', '5(a)'): dict(f=[('x**3 - 5*x + 3', ''), ('x**2 - 2*x + 2', '')], x=(-3, 3), y=(-10, 20), grid=(1, 5),
                                         xt=[-3, 3], yt=[-10, 20],
                                         labels=[[('t', 'f('), ('i', 'x'), ('t', ') = '), ('i', 'x'), ('sup', '3'), ('t', ' − 5'), ('i', 'x'), ('t', ' + 3')],
                                                 [('t', 'g('), ('i', 'x'), ('t', ') = '), ('i', 'x'), ('sup', '2'), ('t', ' − 2'), ('i', 'x'), ('t', ' + 2')]]),
    ('0607_2022MJ_43_q07', '7(a)'): {'venn': [{'sets': 'AB', 'shade': 'not (A or B)', 'cap': "(A ∪ B)'"},
                                              {'sets': 'PQ', 'shade': '(P and not Q) or (Q and not P)', 'cap': "(P ∩ Q') ∪ (P' ∩ Q)"}],
                                     'stack': True, 'w': 190.0, 'h': 230.0},
    # 2022 ON
    ('0607_2022ON_31_q11', '11(a)(i)'): dict(NO, f=[('x**2 - 1', '')], x=(-2, 2), y=(-7, 7), grid=(0.5, 1), xt=[-2, 2], yt=[-7, 7]),
    ('0607_2022ON_31_q11', '11(b)(i)'): dict(NO, f=[('x**2 - 1', ''), ('x**3 - x', '')], x=(-2, 2), y=(-7, 7), grid=(0.5, 1),
                                             xt=[-2, 2], yt=[-7, 7]),
    ('0607_2022ON_32_q11', '11(a)'): dict(NO, f=[('-x**2 + 4*x + 5', '')], x=(-2, 6), y=(-7, 10), grid=(1, 1), xt=[-2, 6], yt=[-7, 10]),
    ('0607_2022ON_41_q05', '5(d)'): dict(NO, f=[('1/((x - 1)*(x - 2)*(x - 3))', ''), ('x - 1', '')], x=(-1, 5), y=(-4, 4),
                                         grid=(0.5, 1), xt=[-1, 5], yt=[-4, 4]),
    ('0607_2022ON_42_q11', '11(a)'): dict(f=[('x + 5/((x - 2)*(x + 3))', '')], dash=False, label=False, x=(-5, 5), y=(-9, 8), grid=(1, 1),
                                          xt=[-5, 5], yt=[-9, 8],
                                          labels=[[('t', 'f('), ('i', 'x'), ('t', ') = '), ('i', 'x'), ('t', ' + '), ('frac', '5', '(x − 2)(x + 3)')]]),   # (round 38: no label)
    ('0607_2022ON_43_q02', '2(a)'): dict(NO, f=[('1/x - 1/x**2', '')], x=(-5, 5), y=(-3, 1), grid=(1, 0.5), xt=[-5, 5], yt=[-3, 1]),
    ('0607_2022ON_61_q09', '9(b)'): dict(NO, f=[('-28*x**2 + 676*x - 2740', '')], x=(0, 25), y=(-3000, 1500), grid=(5, 500),
                                         xt=[25], yt=[], ylab='P'),
    ('0607_2022ON_62_q08', '8(c)'): dict(NO, f=[('2400/(100 - x)', '')], x=(0, 90), y=(0, 250), grid=(10, 25), xt=[90], yt=[], ylab='T'),
    ('0607_2022ON_62_q08', '8(e)(i)'): dict(NO, h=1.0, f=[('2400/(100 - x)', '')], x=(0, 100), y=(0, 500), grid=(10, 50), xt=[90], yt=[],
                                            ylab='T', vlines=[95]),
    ('0607_2022ON_63_q07', '7(b)(ii)'): dict(NO, f=[('9.92/(0.64 - x**2) + 10', '')], x=(0, 5), y=(-50, 150), grid=(0.5, 25),
                                             xt=[5], yt=[-50, 150], xlab='v', ylab='T'),
    # 2023 FM
    ('0607_2023FM_32_q02', '2(c)'): {'bars': [('2', 3), ('3', 3), ('4', 4), ('5', 2), ('6', 5), ('7', 6), ('8', 2)], 'y': (0, 6),
                                     'yt': [0, 1, 2, 3, 4, 5, 6], 'grid': (None, 0.5), 'w': 230.0, 'h': 120.0},
    ('0607_2023FM_32_q12', '12(a)'): dict(NO, f=[('(3*x + 2)/x', '')], x=(-3, 3), y=(-3, 6), grid=(0.5, 1), xt=[-3, 3], yt=[-3, 6]),
    ('0607_2023FM_32_q12', '12(c)'): dict(NO, f=[('(3*x + 2)/x', ''), ('x + 3', '')], x=(-3, 3), y=(-3, 6), grid=(0.5, 1),
                                          xt=[-3, 3], yt=[-3, 6]),
    ('0607_2023FM_42_q06', '6(a)'): dict(NO, f=[('2 - x**2/(x**2 - x - 2)', '')], x=(-5, 5), y=(-5, 5), grid=(1, 1), xt=[-5, 5], yt=[-5, 5]),
    ('0607_2023FM_42_q06', '6(d)'): dict(NO, f=[('2 - x**2/(x**2 - x - 2)', ''), ('3 - x if x >= -2 else None', '')], x=(-5, 5),
                                         y=(-5, 5), grid=(1, 1), xt=[-5, 5], yt=[-5, 5]),
    # 2023 MJ
    ('0607_2023MJ_31_q11', '11(a)(i)'): dict(NO, f=[('3*2**x', '')], x=(-1, 3), y=(-5, 25), grid=(0.5, 5), xt=[-1, 3], yt=[-5, 25]),
    ('0607_2023MJ_31_q11', '11(b)'): dict(NO, f=[('3*2**x', ''), ('4*x + 3', '')], x=(-1, 3), y=(-5, 25), grid=(0.5, 5),
                                          xt=[-1, 3], yt=[-5, 25]),
    ('0607_2023MJ_32_q12', '12(a)'): dict(NO, f=[('2*x**2 - 5*x - 3', '')], x=(-2, 5), y=(-10, 25), grid=(1, 5), xt=[-2, 5], yt=[-10, 25]),
    ('0607_2023MJ_32_q12', '12(b)'): dict(NO, f=[('2*x**2 - 5*x - 3', ''), ('x + 5', '')], x=(-2, 5), y=(-10, 25), grid=(1, 5),
                                          xt=[-2, 5], yt=[-10, 25]),
    ('0607_2023MJ_33_q06', '6(b)(i)'): {'w': 250.0, 'h': 170.0, 'tree': {
        'first': [('0.80', ['Fries']), ('0.20', ['No fries'])],
        'second': [[('0.80', ['Fries']), ('0.20', ['No fries'])], [('0.80', ['Fries']), ('0.20', ['No fries'])]]}},
    ('0607_2023MJ_33_q11', '11(a)(i)'): dict(NO, f=[('x**2 + 7*x', '')], x=(-8, 3), y=(-15, 30), grid=(1, 5), xt=[-8, 3], yt=[-15, 30]),
    ('0607_2023MJ_33_q11', '11(b)'): dict(NO, f=[('x**2 + 7*x', ''), ('36/x', '')], x=(-8, 3), y=(-15, 30), grid=(1, 5),
                                          xt=[-8, 3], yt=[-15, 30]),
    ('0607_2023MJ_41_q03', '3(a)'): dict(NO, f=[('abs(math.cos(math.radians(x)))', '')], x=(0, 360), y=(-1, 1), grid=(30, 0.5),
                                         xt=[360], yt=[-1, 1]),
    ('0607_2023MJ_42_q06', '6(a)'): dict(NO, f=[('(x**2 + 3*x)/((x - 2)*(x + 1))', '')], x=(-6, 6), y=(-9, 9), grid=(1, 3),
                                         xt=[-6, 6], yt=[-9, 9]),
    ('0607_2023MJ_42_q06', '6(d)(i)'): dict(NO, f=[('(x**2 + 3*x)/((x - 2)*(x + 1))', ''), ('x - 3', '')], x=(-6, 6), y=(-9, 9),
                                            grid=(1, 3), xt=[-6, 6], yt=[-9, 9]),
    ('0607_2023MJ_63_q10', '10(a)'): dict(NO, f=[('2**(-x)', ''), ('2**(-x/5)', '')], x=(0, 5), y=(0, 1), grid=(0.5, 0.1),
                                          xt=[5], yt=[1], xlab='d', ylab='R'),          # R = 2^(-d/p), p = 1 and 5
    # 2023 ON
    ('0607_2023ON_22_q11', '11(a)'): {'venn': {'sets': 'AB', 'shade': 'not (A or B)'}, 'w': 180.0, 'h': 100.0},
    ('0607_2023ON_42_q05', '5(a)(i)'): dict(NO, f=[('-0.5*x + 3', ''), ('(x + 5)/2', ''), ('x', '')], x=(-6, 7), y=(-5, 8),
                                            grid=(1, 1), xt=[-6, 7], yt=[-5, 8]),
    ('0607_2023ON_42_q05', '5(b)(i)'): dict(NO, f=[('(x - 2)**3 - 5*x + 12', '')], x=(-1, 4.7), y=(-10, 9), grid=(0.5, 1),
                                            xt=[-1, 4.7], yt=[-10, 9]),
    ('0607_2023ON_42_q05', '5(b)(iv)'): dict(NO, f=[('(x - 2)**3 - 5*x + 12', ''), ('-(x - 1)**2', '')], x=(-1, 4.7), y=(-10, 9),
                                             grid=(0.5, 1), xt=[-1, 4.7], yt=[-10, 9]),
    ('0607_2023ON_43_q04', '4(a)'): dict(f=[('2*x**3 - 3*x**2 - 12*x + 7', '')], dash=False, x=(-3, 4), y=(-40, 40), grid=(1, 10),
                                         xt=[-3, 4], yt=[-40, 40],
                                         labels=[[('t', 'f('), ('i', 'x'), ('t', ') = 2'), ('i', 'x'), ('sup', '3'), ('t', ' − 3'), ('i', 'x'),
                                                  ('sup', '2'), ('t', ' − 12'), ('i', 'x'), ('t', ' + 7')]]),
    ('0607_2023ON_43_q10', '10(b)(i)'): dict(f=[('(4*x - 1)/(3 - 2*x)', '')], dash=False, x=(-2, 4), y=(-10, 10), grid=(0.5, 2),
                                             xt=[-2, 4], yt=[-10, 10], labels=[[('i', 'y'), ('t', ' = '), ('frac', '4x − 1', '3 − 2x')]]),
    ('0607_2023ON_61_q06', '6(b)'): dict(NO, h=1.0, f=[('7*x', '')], x=(0, 10), y=(0, 70), grid=(1, 10), xt=[2, 4, 6, 8, 10],
                                         yt=[35, 70], xlab='a', ylab='b'),          # b = 7a (MS 6(a))
    ('0607_2023ON_62_q06', '6(a)(ii)'): dict(NO, f=[('8/x + x/2', '')], x=(0, 8), y=(0, 10), grid=(1, 1), xt=[8], yt=[10],
                                             xlab='h', ylab='r'),                                     # w = 8 (MS 6(a)(i))
    ('0607_2023ON_62_q07', '7(b)(ii)'): dict(NO, f=[('8/x + x/2', ''), ('x**2/8 + 2', '')], x=(0, 8), y=(0, 10), grid=(1, 1),
                                             xt=[8], yt=[10], xlab='h', ylab='r'),                    # lancet r = h²/8 + 2 (MS 7(b)(i))
    ('0607_2023ON_63_q05', '5(c)(iii)'): dict(NO, h=1.0, f=[('8*x', '')], x=(0, 25), y=(0, 200), grid=(5, 25), xt=[25], yt=[200],
                                              xlab='h', ylab='t'),                                    # t = 8h (MS 5(c))
    # 2018 (M3)
    ('0607_2018MJ_31_q11', '11(a)'): dict(NO, f=[('-2*x**2 + 12*x - 10', '')], x=(0, 6), y=(-10, 10), grid=(1, 2), xt=[6], yt=[-10, 10]),
    ('0607_2018MJ_42_q02', '2(a)'): dict(NO, f=[('1 - x/(x**2 - 9)', '')], x=(-5, 5), y=(-5, 5), grid=(1, 1), xt=[-5, 5], yt=[-5, 5]),
    ('0607_2018ON_41_q09', '9(a)'): dict(NO, f=[('x**3 - 3*x**2 - 4*x + 1', '')], x=(-3, 5), y=(-50, 50), grid=(1, 10),
                                         xt=[-3, 5], yt=[-50, 50]),
    ('0607_2018ON_62_q06', '6(a)(iv)'): dict(NO, f=[('1.5*x*(15/math.cos(math.radians(30)) - 2*x)**2*math.sin(math.radians(120)) if x <= 8.66 else None', '')],
                                             x=(0, 9), y=(0, 550), grid=(1, 50), xt=[9], yt=[550], ylab='V'),
    ('0607_2018ON_63_q05', '5(b)(ii)'): dict(NO, f=[('-0.46*x**2 + 8.7*x - 32.8', '')], x=(5, 12), y=(-2, 10), grid=(1, 2),
                                             xt=[5, 12], yt=[2, 4, 6, 8, 10], xlab='r', ylab='d'),
    ('0607_2018ON_63_q06', '6(a)'): dict(NO, f=[('math.sin(math.radians(x))*math.cos(math.radians(x))', '')], x=(0, 90), y=(0, 0.6),
                                         grid=(10, 0.1), xt=[90], yt=[0.5], xlab='a'),
    # 2020 (M3)
    ('0607_2020MJ_23_q15', '15(a)'): {'venn': {'sets': 'ABC', 'shade': 'A and B and not C'}, 'w': 180.0, 'h': 110.0},
    ('0607_2020MJ_31_q09', '9(b)'): dict(NO, f=[('-2*x**2 + 5*x + 3', ''), ('2*x + 1', '')], x=(-1, 3.5), y=(-4, 8), grid=(0.5, 1),
                                         xt=[-1, 3.5], yt=[-4, 8]),
    ('0607_2020MJ_32_q11', '11(a)(i)'): dict(NO, f=[('x**2 + 2*x - 8', '')], x=(-5, 5), y=(-20, 30), grid=(1, 5), xt=[-5, 5], yt=[-20, 30]),
    ('0607_2020MJ_32_q11', '11(b)'): dict(NO, f=[('x**2 + 2*x - 8', ''), ('3*x - 2', '')], x=(-5, 5), y=(-20, 30), grid=(1, 5),
                                          xt=[-5, 5], yt=[-20, 30]),
    ('0607_2020MJ_62_q07', '7(c)'): dict(NO, f=[('36.1*x', ''), ('22*x', '')], x=(0, 3), y=(0, 110), grid=(0.5, 10), xt=[3],
                                         yt=[20, 40, 60, 80, 100], xlab='t', ylab='d'),          # 130 km/h and d = 22t (MS 7(a), 7(b))
    ('0607_2020MJ_62_q07', '7(d)'): dict(NO, f=[('36.1*x', ''), ('22*x', '')], band=('22*x', '36.1*x'), x=(0, 3), y=(0, 110),
                                         grid=(0.5, 10), xt=[3], yt=[20, 40, 60, 80, 100], xlab='t', ylab='d'),
    ('0607_2020MJ_62_q09', '9(c)'): dict(NO, f=[('x**2/6', ''), ('x**2/14', '')], x=(0, 20), y=(0, 70), grid=(2, 10), xt=[20],
                                         yt=[10, 20, 30, 40, 50, 60, 70], xlab='v', ylab='b'),   # b = v²/14, v²/6 (MS 9(a), 9(b))
    ('0607_2020ON_31_q09', '9(a)(i)'): dict(NO, f=[('x**2 + 4*x + 3', '')], x=(-6, 4), y=(-10, 40), grid=(1, 5), xt=[-6, 4], yt=[-10, 40]),
    ('0607_2020ON_31_q09', '9(b)'): dict(NO, f=[('x**2 + 4*x + 3', ''), ('-x**2 - 2*x + 15', '')], x=(-6, 4), y=(-10, 40), grid=(1, 5),
                                         xt=[-6, 4], yt=[-10, 40]),
    ('0607_2020ON_32_q10', '10(a)(i)'): dict(NO, f=[('8*1.4**(-x) + 2', '')], x=(-1, 12), y=(-1, 15), grid=(1, 1), xt=[-1, 12], yt=[-1, 15]),
    ('0607_2020ON_32_q10', '10(b)'): dict(NO, f=[('8*1.4**(-x) + 2', ''), ('x + 3', '')], x=(-1, 12), y=(-1, 15), grid=(1, 1),
                                          xt=[-1, 12], yt=[-1, 15]),
    ('0607_2020ON_61_q06', '6(c)'): dict(NO, f=[('10/7*(1 + math.sqrt(x))/(1 - math.sqrt(x))', '')], x=(0, 1), y=(0, 60), grid=(0.1, 10),
                                         xt=[1], yt=[20, 40, 60], xlab='q', ylab='T'),            # T as n grows (MS 6(b))
    ('0607_2023ON_32_q11', '11(a)(i)'): dict(NO, f=[('x**2 - x - 4', '')], x=(-2, 4), y=(-10, 10), grid=(0.5, 2), xt=[-2, 4], yt=[-10, 10]),
    ('0607_2023ON_32_q11', '11(b)'): dict(NO, f=[('x**2 - x - 4', ''), ('-x**2 + 3*x + 2', '')], x=(-2, 4), y=(-10, 10), grid=(0.5, 2),
                                          xt=[-2, 4], yt=[-10, 10]),
    ('0607_2023ON_12_q20', '20'): {'venn': {'sets': 'SF', 'names': ['Sandwich', 'Fruit'], 'nums': {'S': 10, 'SF': 20, 'F': 20, '': 70}},
                                   'w': 190.0, 'h': 105.0},
    ('0607_2023ON_22_q11', '11(c)'): {'venn': {'sets': 'AC', 'nums': {'A': 10, 'AC': 5, 'C': 9, '': 11}}, 'w': 180.0, 'h': 100.0},
    # faint MS graphs found by maths_check.picture_checks (2026-11-24)
    ('0607_2018ON_41_q03', '3(a)'): dict(NO, f=[('1 - 2*math.sin(math.radians(2*x - 10))', '')], x=(-90, 90), y=(-4, 4), grid=(15, 1),
                                         xt=[-90, 90], yt=[-4, 4]),
    ('0607_2018ON_61_q07', '7(b)(ii)'): dict(NO, f=[('math.sqrt(3.61*x*x - 2.25) - math.sqrt(x*x - 2.25)', '')], x=(0, 6), y=(0, 6),
                                             grid=(0.5, 1), xt=[6], yt=[], ylab='C'),
    ('0607_2023MJ_62_q06', '6(b)(iii)'): dict(NO, f=[('3*x*x + 50000/x - 2*x + 1', '')], x=(0, 60), y=(0, 10000), grid=(5, 1000),
                                              xt=[60], yt=[10000], xlab='L', ylab='A'),
    # 2021 MJ Venns
    ('0607_2021MJ_11_q14', '14'): {'venn': [{'sets': 'AB', 'shade': 'A or B', 'cap': 'A ∪ B'},
                                            {'sets': 'CD', 'shade': 'C and D', 'cap': 'C ∩ D'}], 'w': 300.0, 'h': 110.0},
    ('0607_2021MJ_12_q20', '20(a)'): {'venn': {'sets': 'ME', 'nums': {'M': 50, 'ME': 15, 'E': 75, '': 10}}, 'w': 180.0, 'h': 100.0},
    ('0607_2021MJ_13_q21', '21(a)'): {'venn': {'sets': 'AB', 'nums': {'A': '1   5\n6   9', 'AB': 4, 'B': '2   7\n10', '': '3\n8'}},
                                      'w': 180.0, 'h': 100.0},
})

def _w(t, s, f='serif', b=False):
    """The text's real width: the SVG draws it with textLength, so a guessed width stretched or squeezed the letters
    (Dhruv round 38: 'why does the font look different'). Minus signs measure ~0 in text_width: counted as 0.5 em."""
    from ms_maths import text_width as tw0           # (the font metrics know Latin-1 only: '–3' measured as 1/4 em
    if all(ord(ch) < 256 for ch in t):               #  and was drawn squeezed - other characters 0.55 em each)
        return tw0(t, f, s, b)
    return round(sum(tw0(ch, f, s, b) if ord(ch) < 256 else 0.55 * s for ch in t), 2)


# ---- RD2 (Dhruv 2026-11-24): the other blurry screenshots drawn as real tables, shapes on their grid, dot patterns,
#      pie charts and mapping diagrams. Each drawer also knows its natural size (natural()), so the row is made tall
#      enough and nothing spills out of its cell.
GREY_TXT = '#8c8c8c'          # values the question gave, printed grey in the mark-scheme table


def _cell_txt(c):
    """'*12' bold, '~3' grey (given in the question), '_n' italic; '\\n' = several lines. -> (lines, style dict)"""
    st = {}
    while c and c[0] in '*~_':
        st[{'*': 'b', '~': 'c', '_': 'i'}[c[0]]] = 1; c = c[1:]
    return c.split('\n'), st


def _lw(t, size, b=False):
    return sum(_w(k, size, b=b) for k in t.split('   ')) + 0.9 * size * t.count('   ')


def _table_size(tb, size):
    rows = tb['rows']; nc = max(len(r) for r in rows); span = tb.get('span', {})
    cw = [0.0] * nc
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            if cell is None or span.get((r, c), 1) > 1:
                continue
            ls, st = _cell_txt(cell)
            cw[c] = max(cw[c], max(_lw(l, size, st.get('b')) for l in ls) + 2 * tb.get('pad', 5.0))
    cw = [max(x, tb.get('minw', 14.0)) for x in cw]
    vs = tb.get('vspan', {})                    # a cell over n rows (its text centred over them): not in a row's height
    rh = [max([len(_cell_txt(c)[0]) for k, c in enumerate(row) if c is not None and vs.get((r, k), 1) == 1] or [1]) * size * 1.2
          + tb.get('vpad', 6.0) for r, row in enumerate(rows)]
    for (r, k), n in vs.items():                # ... but the rows it covers are tall enough for it
        need = len(_cell_txt(rows[r][k])[0]) * size * 1.2 + tb.get('vpad', 6.0) - sum(rh[r:r + n])
        if need > 0:
            rh[r + n - 1] += need
    return cw, rh


def _draw_table(sp, w, h, size=9.0):
    """A table drawn as rules + text (Dhruv: 'tables as real tables'). sp['table'] = {'rows': [[cell, ...]], 'shade':
    [(r, c)], 'span': {(r, c): n} (a cell over n columns; the cells it covers are None), 'noframe': True (only the
    inner rules: a stem-and-leaf), 'hlines': only these row rules (default all), 'align': 'c' | 'l'}."""
    tb = sp['table']; size = _tsize(tb, w)
    cw, rh = _table_size(tb, size)
    k = min(1.0, (w - 2) / sum(cw))                   # too wide for the column: the whole table scales (never clipped)
    if k < 1.0:
        size *= k; cw, rh = _table_size(tb, size)
    L, T = [], []
    x0, y0 = 1.0, 1.0
    xs = [x0]
    for c in cw:
        xs.append(xs[-1] + c)
    ys = [y0]
    for r in rh:
        ys.append(ys[-1] + r)
    span = tb.get('span', {})
    for (r, c) in tb.get('shade', []):
        n = span.get((r, c), 1)
        L.append({'d': f'M{xs[c]:.2f} {ys[r]:.2f}H{xs[c + n]:.2f}V{ys[r + 1]:.2f}H{xs[c]:.2f}Z', 'fill': '#d9d9d9'})
    frame = not tb.get('noframe')
    for r in range(len(ys)):
        if (r in (0, len(ys) - 1) and not frame) or ('hlines' in tb and r not in tb['hlines']):
            continue
        for c in range(len(cw)):                       # (a cell merged with the one above has no rule on top: 'nohl')
            if (r, c) not in tb.get('nohl', ()):
                L.append({'d': f'M{xs[c]:.2f} {ys[r]:.2f}H{xs[c + 1]:.2f}', 'stroke': '#000000', 'sw': 0.6})
    for c in range(len(xs)):
        if (c in (0, len(xs) - 1) and not frame) or ('vlines' in tb and c not in tb['vlines']):
            continue
        for r in range(len(rh)):                       # a column rule stops at a cell spanning over it
            if any(span.get((r, c0), 1) > 1 and c0 < c < c0 + span[(r, c0)] for c0 in range(c)):
                continue
            L.append({'d': f'M{xs[c]:.2f} {ys[r]:.2f}V{ys[r + 1]:.2f}', 'stroke': '#000000', 'sw': 0.6})
    for r, row in enumerate(tb['rows']):
        for c, cell in enumerate(row):
            if cell is None or cell == '':
                continue
            n = span.get((r, c), 1)
            ls, st = _cell_txt(cell)
            nv = tb.get('vspan', {}).get((r, c), 1)
            for j, t in enumerate(ls):
                tw = _lw(t, size, st.get('b'))
                yb = ys[r] + (ys[r + nv] - ys[r] - len(ls) * size * 1.2) / 2 + (j + 0.78) * size * 1.2
                xl = xs[c] + tb.get('pad', 5.0) if tb.get('align') == 'l' else (xs[c] + xs[c + n]) / 2 - tw / 2
                for tok in t.split('   '):           # (leaves '8   9   9': each its own text - spaces collapse in the SVG
                    w_ = _w(tok, size, b=st.get('b'))  #  and the text was stretched to its width)
                    t_ = {'t': tok, 'x': round(xl, 2), 'y': round(yb, 2), 'w': w_, 's': round(size, 2)}
                    if st.get('b'): t_['b'] = 1
                    if st.get('i'): t_['i'] = 1
                    if st.get('c'): t_['c'] = GREY_TXT
                    T.append(t_); xl += w_ + 0.9 * size
    return L, T


def _iso(p):
    return (p[0], p[1] * 0.8660254)


def _isov(p):                                         # (RD2) the triangle lattice turned 90°: columns of dots (hexagons
    return (p[0] * 0.8660254, p[1])                   #  pointing up, 2025 FM 52 q2)


def _draw_plane(sp, w, h, size=9.0):
    """Shapes on squared paper / dotty paper / plain (sp['plane'], or a list sp['panels'] side by side with an 'OR' or
    caption between them). Grid units, y up. {'style': 'squares' | 'dots' | 'iso' | 'none', 'n': (x0, x1, y0, y1),
    'axes': {'xt': [...], 'yt': [...]} (axes through 0 with numbers), 'polys': [{'p': [(x, y)], 'fill': '#bfbfbf',
    'open': True, 'sw': 1.2, 'dash': '3 2'}], 'cells': [(x, y, colour)] (a filled unit square, lower left corner),
    'pts': [(x, y)] (dots), 'big': radius of the dots, 'crosses': [(x, y)], 'text': [(x, y, 'txt', {'b': 1})]}."""
    pans = sp['panels'] if 'panels' in sp else [sp['plane']]
    seps = sp.get('seps', [])                          # text between panels ('or')
    gap = [max(14.0, _w(s_, size) + 10) for s_ in seps] + [0.0] * len(pans)
    widths = [(p['n'][1] - p['n'][0]) for p in pans]
    heights = [(p['n'][3] - p['n'][2]) * (0.8660254 if p.get('style') == 'iso' else 1) for p in pans]
    widths = [w_ * (0.8660254 if p.get('style') == 'isov' else 1) for w_, p in zip(widths, pans)]
    ax_room = lambda p: (22.0 if p.get('axes') else 6.0)
    stack = sp.get('stack')                            # (RD2) panels one above the other, 'OR' between them
    if stack:
        avail_h = h - (len(pans) - 1) * (size * 1.8) - sum(ax_room(p) + 6 for p in pans)
        u = min(min((w - ax_room(p) - 8) / ww for p, ww in zip(pans, widths)), avail_h / sum(heights))
    else:
        avail_w = w - sum(gap[:len(pans) - 1]) - sum(ax_room(p) + 6 for p in pans)
        u = min(avail_w / sum(widths), min((h - ax_room(p) - 8) / hh for p, hh in zip(pans, heights)))
    u = min(u, sp.get('u', (pans[0].get('u') if len(pans) == 1 else None) or 14.0))
    L, T = [], []
    ox = 0.0; oy = 0.0
    for k, p in enumerate(pans):
        x0, x1, y0, y1 = p['n']; iso = p.get('style') == 'iso'; isv = p.get('style') == 'isov'
        left = ax_room(p) + 2 if p.get('axes') else 4.0
        top = 6.0 + oy
        hh = heights[k] * u
        def P(q, ox=ox, left=left):
            a, b = _iso(q) if iso else (_isov(q) if isv else q)
            return (ox + left + (a - x0 * (0.8660254 if isv else 1)) * u, top + hh - (b - (y0 * (0.8660254 if iso else 1))) * u)
        st = p.get('style', 'squares')
        L0_ = len(L)                                   # (round 39) shaded shapes go UNDER the grid: see-through, as printed
        if st == 'squares':
            mn = p.get('minor', 1)                     # 'minor': n light lines per unit square (GeoGebra: 5 x 5 small
            if mn > 1:                                 #  squares in each unit, Dhruv round 39 2023 MJ 63 q4)
                for i in range(int(math.ceil(x0 * mn)), int(math.floor(x1 * mn)) + 1):
                    if i % mn:
                        L.append({'d': f'M{P((i / mn, y0))[0]:.2f} {P((i / mn, y0))[1]:.2f}V{P((i / mn, y1))[1]:.2f}', 'stroke': '#e3e3e3', 'sw': 0.3})
                for j in range(int(math.ceil(y0 * mn)), int(math.floor(y1 * mn)) + 1):
                    if j % mn:
                        L.append({'d': f'M{P((x0, j / mn))[0]:.2f} {P((x0, j / mn))[1]:.2f}H{P((x1, j / mn))[0]:.2f}', 'stroke': '#e3e3e3', 'sw': 0.3})
            for i in range(int(math.ceil(x0)), int(math.floor(x1)) + 1):
                L.append({'d': f'M{P((i, y0))[0]:.2f} {P((i, y0))[1]:.2f}V{P((i, y1))[1]:.2f}', 'stroke': '#b0b0b0', 'sw': 0.4})
            for j in range(int(math.ceil(y0)), int(math.floor(y1)) + 1):
                L.append({'d': f'M{P((x0, j))[0]:.2f} {P((x0, j))[1]:.2f}H{P((x1, j))[0]:.2f}', 'stroke': '#b0b0b0', 'sw': 0.4})
        elif st == 'isov':
            d = []
            for i in range(int(math.ceil(x0)), int(math.floor(x1)) + 1):
                off = 0.5 * (i % 2)
                j = math.ceil(y0 - off)
                while j + off <= y1 + 1e-9:
                    d.append(_circle(*P((i, j + off)), p.get('dot', 0.9))); j += 1
            L.append({'d': ''.join(d), 'fill': '#808080'})
        elif st in ('dots', 'iso'):
            d = []
            for j in range(int(math.ceil(y0)), int(math.floor(y1)) + 1):
                off = 0.5 * (j % 2) if iso else 0.0
                i = math.ceil(x0 - off)
                while i + off <= x1 + 1e-9:
                    cx, cy = P((i + off, j)); r_ = p.get('dot', 0.9)
                    d.append(_circle(cx, cy, r_)); i += 1
            L.append({'d': ''.join(d), 'fill': '#808080'})
        for (cx_, cy_, col) in p.get('cells', []):
            a = P((cx_, cy_)); b = P((cx_ + 1, cy_ + 1))
            L.append({'d': f'M{a[0]:.2f} {b[1]:.2f}H{b[0]:.2f}V{a[1]:.2f}H{a[0]:.2f}Z', 'fill': col})
        if p.get('axes'):
            ax = p['axes']
            xa, ya = P((x0, 0)), P((0, y0))
            L.append({'d': f'M{P((x0, 0))[0]:.2f} {xa[1]:.2f}H{P((x1, 0))[0] + 5:.2f}', 'stroke': '#000000', 'sw': 0.7})
            L.append({'d': f'M{ya[0]:.2f} {P((0, y0))[1]:.2f}V{P((0, y1))[1] - 5:.2f}', 'stroke': '#000000', 'sw': 0.7})
            s2 = size * 0.75                          # (round 39: axis numbers small, never mixed up with the areas)
            for v in ax.get('xt', []):
                t = _num(v); tw = _w(t, s2)
                T.append({'t': t, 'x': round(P((v, 0))[0] - tw / 2 - (2.5 if v == 0 else 0), 2), 'y': round(xa[1] + s2 + 2, 2), 'w': tw, 's': s2, '_ax': 1})
            for v in ax.get('yt', []):
                if v == 0:
                    continue
                t = _num(v); tw = _w(t, s2)
                T.append({'t': t, 'x': round(ya[0] - 3 - tw, 2), 'y': round(P((0, v))[1] + s2 * 0.35, 2), 'w': tw, 's': s2, '_ax': 1})
        for pl in p.get('polys', []):
            q = [P(v) for v in pl['p']]
            dd = 'M' + 'L'.join(f'{a:.2f} {b:.2f}' for a, b in q) + ('' if pl.get('open') else 'Z')
            if pl.get('fill'):
                L.insert(L0_, {'d': dd, 'fill': pl['fill']}) if p.get('under', True) and st == 'squares' else L.append({'d': dd, 'fill': pl['fill']})
            ln = {'d': dd, 'stroke': '#000000', 'sw': pl.get('sw', 1.2)}
            if pl.get('dash'):
                ln['dash'] = pl['dash']
            if pl.get('sw', 1.2) > 0:
                L.append(ln)
        for (ccx, ccy, cr) in p.get('circles', []):     # circles (radius in grid units)
            L.append({'d': _circle(*P((ccx, ccy)), cr * u), 'stroke': '#000000', 'sw': 0.9})
        for (ccx, ccy, cr, a0, a1) in p.get('arcs', []):  # angle arcs, degrees anticlockwise from the x direction
            q = [P((ccx + cr * math.cos(math.radians(a0 + (a1 - a0) * i / 24)),
                    ccy + cr * math.sin(math.radians(a0 + (a1 - a0) * i / 24)))) for i in range(25)]
            L.append({'d': 'M' + 'L'.join(f'{a:.2f} {b:.2f}' for a, b in q), 'stroke': '#000000', 'sw': 0.8})
        r_ = p.get('big', 1.8)
        if p.get('pts'):
            L.append({'d': ''.join(_circle(*P(v), r_) for v in p['pts']), 'fill': '#000000'})
        for v in p.get('crosses', []):
            cx, cy = P(v); c_ = 2.6
            L.append({'d': f'M{cx - c_:.2f} {cy - c_:.2f}L{cx + c_:.2f} {cy + c_:.2f}M{cx - c_:.2f} {cy + c_:.2f}L{cx + c_:.2f} {cy - c_:.2f}',
                      'stroke': '#000000', 'sw': 1.1})
        for tx in p.get('text', []):
            a, b, t = tx[:3]; o = tx[3] if len(tx) > 3 else {}
            s_ = o.get('s', size); tw = _w(t, s_, b=o.get('b')); cx, cy = P((a, b))
            t_ = {'t': t, 'x': round(cx - tw / 2, 2), 'y': round(cy + s_ * 0.35, 2), 'w': tw, 's': s_}
            if o.get('root'):                          # a root sign round the text (2025 FM 62 10(a), round 39)
                xl_, yb_ = cx - tw / 2, cy + s_ * 0.35
                L.append({'d': f'M{xl_ - 7.5:.2f} {yb_ - 0.35 * s_:.2f}L{xl_ - 6:.2f} {yb_ - 0.45 * s_:.2f}L{xl_ - 3.8:.2f} {yb_ + 0.15 * s_:.2f}'
                               f'L{xl_ - 1.2:.2f} {yb_ - 1.05 * s_:.2f}H{xl_ + tw + 1:.2f}', 'stroke': '#000000', 'sw': 0.7})
            if o.get('b'): t_['b'] = 1
            if o.get('i'): t_['i'] = 1
            T.append(t_)
        pw = widths[k] * u + left + 6
        if stack:
            ph = hh + (ax_room(p) if p.get('axes') else 0) + 6
            if k < len(seps):
                t = seps[k]; tw = _w(t, size)
                T.append({'t': t, 'x': round(left + widths[k] * u / 2 - tw / 2, 2), 'y': round(oy + ph + size * 1.1, 2), 'w': tw, 's': size})
            oy += ph + size * 1.8
            continue
        if k < len(seps):
            t = seps[k]; tw = _w(t, size)
            T.append({'t': t, 'x': round(ox + pw + (gap[k] - tw) / 2, 2), 'y': round(top + hh / 2 + size * 0.35, 2), 'w': tw, 's': size})
        ox += pw + gap[k]
    ov = lambda a, b: a['x'] < b['x'] + b['w'] + 1 and b['x'] < a['x'] + a['w'] + 1 and abs(a['y'] - b['y']) < 0.8 * max(a['s'], b['s'])
    T = [t for t in T if not (t.get('_ax') and any(ov(t, o) for o in T if not o.get('_ax')))]   # (round 39) an axis number
    for t in T:                                                    # never mixed up with an area or a letter: it goes
        t.pop('_ax', None)
    return L, T


def _draw_pie(sp, w, h, size=9.0):
    """A pie chart: sp['pie'] = [(angle in degrees, label)], drawn clockwise from 'start' (degrees from 12 o'clock)."""
    L, T = [], []
    r = min(w, h) / 2 - 4
    cx, cy = r + 4, h / 2
    L.append({'d': _circle(cx, cy, r), 'stroke': '#000000', 'sw': 0.8})
    a = sp.get('start', 0.0)
    for ang, lab in sp['pie']:
        t = math.radians(a)
        L.append({'d': f'M{cx:.2f} {cy:.2f}L{cx + r * math.sin(t):.2f} {cy - r * math.cos(t):.2f}', 'stroke': '#000000', 'sw': 0.8})
        m = math.radians(a + ang / 2)
        for j, ln in enumerate(lab.split('\n')):
            tw = _w(ln, size)
            T.append({'t': ln, 'x': round(cx + 0.58 * r * math.sin(m) - tw / 2, 2),
                      'y': round(cy - 0.58 * r * math.cos(m) + size * 0.35 + (j - (lab.count('\n')) / 2) * size * 1.15, 2), 'w': tw, 's': size})
        a += ang
    return L, T


def _draw_map(sp, w, h, size=9.0):
    """A mapping diagram: two ovals with the numbers in them, arrows from left to right. sp['map'] = {'l': [...], 'r':
    [...], 'a': [(i, j)]}."""
    m = sp['map']; L, T = [], []
    n = max(len(m['l']), len(m['r']))
    rw = max(_w(t, size) for t in m['l'] + m['r']) / 2 + 14
    ry = n * size * 1.1 + 8
    cy = h / 2
    lx, rx = 4 + rw, w - 4 - rw
    for ox_, vals in ((lx, m['l']), (rx, m['r'])):
        k = 0.5523
        L.append({'d': f'M{ox_ + rw:.2f} {cy:.2f}C{ox_ + rw:.2f} {cy + k * ry:.2f} {ox_ + k * rw:.2f} {cy + ry:.2f} {ox_:.2f} {cy + ry:.2f}'
                       f'C{ox_ - k * rw:.2f} {cy + ry:.2f} {ox_ - rw:.2f} {cy + k * ry:.2f} {ox_ - rw:.2f} {cy:.2f}'
                       f'C{ox_ - rw:.2f} {cy - k * ry:.2f} {ox_ - k * rw:.2f} {cy - ry:.2f} {ox_:.2f} {cy - ry:.2f}'
                       f'C{ox_ + k * rw:.2f} {cy - ry:.2f} {ox_ + rw:.2f} {cy - k * ry:.2f} {ox_ + rw:.2f} {cy:.2f}Z', 'stroke': '#000000', 'sw': 0.9})
    yv = lambda i, cnt: cy + (i - (cnt - 1) / 2) * size * 2.0
    for i, t in enumerate(m['l']):
        tw = _w(t, size); T.append({'t': t, 'x': round(lx - tw / 2, 2), 'y': round(yv(i, len(m['l'])) + size * 0.35, 2), 'w': tw, 's': size})
    for j, t in enumerate(m['r']):
        tw = _w(t, size); T.append({'t': t, 'x': round(rx - tw / 2, 2), 'y': round(yv(j, len(m['r'])) + size * 0.35, 2), 'w': tw, 's': size})
    for i, j in m['a']:
        a_ = (lx + _w(m['l'][i], size) / 2 + 3, yv(i, len(m['l']))); b_ = (rx - _w(m['r'][j], size) / 2 - 3, yv(j, len(m['r'])))
        L.append({'d': f'M{a_[0]:.2f} {a_[1]:.2f}L{b_[0] - 4:.2f} {b_[1]:.2f}', 'stroke': '#000000', 'sw': 0.8})
        ang = math.atan2(b_[1] - a_[1], b_[0] - a_[0]); c, s = math.cos(ang), math.sin(ang)
        L.append({'d': f'M{b_[0]:.2f} {b_[1]:.2f}L{b_[0] - 5 * c + 2 * s:.2f} {b_[1] - 5 * s - 2 * c:.2f}L{b_[0] - 5 * c - 2 * s:.2f} {b_[1] - 5 * s + 2 * c:.2f}Z',
                  'fill': '#000000'})
    return L, T


MS_SIZE = 11.0                                     # the mark scheme's own text size


def _tsize(tb, w=330.0):
    """(Dhruv round 39) a table is drawn at the mark scheme's normal size when it fits the column's width (the row
    grows), else at its own smaller size (then scaled down to the width)."""
    return MS_SIZE              # (too wide at 11 pt: _draw_table scales it down to the column, never below what it had)


def natural(sp, size=9.0):
    """(w, h) the drawing needs (tables), else None: the row is made at least this tall."""
    if 'table' in sp:
        cw, rh = _table_size(sp['table'], _tsize(sp['table']))
        return sum(cw) + 2, sum(rh) + 2
    return None


def _pchip(pts):
    """A smooth increasing curve through data points (cumulative frequency): monotone cubic, as drawn by hand."""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; n = len(pts)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [0.0 if d[i - 1] * d[i] <= 0 else 2 / (1 / d[i - 1] + 1 / d[i]) for i in range(1, n - 1)] + [d[-1]]
    out = []
    for i in range(n - 1):
        hh = xs[i + 1] - xs[i]
        for k in range(12):
            t = k / 12
            h00, h10, h01, h11 = 2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2
            out.append((xs[i] + t * hh, h00 * ys[i] + h10 * hh * m[i] + h01 * ys[i + 1] + h11 * hh * m[i + 1]))
    return out + [pts[-1]]


def _draw_tree(sp, w, h, size=8.0):
    """A completed two-stage tree diagram drawn as lines and text like the question's own (probabilities on the branches)."""
    tr = sp['tree']
    L, T = [], []
    from ms_maths import text_width as tw0
    tw = lambda t: _w(t, size)
    def txt(lines, x, yc, right=False):                       # a block of lines centred on yc, left edge at x
        lh = size * 1.15                                      # (round 39: the branch points at the word's middle as in
        y0 = yc - (len(lines) - 1) * lh / 2 + size * (0.08 if 'geom' in tr else 0.33)   # the question, not its top)
        for k, t in enumerate(lines):
            T.append({'t': t, 'x': round(x - (tw(t) if right else 0), 2), 'y': round(y0 + k * lh, 2), 'w': round(tw(t), 2), 's': size})
    def br(x0, y0, x1, y1, prob, upper):
        L.append({'d': f'M{x0:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}', 'stroke': '#000000', 'sw': 0.8})
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if 'geom' in tr:                                  # (round 39) as the question's answer lines: the fraction ends
            f_ = 0.38 if x0 < 10 else 0.3                 # before the branch's middle (pairs of branches never crowd it)
            mx = x0 + f_ * (x1 - x0) + 6
            my = y0 + f_ * (y1 - y0)
        if '/' in prob:                                   # a fraction written as a fraction (16/30 -> 16 over 30)
            nu, de = prob.split('/')
            fw = max(tw(nu), tw(de)) + 2
            fx = mx - fw - 3                             # right edge just left of the branch's middle, clear of the
            ly = y0 + (y1 - y0) * (fx + fw - x0) / max(1.0, x1 - x0)   # line (Dhruv round 38: the 15/29 sat on its branch)
            fy = ly - 3 - size if upper else ly + 3 + size * 0.75     # the bar's height
            for t_, yb in ((nu, fy - 1.5), (de, fy + size - 0.5)):
                T.append({'t': t_, 'x': round(fx + (fw - tw(t_)) / 2, 2), 'y': round(yb, 2), 'w': round(tw(t_), 2), 's': size})
            L.append({'d': f'M{fx:.2f} {fy + 0.5:.2f}H{fx + fw:.2f}V{fy + 1.0:.2f}H{fx:.2f}Z', 'fill': '#000000'})
            return
        if 'geom' in tr:                                  # (round 40) a decimal like a fraction: right edge left of the
            fx = mx - tw(prob) - 3                        # branch, the text clear of the line at that x
            ly = y0 + (y1 - y0) * (fx + tw(prob) - x0) / max(1.0, x1 - x0)
            T.append({'t': prob, 'x': round(fx, 2), 'y': round(ly - 3 if upper else ly + 3 + size * 0.75, 2), 'w': round(tw(prob), 2), 's': size})
            return
        if upper:
            T.append({'t': prob, 'x': round(mx - tw(prob) - 1, 2), 'y': round(my - 1.5, 2), 'w': round(tw(prob), 2), 's': size})
        else:
            T.append({'t': prob, 'x': round(mx - tw(prob) - 1, 2), 'y': round(my + size + 0.5, 2), 'w': round(tw(prob), 2), 's': size})
    rx, ry = 4.0, h / 2
    e1 = 0.24 * w
    f1 = 0.52 * w
    e2 = 0.66 * w
    d1, d2 = 0.24 * h, 0.15 * h
    if 'geom' in tr:                           # (round 39) the question's own tree: branch ends (x0, x1, x2, x3, pt) and
        g = tr['geom']                         # the rises (d1, d2) of its first and second branches, scaled to fit
        lw_ = max(tw(t) for _, ls_ in tr['first'] for t in ls_ + [t2 for sec in tr['second'] for _, l2 in sec for t2 in l2])
        k = min((w - 8 - lw_) / (g[3] - g[0]), (h - 4) / (2 * (g[4] + g[5] + (g[6] if len(g) > 6 else 0))))
        rx = 4.0; e1, f1, e2 = rx + (g[1] - g[0]) * k, rx + (g[2] - g[0]) * k, rx + (g[3] - g[0]) * k
        d1, d2 = g[4] * k, g[5] * k
        off = g[6] * k if len(g) > 6 else 0.0  # (round 40) each second tree sits this much further out than its branch end
        d1 = max(d1, (2 * (2 * size + 4) + 6 + 0.6 * d2) / 2)   # (a narrow column: the first branches open just enough
        ry = d1 + off + d2 + 2 + 0.5 * size                    #  that the middle fractions never touch; a 2-line end label
        #                                                        stays inside the cell, round 40)
    for i, (prob, lines) in enumerate(tr['first']):
        yn = ry + (-d1 if i == 0 else d1) if 'geom' in tr else h * (0.26 if i == 0 else 0.74)
        br(rx, ry, e1, yn, prob, i == 0)
        txt(lines, e1 + 3, yn)
        y2 = yn + ((-off if i == 0 else off) if 'geom' in tr else 0)
        for j, (p2, l2) in enumerate(tr['second'][i]):
            ye = y2 + (-1 if j == 0 else 1) * d2
            br(f1, y2, e2, ye, p2, j == 0)
            txt(l2, e2 + 3, ye)
    return L, T


def _circle(cx, cy, r):
    k = 0.5523 * r
    return (f'M{cx + r:.2f} {cy:.2f}C{cx + r:.2f} {cy + k:.2f} {cx + k:.2f} {cy + r:.2f} {cx:.2f} {cy + r:.2f}'
            f'C{cx - k:.2f} {cy + r:.2f} {cx - r:.2f} {cy + k:.2f} {cx - r:.2f} {cy:.2f}'
            f'C{cx - r:.2f} {cy - k:.2f} {cx - k:.2f} {cy - r:.2f} {cx:.2f} {cy - r:.2f}'
            f'C{cx + k:.2f} {cy - r:.2f} {cx + r:.2f} {cy - k:.2f} {cx + r:.2f} {cy:.2f}Z')


def _draw_venns(sp, w, h, size=9.0):
    """Venn diagram(s) like the question's: a box (U at its top left), 2 or 3 circles with their letters, numbers in the
    regions, a region shaded grey. sp['venn']: one dict or a list (drawn side by side, or one above the other with
    'stack': True): {'sets': 'AB' | 'ABC', 'shade': python expression over the set letters (e.g. 'not (A or B)'),
    'nums': {'A': 10, 'AB': 5, 'B': 9, '': 11}  (region = the letters it is in, '' = outside), 'cap': caption under it}."""
    from ms_maths import text_width as tw0
    tw = lambda t, s_=size: _w(t, s_)
    vs = sp['venn'] if isinstance(sp['venn'], list) else [sp['venn']]
    L, T = [], []
    n = len(vs); stack = sp.get('stack', False)
    cw, chh = (w, h / n) if stack else (w / n, h)
    for k, vd in enumerate(vs):
        ox, oy = (0.0, k * chh) if stack else (k * cw, 0.0)
        cap = vd.get('cap')
        bw = min(cw - 14, 1.6 * (chh - (14 if cap else 2) - 8)); bh = bw / 1.6
        bx, by = ox + 10 + (cw - 14 - bw) / 2, oy + 6
        sets = vd.get('sets', 'AB'); names = vd.get('names', sets)
        r = bh * (0.30 if len(sets) == 3 else 0.36)
        if len(sets) == 2:
            cs = [(bx + bw / 2 - 0.62 * r, by + bh / 2), (bx + bw / 2 + 0.62 * r, by + bh / 2)]
        else:
            cs = [(bx + bw / 2 - 0.6 * r, by + bh * 0.40), (bx + bw / 2 + 0.6 * r, by + bh * 0.40), (bx + bw / 2, by + bh * 0.40 + 0.95 * r)]
        inside = lambda x, y: {sets[i]: (x - cx) ** 2 + (y - cy) ** 2 <= r * r for i, (cx, cy) in enumerate(cs)}
        if vd.get('shade'):
            rule = eval('lambda ' + ', '.join(sets) + ': ' + vd['shade'])
            d, step = [], 0.5
            y = by + step / 2
            while y < by + bh:
                x, run = bx, None
                while x <= bx + bw + 1e-6:
                    on = x < bx + bw and rule(**inside(x + 0.25, y))
                    if on and run is None:
                        run = x
                    if not on and run is not None:
                        d.append(f'M{run:.2f} {y - step / 2:.2f}H{x:.2f}V{y + step / 2:.2f}H{run:.2f}Z'); run = None
                    x += 0.5
                if run is not None:                       # a run reaching the box's right side
                    d.append(f'M{run:.2f} {y - step / 2:.2f}H{bx + bw:.2f}V{y + step / 2:.2f}H{run:.2f}Z')
                y += step
            if d:
                L.append({'d': ''.join(d), 'fill': '#bfbfbf'})
        L.append({'d': f'M{bx:.2f} {by:.2f}H{bx + bw:.2f}V{by + bh:.2f}H{bx:.2f}Z', 'stroke': '#000000', 'sw': 0.8})
        for cx, cy in cs:
            L.append({'d': _circle(cx, cy, r), 'stroke': '#000000', 'sw': 0.8})
        T.append({'t': 'U', 'x': round(bx - 9, 2), 'y': round(by + size * 0.8, 2), 'w': tw('U'), 's': size})
        for i, (cx, cy) in enumerate(cs):              # set letters outside the circles, near the top
            nm = names[i]
            if len(sets) == 3 and i == 2:
                lx, ly = cx + 0.95 * r, cy + 0.80 * r      # (RD2: off the circle's line)
            else:
                lx, ly = cx + (-0.95 if i == 0 else 0.75) * r, cy - 0.78 * r
            if len(nm) > 2:                         # a word ('Sandwich'): in the box's top corner, upright, as printed
                lx = bx + 4 if i == 0 else bx + bw - 4 - tw(nm)
                T.append({'t': nm, 'x': round(lx, 2), 'y': round(by + size + 2, 2), 'w': tw(nm), 's': size})
                continue
            T.append({'t': nm, 'x': round(lx, 2), 'y': round(ly, 2), 'w': tw(nm), 's': size, 'i': 1})
        # number positions: the centre of each region (found by sampling)
        acc = {}
        for yy in range(int(by) + 1, int(by + bh), 2):
            for xx in range(int(bx) + 1, int(bx + bw), 2):
                key = ''.join(c for c, on in inside(xx, yy).items() if on)
                acc.setdefault(key, []).append((xx, yy))
        for key, val in vd.get('nums', {}).items():
            key = ''.join(sorted(key, key=sets.index))
            pts = acc.get(key)
            if not pts:
                continue
            if key == '' and vd.get('out') == 'bottom':   # (RD2) a long list outside the circles: under them, centred
                px, py = bx + bw / 2, by + bh - 4
            elif key == '' and vd.get('out') == 'left':   # a column of numbers at the box's left side
                px, py = bx + 4 + max(tw(t_) for t_ in str(val).split('\n')) / 2, by + bh / 2 + size * 0.35
            elif key == '':
                px, py = bx + bw - 12, by + bh - 6 - (str(val).count('\n')) * size * 0.6
            else:
                px = sum(a for a, b in pts) / len(pts); py = sum(b for a, b in pts) / len(pts) + size * 0.35
            ls_ = str(val).split('\n')                     # several lines ('1 5\n6 9'): stacked round the centre
            for j, t in enumerate(ls_):
                yy = py + (j - (len(ls_) - 1) / 2) * size * 1.2
                xx = px - _lw(t, size) / 2                 # (RD2) '1   5': each number its own text (no stretched spaces)
                for tok in t.split('   '):
                    T.append({'t': tok, 'x': round(xx, 2), 'y': round(yy, 2), 'w': tw(tok), 's': size}); xx += tw(tok) + 0.9 * size
        if cap:
            T.append({'t': cap, 'x': round(bx + bw / 2 - tw(cap) / 2, 2), 'y': round(by + bh + size + 4, 2), 'w': tw(cap), 's': size})
    return L, T


def _draw_bars(sp, w, h, size=9.0):
    """A bar chart on the question's grid: sp['bars'] = [(category, value)], 'y': window, 'yt': labelled ticks."""
    from ms_maths import text_width as tw0
    tw = lambda t, s_=size: _w(t, s_)
    L, T = [], []
    y0, y1 = sp['y']; bars = sp['bars']
    pl, pr, pt, pb = 30.0, 6.0, 8.0, 16.0
    W, H = w - pl - pr, h - pt - pb
    Y = lambda v: pt + (y1 - v) / (y1 - y0) * H
    gy = sp.get('grid', (None, None))[1]
    slot = W / len(bars)
    if gy:
        k = math.ceil(y0 / gy)
        while k * gy <= y1 + 1e-9:
            L.append({'d': f'M{pl:.2f} {Y(k * gy):.2f}H{pl + W:.2f}', 'stroke': '#cfcfcf', 'sw': 0.4}); k += 1
        for i in range(len(bars) * 2 + 1):
            L.append({'d': f'M{pl + i * slot / 2:.2f} {Y(y1):.2f}V{Y(y0):.2f}', 'stroke': '#cfcfcf', 'sw': 0.4})
    for i, (cat, val) in enumerate(bars):
        x0_, x1_ = pl + (i + 0.25) * slot, pl + (i + 0.75) * slot
        L.append({'d': f'M{x0_:.2f} {Y(y0):.2f}V{Y(val):.2f}H{x1_:.2f}V{Y(y0):.2f}', 'stroke': '#000000', 'sw': 0.8})
        T.append({'t': cat, 'x': round((x0_ + x1_) / 2 - tw(cat, size * 0.9) / 2, 2), 'y': round(Y(y0) + size + 2, 2),
                  'w': tw(cat, size * 0.9), 's': size * 0.9})
    L.append({'d': f'M{pl:.2f} {Y(y0):.2f}H{pl + W:.2f}', 'stroke': '#000000', 'sw': 0.8})
    L.append({'d': f'M{pl:.2f} {Y(y0) + 2:.2f}V{Y(y1) - 6:.2f}', 'stroke': '#000000', 'sw': 0.8})
    L.append({'d': f'M{pl:.2f} {Y(y1) - 6:.2f}l-1.8 4h3.6z', 'fill': '#000000'})
    for v in sp.get('yt', []):
        L.append({'d': f'M{pl - 2:.2f} {Y(v):.2f}H{pl:.2f}', 'stroke': '#000000', 'sw': 0.6})
        t = _num(v)
        T.append({'t': t, 'x': round(pl - 3 - tw(t), 2), 'y': round(Y(v) + size * 0.35, 2), 'w': tw(t), 's': size})
    return L, T


def spec(qid, label):
    sp = SPECS.get((qid, label))
    if sp and natural(sp):                     # a table: the row is made as tall as the drawn table (nothing spills)
        nw, nh = natural(sp)
        sp = dict(sp, w=max(sp.get('w', 0), nw), h=max(sp.get('h', 0), nh))
    return sp


def _num(v):
    return ('%g' % v).replace('-', '–')        # the MS prints an en dash for minus


def draw(sp, w, h, size=9.0):
    """-> (lines, texts) in a box w x h (pt), origin top left. lines: {'d', 'stroke', 'sw'}; texts: {'t', 'x', 'y', 'w', 's'}."""
    if 'graphs' in sp:                         # (RD2) two graphs one above the other in one screenshot (2025 MJ 62 9(c)(i))
        from ms_layout import _map_path
        L, T = [], []
        hh = h / len(sp['graphs'])
        for k, g in enumerate(sp['graphs']):
            gL, gT = draw(g, w, hh - 4, size)
            L += [dict(l_, d=_map_path(l_['d'], lambda x: x, lambda y, k=k: y + k * hh)) for l_ in gL]
            T += [dict(t_, y=round(t_['y'] + k * hh, 2)) for t_ in gT]
        return L, T
    if 'tree' in sp:
        return _draw_tree(sp, w, h, size)
    if 'venn' in sp:
        return _draw_venns(sp, w, h, size)
    if 'bars' in sp:
        return _draw_bars(sp, w, h, size)
    if 'table' in sp:
        return _draw_table(sp, w, h, size)
    if 'plane' in sp or 'panels' in sp:
        return _draw_plane(sp, w, h, size)
    if 'pie' in sp:
        return _draw_pie(sp, w, h, size)
    if 'map' in sp:
        return _draw_map(sp, w, h, size)
    from ms_maths import text_width as tw0
    # text_width measures some Unicode signs (−, –) as ~0 and the label was squeezed; an estimate never below 0.5 em/char
    text_width = lambda t, f, s: _w(t, s, f)
    L, T = [], []
    pl, pr, pt, pb = 22.0, 16.0, 12.0, 14.0                # room for tick labels, arrows and the y letter
    x0, x1 = sp['x']; y0, y1 = sp['y']
    if not (x0 < 0 < x1):                                  # (RD2) the y numbers stand left of the window: room for the
        pl = max(pl, max([_w(_num(v), size) for v in sp.get('yt', [])] + [0]) + 7)   # widest ('146000', '1.2585': spilled)
    W, H = max(20.0, w - pl - pr), max(20.0, h - pt - pb)
    if sp.get('ar'):                                       # (Dhruv round 39) the printed screenshot's shape: a square
        W, H = min(W, H * sp['ar']), min(H, W / sp['ar'])  # screenshot stays square (2022 MJ 41 9(b)(i))
    X = lambda x: pl + (x - x0) / (x1 - x0) * W
    Y = lambda y: pt + (y1 - y) / (y1 - y0) * H
    gx, gy = sp.get('grid') or (None, None)               # grid=None: the printed screenshot has no grid (round 39)
    if gx:                                                 # light grey grid as printed: 'gmaj' (kx, ky) every kx-th line
        kx_, ky_ = sp.get('gmaj', (0, 0))                  # darker (Desmos / GeoGebra major lines, round 39);
        if sp.get('gdots'):                                # 'gdots': dots at the grid points (dotted paper)
            d_ = []
            i = math.ceil(x0 / gx)
            while i * gx <= x1 + 1e-9:
                j = math.ceil(y0 / gy)
                while j * gy <= y1 + 1e-9:
                    d_.append(_circle(X(i * gx), Y(j * gy), 0.55)); j += 1
                i += 1
            L.append({'d': ''.join(d_), 'fill': '#909090'})
        else:
            k = math.ceil(x0 / gx - 1e-9)
            while k * gx <= x1 + 1e-9:
                mj = kx_ and abs(round(k) % kx_) == 0
                L.append({'d': f'M{X(k * gx):.2f} {Y(y1):.2f}V{Y(y0):.2f}', 'stroke': '#a6a6a6' if mj else ('#dedede' if kx_ else '#cfcfcf'),
                          'sw': 0.5 if mj else 0.35}); k += 1
            k = math.ceil(y0 / gy - 1e-9)
            while k * gy <= y1 + 1e-9:
                mj = ky_ and abs(round(k) % ky_) == 0
                L.append({'d': f'M{X(x0):.2f} {Y(k * gy):.2f}H{X(x1):.2f}', 'stroke': '#a6a6a6' if mj else ('#dedede' if ky_ else '#cfcfcf'),
                          'sw': 0.5 if mj else 0.35}); k += 1
    if sp.get('band'):                         # the region between two curves shaded (2020 MJ 62 7(d))
        lo, hi = (eval('lambda x: ' + e, {'math': math}) for e in sp['band'])
        xs = [x0 + (x1 - x0) * i / 200 for i in range(201)]
        cl = lambda v: min(max(v, y0), y1)
        pts = [(X(x), Y(cl(lo(x)))) for x in xs] + [(X(x), Y(cl(hi(x)))) for x in reversed(xs)]
        L.append({'d': 'M' + 'L'.join(f'{a:.2f} {b:.2f}' for a, b in pts) + 'Z', 'fill': '#d0d0d0'})
    ax_y = Y(0) if y0 <= 0 <= y1 else Y(y0)
    ax_x = X(0) if x0 <= 0 <= x1 else X(x0)
    L.append({'d': f'M{X(x0) - 3:.2f} {ax_y:.2f}H{X(x1) + 6:.2f}', 'stroke': '#000000', 'sw': 0.8})
    L.append({'d': f'M{X(x1) + 6:.2f} {ax_y:.2f}l-4 -1.8v3.6z', 'fill': '#000000'})
    L.append({'d': f'M{ax_x:.2f} {Y(y0) + 3:.2f}V{Y(y1) - 6:.2f}', 'stroke': '#000000', 'sw': 0.8})
    L.append({'d': f'M{ax_x:.2f} {Y(y1) - 6:.2f}l-1.8 4h3.6z', 'fill': '#000000'})
    ts = sp.get('ts', round(size * 0.8, 2))          # tick numbers small (Dhruv round 39), the same serif font
    for v in sp.get('xt', []):
        L.append({'d': f'M{X(v):.2f} {ax_y - 2:.2f}V{ax_y + 2:.2f}', 'stroke': '#000000', 'sw': 0.6})
        t = _num(v); tw = text_width(t, 'serif', ts)
        T.append({'t': t, 'x': round(X(v) - tw / 2, 2), 'y': round((Y(y0) + 1 + ts) if sp.get('xlow') else (ax_y + 2 + ts), 2),
                  'w': tw, 's': ts, '_tk': 'x', '_v': X(v)})  # ('xlow': under the window - a curve along the axis, 2023 MJ 63 q12)
    for v in sp.get('yt', []):
        L.append({'d': f'M{ax_x - 2:.2f} {Y(v):.2f}H{ax_x + 2:.2f}', 'stroke': '#000000', 'sw': 0.6})
        t = _num(v); tw = text_width(t, 'serif', ts)
        T.append({'t': t, 'x': round(ax_x - 3 - tw, 2), 'y': round(Y(v) + ts * 0.35, 2), 'w': tw, 's': ts, '_tk': 'y', '_v': Y(v)})
    nx_ = len(sp.get('xt', []))                         # (RD2) a y number that would touch an x number goes (the
    for t_ in [t_ for t_ in T[nx_:] if any(abs(t_['y'] - o['y']) < ts and t_['x'] < o['x'] + o['w'] + 1   # '–1' / '–1'
                                           and o['x'] < t_['x'] + t_['w'] + 1 for o in T[:nx_])]:            #  at the origin)
        T.remove(t_)
    tick_txt = list(T)
    xl = sp.get('xlab', 'x')
    if xl: T.append({'t': xl, 'x': round(X(x1) + 8, 2), 'y': round(ax_y + size * 0.35, 2), 'w': _w(xl, size), 's': size, 'i': 1})
    yl = sp.get('ylab', 'y')
    if yl: T.append({'t': yl, 'x': round(ax_x + 4, 2), 'y': round(Y(y1) - 6 + size * 0.35, 2), 'w': _w(yl, size), 's': size, 'i': 1})
    #  (beside the arrow tip, above the window: on the window's top edge it sat on a curve, Dhruv round 38 2021 MJ 62 q9)
    dashes = [None, '3 2', '1 1.5']
    for n, (expr, lab) in enumerate(sp['f']):
        f = eval('lambda x: ' + expr, {'math': math})
        segs, cur, prev = [], [], None
        N = 600
        for i in range(N + 1):
            x = x0 + (x1 - x0) * i / N
            try:
                y = f(x)
                ok = isinstance(y, float) or isinstance(y, int)
                y = float(y)
                ok = ok and math.isfinite(y)
            except (ZeroDivisionError, ValueError, OverflowError, TypeError):
                ok = False
            if ok and prev is not None and abs(y - prev) > 0.5 * (y1 - y0):
                ok_jump = False                               # a jump across the window: an asymptote, the curve breaks
            else:
                ok_jump = True
            if not ok or not ok_jump or not (y0 - 0.02 * (y1 - y0) <= y <= y1 + 0.02 * (y1 - y0)):
                if len(cur) > 1:
                    segs.append(cur)
                cur = [(X(x), Y(min(max(y, y0), y1)))] if ok and ok_jump is False and y0 <= y <= y1 else []
                prev = y if ok else None
                continue
            cur.append((X(x), Y(y))); prev = y
        if len(cur) > 1:
            segs.append(cur)
        for sg in segs:
            d = 'M' + 'L'.join(f'{a:.2f} {b:.2f}' for a, b in sg)
            ln = {'d': d, 'stroke': '#000000', 'sw': 1.0}
            if dashes[n % 3] and sp.get('dash', True):      # ('dash': False - all curves solid, as printed)
                ln['dash'] = dashes[n % 3]
            L.append(ln)
    if sp.get('smooth') and sp.get('points'):    # a smooth curve through the plotted points (cumulative frequency, RD2)
        L.append({'d': 'M' + 'L'.join(f'{X(a):.2f} {Y(b):.2f}' for a, b in _pchip(sorted(sp['points']))), 'stroke': '#000000', 'sw': 1.0})
    if sp.get('dots') and sp.get('points'):    # (RD2) points printed as dots, not crosses
        L.append({'d': ''.join(_circle(X(a), Y(b), 1.6) for a, b in sp['points']), 'fill': '#000000'})
    for px, py in ([] if sp.get('dots') else sp.get('points', [])):   # plotted points as crosses x (2020 ON 62 6(a))
        cx, cy, r_ = X(px), Y(py), 2.2
        L.append({'d': f'M{cx - r_:.2f} {cy - r_:.2f}L{cx + r_:.2f} {cy + r_:.2f}M{cx - r_:.2f} {cy + r_:.2f}L{cx + r_:.2f} {cy - r_:.2f}',
                  'stroke': '#000000', 'sw': 0.8})
    cpts = []                                  # (round 39) a tick number never sits on a curve: below / above the x axis,
    for l_ in L:                               # left / right of the y axis, whichever is free; only if none is free it
        if l_.get('stroke') == '#000000' and l_['d'].count('L') > 3:     # keeps a white ground (the curve breaks there)
            nums = [float(v) for v in __import__('re').findall(r'-?\d+\.?\d*', l_['d'])]
            cpts += list(zip(nums[0::2], nums[1::2]))
    def free_(x_, y_, t_):
        return not any(x_ - 1 <= a <= x_ + t_['w'] + 1 and y_ - 0.8 * t_['s'] <= b <= y_ + 0.25 * t_['s'] for a, b in cpts)
    for t_ in tick_txt:
        if t_.get('_tk') == 'x' and not sp.get('xlow'):
            cands = [(t_['x'], t_['y']), (t_['x'], round(ax_y - 3, 2))]
        elif t_.get('_tk') == 'y':
            cands = [(t_['x'], t_['y']), (round(ax_x + 3, 2), t_['y'])]
        else:
            cands = [(t_['x'], t_['y'])]
        ok_ = next(((a, b) for a, b in cands if free_(a, b, t_)), None)
        if ok_:
            t_['x'], t_['y'] = ok_
        else:
            L.append({'d': f"M{t_['x'] - 0.8:.2f} {t_['y'] - 0.72 * t_['s']:.2f}H{t_['x'] + t_['w'] + 0.8:.2f}"
                           f"V{t_['y'] + 0.22 * t_['s']:.2f}H{t_['x'] - 0.8:.2f}Z", 'fill': '#ffffff'})
    for t_ in T:
        t_.pop('_tk', None); t_.pop('_v', None)
    for vx in sp.get('vlines', []):          # a vertical line (x = 95, 2022 ON 62 8(e)(i))
        L.append({'d': f'M{X(vx):.2f} {Y(y0):.2f}V{Y(y1):.2f}', 'stroke': '#000000', 'sw': 1.0})
    for tx, ty, tt in sp.get('tags', []):      # a printed label next to its curve ('a = 2.5', 2021 MJ 62 9(c)(i))
        T.append({'t': tt, 'x': round(X(tx), 2), 'y': round(Y(ty), 2), 'w': _w(tt, 7.0), 's': 7.0})
    # the function label(s) (Dhruv round 33: only where the printed graph has one, small, never over the curves or the
    # axes, fractions as fractions): pieces ('t', text) / ('i', italic) / ('sup', text) / ('frac', num, den)
    if not sp.get('label', True):
        return L, T
    ls_ = sp.get('labels') or [[('t', lab)] for _, lab in sp['f']]
    ls = 7.0                                            # label size
    def piece_w(pc):
        if pc[0] == 'frac':
            return max(text_width(pc[1], 'serif', ls * 0.9), text_width(pc[2], 'serif', ls * 0.9)) + 1.5
        if pc[0] == 'sup':
            return text_width(pc[1], 'serif', ls * 0.7)
        return text_width(pc[1], 'serif', ls)
    def lab_h(lab):
        return ls * 2.3 if any(pc[0] == 'frac' for pc in lab) else ls * 1.35
    samp = len(sp['f']) > 1
    widths = [sum(piece_w(pc) for pc in lab) + (13 if samp else 0) for lab in ls_]
    bw, bh = max(widths) + 2, sum(lab_h(l_) for l_ in ls_) + 2
    pts = []                                            # every drawn curve point, the axes and the edges: kept clear
    for l_ in L:
        if l_.get('stroke') == '#000000':
            nums = [float(v) for v in __import__('re').findall(r'-?\d+\.?\d*', l_['d'])]
            pts += list(zip(nums[0::2], nums[1::2]))
    n_ax = int(max(W, H) / 3) + 2                       # the axes are long lines with only 2 end points: sampled, so a
    pts += [(X(x0) + (X(x1) - X(x0)) * i / n_ax, ax_y) for i in range(n_ax + 1)]   # label is never put over an axis (RD2)
    pts += [(ax_x, Y(y0) + (Y(y1) - Y(y0)) * i / n_ax) for i in range(n_ax + 1)]
    for t_ in T:                                        # tick numbers and axis letters are kept clear too
        for fx_ in (0, 0.5, 1):
            for fy_ in (0, 1):
                pts.append((t_['x'] + fx_ * t_['w'], t_['y'] - fy_ * t_['s'] * 0.75))
    def hits(bx_, by_):
        m = 2.5
        return sum(1 for a, b in pts if bx_ - m <= a <= bx_ + bw + m and by_ - m <= b <= by_ + bh + m)
    cands = []
    for fx in (0.98, 0.6, 0.3, 0.02):
        for fy in (0.02, 0.3, 0.6, 0.98):
            bx_ = pl + 3 + fx * (W - bw - 6); by_ = pt + 3 + fy * (H - bh - 6)
            cands.append((hits(bx_, by_), -fx, fy, bx_, by_))
    _, _, _, bx, by = min(cands)
    L.append({'d': f'M{bx:.2f} {by:.2f}H{bx + bw:.2f}V{by + bh:.2f}H{bx:.2f}Z', 'fill': '#ffffff'})   # no border
    yy = by + 1
    for n, lab in enumerate(ls_):
        h_ = lab_h(lab); base = yy + h_ / 2 + ls * 0.35; xx = bx + 1
        if samp:
            ln = {'d': f'M{xx:.2f} {base - ls * 0.3:.2f}h10', 'stroke': '#000000', 'sw': 1.0}
            if dashes[n % 3]:
                ln['dash'] = dashes[n % 3]
            L.append(ln); xx += 13
        for pc in lab:
            w_ = piece_w(pc)
            if pc[0] == 'frac':
                s2 = ls * 0.9
                for txt, yb in ((pc[1], base - ls * 0.62), (pc[2], base + ls * 0.78)):
                    tw = text_width(txt, 'serif', s2)
                    T.append({'t': txt, 'x': round(xx + (w_ - tw) / 2, 2), 'y': round(yb, 2), 'w': tw, 's': s2})
                L.append({'d': f'M{xx + 0.5:.2f} {base - ls * 0.3 - 0.25:.2f}H{xx + w_ - 0.5:.2f}V{base - ls * 0.3 + 0.25:.2f}'
                               f'H{xx + 0.5:.2f}Z', 'fill': '#000000'})
            elif pc[0] == 'sup':
                T.append({'t': pc[1], 'x': round(xx, 2), 'y': round(base - ls * 0.4, 2), 'w': w_, 's': ls * 0.7, 'i': 1})
            else:
                t_ = {'t': pc[1], 'x': round(xx, 2), 'y': round(base, 2), 'w': w_, 's': ls}
                if pc[0] == 'i':
                    t_['i'] = 1
                T.append(t_)
            xx += w_
        yy += h_
    return L, T


# ---- RD2 (Dhruv 2026-11-24): every other flagged screenshot of all 0607 batches (M0, M1, M2, M3) drawn again. Graphs
# from the question's function on the question's own axes (ticks as printed there); a function label only where the
# screenshot prints one. Tables, shapes on grids, dot patterns, pie charts, mapping diagrams: the drawers above.
CUM = [(0, 0), (10, 6), (20, 14), (30, 21), (40, 27), (50, 30)]          # 2014 MJ 32 q14 (c)
SPECS.update({
    # group 1 (M0: 2014 MJ, 2019 ON, 2020, 2021 FM)
    ('0607_2014MJ_21_q07', '7(a)'): dict(NO, f=[('12 - 2*x if 0 <= x <= 6 else None', ''), ('(36 - 3*x)/4', '')], vlines=[1],
                                         x=(0, 12), y=(0, 12), grid=(1, 1), xt=[2, 4, 6, 8, 10, 12], yt=[2, 4, 6, 8, 10, 12],
                                         tags=[(1.6, 10.6, 'R')]),
    ('0607_2014MJ_32_q10', '10(d)'): dict(NO, f=[('2*x**2 - 5*x - 8', ''), ('-2*x - 3', '')], x=(-2, 4), y=(-12, 10), grid=(1, 2),
                                          xt=[-2, 4], yt=[-12, 10]),
    ('0607_2014MJ_32_q14', '14(d)'): dict(NO, f=[], points=CUM, smooth=True, x=(0, 50), y=(0, 30), grid=(5, 5),
                                          xt=[10, 20, 30, 40, 50], yt=[5, 10, 15, 20, 25, 30], ylab=''),
    ('0607_2014MJ_41_q06', '6(a)'): dict(NO, f=[('abs(4*x**2 - 9)', '')], x=(-2, 2), y=(-10, 10), grid=(0.5, 2), xt=[-2, 2], yt=[-10, 10]),
    ('0607_2014MJ_41_q14', '14(a)(i)'): dict(f=[('x**2/(x**2 - 2*x - 3)', '')], dash=False, x=(-5, 5), y=(-4, 4), grid=(1, 1),
                                             xt=[-5, 5], yt=[-4, 4],
                                             labels=[[('t', 'f('), ('i', 'x'), ('t', ') = '), ('frac', 'x²', 'x² − 2x − 3')]]),
    ('0607_2014MJ_61_q08', '8(a)(i)'): dict(NO, f=[('math.sin(math.radians(3*x))', '')], x=(0, 360), y=(-1, 1), grid=(30, 0.5),
                                            xt=list(range(30, 361, 30)), yt=[-1, -0.5, 0.5, 1], xlow=True),
    ('0607_2019ON_31_q10', '10(a)'): dict(NO, f=[('x**3 - 5*x**2 + 2*x + 8', '')], x=(-2, 5), y=(-25, 20), grid=(1, 5),
                                          xt=[-2, 5], yt=[-25, 20]),
    ('0607_2019ON_41_q03', '3(c)'): dict(NO, f=[('1/(1 - x**3)', ''), ('x**2 if -2 <= x <= 2 else None', '')], x=(-3, 3), y=(-2, 4),
                                         grid=(1, 1), xt=[-3, 3], yt=[-2, 4]),
    ('0607_2019ON_42_q02', '2(f)(i)'): dict(f=[('1/(x - 2)', ''), ('x**2', '')], dash=False, x=(-3, 3), y=(-3, 9), grid=(1, 1),
                                            xt=[-3, 3], yt=[-3, 9],
                                            labels=[[('t', 'f('), ('i', 'x'), ('t', ') = '), ('frac', '1', 'x − 2')],
                                                    [('t', 'h('), ('i', 'x'), ('t', ') = '), ('i', 'x'), ('sup', '2')]]),
    ('0607_2019ON_42_q12', '12(a)'): dict(f=[('1/(x*(x - 1)*(x + 1))', '')], dash=False, x=(-3, 3), y=(-4, 4), grid=(1, 1),
                                          xt=[-3, 3], yt=[-4, 4],
                                          labels=[[('t', 'f('), ('i', 'x'), ('t', ') = '), ('frac', '1', 'x(x − 1)(x + 1)')]]),
    ('0607_2019ON_62_q09', '9(a)'): dict(NO, f=[('56.2 - 15.6*math.log10(x)', '')], x=(0, 10), y=(0, 100), grid=(1, 10),
                                         xt=[10], yt=[100], ylab='P'),
    ('0607_2019ON_62_q10', '10(b)'): dict(NO, f=[('100/(1 + 0.4*x)', ''), ('56.2 - 15.6*math.log10(x)', '')], x=(0, 10), y=(0, 100),
                                          grid=(1, 10), xt=[10], yt=[100], ylab='P'),     # a = 0.4 (MS 10(a)); Eddie's model too
    ('0607_2019ON_63_q09', '9(a)'): dict(NO, f=[('5e-24*x**9.64', '')], x=(400, 600), y=(0, 3000), grid=(25, 250),
                                         xt=[400, 600], yt=[3000], xlab='h', ylab='D'),
    ('0607_2020ON_41_q03', '3(b)'): dict(NO, f=[('(4*x - 1)*(2*x + 3)', ''), ('-5', '')], x=(-1.2, 0.4), y=(-7, 1), grid=(0.2, 1),
                                         xt=[-1], yt=[]),      # the GDC method: y = (4x - 1)(2x + 3) meets y = -5 (MS 'GDC')
    ('0607_2021FM_12_q24', '24'): dict(NO, f=[('2*abs(x + 2)', ''), ('2*abs(x + 1)', '')], dash=True, x=(-4, 2), y=(-2, 4), grid=(1, 1),
                                       xt=[-4, -3, -2, -1, 1, 2], yt=[-2, -1, 1, 2, 3, 4]),   # y = f(x + 1) solid, f dotted as printed
    ('0607_2021FM_32_q12', '12(a)'): dict(NO, f=[('0.5**x', '')], x=(-3, 3), y=(-5, 8), grid=(0.5, 1), xt=[-3, 3], yt=[-5, 8]),
})
SPECS.update({
    # group 2
    ('0607_2021FM_32_q12', '12(c)'): dict(NO, f=[('0.5**x', ''), ('4 - x**2', '')], x=(-3, 3), y=(-5, 8), grid=(0.5, 1), xt=[-3, 3], yt=[-5, 8]),
    ('0607_2021FM_42_q03', '3(e)(i)'): dict(NO, h=190.0, f=[('4', ''), ('3 - x', ''), ('x - 1', '')], x=(-2, 7), y=(-2, 7), grid=(1, 1),
                                            xt=[-2, -1, 1, 2, 3, 4, 5, 6, 7], yt=[-2, -1, 1, 2, 3, 4, 5, 6, 7]),
    ('0607_2021FM_42_q07', '7(a)'): dict(NO, f=[('1/(x - 2)', '')], x=(-4, 3), y=(-3, 13), grid=(1, 1), xt=[-4, 3], yt=[-3, 13]),
    ('0607_2021FM_62_q08', '8(b)'): dict(NO, f=[('120/(math.pi*x*x)', '')], x=(0, 12), y=(0, 12), grid=(1, 1), xt=[12], yt=[12],
                                         xlab='d', ylab='h'),               # h = 120/(πd²) (MS 8(a))
    ('0607_2021FM_62_q09', '9(c)(ii)'): dict(NO, f=[('80/(math.pi*x*x)', '')], x=(0, 12), y=(0, 12), grid=(1, 1), xt=[12], yt=[12],
                                             xlab='d', ylab='w'),
    ('0607_2021FM_62_q09', '9(d)(ii)'): dict(NO, f=[('80/(math.pi*x*x)', ''), ('8.6/x', '')], x=(0, 12), y=(0, 12), grid=(1, 1),
                                             xt=[12], yt=[12], xlab='d', ylab='w'),   # w = 8.6/d (MS 9(d)(i))
    ('0607_2021MJ_41_q06', '6(c)'): dict(NO, f=[('1.04**x', ''), ('1 + 0.065*x', '')], x=(0, 28), y=(1, 3.2), grid=(2, 0.2),
                                         xt=[], yt=[]),      # e.g. y = 1.04^x and y = 1 + 0.065x (MS); no numbers printed
    ('0607_2021MJ_41_q11', '11(b)'): {'alts': [
        dict(NO, f=[('6*x - 1', ''), ('(5 + x)/(2*x + 3)', '')], x=(-3, 1), y=(-8, 4), grid=(0.5, 1), xt=[], yt=[]),
        dict(NO, f=[('(6*x - 1)*(2*x + 3)', ''), ('5 + x', '')], x=(-2.2, 0.8), y=(-9, 8), grid=(0.5, 1), xt=[], yt=[])]},
    ('0607_2022MJ_41_q09', '9(b)(i)'): dict(NO, f=[('-(x + 6)*(x - 3)**2/27', ''), ('-(x + 8)*(x - 1)**2/27', '')], x=(-10, 10),
                                            y=(-10, 10), grid=(1, 1), xt=[-10, -5, 5, 10], yt=[-10, -5, 5, 10]),
    #   (j fits the printed sketch exactly: zeros -6 and 3 (touching), min (-3, -4), y-intercept -2; j(x + 2) = j moved 2 left)
    ('0607_2022ON_62_q06', '6(b)'): dict(NO, f=[('2*6**(x - 1) - 1', ''), ('2e7', '')], x=(0, 10.5), y=(0, 3e7), grid=(1, 2.5e6),
                                      xt=[], yt=[], xlab='n', ylab=''),   # the graphical way: 2 × 6^(n-1) - 1 against 20 000 000
    ('0607_2023ON_61_q10', '10'): dict(NO, f=[('7*x', ''), ('4*x + 16', ''), ('37*math.log10(x) + 31 if x > 0 else None', '')],
                                       x=(0, 20), y=(0, 140), grid=(2, 10), xt=[], yt=[], xlab='a', ylab='b'),   # Models M, N, P
    ('0607_2024FM_32_q10', '10(a)'): dict(NO, f=[('x**2 + 3*x', '')], x=(-4, 4), y=(-30, 30), grid=(1, 5), xt=[-4, 4], yt=[-30, 30]),
    ('0607_2024FM_32_q10', '10(c)'): dict(NO, f=[('x**2 + 3*x', ''), ('5 + 3*x - x**2', '')], x=(-4, 4), y=(-30, 30), grid=(1, 5),
                                          xt=[-4, 4], yt=[-30, 30]),
    ('0607_2024FM_42_q01', '1(a)'): dict(NO, f=[('math.sin(math.radians(x))**2', '')], x=(-180, 180), y=(-1.5, 1.5), grid=(30, 0.5),
                                         xt=[-180, 180], yt=[-1.5, 1.5]),
    ('0607_2024FM_42_q01', '1(c)(i)'): dict(NO, f=[('math.sin(math.radians(x))**2', ''), ('0.002*x + 0.5', '')], x=(-180, 180),
                                            y=(-1.5, 1.5), grid=(30, 0.5), xt=[-180, 180], yt=[-1.5, 1.5]),
})
SPECS[('0607_2022ON_62_q06', '2')] = SPECS[('0607_2022ON_62_q06', '6(b)')]   # (maths_check reads this row's label as '2')
INT = lambda a, b: [v for v in range(a, b + 1) if v]
SPECS.update({
    # group 3 (M1: 2024)
    ('0607_2024FM_62_q08', '8(f)'): dict(NO, f=[('(96 + 24*x)/(2 + x)', '')], x=(0, 20), y=(0, 50), grid=(2, 5), xt=[20], yt=[48],
                                         ylab='S'),
    ('0607_2024FM_62_q09', '9(c)'): dict(NO, f=[('(96 + 24*x)/(2 + x)', ''), ('(144 + 48*x)/(6 + x)', '')], x=(0, 20), y=(0, 50),
                                         grid=(2, 5), xt=[20], yt=[], ylab=''),      # S and Y on the same axes
    ('0607_2024MJ_13_q18', '18'): dict(NO, h=160.0, f=[('x + 2', '')], x=(-4, 4), y=(-4, 4), grid=(1, 1), xt=INT(-4, 4), yt=INT(-4, 4)),
    ('0607_2024MJ_31_q07', '7(d)(i)'): dict(NO, h=170.0, f=[('0.5*x*(5 - x) + 2 if 0 <= x <= 5 else None', '')], x=(-4, 8), y=(-4, 6),
                                            grid=(1, 1), xt=INT(-4, 8), yt=INT(-4, 6)),   # f(x) = 0.5x(5 - x) fits the printed arc
    ('0607_2024MJ_31_q07', '7(d)(ii)'): dict(NO, h=170.0, f=[('0.5*(x + 3)*(2 - x) if -3 <= x <= 2 else None', '')], x=(-4, 8), y=(-4, 6),
                                             grid=(1, 1), xt=INT(-4, 8), yt=INT(-4, 6)),
    ('0607_2024MJ_31_q11', '11(b)'): dict(NO, f=[('x**2 + 2*x - 3', ''), ('-x**2 + x + 2', '')], x=(-4, 3), y=(-18, 12), grid=(1, 2),
                                          xt=[-4, 3], yt=[-18, 12]),
    ('0607_2024MJ_32_q11', '11(a)'): dict(NO, f=[('2/(x - 2)', '')], x=(-3, 5), y=(-5, 11), grid=(1, 1), xt=[-3, 5], yt=[-5, 11]),
    ('0607_2024MJ_32_q11', '11(d)'): dict(NO, f=[('2/(x - 2)', ''), ('2*x + 1', '')], x=(-3, 5), y=(-5, 11), grid=(1, 1), xt=[-3, 5], yt=[-5, 11]),
    ('0607_2024MJ_33_q12', '12(a)(i)'): dict(NO, f=[('2*x**2 - 6*x', '')], x=(-4, 6), y=(-10, 60), grid=(1, 10), xt=[-4, 6], yt=[-10, 60]),
    ('0607_2024MJ_33_q12', '12(b)'): dict(NO, f=[('2*x**2 - 6*x', ''), ('x**2 - 4*x + 15', '')], x=(-4, 6), y=(-10, 60), grid=(1, 10),
                                          xt=[-4, 6], yt=[-10, 60]),
    ('0607_2024MJ_41_q06', '6(a)'): dict(NO, f=[('2 - abs(1 - 0.5*x**2)', '')], x=(-3, 3), y=(-3, 3), grid=(0.5, 0.5), xt=[-3, 3], yt=[-3, 3]),
    ('0607_2024MJ_43_q05', '5(a)'): dict(f=[('5 + 2*x - 4*x**2 - x**3', '')], dash=False, x=(-5, 2), y=(-20, 20), grid=(1, 5), xt=[-5, 2],
                                         yt=[-20, 20], labels=[[('t', 'f('), ('i', 'x'), ('t', ') = 5 + 2'), ('i', 'x'), ('t', ' − 4'),
                                                                ('i', 'x'), ('sup', '2'), ('t', ' − '), ('i', 'x'), ('sup', '3')]]),
    ('0607_2024MJ_62_q10', '10(b)(ii)'): dict(NO, f=[('48 + 28800/x if x >= 200 else None', '')], x=(0, 1600), y=(0, 200), grid=(100, 20),
                                              xt=[200, 1600], yt=[], xlab='L', ylab='C'),
    ('0607_2024MJ_63_q07', '7(c)'): dict(NO, f=[('x*(300 - x)', '')], x=(0, 300), y=(0, 24000), grid=(25, 2000), xt=[100, 200, 300],
                                         yt=[6000, 12000, 18000, 24000], ylab='A'),     # (numbers as on the printed screenshot)
    ('0607_2024MJ_63_q10', '10(b)'): dict(NO, f=[('40000*math.sin(math.radians(x))*math.cos(math.radians(x))', '')], x=(0, 90),
                                          y=(0, 30000), grid=(10, 5000), xt=[90], yt=[30000], xlab='w', ylab='A'),
    ('0607_2024ON_31_q11', '11(a)(i)'): dict(NO, f=[('5/x', '')], x=(-3, 3), y=(-15, 15), grid=(0.5, 2.5), xt=[-3, 3], yt=[-15, 15], xlow=True),
})
for _a, _b in ((('0607_2024FM_62_q08', '48'), '8(f)'), (('0607_2024MJ_63_q07', '0'), '7(c)'), (('0607_2024MJ_63_q10', '0'), '10(b)')):
    SPECS[_a] = SPECS[(_a[0], _b)]          # (maths_check reads these rows' label as a number of the cell)
SPECS.update({
    # group 4 (M1: 2024 ON, 2025 FM/MJ)
    ('0607_2024ON_31_q11', '11(b)'): dict(NO, f=[('5/x', ''), ('3*x - 2', '')], x=(-3, 3), y=(-15, 15), grid=(0.5, 2.5), xt=[-3, 3],
                                          yt=[-15, 15], xlow=True),
    ('0607_2024ON_32_q12', '12(a)(i)'): dict(NO, f=[('x**3 + 6*x**2', '')], x=(-6, 2), y=(-5, 40), grid=(1, 5), xt=[-6, 2], yt=[-5, 40]),
    ('0607_2024ON_32_q12', '12(b)'): dict(NO, f=[('x**3 + 6*x**2', ''), ('10 - 3*x', '')], x=(-6, 2), y=(-5, 40), grid=(1, 5),
                                          xt=[-6, 2], yt=[-5, 40]),
    ('0607_2024ON_41_q09', '9(a)'): dict(NO, f=[('1/((2*x - 3)*(2*x + 1))', '')], x=(-2, 4), y=(-4, 4), grid=(0.5, 1), xt=[-2, 4], yt=[-4, 4]),
    ('0607_2024ON_43_q04', '4(a)'): dict(NO, f=[('x**3 - 4*x + 2', '')], x=(-3, 3), y=(-13, 17), grid=(1, 2), xt=[-3, 3], yt=[-13, 17]),
    ('0607_2024ON_43_q04', '4(c)'): dict(NO, f=[('x**3 - 4*x + 2', ''), ('3/x + x**2', '')], x=(-3, 3), y=(-13, 17), grid=(1, 2),
                                         xt=[-3, 3], yt=[-13, 17]),
    ('0607_2024ON_61_q02', '2(d)'): dict(NO, h=1.0, f=[('1.5*x**2 + 0.5*x', '')], x=(0, 25), y=(0, 1000), grid=(5, 100), xt=[], yt=[],
                                         xlab='k', ylab=''),         # the GDC way: total cards 1.5k² + 0.5k (= 737)
    ('0607_2024ON_61_q03', '3(c)'): dict(NO, f=[('x*(x + 1)*(x - 1)/6', '')], x=(0, 30), y=(0, 4000), grid=(5, 500), xt=[], yt=[],
                                         xlab='t', ylab='H'),       # H = t(t + 1)(t - 1)/6 (= 2925)
    ('0607_2024ON_61_q05', '5(c)'): dict(NO, f=[('268 - 248*x**0.0139', ''), ('10', '')], x=(5, 20), y=(9, 15), grid=(1, 0.5),
                                         xt=[5, 10, 15, 20], yt=[10, 11, 12, 13, 14, 15]),   # y = 268 - 248x^0.0139 (MS 5(b))
    ('0607_2024ON_61_q06', '6(a)'): dict(NO, f=[('0.0381*x**2 - 6.23*x + 269', '')], x=(82, 105), y=(10, 40), grid=(1, 5),
                                         xt=[82, 105], yt=[10, 20, 30, 40]),
    ('0607_2024ON_62_q09', '9(a)'): dict(NO, f=[('(100/x)**2', '')], x=(0, 10), y=(0, 3000), grid=(1, 250), xt=[10], yt=[3000],
                                         xlab='D', ylab='N'),       # N = (100/D)² (MS 8)
    ('0607_2025FM_32_q16', '16(a)'): dict(NO, f=[('2*x**2 + x - 6', '')], x=(-3, 4), y=(-12, 30), grid=(1, 3), xt=[-3, 4], yt=[-12, 30]),
    ('0607_2025FM_32_q16', '16(b)(i)'): dict(NO, f=[('2*x**2 + x - 6', ''), ('3 + 2*x - x**2', '')], x=(-3, 4), y=(-12, 30), grid=(1, 3),
                                             xt=[-3, 4], yt=[-12, 30]),
    ('0607_2025FM_42_q08', '8(a)'): dict(NO, f=[('1/(1 + x**2)', '')], x=(-3, 3), y=(-2, 2), grid=(0.5, 0.5), xt=[-3, 3], yt=[-2, 2]),
    ('0607_2025FM_42_q08', '8(b)'): dict(NO, col=3, f=[('1/(1 + x**2)', ''), ('x**2 + x - 1', '')], x=(-3, 3), y=(-2, 2), grid=(0.5, 0.5),
                                         xt=[-3, 3], yt=[-2, 2]),
    ('0607_2025MJ_23_q14', '14(b)'): dict(NO, f=[('math.cos(math.radians(x))', '')], x=(0, 360), y=(-1, 1), grid=(30, 0.5), xt=[360],
                                          yt=[-1, 1]),
})
for _a, _b in ((('0607_2024ON_61_q02', '3'), '2(d)'), (('0607_2024ON_61_q03', '3'), '3(c)'), (('0607_2024ON_61_q05', '10'), '5(c)')):
    SPECS[_a] = SPECS[(_a[0], _b)]
DV = '(x*x + x*math.sqrt(x*x + 80))/20'                 # 2025 MJ 62: D = (V² + V√(V² + 80))/20 (MS 9(b))
SPECS.update({
    # group 5 (M1: 2025 MJ / ON)
    ('0607_2025MJ_31_q18', '18(a)'): dict(NO, f=[('7/(x + 2)', '')], x=(-10, 10), y=(-10, 10), grid=(1, 1), xt=[-10, 10], yt=[-10, 10]),
    ('0607_2025MJ_31_q18', '18(c)'): dict(NO, f=[('7/(x + 2)', ''), ('x/5', '')], x=(-10, 10), y=(-10, 10), grid=(1, 1), xt=[-10, 10],
                                          yt=[-10, 10]),
    ('0607_2025MJ_32_q17', '17(a)'): dict(NO, f=[('(3*x + 6)/(x - 2)', '')], x=(-10, 10), y=(-10, 10), grid=(1, 1), xt=[-10, 10], yt=[-10, 10]),
    ('0607_2025MJ_32_q17', '17(c)'): dict(NO, f=[('(3*x + 6)/(x - 2)', ''), ('x', '')], x=(-10, 10), y=(-10, 10), grid=(1, 1),
                                          xt=[-10, 10], yt=[-10, 10]),
    ('0607_2025MJ_33_q17', '17(a)(i)'): dict(NO, f=[('x**3 + 6*x**2 + 2*x - 20', '')], x=(-6, 3), y=(-35, 70), grid=(1, 5),
                                             xt=[-6, 3], yt=[-35, 70]),
    ('0607_2025MJ_33_q17', '17(b)'): dict(NO, f=[('x**3 + 6*x**2 + 2*x - 20', ''), ('3*x + 10', '')], x=(-6, 3), y=(-35, 70), grid=(1, 5),
                                          xt=[-6, 3], yt=[-35, 70]),
    ('0607_2025MJ_41_q11', '11(a)'): dict(f=[('x**3/((x + 2)*(x - 3))', '')], dash=False, x=(-10, 10), y=(-20, 20), grid=(1, 2.5),
                                          xt=[-10, 10], yt=[-20, 20],
                                          labels=[[('t', 'f('), ('i', 'x'), ('t', ') = '), ('frac', 'x³', '(x + 2)(x − 3)')]]),
    ('0607_2025MJ_42_q13', '13'): dict(NO, f=[('5*0.8**x', ''), ('2*x + 7', '')], x=(-5, 5), y=(-12, 15), grid=(1, 2), xt=[-4, -2, 2, 4],
                                       yt=[-10, 10]),       # no axes in the question: the printed screenshot's window
    ('0607_2025MJ_62_q07', '7(c)(ii)'): dict(NO, f=[('10*x + 2 - 4.9*x*x', '')], x=(0, 2.3), y=(0, 8), grid=(0.25, 1), xt=[1, 2],
                                             yt=[2, 4, 6], ylab='H'),
    ('0607_2025MJ_62_q09', '9(c)(i)'): {'col': 3, 'graphs': [
        dict(NO, f=[(DV, ''), ('82.98', '')], x=(0, 30), y=(0, 120), grid=(5, 20), xt=[30], yt=[100], xlab='V', ylab='D'),
        dict(NO, f=[(DV + ' - 82.98', '')], x=(-30, 30), y=(-100, 100), grid=(5, 25), xt=[], yt=[], xlab='V', ylab='')]},
    ('0607_2025MJ_63_q08', '8(a)'): dict(NO, f=[('-0.32*x*x + 12.4*x + 2', '')], x=(0, 30), y=(0, 140), grid=(2, 10), xt=[30],
                                         yt=[50, 100], ylab='L'),                       # Irene: L = -0.32x² + 12.4x + 2 (MS 6(b))
    ('0607_2025MJ_63_q08', '8(b)'): dict(NO, f=[('123/(1 + 3.2*10**(-0.103*x))', '')], x=(0, 30), y=(0, 140), grid=(2, 10), xt=[30],
                                         yt=[50, 100], ylab='L'),                       # Mayuko: k = 0.103 (MS 7(c))
    ('0607_2025ON_31_q19', '19(a)'): dict(NO, f=[('(3 - x)*(x - 5)', '')], x=(0, 8), y=(-16, 4), grid=(1, 2), xt=[8], yt=[-16, 4]),
    ('0607_2025ON_33_q18', '18(a)'): dict(NO, f=[('2*x**2 - 8*x + 3', '')], x=(-1, 5), y=(-10, 15), grid=(1, 2.5), xt=[-1, 5], yt=[-10, 15]),
    ('0607_2025ON_41_q08', '8(a)'): dict(f=[('2**x/(x + 2)', '')], dash=False, x=(-5, 5), y=(-5, 5), grid=(1, 1), xt=[-5, 5], yt=[-5, 5],
                                         labels=[[('t', 'f('), ('i', 'x'), ('t', ') = '), ('frac', '2ˣ', 'x + 2')]]),
    ('0607_2025ON_42_q08', '8(a)(i)'): dict(NO, f=[('1/((2*x - 1)*(x + 1)) - 1', '')], x=(-4, 4), y=(-4, 4), grid=(0.5, 0.5),
                                            xt=[-4, 4], yt=[-4, 4], xlow=True),
})
VL = '0.5*x*x + 1.5*x'                       # 2025 ON 62: vertical lines in Tower t (MS 2(c))
SPECS.update({
    # group 6 (M1: 2025 ON, 2026)
    ('0607_2025ON_42_q08', '8(b)'): dict(NO, f=[('1/((2*x - 1)*(x + 1)) - 1', ''), ('0.5*(x + 1)', '')], x=(-4, 4), y=(-4, 4),
                                         grid=(0.5, 0.5), xt=[-4, 4], yt=[-4, 4], xlow=True),
    ('0607_2025ON_43_q04', '4(f)(ii)'): dict(NO, f=[('x**4 + 4*x**3', ''), ('20 + 10*x', '')], vlines=[-2],
                                             band=('x**4 + 4*x**3 if x <= -2 else 0', 'max(20 + 10*x, x**4 + 4*x**3) if x <= -2 else 0'),
                                             x=(-4.5, 2), y=(-30, 50), grid=(0.5, 5), xt=[-4.5, 2], yt=[-30, 50], tags=[(-3.2, -15, 'R')]),
    ('0607_2025ON_61_q05', '5(b)(i)'): dict(NO, f=[('195/(39*x + 160)', '')], x=(0, 50), y=(0, 1.2), grid=(5, 0.1),
                                            xt=[10, 20, 30, 40, 50], yt=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2], xlab='h', ylab='d'),
    ('0607_2025ON_61_q05', '5(c)(i)'): dict(NO, f=[('1/math.log10(2*x + 3) - 0.5', '')], x=(0, 50), y=(0, 1.2), grid=(5, 0.1),
                                            xt=[10, 20, 30, 40, 50], yt=[0.2, 0.4, 0.6, 0.8, 1.0, 1.2], xlab='h', ylab='d'),
    ('0607_2025ON_62_q02', '2(d)'): {'alts': [
        dict(NO, f=[(VL, ''), ('902', '')], x=(0, 45), y=(0, 1000), grid=(5, 100), xt=[], yt=[], xlab='t', ylab=''),
        dict(NO, col=3, f=[(VL, '')], x=(0, 45), y=(0, 1000), grid=(5, 100), xt=[], yt=[], xlab='t', ylab='')]},
    ('0607_2025ON_62_q04', '4(b)'): dict(NO, f=[('0.001595*x*x - 6.399*x + 6419', '')], x=(2020, 2050), y=(0, 4.5), grid=(5, 0.5),
                                         xt=[2020, 2050], yt=[1.2585], xlab='t', ylab='m'),
    ('0607_2025ON_63_q01', '1(a)(i)'): dict(NO, f=[('1.5*x*x - 6*x + 4', ''), ('3*x*x - 6*x + 4', ''), ('x*x - 6*x + 4', '')],
                                            x=(-1, 7), y=(-6, 6), grid=(1, 1), xt=[2, 4, 6], yt=[-6, -4, -2, 2, 4, 6]),
    ('0607_2025ON_63_q02', '2(a)(i)'): dict(NO, h=160.0, f=[(f'x*x + {b}*x', '') for b in (-6, -4, -2, 0, 2, 4, 6)], x=(-8, 6), y=(-10, 8),
                                            grid=(1, 1), xt=[-8, -6, -4, -2, 2, 4, 6], yt=[-10, -8, -6, -4, -2, 2, 4, 6, 8]),
    ('0607_2025ON_63_q04', '4(d)'): dict(NO, f=[('100*x/(200 - x)', '')], x=(0, 100), y=(0, 100), grid=(10, 10), xt=[100], yt=[100]),
    ('0607_2026FM_32_q17', '17(a)'): dict(NO, f=[('6/(4 - x)', '')], x=(-5, 10), y=(-10, 15), grid=(1, 1), xt=[-5, 10], yt=[-10, 15]),
    ('0607_2026FM_32_q17', '17(c)'): dict(NO, f=[('6/(4 - x)', ''), ('5 - x', '')], x=(-5, 10), y=(-10, 15), grid=(1, 1), xt=[-5, 10],
                                          yt=[-10, 15]),
    ('0607_2026FM_42_q10', '10(a)'): dict(f=[('2*x/(x*x + x - 12)', '')], dash=False, x=(-8, 8), y=(-8, 8), grid=(1, 1), xt=[-8, 8],
                                          yt=[-8, 8], labels=[[('t', 'f('), ('i', 'x'), ('t', ') = '), ('frac', '2x', 'x² + x − 12')]]),
    ('0607_2026FM_62_q06', '6(a)'): dict(NO, f=[('144000 + 19200/x + 12*x', '')], x=(0, 150), y=(144000, 146000), grid=(10, 250),
                                         xt=[150], yt=[144000, 145000, 146000], ylab='T'),
    ('0607_2026MJ_31_q17', '17(a)'): dict(NO, f=[('2*x*x - 5*x + 1', '')], x=(-2, 4), y=(-5, 20), grid=(0.5, 2.5), xt=[-2, 4], yt=[-5, 20]),
    ('0607_2026MJ_32_q14', '14(a)(i)'): dict(NO, f=[('x*x + 2', ''), ('x**3 + x*x - 5*x + 2', '')],
                                             x=(-3, 3), y=(-5, 25), grid=(0.5, 2.5), xt=[-3, 3], yt=[-5, 25]),   # (the screenshot shows both)
})
F43 = '1/(x - 2) + 3/(2*x - 1)'                      # 2026 MJ 43 q9 f(x)
SPECS.update({
    # group 7 (M1: 2026 MJ)
    ('0607_2026MJ_32_q14', '14(b)'): dict(NO, f=[('x*x + 2', ''), ('x**3 + x*x - 5*x + 2', '')], x=(-3, 3), y=(-5, 25), grid=(0.5, 2.5),
                                          xt=[-3, 3], yt=[-5, 25]),
    ('0607_2026MJ_33_q20', '20(a)'): dict(NO, f=[('x*x - 4*x + 3', '')], x=(-2, 4), y=(-2, 20), grid=(0.5, 2), xt=[-2, 4], yt=[-2, 20]),
    ('0607_2026MJ_41_q06', '6(a)'): dict(NO, f=[('0.5*x**3 - 2*x + 2', '')], x=(-3, 3), y=(-6, 10), grid=(0.5, 1), xt=[-3, 3], yt=[-6, 10]),
    ('0607_2026MJ_41_q17', '17'): dict(NO, f=[('x*x + 3*x - 6', '')], x=(-6, 2.5), y=(-10, 10), grid=(1, 2), xt=[-5], yt=[-10, 10]),
    #   (no axes in the question: the printed screenshot's window)
    ('0607_2026MJ_42_q05', '5(a)'): dict(NO, f=[('5/x**2 + 1/x**3', '')], x=(-2, 2), y=(-5, 25), grid=(0.5, 2.5), xt=[-2, 2], yt=[-5, 25]),
    ('0607_2026MJ_43_q09', '9(a)(i)'): dict(NO, f=[(F43, '')], x=(-4, 4), y=(-6, 6), grid=(0.5, 1), xt=[-4, 4], yt=[-6, 6]),
    ('0607_2026MJ_43_q09', '9(b)'): dict(NO, f=[(F43, ''), ('x - 1', '')], x=(-4, 4), y=(-6, 6), grid=(0.5, 1), xt=[-4, 4], yt=[-6, 6]),
    ('0607_2026MJ_43_q17', '17(a)'): dict(NO, f=[('2**x', ''), ('0.5*x + 1.5', '')], x=(-4, 2.5), y=(-0.5, 4), grid=(0.5, 0.5), xt=[], yt=[]),
    ('0607_2026MJ_61_q06', '6(b)'): dict(NO, f=[('math.pi*x*(20 - x)**2/4', '')], x=(0, 20), y=(0, 1000), grid=(1, 100), xt=[20], yt=[],
                                         xlab='h', ylab='V'),     # V = πh(20 - h)²/4 (question 6(a))
    ('0607_2026MJ_61_q07', '7(b)(ii)'): dict(NO, f=[('4*math.pi*x**3/(x - 8) if x > 8 else None', '')], x=(0, 25), y=(0, 20000),
                                             grid=(2.5, 2000), xt=[], yt=[], xlab='R', ylab='V'),   # V = 4πR³/(R - 8) (7(b)(i))
    ('0607_2026MJ_63_q09', '9'): dict(NO, f=[('50*math.sqrt(1 + x*x/9)', ''), ('100', '')], x=(0, 8.5), y=(0, 130), grid=(0.5, 10),
                                      xt=[], yt=[], xlab='t', ylab=''),     # H = 50√(1 + t²/3²) = 100 (MS)
})
CHIRP = [(14, 83), (16, 88), (17, 102), (19, 106), (21, 129), (22, 138), (23, 157), (25, 180), (27, 208)]   # 2022 MJ 62 table
ARRIVE = [(60, 23), (120, 42), (180, 58), (240, 71), (300, 80), (360, 86), (420, 92), (480, 96), (540, 98), (600, 99), (660, 99),
          (720, 99), (780, 100), (840, 100), (900, 100)]                                                        # 2022 MJ 63 9(a)
SPECS.update({
    # data plots and bar charts (RD2)
    ('0607_2019ON_62_q07', '7(b)'): dict(NO, f=[], points=[(0, 16000), (1, 8000), (2, 4000), (3, 2000), (4, 1000), (5, 500), (6, 250)],
                                         smooth=True, x=(0, 6), y=(0, 16000), grid=(0.5, 1000), xt=[1, 2, 3, 4, 5, 6],
                                         yt=[4000, 8000, 12000, 16000], ylab='V'),
    ('0607_2019ON_62_q08', '8(a)'): dict(NO, f=[], points=[(0, 100), (1, 72), (2, 58), (3, 48), (4, 44), (5, 42), (6, 40)], x=(0, 6),
                                         y=(0, 100), grid=(0.5, 10), xt=[1, 2, 3, 4, 5, 6], yt=[20, 40, 60, 80, 100], ylab='P'),
    ('0607_2020MJ_63_q06', '6(a)(i)'): dict(NO, f=[], dots=True, points=[(1, 2), (2, 3), (3, 5), (4, 7), (5, 2), (6, 4), (7, 8), (8, 1)],
                                            x=(0, 9), y=(0, 9), grid=(1, 1), xt=[5], yt=[1, 2, 3, 4, 5, 6, 7, 8, 9], xlab='n',
                                            ylab='D(Pₙ)'),          # digital roots of the primes 2, 3, 5, 7 (and 11, 13, 17, 19 printed)
    ('0607_2021MJ_62_q08', '8(c)(i)'): dict(NO, f=[('0.0048*x*x - 0.1619*x + 1.3281 if 2 <= x <= 22 else None', '')], dash=True,
                                            x=(0, 25), y=(-0.1, 1), grid=(1, 0.1), xt=[5, 10, 15, 20, 25], yt=[0.5, 1], xlab='F',
                                            ylab='p', points=[(2, 0.99), (4, 0.85), (6, 0.56), (8, 0.26), (10, 0.11), (12, 0.04),
                                                              (14, 0.02), (16, 0.02), (18, 0.02), (20, 0.02), (22, 0.01)]),
    ('0607_2022MJ_62_q08', '8(b)'): dict(NO, f=[('0.5*x*x - 11*x + 136', '')], points=CHIRP, x=(10, 30), y=(70, 220), grid=(1, 10),
                                         xt=[15, 20, 25, 30], yt=[80, 120, 160, 200], xlab='T', ylab='N'),   # a = -11, b = 136 (MS 8(a))
    ('0607_2022MJ_63_q10', '10(f)'): dict(NO, f=[('13*(x - 54)**(1/3) if x >= 54 else None', '')], dots=True, points=ARRIVE, x=(0, 900),
                                          y=(0, 110), grid=(50, 10), xt=[300, 600, 900], yt=[50, 100], xlab='t', ylab='p'),
    ('0607_2022ON_32_q07', '7(c)'): dict(NO, f=[], points=[(0, 0), (15, 2), (30, 6), (45, 15), (60, 27), (75, 42), (90, 54), (105, 58),
                                                           (120, 60)], smooth=True, x=(0, 120), y=(0, 60), grid=(10, 5),
                                         xt=[20, 40, 60, 80, 100, 120], yt=[10, 20, 30, 40, 50, 60], xlab='t', ylab=''),
    ('0607_2024MJ_31_q02', '2(f)'): {'bars': [('blue', 7), ('yellow', 3), ('pink', 2), ('green', 5), ('purple', 4)], 'y': (0, 8),
                                     'yt': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'grid': (None, 1), 'w': 230.0, 'h': 140.0},
    ('0607_2024MJ_32_q08', '8(d)(i)'): {'bars': [('Walk', 4), ('Bicycle', 6), ('Bus', 7), ('Car', 3)], 'y': (0, 8),
                                        'yt': [0, 1, 2, 3, 4, 5, 6, 7, 8], 'grid': (None, 1), 'w': 200.0, 'h': 140.0},
    ('0607_2025FM_42_q09', '9(a)'): dict(NO, f=[], points=[(1, 4), (2, 6), (3, 3), (4, 8), (6, 6), (7, 7), (8, 7), (9, 8), (10, 9)],
                                         x=(0, 10), y=(0, 10), grid=(1, 1), xt=[2, 4, 6, 8, 10], yt=[2, 4, 6, 8, 10]),
    ('0607_2026MJ_13_q06', '6(a)'): {'bars': [('water', 20), ('milk', 8), ('juice', 12)], 'y': (0, 20),
                                     'yt': [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20], 'grid': (None, 1), 'w': 170.0, 'h': 170.0},
})
SPECS[('0607_2019ON_62_q08', '7')] = SPECS[('0607_2019ON_62_q08', '8(a)')]
SPECS.update({
    # probability trees, pie charts, mapping diagrams (RD2)
    ('0607_2019ON_31_q12', '12(a)'): {'w': 270.0, 'h': 180.0, 'tree': {
        'first': [('5/7', ['school day']), ('2/7', ['non-school', 'day'])],
        'second': [[('9/10', ['gets up', 'before 7 am']), ('1/10', ['does not get', 'up before 7 am'])],
                   [('1/20', ['gets up', 'before 7 am']), ('19/20', ['does not get', 'up before 7 am'])]]}},
    ('0607_2026FM_12_q19', '19(a)'): {'w': 230.0, 'h': 170.0, 'tree': {
        'first': [('1/4', ['tea']), ('3/4', ['not tea'])],
        'second': [[('1/4', ['tea']), ('3/4', ['not tea'])], [('1/4', ['tea']), ('3/4', ['not tea'])]]}},
    ('0607_2026MJ_11_q14', '14(b)(i)'): {'w': 250.0, 'h': 170.0, 'tree': {
        'first': [('6/11', ['apple']), ('5/11', ['not an', 'apple'])],
        'second': [[('6/11', ['apple']), ('5/11', ['not an', 'apple'])], [('6/11', ['apple']), ('5/11', ['not an', 'apple'])]]}},
    ('0607_2022ON_32_q04', '4(b)(ii)'): {'pie': [(60, '27'), (105, '28'), (120, '29'), (75, '30')], 'w': 160.0, 'h': 150.0},
    ('0607_2023ON_31_q03', '3(b)'): {'pie': [(75, 'books'), (165, 'food'), (120, 'clothes')], 'w': 160.0, 'h': 150.0},
    ('0607_2023ON_31_q09', '9(a)'): {'map': {'l': ['0', '1', '2'], 'r': ['–1', '2', '5'], 'a': [(0, 0), (1, 1), (2, 2)]},
                                     'w': 150.0, 'h': 90.0},
    ('0607_2025FM_12_q04', '4'): {'map': {'l': ['[5]', '[–2]', '0'], 'r': ['16', '2', '[6]'], 'a': [(0, 0), (1, 1), (2, 2)]},
                                  'w': 170.0, 'h': 100.0},
})
_S3 = 3 ** 0.5
_AB = (300 * math.sin(math.radians(60)), 300 * math.cos(math.radians(60)))        # 2020 MJ 31 q8: B from A, C from B
_C = (_AB[0] + 220 * math.sin(math.radians(150)), _AB[1] + 220 * math.cos(math.radians(150)))
SPECS.update({
    # sketches with clear data (RD2)
    ('0607_2020MJ_31_q08', '8(a)'): {'w': 260.0, 'h': 130.0, 'plane': {
        'style': 'none', 'n': (-30, 400, -70, 200),
        'polys': [{'p': [(0, 0), _AB, _C], 'open': True, 'sw': 0.9}, {'p': [_C, (0, 0)], 'open': True, 'sw': 0.7, 'dash': '3 2'},
                  {'p': [(0, 0), (0, 70)], 'open': True, 'sw': 0.7}, {'p': [_AB, (_AB[0], _AB[1] + 50)], 'open': True, 'sw': 0.7}],
        'arcs': [(0, 0, 22, 90, 30), (_AB[0], _AB[1], 18, 90, -60)],
        'text': [(-14, -12, 'A', {'i': 1}), (_AB[0] - 16, _AB[1] + 12, 'B', {'i': 1}), (_C[0] + 10, _C[1] - 8, 'C', {'i': 1}),
                 (0, 84, 'North', {'s': 8}), (30, 42, '060°', {'s': 8}), (_AB[0] + 35, _AB[1] + 10, '150°', {'s': 8}),
                 (120, 100, '300 m', {'s': 8}), (_AB[0] + 92, _AB[1] - 90, '220 m', {'s': 8})]}},
    ('0607_2021MJ_52_q05', '5(a)'): {'w': 200.0, 'h': 150.0, 'plane': {
        'style': 'iso', 'n': (-4, 4, -4, 4), 'dot': 0.9,
        'circles': [(0, 0, 1), (0, 0, _S3), (0, 0, 2), (0, 0, 7 ** 0.5), (0, 0, 3)],     # the 5th nearest neighbours: radius 3
        'text': [(0, 0, 'X', {'b': 1, 's': 7})]}},
    ('0607_2023MJ_32_q07', '7(a)'): {'w': 250.0, 'h': 130.0, 'plane': {
        'style': 'none', 'n': (0, 10, 0, 5.2),
        'polys': [{'p': [(0, 0), (10, 0), (10, 5.2), (0, 5.2)], 'sw': 0.7}, {'p': [(5, 0), (5, 5.2)], 'open': True, 'sw': 0.7},
                  {'p': [(0, 2.6), (10, 2.6)], 'open': True, 'sw': 0.7},
                  {'p': [(1.5, 4.9), (1.5, 3.4), (3.3, 3.4)], 'open': True, 'sw': 0.9},                 # right angle
                  {'p': [(1.5, 3.65), (1.75, 3.65), (1.75, 3.4)], 'open': True, 'sw': 0.6},
                  {'p': [(6.3, 4.7), (7.6, 3.4), (9.2, 3.4)], 'open': True, 'sw': 0.9},                 # obtuse
                  {'p': [(3.4, 1.4), (1.6, 0.8), (3.6, 0.8)], 'open': True, 'sw': 0.9},                 # acute
                  {'p': [(7.2, 2.1), (7.5, 1.2), (8.3, 0.6)], 'open': True, 'sw': 0.9}],                # reflex
        'arcs': [(7.6, 3.4, 0.35, 0, 135), (1.6, 0.8, 0.6, 0, 18.4), (7.5, 1.2, 0.3, 108.4, 323.1 + 360 - 360)],
        'text': [(2.5, 2.9, 'A right angle', {'s': 7}), (7.5, 2.9, 'An obtuse angle', {'s': 7}),
                 (2.5, 0.3, 'An acute angle', {'s': 7}), (7.5, 0.3, 'A reflex angle', {'s': 7})]}},
})
CK = '✓'
SPECS.update({
    # tables (RD2): '*' bold (the answer), '~' grey (given in the question), as printed
    ('0607_2018ON_63_q01', '1(a)'): {'table': {'rows': [['Number of dots in row', 'Number of pairs of nearest neighbours'],
                                                       ['~2', '~1'], ['3', '*2'], ['~4', '~3'], ['5', '*4'], ['6', '*5'], ['', ''],
                                                       ['_n', '*n − 1']], 'size': 8.0}},
    ('0607_2018ON_63_q01', '1(b)'): {'table': {'rows': [['Number of dots in row', 'Total number of different\narrangements of two crosses'],
                                                       ['2', '~1'], ['3', '*3'], ['4', '~6'], ['5', '*10'], ['6', '~15'], ['', ''],
                                                       ['_n', '']], 'shade': [(7, 1)], 'size': 8.0}},
    ('0607_2021MJ_52_q01', '1(a)'): {'table': {'rows': [
        ['Point', 'At the centre of\na square', 'Inside a square,\nnot at its centre', 'On the side of\ntwo squares', 'Where 4\nsquares meet'],
        ['(0, 0)', '~' + CK, '', '', ''], ['(–1, 0.5)', '', '', '~' + CK, ''], ['(0.5, 0.5)', '', '', '', '~' + CK],
        ['(1.5, 1.5)', '', '', '', '*' + CK], ['(0, 1.5)', '', '', '*' + CK, ''], ['(0.25, 0)', '', '*' + CK, '', ''],
        ['(100.5, 99.5)', '', '', '', '*' + CK]], 'size': 7.0, 'pad': 3.0}},
    ('0607_2021MJ_62_q04', '4'): {'table': {'rows': [['4th'], ['8'], ['4']], 'size': 9.0, 'minw': 40.0}},
    ('0607_2023ON_52_q01', '2'): {'table': {'rows': [
        ['Hour shown\nby hand H\n(x)', 'Angle between hand H\nand hand M', None], [None, 'Clockwise\nangle', 'Anticlockwise\nangle'],
        ['1', '~30', '~330'], ['2', '*60', '*300'], ['3', '*90', '*270'], ['4', '~120', '~240'], ['5', '*150', '*210'],
        ['6', '~180', '*180']], 'span': {(0, 1): 2}, 'vspan': {(0, 0): 2}, 'nohl': [(1, 0)], 'size': 8.0}},
    ('0607_2023ON_52_q03', '3'): {'table': {'rows': [
        ['Number of\nminutes after\n1.00 am (m)', 'Angle rotated\nafter 1.00 am', None, 'Clockwise\nangle between\nthe hands (c)'],
        [None, 'Hand H\nangle', 'Hand M\nangle', None],
        ['6', '*3', '*36', '*3'], ['7', '~3.5', '~42', '~8.5'], ['8', '*4', '*48', '*14'], ['9', '*4.5', '*54', '*19.5'],
        ['10', '~5', '~60', '~25']], 'span': {(0, 1): 2}, 'vspan': {(0, 0): 2, (0, 3): 2}, 'nohl': [(1, 0), (1, 3)], 'size': 7.5, 'pad': 4.0}},
    ('0607_2024ON_11_q02', '2'): {'table': {'rows': [['70', '15', '85'], ['65', '20', '85'], ['85', '40', '125'], ['80', '25', '105'],
                                                    ['300', '100', '400']],
                                           'shade': [(0, 0), (0, 2), (1, 1), (1, 2), (2, 0), (2, 1), (3, 1), (3, 2), (4, 0), (4, 2)],
                                           'size': 9.0, 'minw': 34.0}},
    ('0607_2024ON_12_q10', '10'): {'table': {'rows': [['0', '*8   9   9   9'], ['1', '*0   2   3   7   7   8'], ['2', '*0   1   2   5'],
                                                     ['Key  1 | 2  represents  12  photos', None]],
                                            'span': {(3, 0): 2}, 'noframe': True, 'hlines': [0, 1, 2, 3], 'vlines': [1],
                                            'align': 'l', 'size': 9.0}},
    ('0607_2026MJ_33_q09', '9(a)'): {'table': {'rows': [['0', '1   1   1   2   4   5   7'], ['1', '0   2   3   6   7   8']],
                                              'noframe': True, 'hlines': [1], 'vlines': [1], 'align': 'l', 'size': 10.0}},
    ('0607_2025ON_11_q01', '1(b)'): {'w': 150.0, 'h': 80.0, 'plane': {
        'style': 'none', 'n': (0, 8, 0, 4.2),
        'text': [(2, 3.4, '7'), (3, 3.4, '2'), (4, 3.4, '3'), (4.6, 3.4, '.'), (5.2, 3.4, '5'), (6.2, 3.4, '8'),
                 (0.6, 2.3, '+'), (2, 2.3, '2'), (3, 2.3, '0'), (4, 2.3, '6'), (4.6, 2.3, '.'), (5.2, 2.3, '6'), (6.2, 2.3, '3'),
                 (2, 0.7, '9'), (3, 0.7, '3'), (4, 0.7, '0'), (4.6, 0.7, '.'), (5.2, 0.7, '2'), (6.2, 0.7, '1')],
        'polys': [{'p': [(0.2, 1.5), (7, 1.5)], 'open': True, 'sw': 0.7}] + [
            {'p': [(a - 0.42, b - 0.5), (a + 0.42, b - 0.5), (a + 0.42, b + 0.5), (a - 0.42, b + 0.5)], 'sw': 0.7}
            for a, b in ((3, 3.4), (4, 2.3), (5.2, 2.3), (2, 0.7), (6.2, 0.7))]}},     # boxed digits = the answers
})
SPECS.update({
    # Venn diagrams (RD2): numbers per region as printed
    ('0607_2019ON_31_q09', '9(d)'): {'venn': {'sets': 'BC', 'shade': 'B and not C'}, 'w': 180.0, 'h': 100.0},
    ('0607_2021FM_32_q09', '9(a)(ii)'): {'venn': {'sets': 'AB', 'nums': {'A': '4\n6\n8', 'AB': '2\n10', 'B': '1\n5', '': '3   7   9'},
                                                  'out': 'bottom'}, 'w': 190.0, 'h': 115.0},
    ('0607_2021FM_32_q09', '9(b)'): {'venn': {'sets': 'PQ', 'shade': 'not (P or Q)'}, 'w': 180.0, 'h': 100.0},
    ('0607_2024FM_42_q06', '6(a)(i)'): {'venn': {'sets': 'PQ', 'nums': {'P': '1   2\n4', 'PQ': '3\n6\n12', 'Q': '9\n15',
                                                                       '': '5   7   8   10   11   13   14'}, 'out': 'bottom'},
                                        'w': 200.0, 'h': 120.0},
    ('0607_2024MJ_13_q19', '19'): {'venn': {'sets': 'PQ', 'nums': {'P': 'c   e\ni   r   y', 'PQ': 'm   h\nt   s', 'Q': 'a',
                                                                  '': 'b   d   v'}, 'out': 'bottom'}, 'w': 200.0, 'h': 120.0},
    ('0607_2024MJ_41_q07', '7(b)(i)'): {'venn': {'sets': 'AB', 'shade': 'A or B'}, 'w': 180.0, 'h': 100.0},
    ('0607_2024ON_41_q07', '7(a)(i)'): {'venn': {'sets': 'CPB', 'nums': {'B': '13 − y', 'CB': '6', 'PB': '11', 'CPB': 'x', 'C': 'y',
                                                                         'CP': '2', 'P': '12'}}, 'w': 200.0, 'h': 150.0},
    ('0607_2025MJ_11_q16', '16(a)'): {'venn': [{'sets': 'AB', 'shade': 'B'}, {'sets': 'AB', 'shade': 'A or B'}], 'w': 300.0, 'h': 90.0},
    ('0607_2025MJ_11_q16', '16(b)'): {'venn': {'sets': 'CL', 'nums': {'C': 43, 'CL': 12, 'L': 20, '': '[5]'}}, 'w': 190.0, 'h': 105.0},
    ('0607_2025MJ_12_q16', '16(a)'): {'venn': {'sets': 'EC', 'nums': {'E': 3, 'EC': 8, 'C': 5, '': 9}}, 'w': 190.0, 'h': 105.0},
    ('0607_2025ON_13_q12', '12(c)'): {'venn': {'sets': 'ET', 'nums': {'E': '8   10', 'ET': '2   4\n6   12', 'T': '1   3',
                                                                      '': '5   7   9   11'}, 'out': 'bottom'}, 'w': 200.0, 'h': 120.0},
    ('0607_2025ON_31_q12', '12(a)(i)'): {'venn': {'sets': 'FG', 'nums': {'F': 35, 'FG': 9, 'G': 34, '': 2}}, 'w': 190.0, 'h': 105.0},
    ('0607_2026MJ_13_q11', '11(a)'): {'venn': {'sets': 'AB', 'nums': {'A': '2\n11', 'AB': '5\n9\n12', 'B': '3\n7',
                                                                      '': '1\n4\n6\n8\n10'}, 'out': 'left'}, 'w': 210.0, 'h': 115.0},
    ('0607_2026MJ_41_q11', '11(b)'): {'venn': {'sets': 'PQR', 'shade': '(Q or R) and not P'}, 'w': 190.0, 'h': 135.0},
})


def _sq(x, y, fill=None, sw=0.8, n=1):
    d = {'p': [(x, y), (x + n, y), (x + n, y + n), (x, y + n)], 'sw': sw}
    if fill:
        d['fill'] = fill
    return d


def _seg(a, b, sw=0.8, dash=None):
    d = {'p': [a, b], 'open': True, 'sw': sw}
    if dash:
        d['dash'] = dash
    return d


def _path_tiles(W, H):
    """The tiles of a path around a W x H rectangle (one tile wide) plus the grey rectangle (2021 MJ 53 / 63 q1-2)."""
    t = [_sq(x, y) for x in range(W + 2) for y in range(H + 2) if x in (0, W + 1) or y in (0, H + 1)]
    return [{'p': [(1, 1), (W + 1, 1), (W + 1, H + 1), (1, H + 1)], 'fill': '#bfbfbf', 'sw': 0.8}] + t


def _cells(cells, added, fill='#000000', dash_inner=True):
    """A shape of unit squares on squared paper: its outline, the printed dashed lines between its squares, the added square."""
    cs = set(cells) | {added}
    P = []
    for (x, y) in cs:                                    # outline: every square edge with no square on the other side
        for (dx, dy, a, b) in ((0, -1, (x, y), (x + 1, y)), (0, 1, (x, y + 1), (x + 1, y + 1)),
                               (-1, 0, (x, y), (x, y + 1)), (1, 0, (x + 1, y), (x + 1, y + 1))):
            if (x + dx, y + dy) not in cs:
                P.append(_seg(a, b, 1.2))
            elif dash_inner and (x + dx, y + dy) > (x, y):
                P.append(_seg(a, b, 0.6, '2 2'))
    return [_sq(added[0], added[1], fill, 0.0)] + P


L_SHAPE = [(1, 2), (2, 2), (1, 1), (1, 0)]                 # 2022 MJ 33 q3 (the printed L of four squares)
SQ_GRID = lambda n: {'style': 'squares', 'n': n, 'under': False}   # (a black added square stays solid over the grid)
RH60 = dict(O=(0, 0), P=(5, 2), Q=(7, 7), R=(2, 5))       # 2023 MJ 53 q3
SPECS.update({
    # shapes on grids (RD2)
    ('0607_2021MJ_52_q03', '3(c)'): {'w': 170.0, 'h': 170.0, 'plane': {
        'style': 'squares', 'n': (-5.5, 5.5, -5.5, 5.5), 'axes': {'xt': [-4, -3, -2, -1, 1, 2, 3, 4], 'yt': [-4, -3, -2, -1, 1, 2, 3, 4]},   # (±5 under the crosses)
        'crosses': [(5, 0), (-5, 0), (0, 5), (0, -5), (3, 4), (4, 3), (-3, 4), (-4, 3), (3, -4), (4, -3), (-3, -4), (-4, -3)]}},
    ('0607_2021MJ_53_q02', '2(a)'): {'w': 140.0, 'h': 150.0, 'stack': True, 'seps': [''],
                                     'panels': [{'style': 'none', 'n': (0, 5, 0, 3), 'polys': _path_tiles(3, 1)},
                                                {'style': 'none', 'n': (0, 6, 0, 3), 'polys': _path_tiles(4, 1)}]},
    ('0607_2021MJ_63_q01', '1(a)'): {'w': 100.0, 'h': 95.0, 'plane': {'style': 'none', 'n': (0, 5, 0, 5), 'polys': _path_tiles(3, 3)}},
    ('0607_2022MJ_33_q03', '3(b)'): {'w': 90.0, 'h': 90.0, 'plane': dict(SQ_GRID((-1, 4, -1, 4)), polys=_cells(L_SHAPE, (0, 0)))},
    ('0607_2022MJ_33_q03', '3(c)(i)'): {'w': 100.0, 'h': 250.0, 'stack': True, 'seps': ['OR', 'OR'], 'panels': [
        dict(SQ_GRID((-1, 4, -1, 4)), polys=_cells(L_SHAPE, (2, 0))), dict(SQ_GRID((-1, 4, -1, 4)), polys=_cells(L_SHAPE, (3, 2))),
        dict(SQ_GRID((-1, 4, -1, 4)), polys=_cells(L_SHAPE, (0, 2)))]},
    ('0607_2022MJ_33_q03', '3(c)(ii)'): {'w': 100.0, 'h': 250.0, 'stack': True, 'seps': ['OR', 'OR'], 'panels': [
        dict(SQ_GRID((-1, 4, -1, 4)), polys=_cells(L_SHAPE, (2, 0)) + [_seg((0, 1.5), (3.5, 1.5), 1.0, '4 2')]),
        dict(SQ_GRID((-1, 4, -1, 4)), polys=_cells(L_SHAPE, (3, 2)) + [_seg((0.5, 3.5), (4, 0), 1.0, '4 2')]),
        dict(SQ_GRID((-1, 4, -1, 4)), polys=_cells(L_SHAPE, (0, 2)) + [_seg((1.5, -0.5), (1.5, 3.5), 1.0, '4 2')])]},
    #   (the added square black, as in 3(b) and 3(c)(i) - Dhruv round 39)
    ('0607_2022ON_63_q01', '1(a)'): {'w': 100.0, 'h': 100.0, 'plane': {
        'style': 'none', 'n': (0, 5, 0, 5), 'polys': [_sq(x, 4, '#bfbfbf') for x in range(4)] + [_sq(4, y, '#bfbfbf') for y in range(5)]}},
    ('0607_2023MJ_53_q01', '1'): {'w': 190.0, 'h': 70.0, 'plane': {
        'style': 'squares', 'n': (-0.5, 8.5, -0.5, 3.5),
        'polys': [_sq(0, 2, None, 0.9), _sq(2, 1, None, 0.9, 2), _sq(5, 0, None, 0.9, 3)],
        'pts': [(0, 2), (1, 2), (0, 3), (1, 3), (2, 1), (4, 1), (2, 3), (4, 3), (5, 0), (8, 0), (5, 3), (8, 3)], 'big': 1.4,
        'text': [(3, 2, '4', {'b': 1}), (6.5, 1.5, '9', {'b': 1})]}},
    ('0607_2023MJ_53_q02', '2(b)'): {'w': 200.0, 'h': 60.0, 'plane': {
        'style': 'squares', 'n': (-0.5, 8.5, -0.5, 2.5),
        'polys': [{'p': [(0, 0), (4, 0), (4, 1)], 'sw': 0.9}, {'p': [(5, 0), (8, 0), (8, 2)], 'sw': 0.9}],
        'pts': [(0, 0), (4, 0), (4, 1), (5, 0), (8, 0), (8, 2)], 'big': 1.4,
        'text': [(3.3, 0.4, '2', {'b': 1}), (7.2, 0.7, '3', {'b': 1})]}},
    ('0607_2023MJ_63_q01', '1'): {'w': 90.0, 'h': 55.0, 'plane': {
        'style': 'squares', 'n': (-0.5, 2.5, -0.5, 1.5), 'polys': [{'p': [(0, 0), (2, 0), (2, 1), (0, 1)], 'sw': 0.9}],
        'pts': [(0, 0), (2, 0), (2, 1), (0, 1)], 'big': 1.4, 'text': [(1.4, 0.5, '2')]}},
    ('0607_2023MJ_63_q02', '2'): {'w': 200.0, 'h': 120.0, 'plane': {
        'style': 'squares', 'n': (-0.5, 9.7, -0.5, 5.5),
        'polys': [{'p': [(0, 2), (6, 2), (6, 3)], 'sw': 0.9}, {'p': [(7.2, 0), (9.2, 0), (9.2, 5)], 'sw': 0.9}],
        'pts': [(0, 2), (6, 2), (6, 3), (7.2, 0), (9.2, 0), (9.2, 5)], 'big': 1.4,
        'text': [(5.4, 2.4, '3'), (8.6, 2.0, '5')]}},
})


def _rhombus(O, P, Q, R, box, lines, nums, axes, n, fill='#bfbfbf', lab=True, qlab='Q', offs=None, u=20.0):
    """A parallelogram on a grid with its surrounding box, the lines that cut the box into triangles and rectangles and the
    printed areas (2023 MJ 53 q3-5, 63 q3-5)."""
    x0, y0, x1, y1 = box if box else (0, 0, 0, 0)
    polys = [{'p': [O, P, Q, R], 'fill': fill, 'sw': 1.0}]
    if box:
        polys.append({'p': [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 'sw': 0.9})
    polys += [_seg(a, b, 0.8) for a, b in lines]
    text = [(x, y, t) for x, y, t in nums]
    if lab:
        o_ = dict({'O': (0.35, -0.35), 'P': (-0.3, 0.35), 'Q': (0.35, 0.3), 'R': (0.3, -0.35)}, **(offs or {}))
        for nm, pt in (('O', O), ('P', P), ('Q', Q), ('R', R)):
            text.append((pt[0] + o_[nm][0], pt[1] + o_[nm][1], qlab if nm == 'Q' else nm, {'s': 8}))
    return {'style': 'squares', 'n': n, 'axes': axes, 'polys': polys, 'pts': [O, P, Q, R], 'big': 1.3, 'text': text, 'u': u}


SPECS.update({
    ('0607_2023MJ_53_q03', '3(b)(ii)'): {'w': 200.0, 'h': 190.0, 'plane': _rhombus(
        (0, 0), (5, 2), (7, 7), (2, 5), (0, 0, 7, 7), [((2, 5), (2, 7)), ((2, 5), (0, 5)), ((5, 2), (5, 0)), ((5, 2), (7, 2))],
        [(1, 6, '4'), (4.2, 6.4, '5'), (0.7, 3.4, '5'), (6.3, 3.8, '5'), (3.2, 0.6, '5'), (6, 1, '4')],
        {'xt': list(range(0, 8)), 'yt': list(range(1, 8))}, (0, 7.4, 0, 7.4))},
    ('0607_2023MJ_53_q04', '4'): {'w': 170.0, 'h': 150.0, 'plane': _rhombus(
        (0, 0), (3, 2), (5, 5), (2, 3), (0, 0, 5, 5), [((2, 3), (2, 5)), ((2, 3), (0, 3)), ((3, 2), (3, 0)), ((3, 2), (5, 2))],
        [(1, 4, '4'), (2.7, 4.4, '3'), (0.6, 2.1, '3'), (4.4, 2.9, '3'), (2.3, 0.6, '3'), (4, 1, '4')],
        {'xt': list(range(0, 6)), 'yt': list(range(1, 6))}, (0, 5.4, 0, 5.4), offs={'R': (-0.3, 0.35), 'P': (0.3, -0.35)})},
    ('0607_2023MJ_53_q05', '5(a)'): {'w': 130.0, 'h': 130.0, 'plane': _rhombus(
        (0, 0), (4, 1), (5, 5), (1, 4), None, [], [], {'xt': list(range(0, 7)), 'yt': list(range(1, 7))}, (0, 6.4, 0, 6.4),
        fill=None, qlab='[Q]')},
    ('0607_2023MJ_53_q05', '5(b)'): {'w': 150.0, 'h': 150.0, 'plane': _rhombus(
        (0, 0), (4, 1), (5, 5), (1, 4), (0, 0, 5, 5), [((1, 4), (1, 5)), ((1, 4), (0, 4)), ((4, 1), (4, 0)), ((4, 1), (5, 1))],
        [(0.5, 4.5, '1'), (2.6, 4.7, '2'), (0.25, 2.6, '2'), (4.7, 2.6, '2'), (2.4, 0.3, '2'), (4.5, 0.5, '1')],
        {'xt': list(range(0, 7)), 'yt': list(range(1, 7))}, (0, 6.4, 0, 6.4), fill=None)},
    ('0607_2023MJ_63_q03', '3(b)(i)'): {'w': 180.0, 'h': 150.0, 'plane': _rhombus(
        (0, 0), (6, 1), (8, 6), (2, 5), (0, 0, 8, 6), [((2, 5), (2, 6)), ((2, 5), (0, 5)), ((6, 1), (6, 0)), ((6, 1), (8, 1))],
        [(1, 5.5, '2'), (4.5, 5.65, '3'), (0.8, 3.2, '5'), (7.2, 2.8, '5'), (3.5, 0.35, '3'), (7, 0.5, '2')],
        {'xt': list(range(0, 9)), 'yt': list(range(1, 7))}, (0, 8.4, 0, 6.4))},
    ('0607_2023MJ_63_q04', '4'): {'w': 220.0, 'h': 150.0, 'plane': _rhombus(
        (0, 0), (3, 4), (-1, 3), (-4, -1), (-4, -1, 3, 4), [((-1, 3), (-1, 4)), ((-1, 3), (-4, 3)), ((0, 0), (0, -1)), ((0, 0), (3, 0))],
        [(-2.5, 3.5, '3'), (0.9, 3.6, '2'), (-3.2, 1.4, '6'), (2.2, 1.7, '6'), (-1.5, -0.72, '2'), (1.5, -0.72, '3')],
        {'xt': [-4, -3, -2, -1, 1, 2, 3], 'yt': [-1, 1, 2, 3, 4]}, (-4.4, 3.4, -1.4, 4.4),
        offs={'Q': (-0.4, 0.35), 'R': (-0.1, -0.4), 'P': (0.3, 0.3), 'O': (0.35, -0.35)})},
    ('0607_2023MJ_63_q05', '5(a)'): {'w': 210.0, 'h': 120.0, 'plane': _rhombus(
        (0, 0), (5, 2), (3, 4), (-2, 2), None, [], [], {'xt': [-2, -1, 0, 1, 2, 3, 4, 5], 'yt': [1, 2, 3, 4]}, (-2.4, 5.4, 0, 4.4),
        qlab='[Q]', offs={'R': (-0.3, -0.4), 'P': (0.2, 0.4)})},
    ('0607_2023MJ_63_q05', '5(b)'): {'w': 210.0, 'h': 120.0, 'plane': _rhombus(
        (0, 0), (5, 2), (3, 4), (-2, 2), (-2, 0, 5, 4), [], [(-1.1, 3.3, '5'), (4.4, 3.4, '2'), (-1.4, 0.7, '2'), (3.2, 0.6, '5')],
        {'xt': [-2, -1, 0, 1, 2, 3, 4, 5], 'yt': [1, 2, 3, 4]}, (-2.4, 5.4, 0, 4.4), offs={'R': (0.25, 0.4), 'P': (0.25, -0.4)})},
})


def _hexv(c, fill='#d9d9d9'):
    """A regular hexagon (side 1) pointing up on the turned triangle lattice, centre c = (column, row)."""
    a, b = c
    return {'p': [(a, b + 1), (a + 1, b + 0.5), (a + 1, b - 0.5), (a, b - 1), (a - 1, b - 0.5), (a - 1, b + 0.5)], 'fill': fill, 'sw': 0.9}


_DIA = lambda k: {'p': [(k, 0), (0, k), (-k, 0), (0, -k)], 'sw': 0.8}
_CS4 = [(x, y) for x in range(-3, 4) for y in range(-3, 4) if abs(x) + abs(y) <= 3]     # centred square pattern 4 (25 dots)
SPECS.update({
    # dot patterns / dotty paper (RD2)
    ('0607_2019ON_62_q06', '6(b)(i)'): {'w': 200.0, 'h': 75.0, 'plane': {
        'style': 'none', 'n': (-0.5, 8.5, 0, 3),
        'polys': [_seg((-0.5, 3), (8.5, 3), 1.2), _seg((-0.5, 0), (8.5, 0), 1.2)] + [_seg((a, 3), (b, 0), 0.7) for a in (0, 4, 8) for b in (0, 4, 8)],
        'pts': [(0, 3), (4, 3), (8, 3), (0, 0), (4, 0), (8, 0)], 'big': 1.6}},
    ('0607_2022FM_52_q03', '3(a)(i)'): {'w': 130.0, 'h': 130.0, 'plane': {
        'style': 'none', 'n': (-3.3, 3.3, -3.3, 3.3), 'polys': [_DIA(1), _DIA(2), _DIA(3)], 'pts': _CS4, 'big': 2.2}},
    ('0607_2022FM_62_q01', '1(a)(i)'): {'w': 130.0, 'h': 130.0, 'plane': {
        'style': 'squares', 'n': (-4, 4, -4, 4),
        'polys': [_DIA(1), _DIA(2), _DIA(3)],     # centred squares: squares of increasing size round the centre dot
        'pts': _CS4, 'big': 2.2}},
    ('0607_2022ON_51_q01', '1(a)'): {'w': 200.0, 'h': 90.0, 'plane': {
        'style': 'iso', 'n': (-1, 5, -1, 2), 'u': 30.0, 'dot': 1.2, 'polys': [{'p': [(0, 0), (4, 0), (3.5, 1), (0.5, 1)], 'sw': 1.5}]}},
    ('0607_2022ON_51_q02', '2(a)'): {'w': 270.0, 'h': 110.0, 'plane': {
        'style': 'iso', 'n': (-1, 8, -1, 3), 'u': 30.0, 'dot': 1.2, 'polys': [{'p': [(0, 0), (7, 0), (6, 2), (1, 2)], 'sw': 1.5}]}},
    ('0607_2024MJ_32_q04', '4(a)(i)'): {'w': 110.0, 'h': 110.0, 'plane': {
        'style': 'squares', 'n': (0, 5, 0, 5), 'pts': [(i + 0.5, 4.5 - j) for j in range(5) for i in range(5 - j)], 'big': 3.0}},
    ('0607_2025FM_52_q02', '2(a)'): {'w': 120.0, 'h': 100.0, 'plane': {
        'style': 'isov', 'n': (-3, 3, -2, 2),
        'polys': [{'p': [(0, 0), (-1, -0.5), (0, -1)], 'fill': '#bfbfbf', 'sw': 0.9}] +
                 [{'p': [(0, 0), a, b], 'fill': '#e6e6e6', 'sw': 0.9} for a, b in (((0, -1), (1, -0.5)), ((1, -0.5), (1, 0.5)),
                                                                                    ((1, 0.5), (0, 1)), ((0, 1), (-1, 0.5)),
                                                                                    ((-1, 0.5), (-1, -0.5)))]}},
    ('0607_2025FM_52_q02', '2(b)'): {'w': 140.0, 'h': 120.0, 'plane': {
        'style': 'isov', 'n': (-3, 3, -3, 3), 'polys': [_hexv((-1, -0.5), '#bfbfbf'), _hexv((0, 1), '#e6e6e6'), _hexv((1, -0.5), '#e6e6e6')]}},
    ('0607_2025FM_52_q02', '2(c)'): {'w': 260.0, 'h': 110.0, 'seps': ['or'], 'panels': [
        {'style': 'isov', 'n': (-3, 3, -2.5, 2.5),
         'polys': [_hexv((-1, -0.5)), _hexv((1, -0.5)), {'p': [(0, 0), (-1, 0.5), (0, 1)], 'fill': '#d9d9d9', 'sw': 0.9},
                   {'p': [(0, 0), (0, 1), (1, 0.5)], 'fill': '#d9d9d9', 'sw': 0.9}]},
        {'style': 'isov', 'n': (-3, 3, -2.5, 2.5),
         'polys': [_hexv((1, 0.5)), _hexv((-1, -0.5)), {'p': [(0, 0), (0, 1), (-1, 0.5)], 'fill': '#d9d9d9', 'sw': 0.9},
                   {'p': [(0, 0), (1, -0.5), (0, -1)], 'fill': '#d9d9d9', 'sw': 0.9}]}]},
})
KEPT.update({
    ('0607_2025FM_62_q10', '10(a)'): 'a sketch of the candidate\'s own diagram whose labels do not match a clear figure (the r sits off the '
                                     'triangle) - kept as printed, Dhruv to decide (RD2)',
})

# ---- Round 39 (Dhruv 2026-11-24): the redrawn graph keeps the PRINTED screenshot's shape ('ar' = its width / height), its
# grid (none where it has none; light lines every 'grid' step, darker every 'gmaj' lines, 'gdots' dotted paper) and its tick
# numbers where they are readable. Read off every screenshot (pipeline: rd2 grid detector + by eye); the ones where the
# grid could not be read for sure are in RD2_GRID_UNSURE (listed for Dhruv).
RD2_LOOK = {
    ('0607_2014MJ_21_q07', '7(a)'): {'grid': None, 'ar': 1.151},
    ('0607_2014MJ_32_q10', '10(d)'): {'grid': (1, 5), 'ar': 4.201},
    ('0607_2014MJ_41_q06', '6(a)'): {'ar': 1.19},
    ('0607_2014MJ_41_q14', '14(a)(i)'): {'grid': None, 'ar': 1.583},
    ('0607_2014MJ_61_q08', '8(a)(i)'): {'grid': (15, 0.2), 'ar': 4.111},
    ('0607_2019ON_31_q10', '10(a)'): {'grid': (1, 5), 'ar': 1.942},
    ('0607_2019ON_41_q03', '3(c)'): {'grid': None, 'ar': 1.893},
    ('0607_2019ON_42_q02', '2(f)(i)'): {'grid': None, 'ar': 1.248},
    ('0607_2019ON_42_q12', '12(a)'): {'grid': None, 'ar': 1.246},
    ('0607_2019ON_62_q07', '7(b)'): {'grid': (0.5, 2000), 'ar': 1.568},
    ('0607_2019ON_62_q08', '7'): {'grid': (0.5, 10), 'gmaj': (2, 2), 'ar': 1.436},
    ('0607_2019ON_62_q09', '9(a)'): {'grid': (0.5, 10), 'gmaj': (2, 2), 'xt': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'yt': [20, 40, 60, 80, 100], 'ar': 1.9},
    ('0607_2019ON_62_q10', '10(b)'): {'grid': (0.5, 10), 'gmaj': (2, 2), 'xt': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'yt': [20, 40, 60, 80, 100], 'ar': 2.444},
    ('0607_2019ON_63_q09', '9(a)'): {'ar': 1.777},
    ('0607_2020MJ_63_q06', '6(a)(i)'): {'grid': (1, 1), 'ar': 0.742},
    ('0607_2020ON_41_q03', '3(b)'): {'grid': None, 'ar': 2.174},
    ('0607_2021FM_12_q24', '24'): {'grid': None, 'ar': 1.065},
    ('0607_2021FM_32_q12', '12(a)'): {'grid': None, 'ar': 1.475},
    ('0607_2021FM_32_q12', '12(c)'): {'grid': None, 'ar': 1.459},
    ('0607_2021FM_42_q03', '3(e)(i)'): {'grid': (1, 1), 'ar': 1.022},
    ('0607_2021FM_42_q07', '7(a)'): {'grid': (1, 1), 'ar': 1.009},
    ('0607_2021FM_62_q08', '8(b)'): {'grid': (1, 2), 'ar': 1.916},
    ('0607_2021FM_62_q09', '9(c)(ii)'): {'grid': (1, 2), 'ar': 2.123},
    ('0607_2021FM_62_q09', '9(d)(ii)'): {'grid': (1, 2), 'ar': 2.117},
    ('0607_2021MJ_41_q06', '6(c)'): {'grid': None, 'ar': 1.741},
    ('0607_2022MJ_41_q09', '9(b)(i)'): {'grid': (1, 1), 'gmaj': (5, 5), 'xt': [-5, 5], 'yt': [-5, 5], 'ar': 1.05},
    ('0607_2022MJ_62_q08', '8(b)'): {'grid': (5, 10), 'yt': [80, 100, 120, 140, 160, 180, 200, 220], 'ar': 0.863},
    ('0607_2022MJ_63_q10', '10(f)'): {'grid': (20, 2), 'gmaj': (5, 5), 'xt': [100, 200, 300, 400, 500, 600, 700, 800, 900], 'yt': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 'ar': 1.972},
    ('0607_2022ON_32_q07', '7(c)'): {'grid': (2, 1), 'gmaj': (10, 10), 'ar': 0.969},
    ('0607_2022ON_62_q06', '2'): {'grid': (0.5, 1000000.0), 'gmaj': (2, 5), 'ar': 1.504},
    ('0607_2023ON_61_q10', '10'): {'ar': 1.473},
    ('0607_2024FM_32_q10', '10(a)'): {'grid': None, 'ar': 1.097},
    ('0607_2024FM_32_q10', '10(c)'): {'grid': None, 'ar': 0.987},
    ('0607_2024FM_42_q01', '1(a)'): {'grid': None, 'ar': 2.099},
    ('0607_2024FM_42_q01', '1(c)(i)'): {'grid': None, 'ar': 2.246},
    ('0607_2024FM_62_q08', '48'): {'grid': (2, 10), 'ar': 1.214},
    ('0607_2024FM_62_q09', '9(c)'): {'grid': (2, 10), 'ar': 1.357},
    ('0607_2024MJ_13_q18', '18'): {'grid': (1, 1), 'ar': 1.003},
    ('0607_2024MJ_31_q07', '7(d)(i)'): {'grid': (1, 1), 'gdots': True, 'ar': 1.131},
    ('0607_2024MJ_31_q07', '7(d)(ii)'): {'grid': (1, 1), 'gdots': True, 'ar': 1.123},
    ('0607_2024MJ_31_q11', '11(b)'): {'grid': None, 'ar': 0.783},
    ('0607_2024MJ_32_q11', '11(a)'): {'grid': None, 'ar': 0.965},
    ('0607_2024MJ_32_q11', '11(d)'): {'grid': None, 'ar': 0.922},
    ('0607_2024MJ_33_q12', '12(a)(i)'): {'grid': None, 'ar': 0.657},
    ('0607_2024MJ_33_q12', '12(b)'): {'grid': None, 'ar': 0.736},
    ('0607_2024MJ_41_q06', '6(a)'): {'grid': (0.5, 0.5), 'gmaj': (2, 2), 'xt': [-2, 2], 'yt': [-2, 2], 'ar': 1.33},
    ('0607_2024MJ_43_q05', '5(a)'): {'grid': None, 'ar': 1.249},
    ('0607_2024MJ_62_q10', '10(b)(ii)'): {'grid': (100, 25), 'gmaj': (2, 2), 'xt': [200, 400, 600, 800, 1000, 1200, 1400, 1600], 'yt': [50, 100, 150, 200], 'ar': 1.752},
    ('0607_2024MJ_63_q07', '0'): {'grid': None, 'ar': 1.584},
    ('0607_2024MJ_63_q10', '0'): {'grid': None, 'ar': 2.145},
    ('0607_2024ON_31_q11', '11(a)(i)'): {'grid': None, 'ar': 0.688},
    ('0607_2024ON_31_q11', '11(b)'): {'grid': None, 'ar': 0.778},
    ('0607_2024ON_32_q12', '12(a)(i)'): {'grid': None, 'ar': 1.073},
    ('0607_2024ON_32_q12', '12(b)'): {'grid': None, 'ar': 1.045},
    ('0607_2024ON_41_q09', '9(a)'): {'grid': (0.5, 0.5), 'gmaj': (2, 2), 'xt': [-2, 2], 'yt': [-4, -2, 2], 'ar': 1.349},
    ('0607_2024ON_43_q04', '4(a)'): {'ar': 1.0},
    ('0607_2024ON_43_q04', '4(c)'): {'ar': 1.0},
    ('0607_2024ON_61_q02', '3'): {'grid': None, 'ar': 0.931},
    ('0607_2024ON_61_q03', '3'): {'grid': None, 'ar': 0.978},
    ('0607_2024ON_61_q05', '10'): {'ar': 1.937},
    ('0607_2024ON_61_q06', '6(a)'): {'grid': None, 'ar': 1.006},
    ('0607_2024ON_62_q09', '9(a)'): {'grid': (1, 500), 'xt': [5, 10], 'yt': [1000, 2000, 3000], 'ar': 2.216},
    ('0607_2025FM_32_q16', '16(a)'): {'grid': None, 'ar': 0.93},
    ('0607_2025FM_32_q16', '16(b)(i)'): {'grid': None, 'ar': 0.853},
    ('0607_2025FM_42_q08', '8(a)'): {'grid': (0.5, 0.5), 'gmaj': (2, 2), 'xt': [-2, 2], 'yt': [-2, 2], 'ar': 1.012},
    ('0607_2025FM_42_q08', '8(b)'): {'grid': (0.5, 0.5), 'gmaj': (2, 2), 'xt': [-2, 2], 'yt': [-2, 2], 'ar': 1.014},
    ('0607_2025FM_42_q09', '9(a)'): {'grid': (1, 1), 'gmaj': (5, 5), 'xt': [5, 10], 'yt': [5, 10], 'ar': 1.0},
    ('0607_2025MJ_23_q14', '14(b)'): {'grid': None, 'ar': 2.101},
    ('0607_2025MJ_31_q18', '18(a)'): {'grid': None, 'ar': 1.041},
    ('0607_2025MJ_31_q18', '18(c)'): {'grid': None, 'ar': 1.054},
    ('0607_2025MJ_32_q17', '17(a)'): {'grid': None, 'ar': 1.041},
    ('0607_2025MJ_32_q17', '17(c)'): {'grid': None, 'ar': 1.039},
    ('0607_2025MJ_33_q17', '17(a)(i)'): {'grid': None, 'ar': 1.031},
    ('0607_2025MJ_33_q17', '17(b)'): {'grid': None, 'ar': 1.081},
    ('0607_2025MJ_41_q11', '11(a)'): {'grid': None, 'ar': 1.245},
    ('0607_2025MJ_42_q13', '13'): {'grid': (0.5, 2), 'gmaj': (4, 5), 'xt': [-4, -2, 2, 4], 'yt': [-10, 10], 'ar': 1.865},
    ('0607_2025MJ_62_q07', '7(c)(ii)'): {'grid': (1, 1), 'xt': [1, 2], 'yt': [1, 2, 3, 4, 5, 6, 7], 'ar': 1.843},
    ('0607_2025MJ_63_q08', '8(a)'): {'grid': (1, 5), 'xt': [5, 10, 15, 20, 25, 30], 'yt': [25, 50, 75, 100, 125], 'ar': 1.91},
    ('0607_2025MJ_63_q08', '8(b)'): {'grid': (1, 5), 'xt': [5, 10, 15, 20, 25, 30], 'yt': [25, 50, 75, 100, 125], 'ar': 1.887},
    ('0607_2025ON_31_q19', '19(a)'): {'grid': None, 'ar': 0.771},
    ('0607_2025ON_33_q18', '18(a)'): {'grid': None, 'ar': 0.606},
    ('0607_2025ON_41_q08', '8(a)'): {'grid': None, 'ar': 1.251},
    ('0607_2025ON_42_q08', '8(a)(i)'): {'grid': (0.5, 0.5), 'gmaj': (2, 2), 'xt': [-2, 2], 'yt': [-4, -2, 2, 4], 'ar': 1.694},
    ('0607_2025ON_42_q08', '8(b)'): {'grid': (0.5, 0.5), 'gmaj': (2, 2), 'xt': [-2, 2], 'yt': [-4, -2, 2, 4], 'ar': 2.485},
    ('0607_2025ON_43_q04', '4(f)(ii)'): {'grid': (0.5, 5), 'gmaj': (2, 2), 'xt': [-4, -3, -2, -1, 1, 2], 'yt': [-30, -20, -10, 0, 10, 20, 30, 40, 50], 'ar': 1.522},
    ('0607_2025ON_61_q05', '5(b)(i)'): {'grid': (2, 0.1), 'gmaj': (5, 5), 'xt': [10, 20, 30, 40, 50], 'yt': [0.5, 1], 'ar': 1.545},
    ('0607_2025ON_61_q05', '5(c)(i)'): {'grid': (2, 0.1), 'gmaj': (5, 5), 'xt': [10, 20, 30, 40, 50], 'yt': [0.5, 1], 'ar': 1.559},
    ('0607_2025ON_62_q04', '4(b)'): {'grid': None, 'ar': 1.634},
    ('0607_2025ON_63_q01', '1(a)(i)'): {'grid': (1, 1), 'ar': 1.486},
    ('0607_2025ON_63_q02', '2(a)(i)'): {'grid': (1, 1), 'ar': 1.332},
    ('0607_2025ON_63_q04', '4(d)'): {'grid': None, 'ar': 1.654},
    ('0607_2026FM_32_q17', '17(a)'): {'grid': None, 'ar': 0.808},
    ('0607_2026FM_32_q17', '17(c)'): {'grid': None, 'ar': 0.767},
    ('0607_2026FM_42_q10', '10(a)'): {'grid': None, 'ar': 1.242},
    ('0607_2026FM_62_q06', '6(a)'): {'grid': (5, 100), 'gmaj': (4, 5), 'xt': [20, 40, 60, 80, 100, 120, 140], 'yt': [144000, 144500, 145000, 145500, 146000], 'ar': 1.611},
    ('0607_2026MJ_31_q17', '17(a)'): {'grid': None, 'ar': 1.205},
    ('0607_2026MJ_32_q14', '14(a)(i)'): {'grid': (1, 2.5), 'ar': 1.42},
    ('0607_2026MJ_32_q14', '14(b)'): {'grid': (1, 2.5), 'ar': 1.677},
    ('0607_2026MJ_33_q20', '20(a)'): {'grid': None, 'ar': 0.705},
    ('0607_2026MJ_41_q06', '6(a)'): {'grid': None, 'ar': 1.668},
    ('0607_2026MJ_41_q17', '17'): {'grid': None, 'ar': 1.624},
    ('0607_2026MJ_42_q05', '5(a)'): {'grid': None, 'ar': 1.799},
    ('0607_2026MJ_43_q09', '9(a)(i)'): {'grid': None, 'ar': 1.88},
    ('0607_2026MJ_43_q09', '9(b)'): {'grid': None, 'ar': 1.843},
    ('0607_2026MJ_43_q17', '17(a)'): {'grid': None, 'ar': 2.178},
    ('0607_2026MJ_61_q06', '6(b)'): {'grid': None, 'ar': 1.569},
    ('0607_2026MJ_61_q07', '7(b)(ii)'): {'grid': None, 'ar': 1.566},
    ('0607_2026MJ_63_q09', '9'): {'grid': None, 'ar': 1.359},
}
RD2_GRID_UNSURE = [('0607_2014MJ_41_q06', '6(a)'), ('0607_2019ON_63_q09', '9(a)'), ('0607_2023ON_61_q10', '10'), ('0607_2024ON_43_q04', '4(a)'), ('0607_2024ON_43_q04', '4(c)'), ('0607_2024ON_61_q05', '10'), ('0607_2025MJ_62_q07', '7(c)(ii)'), ('0607_2025ON_63_q01', '1(a)(i)')]
for _k, _o in RD2_LOOK.items():
    if _k in SPECS and 'x' in SPECS[_k]:
        SPECS[_k] = dict(SPECS[_k], **_o)
for _a, _b in ((('0607_2024FM_62_q08', '48'), '8(f)'), (('0607_2024MJ_63_q07', '0'), '7(c)'), (('0607_2024MJ_63_q10', '0'), '10(b)'),
               (('0607_2024ON_61_q02', '3'), '2(d)'), (('0607_2024ON_61_q03', '3'), '3(c)'), (('0607_2024ON_61_q05', '10'), '5(c)'),
               (('0607_2019ON_62_q08', '7'), '8(a)'), (('0607_2022ON_62_q06', '2'), '6(b)')):
    if _a in RD2_LOOK and (_a[0], _b) in SPECS and 'x' in SPECS[(_a[0], _b)]:
        SPECS[(_a[0], _b)] = dict(SPECS[(_a[0], _b)], **RD2_LOOK[_a])   # (the same picture under its real label)
# the pictures with several graphs (alts / graphs): grid and numbers as printed
SPECS[('0607_2021MJ_41_q11', '11(b)')] = {'alts': [dict(a, grid=None, ar=ar_) for a, ar_ in zip(SPECS[('0607_2021MJ_41_q11', '11(b)')]['alts'], (1.53, 1.44))]}
SPECS[('0607_2025MJ_62_q09', '9(c)(i)')] = {'col': 3, 'graphs': [
    dict(NO, f=[(DV, ''), ('82.98', '')], x=(0, 31), y=(0, 125), grid=None, ar=1.6, xt=[30], yt=[100], xlab='V', ylab='D'),
    dict(NO, f=[(DV + ' - 82.98', '')], x=(-42, 48), y=(-150, 147), grid=None, ar=1.6, xt=[-30, 30], yt=[-100, 100], xlab='V', ylab='D')]}
#   (lower graph: window, -30 / 30 and 100 / -100 read off the printed screenshot, Dhruv round 39)
_al = SPECS[('0607_2025ON_62_q02', '2(d)')]['alts']
SPECS[('0607_2025ON_62_q02', '2(d)')] = {'alts': [dict(_al[0], grid=(5, 100), ar=2.26), dict(_al[1], grid=None, ar=1.6)]}
RD2_GRID_UNSURE.append(('0607_2025ON_62_q02', '2(d)'))

for _k in [('0607_2023MJ_53_q01', '1'), ('0607_2023MJ_53_q02', '2(b)'), ('0607_2023MJ_53_q03', '3(b)(ii)'), ('0607_2023MJ_53_q04', '4'),
           ('0607_2023MJ_53_q05', '5(a)'), ('0607_2023MJ_53_q05', '5(b)'), ('0607_2023MJ_63_q01', '1'), ('0607_2023MJ_63_q02', '2'),
           ('0607_2023MJ_63_q03', '3(b)(i)'), ('0607_2023MJ_63_q04', '4'), ('0607_2023MJ_63_q05', '5(a)'), ('0607_2023MJ_63_q05', '5(b)')]:
    SPECS[_k] = dict(SPECS[_k], plane=dict(SPECS[_k]['plane'], minor=5))   # GeoGebra paper: 5 x 5 small squares per unit (round 39)
TREE_GEOM = {    # (Dhruv round 40: EVERY MS tree like the question's tree) measured with pipeline/tree_geom.py on the question paper
    ('0607_2023MJ_32_q11', '11(a)'): (145.9, 221.5, 306.1, 381.6, 34.2, 34.2, 38.5),
    ('0607_2021ON_31_q07', '7(b)(i)'): (156.5, 256.8, 296.2, 396.4, 48.5, 48.5, 12.2),
    ('0607_2022MJ_33_q11', '11(a)'): (145.2, 241.2, 280.3, 376.2, 46.0, 37.9, 7.2),
    ('0607_2023MJ_33_q06', '6(b)(i)'): (156.0, 251.2, 302.3, 397.6, 54.2, 43.7, 1.7),
    ('0607_2019ON_31_q12', '12(a)'): (97.4, 208.4, 260.5, 371.5, 42.0, 42.0, 15.4),
    ('0607_2026FM_12_q19', '19(a)'): (151.5, 264.6, 303.9, 408.2, 57.6, 46.4, 2.5),
    ('0607_2026MJ_11_q14', '14(b)(i)'): (144.0, 256.9, 307.2, 420.1, 55.3, 37.6, 5.1)}
for _k, _g in TREE_GEOM.items():
    SPECS[_k] = dict(SPECS[_k], tree=dict(SPECS[_k]['tree'], geom=_g))   # branch lengths and angles of the question's tree
assert all('geom' in v['tree'] for v in SPECS.values() if isinstance(v, dict) and 'tree' in v), 'tree without geom: run tree_geom.py'
KEPT.pop(('0607_2025FM_62_q10', '10(a)'), None)
SPECS[('0607_2025FM_62_q10', '10(a)')] = {'w': 200.0, 'h': 70.0, 'plane': {      # (Dhruv round 39: redraw it; the box round
    'style': 'none', 'n': (-4, 100, -33, 14), 'u': 1.9,                            #  the root was the screenshot's edge)
    'polys': [_seg((0, 0), (96, 0), 1.4), _seg((0, 0), (43, -31), 1.4), _seg((43, 0), (43, -31), 0.8, '2 1.5'),
              {'p': [(43, -4), (47, -4), (47, 0)], 'open': True, 'sw': 0.6},
              ],
    'text': [(22.5, 6.5, 'r² − w²', {'i': 1, 'root': True}), (66, 6.5, 'r', {'i': 1})]}}
SPECS[('0607_2025FM_62_q10', '10(a)')]['plane']['u'] = 1.8      # (the root sign is placed for this scale)
# (round 39) two tables were never drawn: maths_check reads their row's label as a number in the cell ('2', '3'), the MS
# builder asks for the real label - the same drawing under both
SPECS[('0607_2023ON_52_q01', '1(d)')] = SPECS[('0607_2023ON_52_q01', '2')]
SPECS[('0607_2023ON_52_q03', '3(b)')] = SPECS[('0607_2023ON_52_q03', '3')]
_p = SPECS[('0607_2023MJ_63_q04', '4')]['plane']           # (Dhruv round 40) the area numbers bold, so they stand out
_p['text'] = [t if len(t) > 3 else (t[0], t[1], t[2], {'b': True}) for t in _p['text']]
SPECS[('0607_2025ON_62_q02', '2(d)')] = {'alts': [dict(a_, h=40.0) for a_ in SPECS[('0607_2025ON_62_q02', '2(d)')]['alts']]}
#   (Dhruv round 40: '2(d) layout messed up') the two small sketches at their PRINTED height: drawn 110 pt tall they grew
#   the row and pushed the text under them down (see ERROR_PATTERNS 278)
