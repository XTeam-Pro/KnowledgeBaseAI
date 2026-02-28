#!/usr/bin/env python3
"""Batch 9: Fix 15 IRRELEVANT topics — remove wrong skills, add correct methods."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 1. Введение в описательную статистику
    {
        "topic_uid": "TOP-VVEDENIE-V-OPISATELNUYU--a52049",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-INTRO-DESCSTAT",
            "title": "Введение в описательную статистику",
            "definition": "Описательная статистика — раздел статистики, систематизирующий и наглядно представляющий данные с помощью числовых характеристик и графиков.",
            "methods": [
                {"uid": "MET-IDSTAT-MEAN", "title": "Вычисление среднего арифметического",
                 "description": "x̄ = (x₁+x₂+…+xₙ)/n. Сумму всех значений делим на их количество.",
                 "examples": [{"uid": "EX-IDSTAT-001", "title": "Среднее оценок", "statement": "Оценки: 4, 5, 3, 4, 5. Найдите среднее.", "solution": "x̄ = (4+5+3+4+5)/5 = 21/5 = 4,2."}]},
                {"uid": "MET-IDSTAT-MEDIAN", "title": "Нахождение медианы",
                 "description": "Упорядочьте данные. Медиана — средний элемент (нечётное n) или среднее двух средних (чётное n).",
                 "examples": [{"uid": "EX-IDSTAT-002", "title": "Медиана ряда", "statement": "Ряд: 2, 5, 7, 8, 12. Медиана?", "solution": "n=5 (нечётное), медиана = 3-й элемент = 7."}]},
                {"uid": "MET-IDSTAT-MODE-RANGE", "title": "Мода и размах выборки",
                 "description": "Мода — наиболее частое значение. Размах = max − min. Характеризуют типичность и разброс данных.",
                 "examples": [{"uid": "EX-IDSTAT-003", "title": "Мода и размах", "statement": "Данные: 3, 5, 5, 7, 9. Мода? Размах?", "solution": "Мода = 5 (встречается 2 раза). Размах = 9−3 = 6."}]},
            ],
        }],
    },

    # 2. Вероятность и статистика
    {
        "topic_uid": "TOP-MATH-PROBABILITY-STATISTICS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PROB-STAT-COMBINED",
            "title": "Вероятность и статистика",
            "definition": "Основы теории вероятностей и статистической обработки данных в школьном курсе математики.",
            "methods": [
                {"uid": "MET-PSTAT-CLASSIC", "title": "Классическое определение вероятности",
                 "description": "P(A) = m/n, где m — число благоприятных исходов, n — общее число равновозможных исходов.",
                 "examples": [{"uid": "EX-PSTAT-001", "title": "Бросок кубика", "statement": "Какова вероятность выпадения чётного числа при бросании кубика?", "solution": "Благоприятные: 2,4,6 (m=3). Всего: 1–6 (n=6). P = 3/6 = 1/2."}]},
                {"uid": "MET-PSTAT-ADDITION", "title": "Правила сложения и умножения вероятностей",
                 "description": "P(A∪B) = P(A)+P(B)−P(A∩B). Для независимых: P(A∩B) = P(A)·P(B).",
                 "examples": [{"uid": "EX-PSTAT-002", "title": "Два события", "statement": "P(A)=0.3, P(B)=0.5, события независимы. P(A∪B)?", "solution": "P(A∩B)=0.3·0.5=0.15. P(A∪B)=0.3+0.5−0.15=0.65."}]},
                {"uid": "MET-PSTAT-STAT-PROC", "title": "Статистическая обработка данных",
                 "description": "Алгоритм: 1) упорядочить данные, 2) найти среднее, медиану, моду, 3) определить размах и отклонения, 4) построить диаграмму.",
                 "examples": [{"uid": "EX-PSTAT-003", "title": "Обработка результатов", "statement": "Баллы: 70, 85, 90, 75, 85. Найдите среднее, моду, медиану.", "solution": "Среднее = 405/5 = 81. Упорядочим: 70,75,85,85,90. Медиана = 85. Мода = 85."}]},
            ],
        }],
    },

    # 3. Геометрические фигуры (уже исправлено в batch1, но аудит ругается — проверим)
    {
        "topic_uid": "TOP-GEOMETRICHESKIE-FIGURY-001",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-GEOM-FIGURES-B9",
            "title": "Геометрические фигуры",
            "definition": "Основные плоские и пространственные геометрические фигуры, их свойства и классификация.",
            "methods": [
                {"uid": "MET-GF-CLASSIFY", "title": "Классификация геометрических фигур",
                 "description": "Плоские: точка, прямая, луч, отрезок, угол, треугольник, четырёхугольник, окружность. Пространственные: куб, параллелепипед, цилиндр, конус, сфера.",
                 "examples": [{"uid": "EX-GF-001", "title": "Классификация", "statement": "Назовите все четырёхугольники.", "solution": "Параллелограмм, прямоугольник, ромб, квадрат, трапеция — все являются четырёхугольниками."}]},
                {"uid": "MET-GF-PROPERTIES", "title": "Свойства геометрических фигур",
                 "description": "Треугольник: сумма углов 180°. Параллелограмм: противоположные стороны равны и параллельны. Окружность: все точки равноудалены от центра.",
                 "examples": [{"uid": "EX-GF-002", "title": "Свойства треугольника", "statement": "В треугольнике два угла: 50° и 70°. Найдите третий.", "solution": "180° − 50° − 70° = 60°."}]},
                {"uid": "MET-GF-CONSTRUCT", "title": "Построение геометрических фигур",
                 "description": "Используйте циркуль и линейку. Построение: перпендикуляр, биссектриса, треугольник по трём сторонам, описанная/вписанная окружность.",
                 "examples": [{"uid": "EX-GF-003", "title": "Построение треугольника", "statement": "Постройте треугольник со сторонами 3, 4, 5 см.", "solution": "1) Отложите отрезок AB=5. 2) Циркулем из A — дуга r=3. 3) Из B — дуга r=4. 4) Пересечение дуг — точка C. △ABC построен."}]},
            ],
        }],
    },

    # 4. Геометрия: задачи повышенного уровня
    {
        "topic_uid": "TOP-MATH-ADVANCED-PLANE-GEOM",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ADV-PLANE-GEOM",
            "title": "Геометрия повышенного уровня",
            "definition": "Сложные задачи планиметрии: вписанные углы, касательные, подобие, метод площадей.",
            "methods": [
                {"uid": "MET-APG-INSCRIBED", "title": "Теорема о вписанном угле",
                 "description": "Вписанный угол = ½ дуги. Вписанные углы, опирающиеся на одну дугу, равны. Угол, опирающийся на диаметр = 90°.",
                 "examples": [{"uid": "EX-APG-001", "title": "Вписанный угол", "statement": "Дуга BC = 120°. Найдите вписанный угол BAC.", "solution": "∠BAC = 120°/2 = 60°."}]},
                {"uid": "MET-APG-TANGENT", "title": "Свойства касательной к окружности",
                 "description": "Касательная ⊥ радиусу. Два отрезка касательных из внешней точки равны. AB² = AC·AD (касательная и секущая).",
                 "examples": [{"uid": "EX-APG-002", "title": "Касательная и секущая", "statement": "Касательная AB=8, секущая ACD: AC=4. Найдите AD.", "solution": "AB² = AC·AD → 64 = 4·AD → AD = 16."}]},
                {"uid": "MET-APG-SIMILARITY", "title": "Подобие треугольников в задачах",
                 "description": "Признаки подобия: по двум углам, по двум сторонам и углу, по трём сторонам. k = отношение сходственных сторон, S₁/S₂ = k².",
                 "examples": [{"uid": "EX-APG-003", "title": "Подобие", "statement": "△ABC∼△DEF, AB=6, DE=9, S(ABC)=20. Найдите S(DEF).", "solution": "k = 9/6 = 3/2. S(DEF) = 20·(3/2)² = 20·9/4 = 45."}]},
            ],
        }],
    },

    # 5. Графы
    {
        "topic_uid": "TOP-GRAFY-21142f",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-GRAPHS-MATH",
            "title": "Теория графов",
            "definition": "Граф — множество вершин и рёбер. Основные понятия: степень вершины, путь, цикл, связность.",
            "methods": [
                {"uid": "MET-GRAPH-DEGREE", "title": "Степень вершины и лемма о рукопожатиях",
                 "description": "Степень вершины = количество инцидентных рёбер. Сумма степеней всех вершин = 2·|E| (чётное число).",
                 "examples": [{"uid": "EX-GRAPH-001", "title": "Лемма о рукопожатиях", "statement": "Граф с 5 вершинами, степени: 2,3,3,2,4. Сколько рёбер?", "solution": "Σ степеней = 2+3+3+2+4 = 14. |E| = 14/2 = 7 рёбер."}]},
                {"uid": "MET-GRAPH-EULER", "title": "Эйлеров путь и эйлеров цикл",
                 "description": "Эйлеров цикл существует ⟺ все вершины чётной степени. Эйлеров путь — ровно 2 вершины нечётной степени.",
                 "examples": [{"uid": "EX-GRAPH-002", "title": "Задача о кёнигсбергских мостах", "statement": "Граф: 4 вершины, степени 3,3,3,5. Существует ли эйлеров путь?", "solution": "Нечётных вершин: 4 (все). Для эйлерова пути нужно ровно 2 → путь не существует."}]},
                {"uid": "MET-GRAPH-CONNECT", "title": "Проверка связности графа",
                 "description": "Граф связен, если из любой вершины можно добраться до любой другой. Метод: обход в глубину или ширину.",
                 "examples": [{"uid": "EX-GRAPH-003", "title": "Связность", "statement": "Вершины: A,B,C,D. Рёбра: AB, BC, CD. Связен ли граф?", "solution": "A→B→C→D — все вершины достижимы. Граф связен."}]},
            ],
        }],
    },

    # 6. Диофантовы уравнения и целочисленные задачи
    {
        "topic_uid": "TOP-MATH-NUMBER-THEORY",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-NUMBER-THEORY",
            "title": "Диофантовы уравнения и теория чисел",
            "definition": "Уравнения в целых числах, свойства делимости, остатки, цикличность.",
            "methods": [
                {"uid": "MET-NT-DIOPHANTINE", "title": "Решение диофантовых уравнений",
                 "description": "ax+by=c имеет решение ⟺ НОД(a,b)|c. Частное решение находят алгоритмом Евклида. Общее: x=x₀+bt/d, y=y₀−at/d.",
                 "examples": [{"uid": "EX-NT-001", "title": "Линейное диофантово", "statement": "3x+5y=1. Найдите все целые решения.", "solution": "НОД(3,5)=1|1 ✓. Частное: x=2, y=−1. Общее: x=2+5t, y=−1−3t."}]},
                {"uid": "MET-NT-MODULAR", "title": "Модульная арифметика",
                 "description": "a ≡ b (mod m) означает m|(a−b). Свойства: сумма, произведение и степени сохраняют сравнимость.",
                 "examples": [{"uid": "EX-NT-002", "title": "Остаток от деления", "statement": "Найдите остаток 2¹⁰⁰ при делении на 7.", "solution": "2¹=2, 2²=4, 2³=1(mod 7). Цикл длины 3. 100=3·33+1. 2¹⁰⁰ ≡ 2¹ ≡ 2(mod 7)."}]},
                {"uid": "MET-NT-DIVISIBILITY", "title": "Признаки делимости и свойства",
                 "description": "Делимость на 2,3,4,5,6,8,9,11. Основная теорема арифметики: любое n>1 раскладывается в произведение простых единственным образом.",
                 "examples": [{"uid": "EX-NT-003", "title": "Признак делимости", "statement": "Делится ли 123456 на 9?", "solution": "Сумма цифр: 1+2+3+4+5+6=21. 21 не делится на 9 → 123456 не делится на 9."}]},
            ],
        }],
    },

    # 7. Дроби
    {
        "topic_uid": "TOPIC-FRACTIONS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-FRACTIONS-B9",
            "title": "Дроби",
            "definition": "Обыкновенные и десятичные дроби, действия с ними, преобразования.",
            "methods": [
                {"uid": "MET-FRAC-ADD-SUB", "title": "Сложение и вычитание дробей",
                 "description": "Приведите к общему знаменателю (НОК). a/b ± c/d = (ad±bc)/(bd). Сократите результат.",
                 "examples": [{"uid": "EX-FRAC-001", "title": "Сложение дробей", "statement": "2/3 + 1/4 = ?", "solution": "НОК(3,4)=12. 2/3=8/12, 1/4=3/12. 8/12+3/12=11/12."}]},
                {"uid": "MET-FRAC-MUL-DIV", "title": "Умножение и деление дробей",
                 "description": "a/b · c/d = ac/(bd). a/b ÷ c/d = a/b · d/c. Перед умножением полезно сократить «крест-накрест».",
                 "examples": [{"uid": "EX-FRAC-002", "title": "Деление дробей", "statement": "3/4 ÷ 2/5 = ?", "solution": "3/4 · 5/2 = 15/8 = 1 7/8."}]},
                {"uid": "MET-FRAC-SIMPLIFY", "title": "Сокращение дробей и приведение к НОЗ",
                 "description": "Сокращение: разделите числитель и знаменатель на их НОД. Приведение: умножьте на дополнительный множитель до НОК знаменателей.",
                 "examples": [{"uid": "EX-FRAC-003", "title": "Сокращение", "statement": "Сократите 18/24.", "solution": "НОД(18,24)=6. 18/24 = 3/4."}]},
            ],
        }],
    },

    # 8. Квадратные неравенства
    {
        "topic_uid": "TOP-KVADRATNYE-NERAVENSTVA-f1ebc9",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-QUAD-INEQ-B9",
            "title": "Квадратные неравенства",
            "definition": "Неравенства вида ax²+bx+c>0 (≥,<,≤). Решение через дискриминант и параболу.",
            "methods": [
                {"uid": "MET-QINEQ-PARABOLA", "title": "Графический метод решения квадратного неравенства",
                 "description": "1) Найдите корни ax²+bx+c=0. 2) Нарисуйте схему параболы (вверх при a>0). 3) Определите знак на промежутках.",
                 "examples": [{"uid": "EX-QINEQ-001", "title": "Графический метод", "statement": "x²−5x+6 > 0.", "solution": "Корни: x=2, x=3. Парабола вверх (a=1>0). Положительна при x<2 и x>3. Ответ: (−∞;2)∪(3;+∞)."}]},
                {"uid": "MET-QINEQ-NOROOTS", "title": "Квадратное неравенство без действительных корней",
                 "description": "Если D<0 и a>0: ax²+bx+c > 0 всегда верно, ax²+bx+c < 0 не имеет решений (и наоборот при a<0).",
                 "examples": [{"uid": "EX-QINEQ-002", "title": "D<0", "statement": "x²+x+1 > 0 — верно ли для всех x?", "solution": "D = 1−4 = −3 < 0, a=1>0 → парабола выше оси Ox → неравенство верно для всех x ∈ ℝ."}]},
                {"uid": "MET-QINEQ-INTERVAL", "title": "Метод интервалов для квадратных неравенств",
                 "description": "Разложите на множители: a(x−x₁)(x−x₂). Отметьте корни на числовой прямой. Определите знак на каждом интервале.",
                 "examples": [{"uid": "EX-QINEQ-003", "title": "Метод интервалов", "statement": "−x²+4x−3 ≥ 0.", "solution": "−(x²−4x+3) ≥ 0 → x²−4x+3 ≤ 0. Корни: 1,3. a=1>0. Парабола ≤ 0 при 1 ≤ x ≤ 3."}]},
            ],
        }],
    },

    # 9. Комбинаторика в вероятности
    {
        "topic_uid": "TOP-KOMBINATORIKA-V-VEROYATN-88900f",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-COMB-PROB-B9",
            "title": "Комбинаторика в вероятности",
            "definition": "Применение комбинаторных формул для подсчёта вероятностей сложных событий.",
            "methods": [
                {"uid": "MET-CPRO-PERM", "title": "Перестановки в задачах на вероятность",
                 "description": "Pₙ = n! — число способов расположить n элементов в ряд. P(A) = благоприятные перестановки / все перестановки.",
                 "examples": [{"uid": "EX-CPRO-001", "title": "Перестановки", "statement": "5 книг случайно ставят на полку. Какова вероятность, что математика окажется первой?", "solution": "Всего: 5!=120. Благоприятных: 4!=24 (остальные 4 в любом порядке). P=24/120=1/5."}]},
                {"uid": "MET-CPRO-COMB", "title": "Сочетания в задачах на вероятность",
                 "description": "C(n,k) = n!/(k!(n−k)!). Используется при выборе k объектов из n без учёта порядка.",
                 "examples": [{"uid": "EX-CPRO-002", "title": "Сочетания", "statement": "Из 10 билетов 3 «счастливых». Вытаскивают 2 наугад. P(оба счастливых)?", "solution": "Благоприятных: C(3,2)=3. Всего: C(10,2)=45. P=3/45=1/15."}]},
                {"uid": "MET-CPRO-MULTI", "title": "Правило умножения и дерево исходов",
                 "description": "Если событие состоит из k этапов с n₁,n₂,…,nₖ вариантами, общее число исходов = n₁·n₂·…·nₖ.",
                 "examples": [{"uid": "EX-CPRO-003", "title": "Правило умножения", "statement": "Бросают монету 3 раза. P(ровно 2 орла)?", "solution": "Всего: 2³=8. Благоприятных: C(3,2)=3 (ООР, ОРО, РОО). P=3/8."}]},
            ],
        }],
    },

    # 10. Многочлены
    {
        "topic_uid": "TOP-MNOGOCHLENY-0cd461",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-POLYNOMIALS-B9",
            "title": "Многочлены",
            "definition": "Многочлен — алгебраическое выражение вида aₙxⁿ+…+a₁x+a₀. Действия: сложение, вычитание, умножение, разложение.",
            "methods": [
                {"uid": "MET-POLY-OPS", "title": "Действия с многочленами",
                 "description": "Сложение/вычитание: приведение подобных. Умножение: каждый член на каждый. Раскрытие скобок.",
                 "examples": [{"uid": "EX-POLY-001", "title": "Умножение многочленов", "statement": "(x+2)(x²−x+3).", "solution": "x·x²−x·x+x·3+2·x²−2·x+2·3 = x³−x²+3x+2x²−2x+6 = x³+x²+x+6."}]},
                {"uid": "MET-POLY-FACTOR-GCF", "title": "Разложение вынесением общего множителя",
                 "description": "Найдите НОД коэффициентов и наименьшую степень переменной. Вынесите за скобку.",
                 "examples": [{"uid": "EX-POLY-002", "title": "Вынесение за скобку", "statement": "6x³−9x²+3x.", "solution": "НОД=3x. 3x(2x²−3x+1)."}]},
                {"uid": "MET-POLY-FORMULAS", "title": "Формулы сокращённого умножения",
                 "description": "(a±b)² = a²±2ab+b². a²−b² = (a−b)(a+b). (a±b)³ = a³±3a²b+3ab²±b³.",
                 "examples": [{"uid": "EX-POLY-003", "title": "Разность квадратов", "statement": "Разложите 4x²−9.", "solution": "4x²−9 = (2x)²−3² = (2x−3)(2x+3)."}]},
            ],
        }],
    },

    # 11. НОД и НОК
    {
        "topic_uid": "TOP-NOD-I-NOK-b29ab2",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-GCD-LCM-B9",
            "title": "НОД и НОК",
            "definition": "НОД — наибольший общий делитель. НОК — наименьшее общее кратное. Применяются при работе с дробями и делимостью.",
            "methods": [
                {"uid": "MET-GCL-FACTORIZE", "title": "НОД и НОК через разложение на простые множители",
                 "description": "Разложите числа на простые множители. НОД = произведение общих множителей в наименьших степенях. НОК = произведение всех множителей в наибольших степенях.",
                 "examples": [{"uid": "EX-GCL-001", "title": "Через разложение", "statement": "НОД(24,36) и НОК(24,36).", "solution": "24=2³·3, 36=2²·3². НОД=2²·3=12. НОК=2³·3²=72."}]},
                {"uid": "MET-GCL-EUCLID", "title": "Алгоритм Евклида для НОД",
                 "description": "НОД(a,b): делите a на b с остатком, затем b на остаток, пока остаток ≠ 0. Последний ненулевой остаток — НОД.",
                 "examples": [{"uid": "EX-GCL-002", "title": "Алгоритм Евклида", "statement": "НОД(84,54).", "solution": "84 = 54·1 + 30. 54 = 30·1 + 24. 30 = 24·1 + 6. 24 = 6·4 + 0. НОД = 6."}]},
                {"uid": "MET-GCL-RELATION", "title": "Связь НОД и НОК",
                 "description": "НОД(a,b) · НОК(a,b) = a·b. Зная НОД, можно найти НОК: НОК = a·b/НОД(a,b).",
                 "examples": [{"uid": "EX-GCL-003", "title": "Связь НОД и НОК", "statement": "НОД(12,18)=6. Найдите НОК.", "solution": "НОК = 12·18/6 = 216/6 = 36."}]},
            ],
        }],
    },

    # 12. Неравенства с модулем
    {
        "topic_uid": "TOP-NERAVENSTVA-S-MODULEM-102864",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ABS-INEQ-B9",
            "title": "Неравенства с модулем",
            "definition": "|a| — расстояние от a до 0 на числовой прямой. Неравенства с модулем раскрываются по определению или геометрически.",
            "methods": [
                {"uid": "MET-ABSI-BASIC", "title": "Раскрытие модуля по определению",
                 "description": "|f(x)| < a ⟺ −a < f(x) < a (при a>0). |f(x)| > a ⟺ f(x) < −a или f(x) > a.",
                 "examples": [{"uid": "EX-ABSI-001", "title": "|x−3| < 5", "statement": "Решите |x−3| < 5.", "solution": "−5 < x−3 < 5 → −2 < x < 8. Ответ: (−2; 8)."}]},
                {"uid": "MET-ABSI-CASES", "title": "Метод раскрытия модуля по промежуткам",
                 "description": "Найдите точки, где выражения под модулями обращаются в 0. Разбейте числовую прямую на промежутки. На каждом раскройте модули и решите.",
                 "examples": [{"uid": "EX-ABSI-002", "title": "Два модуля", "statement": "|x−1| + |x+2| > 5.", "solution": "Критические точки: x=1, x=−2. При x≥1: (x−1)+(x+2)>5 → 2x+1>5 → x>2. При −2≤x<1: (1−x)+(x+2)>5 → 3>5 — нет решений. При x<−2: (1−x)+(−x−2)>5 → −2x−1>5 → x<−3. Ответ: (−∞;−3)∪(2;+∞)."}]},
                {"uid": "MET-ABSI-GEOM", "title": "Геометрическая интерпретация модуля",
                 "description": "|x−a| — расстояние от x до a. |x−a|<r ⟺ x∈(a−r, a+r). |x−a|>r ⟺ x∈(−∞, a−r)∪(a+r, +∞).",
                 "examples": [{"uid": "EX-ABSI-003", "title": "Геометрический смысл", "statement": "|x−5| ≤ 2. Интерпретируйте и решите.", "solution": "Расстояние от x до 5 не более 2. x ∈ [5−2; 5+2] = [3; 7]."}]},
            ],
        }],
    },

    # 13. Объёмы
    {
        "topic_uid": "TOP-OBYOMY-d44ad9",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-VOLUMES-B9",
            "title": "Объёмы геометрических тел",
            "definition": "Формулы объёмов: призма, пирамида, цилиндр, конус, шар, тела вращения.",
            "methods": [
                {"uid": "MET-VOL9-PRISM", "title": "Объём призмы и цилиндра",
                 "description": "V(призмы) = S(основания)·h. V(цилиндра) = πr²h. Прямая и наклонная призма: h — расстояние между основаниями.",
                 "examples": [{"uid": "EX-VOL9-001", "title": "Объём цилиндра", "statement": "r=3, h=10. V=?", "solution": "V = π·9·10 = 90π ≈ 282.7."}]},
                {"uid": "MET-VOL9-PYRAMID", "title": "Объём пирамиды и конуса",
                 "description": "V(пирамиды) = ⅓·S(основания)·h. V(конуса) = ⅓πr²h.",
                 "examples": [{"uid": "EX-VOL9-002", "title": "Объём пирамиды", "statement": "Основание — квадрат 6×6, h=10. V=?", "solution": "V = ⅓·36·10 = 120."}]},
                {"uid": "MET-VOL9-SPHERE", "title": "Объём шара и его частей",
                 "description": "V(шара) = ⁴⁄₃πr³. S(сферы) = 4πr². Объём шарового сегмента: V = πh²(3r−h)/3.",
                 "examples": [{"uid": "EX-VOL9-003", "title": "Объём шара", "statement": "r=6. V=?", "solution": "V = ⁴⁄₃·π·216 = 288π ≈ 904.8."}]},
            ],
        }],
    },

    # 14. Операции и свойства
    {
        "topic_uid": "TOP-OPERATSII-I-SVOJSTVA-b8ac93",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-OPS-PROPS-B9",
            "title": "Операции и свойства арифметических действий",
            "definition": "Четыре арифметические операции, их свойства: коммутативность, ассоциативность, дистрибутивность.",
            "methods": [
                {"uid": "MET-OPS-COMMUT", "title": "Коммутативность и ассоциативность",
                 "description": "a+b=b+a, a·b=b·a (коммутативность). (a+b)+c=a+(b+c), (a·b)·c=a·(b·c) (ассоциативность). Позволяют менять порядок действий.",
                 "examples": [{"uid": "EX-OPS-001", "title": "Удобная группировка", "statement": "17+28+83+72.", "solution": "(17+83)+(28+72) = 100+100 = 200."}]},
                {"uid": "MET-OPS-DISTRIB", "title": "Дистрибутивность умножения",
                 "description": "a·(b+c) = a·b + a·c. Используется для раскрытия скобок и упрощения вычислений.",
                 "examples": [{"uid": "EX-OPS-002", "title": "Дистрибутивность", "statement": "25·104.", "solution": "25·(100+4) = 25·100+25·4 = 2500+100 = 2600."}]},
                {"uid": "MET-OPS-INVERSE", "title": "Обратные операции",
                 "description": "Вычитание — обратная операция к сложению. Деление — обратная к умножению. a−b=c ⟺ c+b=a. a÷b=c ⟺ c·b=a.",
                 "examples": [{"uid": "EX-OPS-003", "title": "Проверка обратной операцией", "statement": "72÷8=? Проверьте.", "solution": "72÷8=9. Проверка: 9·8=72 ✓."}]},
            ],
        }],
    },

    # 15. Переменные и выражения
    {
        "topic_uid": "TOP-PEREMENNYE-I-VYRAZHENIYA-3652b0",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-VARS-EXPR-B9",
            "title": "Переменные и выражения",
            "definition": "Буквенные выражения, подстановка значений, упрощение. Основа алгебры.",
            "methods": [
                {"uid": "MET-VE-SUBST", "title": "Подстановка значений в выражение",
                 "description": "Замените каждую переменную данным числом и вычислите. Соблюдайте порядок действий.",
                 "examples": [{"uid": "EX-VE-001", "title": "Подстановка", "statement": "Найдите 3a+2b при a=4, b=5.", "solution": "3·4+2·5 = 12+10 = 22."}]},
                {"uid": "MET-VE-SIMPLIFY", "title": "Упрощение выражений",
                 "description": "Приведите подобные члены: одинаковые буквенные части складываются/вычитаются. 3x+5x=8x. 2a−7a=−5a.",
                 "examples": [{"uid": "EX-VE-002", "title": "Подобные члены", "statement": "4x+3y−2x+y.", "solution": "(4x−2x)+(3y+y) = 2x+4y."}]},
                {"uid": "MET-VE-COMPOSE", "title": "Составление выражений по условию задачи",
                 "description": "Обозначьте неизвестное буквой. Переведите слова в математические операции: «больше на» → +, «в ... раз» → ·.",
                 "examples": [{"uid": "EX-VE-003", "title": "Составление выражения", "statement": "Карандаш стоит x руб., ручка — в 3 раза дороже. Стоимость 2 карандашей и 1 ручки?", "solution": "Ручка: 3x. Стоимость: 2x+3x = 5x руб."}]},
            ],
        }],
    },
]

def _merge_node(session, label, uid, props):
    all_props = {"uid": uid, "type": label, "tenant_id": TENANT_ID, "lifecycle_status": "ACTIVE", "updated_at": NOW_MS, **props}
    session.run(f"MERGE (n:{label} {{uid: $uid, tenant_id: $tid}}) SET n += $props", uid=uid, tid=TENANT_ID, props=all_props)

def _merge_rel(session, from_uid, rel_type, to_uid):
    session.run(f"MATCH (a {{uid: $from_uid, tenant_id: $tid}}), (b {{uid: $to_uid, tenant_id: $tid}}) MERGE (a)-[:{rel_type}]->(b)", from_uid=from_uid, to_uid=to_uid, tid=TENANT_ID)

def _delete_all_skill_rels(session, topic_uid, dry_run):
    existing = session.run("MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[:REQUIRES_SKILL]->(sk:Skill) RETURN sk.uid AS uid, sk.title AS title", uid=topic_uid, tid=TENANT_ID).data()
    if not existing: return 0
    for s in existing: print(f"      🗑️  Удаляю: {topic_uid} → {s['uid']} ({s['title']})")
    if not dry_run:
        session.run("MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[r:REQUIRES_SKILL]->(sk:Skill) DELETE r", uid=topic_uid, tid=TENANT_ID)
    return len(existing)

def seed(dry_run=False):
    repo = Neo4jRepo()
    drv = repo.driver
    stats = {"topics": 0, "skills": 0, "methods": 0, "examples": 0, "rels": 0, "deleted_rels": 0}
    try:
        with drv.session() as session:
            for entry in DATA:
                topic_uid = entry["topic_uid"]
                print(f"\n[Topic] {topic_uid}")
                if entry.get("remove_all_old_skills"):
                    stats["deleted_rels"] += _delete_all_skill_rels(session, topic_uid, dry_run)
                stats["topics"] += 1
                for skill in entry.get("skills", []):
                    skill_uid = skill["uid"]
                    skill_props = {k: v for k, v in skill.items() if k not in ("uid", "methods")}
                    print(f"  [Skill] {skill_uid}: {skill.get('title', '')}")
                    if not dry_run:
                        _merge_node(session, "Skill", skill_uid, skill_props)
                        _merge_rel(session, topic_uid, "REQUIRES_SKILL", skill_uid)
                    stats["skills"] += 1; stats["rels"] += 1
                    for method in skill.get("methods", []):
                        method_uid = method["uid"]
                        method_props = {k: v for k, v in method.items() if k not in ("uid", "examples")}
                        print(f"    [Method] {method_uid}: {method.get('title', '')}")
                        if not dry_run:
                            _merge_node(session, "Method", method_uid, method_props)
                            _merge_rel(session, skill_uid, "HAS_METHOD", method_uid)
                        stats["methods"] += 1; stats["rels"] += 1
                        for ex in method.get("examples", []):
                            ex_props = {k: v for k, v in ex.items() if k != "uid"}
                            if not dry_run:
                                _merge_node(session, "Example", ex["uid"], ex_props)
                                _merge_rel(session, method_uid, "HAS_EXAMPLE", ex["uid"])
                            stats["examples"] += 1; stats["rels"] += 1
    finally:
        repo.close()
    mode = "(DRY RUN)" if dry_run else "(ПРИМЕНЕНО)"
    print(f"\n{'='*60}\nBatch 9 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
