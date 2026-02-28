#!/usr/bin/env python3
"""Batch 11: Fix 15 FEW_METHODS topics — add methods to reach ≥3."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 1. Алгебра: задачи повышенного уровня (1 method → 3)
    {
        "topic_uid": "TOP-MATH-ADVANCED-ALGEBRA",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ADV-ALGEBRA-B11",
            "title": "Алгебра повышенного уровня",
            "definition": "Задачи с параметрами, делимость, модульные уравнения, нестандартные задачи алгебры.",
            "methods": [
                {"uid": "MET-AA-PARAM", "title": "Уравнения и неравенства с параметром",
                 "description": "Рассмотрите параметр как «фиксированное число». Постройте графики в зависимости от параметра. Найдите критические значения.",
                 "examples": [{"uid": "EX-AA-001", "title": "Параметр", "statement": "При каких a уравнение x²−2ax+a+2=0 имеет два корня?", "solution": "D=4a²−4(a+2)>0 → a²−a−2>0 → (a−2)(a+1)>0. Ответ: a<−1 или a>2."}]},
                {"uid": "MET-AA-FUNCTIONAL", "title": "Функциональные уравнения",
                 "description": "Подставляйте частные значения x. Ищите закономерности. Проверяйте решение подстановкой в исходное уравнение.",
                 "examples": [{"uid": "EX-AA-002", "title": "Функциональное уравнение", "statement": "f(x+1)=f(x)+2x+1, f(0)=0. Найдите f(x).", "solution": "f(1)=1, f(2)=4, f(3)=9. Гипотеза: f(x)=x². Проверка: (x+1)²=x²+2x+1 ✓."}]},
                {"uid": "MET-AA-MODULAR-EQ", "title": "Уравнения с модулем",
                 "description": "Раскройте модуль по определению. Разбейте на случаи. Проверьте каждое решение в исходном уравнении.",
                 "examples": [{"uid": "EX-AA-003", "title": "Уравнение с модулем", "statement": "|2x−3|=x+1.", "solution": "1) 2x−3≥0 (x≥1.5): 2x−3=x+1 → x=4. 2) 2x−3<0 (x<1.5): −2x+3=x+1 → x=2/3. Оба входят. Ответ: 2/3 и 4."}]},
            ],
        }],
    },

    # 2. Алгебраические преобразования (2 → 3)
    {
        "topic_uid": "TOP-MATH-ALGEBRA-TRANSFORMS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ALG-TRANSFORM-B11",
            "title": "Алгебраические преобразования",
            "definition": "Упрощение выражений, тождественные преобразования, формулы сокращённого умножения.",
            "methods": [
                {"uid": "MET-AT-FSU", "title": "Формулы сокращённого умножения",
                 "description": "(a±b)²=a²±2ab+b². a²−b²=(a−b)(a+b). (a±b)³=a³±3a²b+3ab²±b³. a³±b³=(a±b)(a²∓ab+b²).",
                 "examples": [{"uid": "EX-AT-001", "title": "Разность квадратов", "statement": "Упростите: (3x+2)²−(3x−2)².", "solution": "= [(3x+2)−(3x−2)]·[(3x+2)+(3x−2)] = 4·6x = 24x."}]},
                {"uid": "MET-AT-FRACTIONS", "title": "Преобразование алгебраических дробей",
                 "description": "Общий знаменатель. Сокращение: разложите числитель и знаменатель на множители. (a/b)·(c/d)=ac/(bd).",
                 "examples": [{"uid": "EX-AT-002", "title": "Сокращение", "statement": "Упростите: (x²−4)/(x²+4x+4).", "solution": "(x−2)(x+2)/(x+2)²=(x−2)/(x+2)."}]},
                {"uid": "MET-AT-RADICALS", "title": "Преобразование выражений с корнями",
                 "description": "√(ab)=√a·√b. √(a/b)=√a/√b. Освобождение от иррациональности в знаменателе: умножьте на сопряжённое.",
                 "examples": [{"uid": "EX-AT-003", "title": "Рационализация", "statement": "Упростите: 6/(√3−1).", "solution": "6(√3+1)/((√3)²−1²) = 6(√3+1)/2 = 3(√3+1) = 3√3+3."}]},
            ],
        }],
    },

    # 3. Анализ таблиц и диаграмм (1 → 3)
    {
        "topic_uid": "TOP-OGE-ANALIZ-TABLITS-I-DIAGRAMM-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-TABLE-DIAGRAM-B11",
            "title": "Анализ таблиц и диаграмм",
            "definition": "Чтение, анализ и интерпретация данных из таблиц, столбчатых, круговых и линейных диаграмм.",
            "methods": [
                {"uid": "MET-TD-READ", "title": "Чтение таблиц и извлечение данных",
                 "description": "Найдите нужную строку и столбец. Определите единицы измерения. Выполните операции: сумма, разность, среднее.",
                 "examples": [{"uid": "EX-TD-001", "title": "Таблица", "statement": "Таблица: Янв-120, Фев-95, Мар-140. На сколько март > февраля?", "solution": "140−95 = 45."}]},
                {"uid": "MET-TD-BAR-PIE", "title": "Анализ столбчатых и круговых диаграмм",
                 "description": "Столбчатая: высота = значение. Круговая: сектор = доля (в %). Сравнивайте визуально и числами.",
                 "examples": [{"uid": "EX-TD-002", "title": "Круговая диаграмма", "statement": "Бюджет семьи: еда 40%, транспорт 15%, жильё 30%, прочее 15%. Бюджет 60000. Расходы на еду?", "solution": "60000·40/100 = 24000 руб."}]},
                {"uid": "MET-TD-LINE", "title": "Анализ графиков и линейных диаграмм",
                 "description": "Определите тренд (рост/падение). Найдите максимум/минимум. Вычислите скорость изменения (наклон).",
                 "examples": [{"uid": "EX-TD-003", "title": "Линейная диаграмма", "statement": "Температура: 6ч=−2°, 12ч=8°, 18ч=5°. В какой период самый быстрый рост?", "solution": "6→12: рост 10° за 6ч ≈ 1.7°/ч. 12→18: падение. Самый быстрый рост: с 6 до 12 часов."}]},
            ],
        }],
    },

    # 4. Выборка и популяция (2 → 3)
    {
        "topic_uid": "TOP-VYBORKA-I-POPULYACIYA-471a66",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-SAMPLE-POP-B11",
            "title": "Выборка и генеральная совокупность",
            "definition": "Генеральная совокупность — все объекты. Выборка — часть для исследования. Репрезентативность и методы отбора.",
            "methods": [
                {"uid": "MET-SP-TYPES", "title": "Виды выборок",
                 "description": "Простая случайная: каждый элемент имеет равную вероятность попасть. Стратифицированная: разделение на группы. Систематическая: каждый k-й.",
                 "examples": [{"uid": "EX-SP-001", "title": "Тип выборки", "statement": "Из 1000 учеников опрашивают каждого 10-го по списку. Какой тип выборки?", "solution": "Систематическая выборка (каждый k-й элемент, k=10)."}]},
                {"uid": "MET-SP-REPR", "title": "Репрезентативность выборки",
                 "description": "Выборка репрезентативна, если отражает структуру генеральной совокупности. Размер выборки влияет на точность. Ошибка выборки ∝ 1/√n.",
                 "examples": [{"uid": "EX-SP-002", "title": "Репрезентативность", "statement": "Из 60% девочек и 40% мальчиков школы опросили 50 человек: 45 девочек и 5 мальчиков. Репрезентативна ли?", "solution": "Нет. В выборке 90% девочек, а в школе 60%. Выборка смещена."}]},
                {"uid": "MET-SP-ESTIMATE", "title": "Оценка параметров генеральной совокупности",
                 "description": "Выборочное среднее x̄ оценивает μ. Выборочная дисперсия s² оценивает σ². Доверительный интервал: x̄ ± z·s/√n.",
                 "examples": [{"uid": "EX-SP-003", "title": "Оценка среднего", "statement": "Выборка n=100: x̄=170 см, s=10. 95%-доверительный интервал для μ?", "solution": "z=1.96. ΔI=1.96·10/√100=1.96. μ ∈ [168.04; 171.96]."}]},
            ],
        }],
    },

    # 5. Геометрические задачи с доказательством (1 → 3)
    {
        "topic_uid": "TOP-OGE-GEOMETRICHESKOE-DOKAZATELSTVO-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-GEOM-PROOF-B11",
            "title": "Геометрические доказательства",
            "definition": "Доказательство геометрических утверждений: признаки равенства и подобия, теоремы о параллельных прямых.",
            "methods": [
                {"uid": "MET-GP-CONGRUENT", "title": "Признаки равенства треугольников",
                 "description": "1-й: по двум сторонам и углу между ними (SAS). 2-й: по стороне и двум прилежащим углам (ASA). 3-й: по трём сторонам (SSS).",
                 "examples": [{"uid": "EX-GP-001", "title": "Равенство △", "statement": "△ABC и △DEF: AB=DE, BC=EF, ∠B=∠E. Докажите △ABC=△DEF.", "solution": "По 1-му признаку (SAS): AB=DE, ∠B=∠E, BC=EF → △ABC=△DEF."}]},
                {"uid": "MET-GP-PARALLEL", "title": "Теоремы о параллельных прямых",
                 "description": "Если накрест лежащие углы равны → прямые параллельны. Сумма односторонних углов = 180° → прямые параллельны.",
                 "examples": [{"uid": "EX-GP-002", "title": "Параллельные прямые", "statement": "Прямые a и b пересечены секущей. ∠1=∠2 (накрест лежащие). Докажите a∥b.", "solution": "По теореме: если накрест лежащие углы равны, то прямые параллельны. ∠1=∠2 → a∥b."}]},
                {"uid": "MET-GP-INDIRECT", "title": "Метод от противного",
                 "description": "Предположите, что утверждение неверно. Выведите следствия. Получите противоречие с условием. Значит, утверждение верно.",
                 "examples": [{"uid": "EX-GP-003", "title": "От противного", "statement": "Докажите: в △ не может быть двух тупых углов.", "solution": "Предположим: ∠A>90° и ∠B>90°. Тогда ∠A+∠B>180°. Но сумма всех углов △=180°. Противоречие → двух тупых углов быть не может."}]},
            ],
        }],
    },

    # 6. Единицы измерения (1 → 3)
    {
        "topic_uid": "TOP-EDINITSY-IZMERENIYA-002",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-UNITS-B11",
            "title": "Единицы измерения",
            "definition": "Меры длины, площади, объёма, массы, времени. Перевод из одних единиц в другие.",
            "methods": [
                {"uid": "MET-UN-LENGTH", "title": "Единицы длины и перевод",
                 "description": "1 км=1000 м, 1 м=100 см=1000 мм, 1 м=10 дм. Для перевода: умножайте/делите на 10, 100, 1000.",
                 "examples": [{"uid": "EX-UN-001", "title": "Перевод длины", "statement": "2 км 350 м = ? м", "solution": "2·1000+350 = 2350 м."}]},
                {"uid": "MET-UN-AREA-VOL", "title": "Единицы площади и объёма",
                 "description": "1 м²=10000 см². 1 км²=1000000 м². 1 м³=1000 дм³=1000000 см³. 1 л=1 дм³.",
                 "examples": [{"uid": "EX-UN-002", "title": "Перевод площади", "statement": "3 м² = ? см²", "solution": "3·10000 = 30000 см²."}]},
                {"uid": "MET-UN-MASS-TIME", "title": "Единицы массы и времени",
                 "description": "1 т=1000 кг, 1 кг=1000 г. 1 ч=60 мин, 1 мин=60 с, 1 сутки=24 ч.",
                 "examples": [{"uid": "EX-UN-003", "title": "Перевод времени", "statement": "3 ч 25 мин = ? мин", "solution": "3·60+25 = 205 мин."}]},
            ],
        }],
    },

    # 7. Задачи с параметром ЕГЭ (1 → 3)
    {
        "topic_uid": "TOP-EGE-ZADACHI-S-PARAMETROM-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PARAM-EGE-B11",
            "title": "Задачи с параметром",
            "definition": "Уравнения и неравенства, содержащие параметр. Поиск всех значений параметра, при которых выполняется условие.",
            "methods": [
                {"uid": "MET-PE-DISCRIM", "title": "Исследование дискриминанта",
                 "description": "Квадратное уравнение с параметром: условие существования корней D≥0. Количество корней: D>0 (два), D=0 (один), D<0 (нет).",
                 "examples": [{"uid": "EX-PE-001", "title": "Дискриминант", "statement": "x²+2ax+a+6=0 имеет два корня. Найдите a.", "solution": "D=4a²−4(a+6)>0 → a²−a−6>0 → (a−3)(a+2)>0. Ответ: a<−2 или a>3."}]},
                {"uid": "MET-PE-GRAPHIC", "title": "Графический метод с параметром",
                 "description": "Постройте семейство графиков в зависимости от параметра. Определите, при каких значениях параметра графики пересекаются нужным образом.",
                 "examples": [{"uid": "EX-PE-002", "title": "Графический метод", "statement": "При каких a прямая y=a касается параболы y=x²?", "solution": "x²=a → y=a горизонтальная прямая. Касается параболы при a=0 (одна общая точка — вершина)."}]},
                {"uid": "MET-PE-SUBSTITUTION", "title": "Метод замены переменной в задачах с параметром",
                 "description": "Выразите параметр через x: a=f(x). Исследуйте область значений f(x). Каждое значение a даёт решения x.",
                 "examples": [{"uid": "EX-PE-003", "title": "Замена", "statement": "x²−2x=a. При каких a ровно 2 решения?", "solution": "f(x)=x²−2x=(x−1)²−1. min f=−1. Два решения при a>−1. При a=−1 — одно. При a<−1 — нет."}]},
            ],
        }],
    },

    # 8. Иррациональные и трансцендентные неравенства (2 → 3)
    {
        "topic_uid": "TOP-MATH-COMPLEX-INEQUALITIES",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-COMPLEX-INEQ-B11",
            "title": "Иррациональные и трансцендентные неравенства",
            "definition": "Неравенства с корнями, показательные и логарифмические неравенства.",
            "methods": [
                {"uid": "MET-CI-IRRATIONAL", "title": "Иррациональные неравенства",
                 "description": "√f(x) > g(x): разбейте на случаи: g(x)<0 (автоматически верно при f(x)≥0) и g(x)≥0 (возведите в квадрат). ОДЗ: f(x)≥0.",
                 "examples": [{"uid": "EX-CI-001", "title": "Иррациональное", "statement": "√(x+3) > x+1.", "solution": "ОДЗ: x≥−3. Если x+1<0 (x<−1): √(x+3)≥0>x+1 ✓ при x∈[−3;−1). Если x+1≥0: x+3>(x+1)² → x²+x−2<0 → x∈(−2;1). Пересечение: [−1;1). Итого: [−3;1)."}]},
                {"uid": "MET-CI-EXPONENTIAL", "title": "Показательные неравенства",
                 "description": "aˣ > aʸ: при a>1 ⟺ x>y, при 0<a<1 ⟺ x<y. Замена t=aˣ сводит к алгебраическому неравенству.",
                 "examples": [{"uid": "EX-CI-002", "title": "Показательное", "statement": "2ˣ−3·2ˣ⁻¹+1 > 0.", "solution": "t=2ˣ: t−3t/2+1>0 → −t/2+1>0 → t<2. 2ˣ<2 → x<1. Ответ: (−∞;1)."}]},
                {"uid": "MET-CI-LOGARITHMIC", "title": "Логарифмические неравенства",
                 "description": "log_a(f(x)) > log_a(g(x)): при a>1 ⟺ f(x)>g(x) (с учётом ОДЗ: f,g>0). При 0<a<1 — знак меняется.",
                 "examples": [{"uid": "EX-CI-003", "title": "Логарифмическое", "statement": "log₂(x+3) ≤ 3.", "solution": "ОДЗ: x+3>0 → x>−3. log₂(x+3)≤3 → x+3≤8 → x≤5. Ответ: (−3; 5]."}]},
            ],
        }],
    },

    # 9. Комбинаторика и вероятность (2 → 3)
    {
        "topic_uid": "TOP-MATH-COMBINATORICS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-COMB-PROB-GENERAL-B11",
            "title": "Комбинаторика и вероятность",
            "definition": "Комбинаторные формулы и их применение в задачах на вероятность.",
            "methods": [
                {"uid": "MET-CG-COUNTING", "title": "Правила подсчёта: сложение и умножение",
                 "description": "Правило сложения: ИЛИ → складываем. Правило умножения: И → перемножаем. Дерево исходов для многоэтапных экспериментов.",
                 "examples": [{"uid": "EX-CG-001", "title": "Правило умножения", "statement": "Сколько 3-значных чисел из цифр 1,2,3,4 без повторений?", "solution": "4·3·2 = 24."}]},
                {"uid": "MET-CG-FORMULAS", "title": "Перестановки, размещения, сочетания",
                 "description": "Pₙ=n!. Aₙᵏ=n!/(n−k)!. Cₙᵏ=n!/(k!(n−k)!). Перестановки с повторениями: n!/(n₁!·n₂!·…).",
                 "examples": [{"uid": "EX-CG-002", "title": "Сочетания", "statement": "Из 8 учеников выбрать 3 для олимпиады. Сколько способов?", "solution": "C(8,3)=8!/(3!·5!)=56."}]},
                {"uid": "MET-CG-PROBABILITY", "title": "Вычисление вероятности через комбинаторику",
                 "description": "P(A)=|A|/|Ω|. Число благоприятных и всех исходов считайте комбинаторными формулами.",
                 "examples": [{"uid": "EX-CG-003", "title": "Вероятность", "statement": "Из колоды 36 карт вытянули 2. P(обе красные)?", "solution": "Красных 18. Благоприятных: C(18,2)=153. Всего: C(36,2)=630. P=153/630=17/70≈0.243."}]},
            ],
        }],
    },

    # 10. Корреляция (2 → 3)
    {
        "topic_uid": "TOP-KORRELYATSIYA-7d5d50",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-CORRELATION-B11",
            "title": "Корреляция",
            "definition": "Статистическая связь между двумя величинами. Коэффициент корреляции Пирсона, его интерпретация.",
            "methods": [
                {"uid": "MET-COR-COEFF", "title": "Коэффициент корреляции Пирсона",
                 "description": "r = Σ(xᵢ−x̄)(yᵢ−ȳ) / √[Σ(xᵢ−x̄)²·Σ(yᵢ−ȳ)²]. −1≤r≤1. |r|>0.7 — сильная связь.",
                 "examples": [{"uid": "EX-COR-001", "title": "Расчёт r", "statement": "x: 1,2,3. y: 2,4,5. Найдите r.", "solution": "x̄=2, ȳ=11/3. Σ(xᵢ−x̄)(yᵢ−ȳ)=(−1)(−5/3)+(0)(1/3)+(1)(4/3)=3. Σ(xᵢ−x̄)²=2. Σ(yᵢ−ȳ)²=14/3. r=3/√(28/3)≈0.98."}]},
                {"uid": "MET-COR-INTERPRET", "title": "Интерпретация корреляции",
                 "description": "r>0: прямая связь (обе растут). r<0: обратная связь. r≈0: связи нет. Корреляция ≠ причинность!",
                 "examples": [{"uid": "EX-COR-002", "title": "Интерпретация", "statement": "r(рост, вес)=0.72. Что это значит?", "solution": "Сильная прямая корреляция: с увеличением роста вес в среднем тоже увеличивается. Но рост не «причина» веса."}]},
                {"uid": "MET-COR-SCATTER", "title": "Диаграмма рассеяния",
                 "description": "Нанесите точки (xᵢ, yᵢ) на координатную плоскость. Визуально оцените характер связи: линейная, нелинейная, отсутствие.",
                 "examples": [{"uid": "EX-COR-003", "title": "Диаграмма рассеяния", "statement": "Точки: (1,1),(2,4),(3,2),(4,5),(5,4). Какая связь?", "solution": "Общий тренд восходящий, но с разбросом. Связь умеренная прямая (r≈0.6)."}]},
            ],
        }],
    },

    # 11. Корреляция и регрессия (2 → 3)
    {
        "topic_uid": "TOP-KORRELYACIYA-I-REGRESSIY-43dd38",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-CORR-REGR-B11",
            "title": "Корреляция и регрессия",
            "definition": "Линейная регрессия y=a+bx. Метод наименьших квадратов. Прогнозирование.",
            "methods": [
                {"uid": "MET-CR-LINEAR", "title": "Линейная регрессия (МНК)",
                 "description": "ŷ=a+bx. b=Σ(xᵢ−x̄)(yᵢ−ȳ)/Σ(xᵢ−x̄)². a=ȳ−bx̄. Линия наилучшего приближения.",
                 "examples": [{"uid": "EX-CR-001", "title": "МНК", "statement": "x: 1,2,3,4. y: 3,5,6,8. Найдите уравнение регрессии.", "solution": "x̄=2.5, ȳ=5.5. b=(−1.5·(−2.5)+...)/5=8/5=1.6. a=5.5−1.6·2.5=1.5. ŷ=1.5+1.6x."}]},
                {"uid": "MET-CR-R2", "title": "Коэффициент детерминации R²",
                 "description": "R²=r² — доля дисперсии y, объяснённая регрессией. R²=1: идеальная модель. R²=0: модель не объясняет данные.",
                 "examples": [{"uid": "EX-CR-002", "title": "R²", "statement": "r=0.9. Какова доля объяснённой дисперсии?", "solution": "R²=0.81=81%. Регрессия объясняет 81% вариации y."}]},
                {"uid": "MET-CR-PREDICT", "title": "Прогнозирование по регрессии",
                 "description": "Подставьте x₀ в уравнение ŷ=a+bx₀. Прогноз надёжен в пределах данных (интерполяция). Экстраполяция — менее надёжна.",
                 "examples": [{"uid": "EX-CR-003", "title": "Прогноз", "statement": "ŷ=1.5+1.6x. Спрогнозируйте y при x=5.", "solution": "ŷ=1.5+1.6·5=9.5. (Экстраполяция — данные были до x=4.)"}]},
            ],
        }],
    },

    # 12. Линейная комбинация (2 → 3)
    {
        "topic_uid": "TOP-LINEJNAYA-KOMBINATSIYA-31422b",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-LIN-COMB-B11",
            "title": "Линейная комбинация",
            "definition": "α₁v₁+α₂v₂+…+αₙvₙ — линейная комбинация векторов. Линейная зависимость и независимость.",
            "methods": [
                {"uid": "MET-LC-DEF", "title": "Вычисление линейной комбинации",
                 "description": "Умножьте каждый вектор на скаляр и сложите покомпонентно. α(a₁,a₂)+β(b₁,b₂)=(αa₁+βb₁, αa₂+βb₂).",
                 "examples": [{"uid": "EX-LC-001", "title": "Линейная комбинация", "statement": "a=(1,2), b=(3,−1). 2a+3b=?", "solution": "2(1,2)+3(3,−1)=(2,4)+(9,−3)=(11,1)."}]},
                {"uid": "MET-LC-INDEP", "title": "Линейная зависимость и независимость",
                 "description": "Векторы линейно зависимы, если один выражается через остальные. На плоскости: 2 вектора зависимы ⟺ коллинеарны.",
                 "examples": [{"uid": "EX-LC-002", "title": "Проверка зависимости", "statement": "a=(2,4), b=(1,2). Зависимы ли?", "solution": "a=2b → линейно зависимы (коллинеарны)."}]},
                {"uid": "MET-LC-DECOMP", "title": "Разложение вектора по базису",
                 "description": "Любой вектор v можно разложить по базису {e₁,e₂}: v=αe₁+βe₂. Коэффициенты находят из системы уравнений.",
                 "examples": [{"uid": "EX-LC-003", "title": "Разложение", "statement": "e₁=(1,0), e₂=(0,1). Разложите v=(3,5) по базису.", "solution": "v=3·e₁+5·e₂."}]},
            ],
        }],
    },

    # 13. Линейные неравенства (2 → 3)
    {
        "topic_uid": "TOP-LINEJNYE-NERAVENSTVA-f61cf0",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-LIN-INEQ-B11",
            "title": "Линейные неравенства",
            "definition": "Неравенства вида ax+b > 0 (≥,<,≤). Системы линейных неравенств. Графическое решение.",
            "methods": [
                {"uid": "MET-LI-SOLVE", "title": "Решение линейных неравенств",
                 "description": "Перенесите x в одну сторону. При умножении/делении на отрицательное — знак неравенства меняется.",
                 "examples": [{"uid": "EX-LI-001", "title": "Линейное неравенство", "statement": "3x−7 > 2x+1.", "solution": "3x−2x > 1+7 → x > 8."}]},
                {"uid": "MET-LI-SYSTEM", "title": "Системы линейных неравенств",
                 "description": "Решите каждое неравенство отдельно. Ответ — пересечение решений (общая часть числовой прямой).",
                 "examples": [{"uid": "EX-LI-002", "title": "Система неравенств", "statement": "2x−1>3 и 5−x>1.", "solution": "2x>4 → x>2. 5−x>1 → x<4. Пересечение: 2<x<4."}]},
                {"uid": "MET-LI-GRAPHIC", "title": "Графическое решение неравенств на плоскости",
                 "description": "Неравенство ax+by>c: нарисуйте прямую ax+by=c. Определите полуплоскость подстановкой тестовой точки.",
                 "examples": [{"uid": "EX-LI-003", "title": "Полуплоскость", "statement": "x+2y≤6. Нарисуйте область.", "solution": "Прямая x+2y=6 (через (0,3) и (6,0)). Подставим (0,0): 0≤6 ✓. Область — под прямой (включая)."}]},
            ],
        }],
    },

    # 14. Независимые события (2 → 3)
    {
        "topic_uid": "TOP-NEZAVISIMYE-SOBYTIYA-bdea5e",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-INDEP-EVENTS-B11",
            "title": "Независимые события",
            "definition": "События A и B независимы, если P(A∩B)=P(A)·P(B). Одно не влияет на другое.",
            "methods": [
                {"uid": "MET-IE-CHECK", "title": "Проверка независимости событий",
                 "description": "Проверьте: P(A∩B)=P(A)·P(B)? Если да — независимы. Или: P(A|B)=P(A)?",
                 "examples": [{"uid": "EX-IE-001", "title": "Проверка", "statement": "P(A)=0.3, P(B)=0.4, P(A∩B)=0.12. Независимы ли?", "solution": "P(A)·P(B)=0.12=P(A∩B). Да, независимы."}]},
                {"uid": "MET-IE-MULTIPLY", "title": "Вероятность совместного наступления",
                 "description": "Для независимых: P(A₁∩A₂∩…∩Aₙ)=P(A₁)·P(A₂)·…·P(Aₙ). Цепочка независимых испытаний.",
                 "examples": [{"uid": "EX-IE-002", "title": "Цепочка", "statement": "Монету бросают 4 раза. P(все орлы)?", "solution": "P=0.5⁴=0.0625=1/16."}]},
                {"uid": "MET-IE-ATLEAST", "title": "Вероятность хотя бы одного события",
                 "description": "P(хотя бы одно)=1−P(ни одного). P(ни одного)=(1−p₁)(1−p₂)·…·(1−pₙ).",
                 "examples": [{"uid": "EX-IE-003", "title": "Хотя бы одно", "statement": "3 стрелка стреляют: P₁=0.7, P₂=0.8, P₃=0.9. P(хотя бы одно попадание)?", "solution": "P(ни одного)=0.3·0.2·0.1=0.006. P(хотя бы одно)=1−0.006=0.994."}]},
            ],
        }],
    },

    # 15. Неравенства и системы неравенств (2 → 3)
    {
        "topic_uid": "TOP-MATH-INEQUALITIES",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-INEQ-SYS-B11",
            "title": "Неравенства и системы неравенств",
            "definition": "Линейные, квадратные, рациональные неравенства. Системы и совокупности неравенств.",
            "methods": [
                {"uid": "MET-IS-INTERVALS", "title": "Метод интервалов",
                 "description": "1) Найдите нули. 2) Отметьте на оси. 3) Определите знак на каждом промежутке (подставьте пробную точку). 4) Выберите нужные промежутки.",
                 "examples": [{"uid": "EX-IS-001", "title": "Метод интервалов", "statement": "(x−1)(x+3) < 0.", "solution": "Нули: 1,−3. Знаки: +,−,+. Ответ: (−3;1)."}]},
                {"uid": "MET-IS-SYSTEMS", "title": "Системы неравенств",
                 "description": "Система: пересечение решений (И). Совокупность: объединение (ИЛИ). Решите каждое отдельно, затем найдите общую часть.",
                 "examples": [{"uid": "EX-IS-002", "title": "Система", "statement": "x²−4<0 и x>−1.", "solution": "x²−4<0: −2<x<2. x>−1. Пересечение: (−1; 2)."}]},
                {"uid": "MET-IS-DOUBLE", "title": "Двойные неравенства",
                 "description": "a < f(x) < b ⟺ система: f(x)>a и f(x)<b. Решите как систему.",
                 "examples": [{"uid": "EX-IS-003", "title": "Двойное неравенство", "statement": "1 < 2x−3 < 7.", "solution": "1<2x−3: x>2. 2x−3<7: x<5. Ответ: (2; 5)."}]},
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
    print(f"\n{'='*60}\nBatch 11 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
