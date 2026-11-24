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
    ('0607_2021MJ_13_q21', '21(a)'): {'venn': {'sets': 'AB', 'nums': {'A': '1  5\n6  9', 'AB': 4, 'B': '2  7\n10', '': '3\n8'}},
                                      'w': 180.0, 'h': 100.0},
})

def _w(t, s, f='serif'):
    """The text's real width: the SVG draws it with textLength, so a guessed width stretched or squeezed the letters
    (Dhruv round 38: 'why does the font look different'). Minus signs measure ~0 in text_width: counted as 0.5 em."""
    from ms_maths import text_width as tw0           # (the font metrics know Latin-1 only: '–3' measured as 1/4 em
    if all(ord(ch) < 256 for ch in t):               #  and was drawn squeezed - other characters 0.55 em each)
        return tw0(t, f, s)
    return round(sum(tw0(ch, f, s) if ord(ch) < 256 else 0.55 * s for ch in t), 2)


def _draw_tree(sp, w, h, size=8.0):
    """A completed two-stage tree diagram drawn as lines and text like the question's own (probabilities on the branches)."""
    tr = sp['tree']
    L, T = [], []
    from ms_maths import text_width as tw0
    tw = lambda t: _w(t, size)
    def txt(lines, x, yc, right=False):                       # a block of lines centred on yc, left edge at x
        lh = size * 1.15
        y0 = yc - (len(lines) - 1) * lh / 2 + size * 0.33
        for k, t in enumerate(lines):
            T.append({'t': t, 'x': round(x - (tw(t) if right else 0), 2), 'y': round(y0 + k * lh, 2), 'w': round(tw(t), 2), 's': size})
    def br(x0, y0, x1, y1, prob, upper):
        L.append({'d': f'M{x0:.2f} {y0:.2f}L{x1:.2f} {y1:.2f}', 'stroke': '#000000', 'sw': 0.8})
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
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
        if upper:
            T.append({'t': prob, 'x': round(mx - tw(prob) - 1, 2), 'y': round(my - 1.5, 2), 'w': round(tw(prob), 2), 's': size})
        else:
            T.append({'t': prob, 'x': round(mx - tw(prob) - 1, 2), 'y': round(my + size + 0.5, 2), 'w': round(tw(prob), 2), 's': size})
    rx, ry = 4.0, h / 2
    e1 = 0.24 * w
    f1 = 0.52 * w
    e2 = 0.66 * w
    for i, (prob, lines) in enumerate(tr['first']):
        yn = h * (0.26 if i == 0 else 0.74)
        br(rx, ry, e1, yn, prob, i == 0)
        txt(lines, e1 + 3, yn)
        for j, (p2, l2) in enumerate(tr['second'][i]):
            ye = yn + (-1 if j == 0 else 1) * 0.15 * h
            br(f1, yn, e2, ye, p2, j == 0)
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
                lx, ly = cx + 0.75 * r, cy + 0.85 * r
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
            if key == '':
                px, py = bx + bw - 12, by + bh - 6 - (str(val).count('\n')) * size * 0.6
            else:
                px = sum(a for a, b in pts) / len(pts); py = sum(b for a, b in pts) / len(pts) + size * 0.35
            ls_ = str(val).split('\n')                     # several lines ('1 5\n6 9'): stacked round the centre
            for j, t in enumerate(ls_):
                yy = py + (j - (len(ls_) - 1) / 2) * size * 1.2
                T.append({'t': t, 'x': round(px - tw(t) / 2, 2), 'y': round(yy, 2), 'w': tw(t), 's': size})
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
    return SPECS.get((qid, label))


def _num(v):
    return ('%g' % v).replace('-', '–')        # the MS prints an en dash for minus


def draw(sp, w, h, size=9.0):
    """-> (lines, texts) in a box w x h (pt), origin top left. lines: {'d', 'stroke', 'sw'}; texts: {'t', 'x', 'y', 'w', 's'}."""
    if 'tree' in sp:
        return _draw_tree(sp, w, h, size)
    if 'venn' in sp:
        return _draw_venns(sp, w, h, size)
    if 'bars' in sp:
        return _draw_bars(sp, w, h, size)
    from ms_maths import text_width as tw0
    # text_width measures some Unicode signs (−, –) as ~0 and the label was squeezed; an estimate never below 0.5 em/char
    text_width = lambda t, f, s: _w(t, s, f)
    L, T = [], []
    pl, pr, pt, pb = 22.0, 16.0, 12.0, 14.0                # room for tick labels, arrows and the y letter
    x0, x1 = sp['x']; y0, y1 = sp['y']
    W, H = max(20.0, w - pl - pr), max(20.0, h - pt - pb)
    X = lambda x: pl + (x - x0) / (x1 - x0) * W
    Y = lambda y: pt + (y1 - y) / (y1 - y0) * H
    gx, gy = sp.get('grid', (None, None))
    if gx:                                                 # light grey grid (the question's window)
        k = math.ceil(x0 / gx)
        while k * gx <= x1 + 1e-9:
            L.append({'d': f'M{X(k * gx):.2f} {Y(y1):.2f}V{Y(y0):.2f}', 'stroke': '#cfcfcf', 'sw': 0.4}); k += 1
        k = math.ceil(y0 / gy)
        while k * gy <= y1 + 1e-9:
            L.append({'d': f'M{X(x0):.2f} {Y(k * gy):.2f}H{X(x1):.2f}', 'stroke': '#cfcfcf', 'sw': 0.4}); k += 1
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
    for v in sp.get('xt', []):
        L.append({'d': f'M{X(v):.2f} {ax_y - 2:.2f}V{ax_y + 2:.2f}', 'stroke': '#000000', 'sw': 0.6})
        t = _num(v); tw = text_width(t, 'serif', size)
        T.append({'t': t, 'x': round(X(v) - tw / 2, 2), 'y': round((Y(y0) + 1 + size) if sp.get('xlow') else (ax_y + 2 + size), 2),
                  'w': tw, 's': size})       # ('xlow': numbers under the window - a curve runs along the axis, 2023 MJ 63 q12)
    for v in sp.get('yt', []):
        L.append({'d': f'M{ax_x - 2:.2f} {Y(v):.2f}H{ax_x + 2:.2f}', 'stroke': '#000000', 'sw': 0.6})
        t = _num(v); tw = text_width(t, 'serif', size)
        T.append({'t': t, 'x': round(ax_x - 3 - tw, 2), 'y': round(Y(v) + size * 0.35, 2), 'w': tw, 's': size})
    xl = sp.get('xlab', 'x')
    T.append({'t': xl, 'x': round(X(x1) + 8, 2), 'y': round(ax_y + size * 0.35, 2), 'w': _w(xl, size), 's': size, 'i': 1})
    yl = sp.get('ylab', 'y')
    T.append({'t': yl, 'x': round(ax_x + 4, 2), 'y': round(Y(y1) - 6 + size * 0.35, 2), 'w': _w(yl, size), 's': size, 'i': 1})
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
    for px, py in sp.get('points', []):        # plotted points as crosses x (2020 ON 62 6(a): the crosses were lost)
        cx, cy, r_ = X(px), Y(py), 2.2
        L.append({'d': f'M{cx - r_:.2f} {cy - r_:.2f}L{cx + r_:.2f} {cy + r_:.2f}M{cx - r_:.2f} {cy + r_:.2f}L{cx + r_:.2f} {cy - r_:.2f}',
                  'stroke': '#000000', 'sw': 0.8})
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
