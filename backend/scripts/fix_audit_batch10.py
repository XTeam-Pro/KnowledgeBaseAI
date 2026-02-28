#!/usr/bin/env python3
"""Batch 10: Fix remaining 19 IRRELEVANT topics."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 1. Планиметрические задачи ЕГЭ
    {
        "topic_uid": "TOP-EGE-PLANIMETRIYA-ZADACHI-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-EGE-PLANIM-B10",
            "title": "Планиметрические задачи ЕГЭ",
            "definition": "Комплексные задачи планиметрии ЕГЭ: подобие, площади, вписанные и описанные окружности.",
            "methods": [
                {"uid": "MET-EP-SIMILAR", "title": "Метод подобия треугольников",
                 "description": "Найдите пару подобных △ (по двум углам). Составьте пропорцию сходственных сторон. S₁/S₂ = k².",
                 "examples": [{"uid": "EX-EP-001", "title": "Подобие в задаче ЕГЭ", "statement": "DE∥BC, AD=3, DB=6, DE=4. BC=?", "solution": "△ADE∼△ABC, k=AD/AB=3/9=1/3. BC=DE·3=12."}]},
                {"uid": "MET-EP-AREAS", "title": "Метод площадей",
                 "description": "S=½ab·sin C. Формула Герона: S=√[p(p−a)(p−b)(p−c)]. Выразите площадь двумя способами и приравняйте.",
                 "examples": [{"uid": "EX-EP-002", "title": "Метод площадей", "statement": "△: a=13, b=14, c=15. S=? BH=?", "solution": "p=21. S=√(21·8·7·6)=84. S=½·15·BH → BH=11.2."}]},
                {"uid": "MET-EP-CIRCLES", "title": "Вписанная и описанная окружности",
                 "description": "r=S/p (вписанная). R=abc/(4S) (описанная). Касательные из одной точки равны.",
                 "examples": [{"uid": "EX-EP-003", "title": "Радиус вписанной", "statement": "△: a=13, b=14, c=15, S=84. r=?", "solution": "p=21. r=84/21=4."}]},
            ],
        }],
    },

    # 2. Планиметрия: базовые задачи
    {
        "topic_uid": "TOP-MATH-PLANE-GEOMETRY",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PLANE-GEOM-BASE",
            "title": "Планиметрия: базовые задачи",
            "definition": "Основные задачи планиметрии: треугольники, четырёхугольники, окружность, координатный метод.",
            "methods": [
                {"uid": "MET-PGB-TRIANGLES", "title": "Свойства и площади треугольников",
                 "description": "S=½ah. Теорема Пифагора: a²+b²=c². Сумма углов 180°. Медиана, биссектриса, высота.",
                 "examples": [{"uid": "EX-PGB-001", "title": "Теорема Пифагора", "statement": "Катеты 5 и 12. Гипотенуза?", "solution": "c²=25+144=169. c=13."}]},
                {"uid": "MET-PGB-QUADS", "title": "Свойства четырёхугольников",
                 "description": "Параллелограмм: S=ah. Трапеция: S=½(a+b)h. Ромб: S=½d₁d₂. Диагонали параллелограмма делятся пополам.",
                 "examples": [{"uid": "EX-PGB-002", "title": "Площадь трапеции", "statement": "Основания 5 и 9, высота 4. S=?", "solution": "S=½(5+9)·4=28."}]},
                {"uid": "MET-PGB-CIRCLE-ARC", "title": "Длина дуги и площадь сектора",
                 "description": "Длина дуги: l=(α/360°)·2πr. Площадь сектора: S=(α/360°)·πr². C=2πr, S(круга)=πr².",
                 "examples": [{"uid": "EX-PGB-003", "title": "Площадь сектора", "statement": "r=6, α=60°. S сектора?", "solution": "S=(60/360)·π·36=6π≈18.85."}]},
            ],
        }],
    },

    # 3. Плоскость в пространстве
    {
        "topic_uid": "TOP-PLOSKOST-V-PROSTRANSTVE-f03ae1",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PLANE-SPACE-B10",
            "title": "Плоскость в пространстве",
            "definition": "Аксиомы стереометрии, взаимное расположение плоскостей, параллельность и перпендикулярность.",
            "methods": [
                {"uid": "MET-PS-AXIOMS", "title": "Аксиомы стереометрии",
                 "description": "Через 3 точки, не лежащие на одной прямой, проходит единственная плоскость. Если 2 точки прямой лежат в плоскости, то вся прямая в ней.",
                 "examples": [{"uid": "EX-PS-001", "title": "Аксиомы", "statement": "Точки A,B,C не коллинеарны. Сколько плоскостей через них?", "solution": "Ровно одна (по аксиоме стереометрии)."}]},
                {"uid": "MET-PS-PARALLEL", "title": "Параллельность плоскостей",
                 "description": "Две плоскости параллельны, если две пересекающиеся прямые одной параллельны другой плоскости. Свойство: сечения параллельны.",
                 "examples": [{"uid": "EX-PS-002", "title": "Параллельные плоскости", "statement": "В кубе ABCDA₁B₁C₁D₁ докажите: ABC∥A₁B₁C₁.", "solution": "AB∥A₁B₁, BC∥B₁C₁ — две пересекающиеся прямые плоскости ABC параллельны A₁B₁C₁ → плоскости параллельны."}]},
                {"uid": "MET-PS-PERP", "title": "Перпендикулярность прямой и плоскости",
                 "description": "Прямая ⊥ плоскости, если она ⊥ двум пересекающимся прямым в этой плоскости. Теорема о трёх перпендикулярах.",
                 "examples": [{"uid": "EX-PS-003", "title": "Перпендикуляр к плоскости", "statement": "AA₁ ⊥ плоскости основания куба. Найдите угол диагонали AC₁ с основанием.", "solution": "AC₁ проектируется в AC. tg α = AA₁/AC = a/(a√2) = 1/√2. α = arctg(1/√2) ≈ 35.3°."}]},
            ],
        }],
    },

    # 4. Прикладная математика
    {
        "topic_uid": "TOP-MATH-APPLIED-MATH",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-APPLIED-MATH-B10",
            "title": "Прикладная математика",
            "definition": "Практические задачи: проценты, пропорции, единицы измерения, оценка и прикидка.",
            "methods": [
                {"uid": "MET-AM-PERCENT", "title": "Задачи на проценты",
                 "description": "Процент — сотая часть. a% от b = a·b/100. Нахождение процента, числа по проценту, процентного изменения.",
                 "examples": [{"uid": "EX-AM-001", "title": "Процент от числа", "statement": "Найдите 15% от 240.", "solution": "15·240/100 = 36."}]},
                {"uid": "MET-AM-PROPORTION", "title": "Пропорции и масштаб",
                 "description": "a/b = c/d → ad = bc (основное свойство). Масштаб 1:1000 означает 1 см на карте = 10 м.",
                 "examples": [{"uid": "EX-AM-002", "title": "Пропорция", "statement": "5 кг яблок стоят 400 руб. Сколько стоят 8 кг?", "solution": "5/400 = 8/x → x = 8·400/5 = 640 руб."}]},
                {"uid": "MET-AM-ESTIMATE", "title": "Оценка и прикидка результата",
                 "description": "Округлите числа до удобных. Проверьте порядок величины. Сравните с ожидаемым результатом.",
                 "examples": [{"uid": "EX-AM-003", "title": "Прикидка", "statement": "49·51 ≈ ?", "solution": "≈ 50·50 = 2500. Точно: 49·51 = 50²−1² = 2499."}]},
            ],
        }],
    },

    # 5. Производная и её применение
    {
        "topic_uid": "TOP-MATH-DERIVATIVES",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-DERIVATIVES-B10",
            "title": "Производная и её применение",
            "definition": "Производная функции, правила дифференцирования, геометрический и физический смысл.",
            "methods": [
                {"uid": "MET-DER-TABLE", "title": "Таблица производных",
                 "description": "(xⁿ)'=nxⁿ⁻¹. (sin x)'=cos x. (cos x)'=−sin x. (eˣ)'=eˣ. (ln x)'=1/x.",
                 "examples": [{"uid": "EX-DER-001", "title": "Табличная производная", "statement": "y=x⁴−3x²+5. y'=?", "solution": "y'=4x³−6x."}]},
                {"uid": "MET-DER-RULES", "title": "Правила дифференцирования",
                 "description": "(f±g)'=f'±g'. (fg)'=f'g+fg'. (f/g)'=(f'g−fg')/g². (f(g(x)))'=f'(g)·g'(x) (цепное правило).",
                 "examples": [{"uid": "EX-DER-002", "title": "Производная произведения", "statement": "y=x²·sin x. y'=?", "solution": "y'=2x·sin x+x²·cos x."}]},
                {"uid": "MET-DER-APPLY", "title": "Применение производной",
                 "description": "Касательная: y=f(a)+f'(a)(x−a). Экстремумы: f'(x)=0. Возрастание: f'(x)>0. Убывание: f'(x)<0.",
                 "examples": [{"uid": "EX-DER-003", "title": "Касательная", "statement": "y=x²−4x+3 в точке x₀=1. Уравнение касательной?", "solution": "f(1)=0. f'(x)=2x−4, f'(1)=−2. y=0+(−2)(x−1)=−2x+2."}]},
            ],
        }],
    },

    # 6. Прямая и плоскость
    {
        "topic_uid": "TOP-PRYAMAYA-I-PLOSKOST-1d0194",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-LINE-PLANE-B10",
            "title": "Прямая и плоскость в пространстве",
            "definition": "Взаимное расположение прямой и плоскости: параллельность, перпендикулярность, наклонная.",
            "methods": [
                {"uid": "MET-LP-PARALLEL", "title": "Признак параллельности прямой и плоскости",
                 "description": "Прямая ∥ плоскости, если она ∥ какой-либо прямой в этой плоскости. Или: прямая не лежит в плоскости и не пересекает её.",
                 "examples": [{"uid": "EX-LP-001", "title": "Параллельность", "statement": "В тетраэдре ABCD. M — середина BC, N — середина CD. Докажите MN∥(ABD).", "solution": "MN — средняя линия △BCD, MN∥BD. BD лежит в (ABD). Значит MN∥(ABD)."}]},
                {"uid": "MET-LP-PERP", "title": "Перпендикулярность прямой и плоскости",
                 "description": "Прямая ⊥ плоскости ⟺ она ⊥ любой прямой в этой плоскости. Достаточно: ⊥ двум пересекающимся.",
                 "examples": [{"uid": "EX-LP-002", "title": "Перпендикуляр", "statement": "SA ⊥ (ABC). AB=AC=5, BC=6, SA=4. Найдите SC.", "solution": "AC=5, SA=4. SC=√(SA²+AC²)=√(16+25)=√41."}]},
                {"uid": "MET-LP-ANGLE", "title": "Угол между прямой и плоскостью",
                 "description": "Угол = угол между прямой и её проекцией на плоскость. Используйте теорему о трёх перпендикулярах.",
                 "examples": [{"uid": "EX-LP-003", "title": "Угол наклонной", "statement": "SO ⊥ (ABC), O — центр. SA=a, угол SA с плоскостью?", "solution": "Проекция SA на плоскость — OA. sin α = SO/SA."}]},
            ],
        }],
    },

    # 7. Пути и циклы
    {
        "topic_uid": "TOP-PUTI-I-TSIKLY-17a10d",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PATHS-CYCLES-B10",
            "title": "Пути и циклы в графах",
            "definition": "Путь — последовательность вершин, соединённых рёбрами. Цикл — замкнутый путь. Эйлеровы и гамильтоновы пути.",
            "methods": [
                {"uid": "MET-PC-EULER", "title": "Эйлеровы пути и циклы",
                 "description": "Эйлеров путь проходит по каждому ребру ровно один раз. Существует ⟺ не более 2 вершин нечётной степени. Цикл: все степени чётные.",
                 "examples": [{"uid": "EX-PC-001", "title": "Эйлеров путь", "statement": "Граф: вершины A(2),B(3),C(3),D(2). Существует ли эйлеров путь?", "solution": "Нечётных вершин: 2 (B и C). Эйлеров путь существует (начало в B или C)."}]},
                {"uid": "MET-PC-HAMILTON", "title": "Гамильтоновы пути",
                 "description": "Гамильтонов путь проходит через каждую вершину ровно один раз. Нет простого критерия. Проверяйте перебором для малых графов.",
                 "examples": [{"uid": "EX-PC-002", "title": "Гамильтонов путь", "statement": "Полный граф K₄ (4 вершины, все соединены). Есть ли гамильтонов цикл?", "solution": "Да, например A→B→C→D→A. В полном графе Kₙ при n≥3 всегда существует гамильтонов цикл."}]},
                {"uid": "MET-PC-SHORTEST", "title": "Кратчайший путь в графе",
                 "description": "Для невзвешенного графа — обход в ширину (BFS). Для взвешенного — алгоритм Дейкстры. Длина = сумма весов рёбер.",
                 "examples": [{"uid": "EX-PC-003", "title": "Кратчайший путь", "statement": "Граф: A-B(3), A-C(1), C-B(1). Кратчайший путь A→B?", "solution": "Прямой: A→B = 3. Через C: A→C→B = 1+1 = 2. Кратчайший = 2."}]},
            ],
        }],
    },

    # 8. Рациональные неравенства
    {
        "topic_uid": "TOP-RATSIONALNYE-NERAVENSTVA-0c5460",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-RAT-INEQ-B10",
            "title": "Рациональные неравенства",
            "definition": "Неравенства вида P(x)/Q(x) > 0 (≥,<,≤). Решение методом интервалов.",
            "methods": [
                {"uid": "MET-RI-STANDARD", "title": "Приведение к стандартному виду",
                 "description": "Перенесите всё в одну сторону. Приведите к общему знаменателю: f(x)/g(x) ≷ 0.",
                 "examples": [{"uid": "EX-RI-001", "title": "Приведение", "statement": "1/(x−1) > 2.", "solution": "1/(x−1)−2 > 0 → (1−2(x−1))/(x−1) > 0 → (3−2x)/(x−1) > 0."}]},
                {"uid": "MET-RI-INTERVALS", "title": "Метод интервалов для рациональных неравенств",
                 "description": "1) Найдите нули числителя и знаменателя. 2) Отметьте на оси. 3) Определите знак на каждом промежутке. 4) Выберите нужные.",
                 "examples": [{"uid": "EX-RI-002", "title": "Метод интервалов", "statement": "(x−2)/(x+3) ≤ 0.", "solution": "Нули: x=2 (числитель), x=−3 (знаменатель). Знаки: (−∞,−3): +, (−3,2): −, (2,+∞): +. Ответ: (−3; 2]."}]},
                {"uid": "MET-RI-SPECIAL", "title": "Особые случаи рациональных неравенств",
                 "description": "Если ≥ 0: включаем нули числителя, исключаем нули знаменателя. Двойные неравенства: a < f(x)/g(x) < b.",
                 "examples": [{"uid": "EX-RI-003", "title": "Строгое/нестрогое", "statement": "(x²−4)/(x−3) ≥ 0.", "solution": "= (x−2)(x+2)/(x−3). Нули: −2, 2, 3. Знаки: +,−,+,+. Ответ: [−2; 2]∪(3; +∞)."}]},
            ],
        }],
    },

    # 9. Стереометрические задачи ЕГЭ
    {
        "topic_uid": "TOP-EGE-STEREOMETRIYA-ZADACHI-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-EGE-STEREO-B10",
            "title": "Стереометрические задачи ЕГЭ",
            "definition": "Задачи на расстояния, углы и сечения в пространственных фигурах.",
            "methods": [
                {"uid": "MET-ES-COORD", "title": "Координатный метод в стереометрии",
                 "description": "Введите систему координат. Задайте вершины координатами. Расстояние, угол, площадь — через формулы аналитической геометрии.",
                 "examples": [{"uid": "EX-ES-001", "title": "Координатный метод", "statement": "Куб ABCDA₁B₁C₁D₁, ребро 1. Расстояние от A до плоскости BC₁D?", "solution": "A(0,0,0), B(1,0,0), C₁(1,1,1), D(0,1,0). Уравнение плоскости BC₁D: x−z=0 (нормаль n=(1,0,−1)). d=|0−0|/√2=0... Пересчитаем: плоскость x+y−z=1. d=|0+0−0−1|/√3=1/√3."}]},
                {"uid": "MET-ES-DISTANCE", "title": "Нахождение расстояний в пространстве",
                 "description": "Между скрещивающимися прямыми: общий перпендикуляр. От точки до плоскости: длина перпендикуляра. Теорема о 3 перпендикулярах.",
                 "examples": [{"uid": "EX-ES-002", "title": "Расстояние до плоскости", "statement": "Правильная пирамида SABC, SA=SB=SC=5, AB=6. Высота пирамиды?", "solution": "Центр основания O — пересечение медиан. AO=6·√3/3=2√3. SO=√(25−12)=√13."}]},
                {"uid": "MET-ES-SECTION", "title": "Построение сечений многогранников",
                 "description": "Сечение строится по 3 точкам. Ищите пересечения с рёбрами и гранями. Используйте параллельность и принадлежность плоскостям.",
                 "examples": [{"uid": "EX-ES-003", "title": "Сечение куба", "statement": "Куб ABCDA₁B₁C₁D₁. Построить сечение через M∈AA₁, N∈BB₁, P∈DD₁.", "solution": "MN — на грани ABB₁A₁. MP — на грани ADD₁A₁. Продолжаем MN и MP до пересечения с другими гранями."}]},
            ],
        }],
    },

    # 10. Стереометрия: объёмы и площади
    {
        "topic_uid": "TOP-MATH-STEREOMETRY",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-STEREO-VOLAREA-B10",
            "title": "Стереометрия: объёмы и площади поверхностей",
            "definition": "Объёмы и площади поверхностей многогранников и тел вращения.",
            "methods": [
                {"uid": "MET-SVA-POLYHEDRA", "title": "Объёмы и площади многогранников",
                 "description": "Призма: V=Sh, S_бок=P·h. Пирамида: V=⅓Sh, S_бок=½P·l (правильная).",
                 "examples": [{"uid": "EX-SVA-001", "title": "Правильная пирамида", "statement": "Правильная 4-угольная пирамида, сторона основания 6, боковое ребро 5. V=?", "solution": "S_осн=36. Высота h=√(25−18)=√7. V=⅓·36·√7=12√7."}]},
                {"uid": "MET-SVA-ROTATION", "title": "Объёмы и площади тел вращения",
                 "description": "Цилиндр: V=πr²h, S_полн=2πr(r+h). Конус: V=⅓πr²h, S_бок=πrl. Шар: V=⁴⁄₃πr³, S=4πr².",
                 "examples": [{"uid": "EX-SVA-002", "title": "Полная поверхность конуса", "statement": "r=3, l=5. S_полн=?", "solution": "S_бок=π·3·5=15π. S_осн=9π. S_полн=24π."}]},
                {"uid": "MET-SVA-COMPOSITE", "title": "Составные тела и комбинации",
                 "description": "Цилиндр + конус, усечённый конус/пирамида. V_усеч = ⅓h(S₁+S₂+√(S₁S₂)).",
                 "examples": [{"uid": "EX-SVA-003", "title": "Усечённый конус", "statement": "Усечённый конус: R=5, r=3, h=4. V=?", "solution": "V=⅓·4·(25π+9π+15π)=⅓·4·49π=196π/3≈205.3."}]},
            ],
        }],
    },

    # 11. Стереометрия: расстояния и углы
    {
        "topic_uid": "TOP-MATH-STEREOMETRY-ADVANCED",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-STEREO-DIST-ANG-B10",
            "title": "Стереометрия: расстояния и углы",
            "definition": "Расстояния и углы между прямыми, прямыми и плоскостями, плоскостями. Сечения.",
            "methods": [
                {"uid": "MET-SDA-DIST", "title": "Расстояния в пространстве",
                 "description": "От точки до плоскости — перпендикуляр. Между скрещивающимися прямыми — общий перпендикуляр. Координатный метод: d=|Ax₀+By₀+Cz₀+D|/√(A²+B²+C²).",
                 "examples": [{"uid": "EX-SDA-001", "title": "Расстояние до плоскости", "statement": "Куб, ребро a. Расстояние от вершины до диагональной плоскости?", "solution": "Координатный метод. Расстояние от A(0,0,0) до плоскости x+y=a: d=a/√2."}]},
                {"uid": "MET-SDA-ANGLES", "title": "Углы в пространстве",
                 "description": "Между прямыми: через направляющие вектора. Между прямой и плоскостью: sin α = |cos(n,l)|. Двугранный угол: через перпендикуляры к ребру.",
                 "examples": [{"uid": "EX-SDA-002", "title": "Двугранный угол", "statement": "Правильная 3-угольная пирамида, ребро a. Двугранный угол при основании?", "solution": "Основание — равносторонний △. Центр O. Высота SO. tg α = SO/OM, где M — середина стороны."}]},
                {"uid": "MET-SDA-SECTION", "title": "Построение сечения по трём точкам",
                 "description": "1) Соедините точки, лежащие в одной грани. 2) Найдите пересечение с другими гранями. 3) Используйте параллельность и принадлежность.",
                 "examples": [{"uid": "EX-SDA-003", "title": "Сечение тетраэдра", "statement": "Тетраэдр ABCD. Точки M∈AB, N∈BC, P∈CD. Постройте сечение MNP.", "solution": "MN — в грани ABC. NP — в грани BCD. Продолжим MN и NP: найдём пересечение с AD и AC для завершения сечения."}]},
            ],
        }],
    },

    # 12. Точка и прямая
    {
        "topic_uid": "TOP-TOCHKA-I-PRYAMAYA-291b4a",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-POINT-LINE-B10",
            "title": "Точка и прямая на плоскости",
            "definition": "Основные геометрические понятия: точка, прямая, луч, отрезок. Аксиомы планиметрии.",
            "methods": [
                {"uid": "MET-PL-BASIC", "title": "Основные понятия и обозначения",
                 "description": "Точка — A,B,C. Прямая — через 2 точки (AB). Луч — полупрямая от начала. Отрезок — часть прямой между двумя точками.",
                 "examples": [{"uid": "EX-PL-001", "title": "Основные понятия", "statement": "На прямой отмечены точки A,B,C. AB=5, BC=3. Найдите AC.", "solution": "Если B между A и C: AC=AB+BC=5+3=8. Если C между A и B: AC=AB−BC=2."}]},
                {"uid": "MET-PL-MIDPOINT", "title": "Середина отрезка и деление в отношении",
                 "description": "Середина M: AM=MB=AB/2. Деление в отношении m:n: координаты M = (nx₁+mx₂)/(m+n).",
                 "examples": [{"uid": "EX-PL-002", "title": "Середина отрезка", "statement": "A(2,3), B(8,7). Координаты середины M?", "solution": "M=((2+8)/2, (3+7)/2) = (5, 5)."}]},
                {"uid": "MET-PL-DISTANCE", "title": "Расстояние между точками",
                 "description": "d = √((x₂−x₁)²+(y₂−y₁)²). На прямой: |AB| = |x_B − x_A|.",
                 "examples": [{"uid": "EX-PL-003", "title": "Расстояние", "statement": "A(1,2), B(4,6). AB=?", "solution": "AB=√((4−1)²+(6−2)²)=√(9+16)=√25=5."}]},
            ],
        }],
    },

    # 13. Уравнения, системы уравнений и неравенства
    {
        "topic_uid": "TOP-MATH-EQUATIONS-SYSTEMS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-EQ-SYS-B10",
            "title": "Уравнения и системы уравнений",
            "definition": "Линейные, квадратные уравнения, системы, методы решения.",
            "methods": [
                {"uid": "MET-EQS-LINEAR", "title": "Линейные уравнения и системы",
                 "description": "ax+b=0 → x=−b/a. Система: метод подстановки, сложения, графический. Определитель: Δ=a₁b₂−a₂b₁.",
                 "examples": [{"uid": "EX-EQS-001", "title": "Система линейных", "statement": "2x+y=7, x−y=2. Решите.", "solution": "Сложим: 3x=9 → x=3. y=7−2·3=1. Ответ: (3;1)."}]},
                {"uid": "MET-EQS-QUADRATIC", "title": "Квадратные уравнения",
                 "description": "ax²+bx+c=0. D=b²−4ac. x=(−b±√D)/(2a). Теорема Виета: x₁+x₂=−b/a, x₁·x₂=c/a.",
                 "examples": [{"uid": "EX-EQS-002", "title": "Квадратное уравнение", "statement": "x²−5x+6=0.", "solution": "D=25−24=1. x=(5±1)/2. x₁=3, x₂=2."}]},
                {"uid": "MET-EQS-NONLINEAR", "title": "Системы нелинейных уравнений и неравенств",
                 "description": "Метод подстановки: выразите одну переменную из одного уравнения, подставьте в другое. Графический метод: пересечение кривых.",
                 "examples": [{"uid": "EX-EQS-003", "title": "Нелинейная система", "statement": "x+y=5, xy=6. Решите.", "solution": "y=5−x. x(5−x)=6 → x²−5x+6=0. x=2,y=3 или x=3,y=2."}]},
            ],
        }],
    },

    # 14. Финансово-экономические расчёты
    {
        "topic_uid": "TOP-MATH-FINANCIAL-ADVANCED",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-FINANCE-B10",
            "title": "Финансово-экономические расчёты",
            "definition": "Процентные ставки, кредиты, вклады, аннуитеты, экономические модели.",
            "methods": [
                {"uid": "MET-FIN-COMPOUND", "title": "Сложные проценты и вклады",
                 "description": "S=P(1+r)ⁿ (наращение). P=S/(1+r)ⁿ (дисконтирование). r — ставка за период, n — число периодов.",
                 "examples": [{"uid": "EX-FIN-001", "title": "Вклад", "statement": "100 000 руб. под 10% годовых на 3 года. Итог?", "solution": "S=100000·1.1³=100000·1.331=133100 руб."}]},
                {"uid": "MET-FIN-ANNUITY", "title": "Аннуитетные и дифференцированные платежи",
                 "description": "Аннуитет: a=S·r(1+r)ⁿ/((1+r)ⁿ−1). Дифференцированный: убывающие платежи, основной долг делится поровну.",
                 "examples": [{"uid": "EX-FIN-002", "title": "Кредит", "statement": "Кредит 600 000 на 3 года, r=10%. Ежегодный аннуитетный платёж?", "solution": "a=600000·0.1·1.1³/(1.1³−1)=600000·0.1331/0.331≈241296 руб."}]},
                {"uid": "MET-FIN-COMPARE", "title": "Сравнение финансовых стратегий",
                 "description": "Сравните итоговые переплаты по разным схемам. Определите выгодность вложений через NPV или полную сумму выплат.",
                 "examples": [{"uid": "EX-FIN-003", "title": "Сравнение схем", "statement": "Кредит 100 000, 2 года, 20%. Сравните аннуитет и дифф. платежи.", "solution": "Аннуитет: переплата ≈ 2·65455−100000=30910. Дифф: переплата = 20000+10000=30000. Дифф. выгоднее."}]},
            ],
        }],
    },

    # 15. Формула Байеса
    {
        "topic_uid": "TOP-FORMULA-BAJESA-9e1a3f",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-BAYES-B10",
            "title": "Формула Байеса",
            "definition": "P(Hᵢ|A) = P(A|Hᵢ)·P(Hᵢ) / ΣP(A|Hⱼ)·P(Hⱼ). Пересчёт вероятностей гипотез после наблюдения события.",
            "methods": [
                {"uid": "MET-BAY-FORMULA", "title": "Формула полной вероятности",
                 "description": "P(A) = Σ P(A|Hᵢ)·P(Hᵢ) — сумма по всем гипотезам. Гипотезы: полная группа несовместных событий.",
                 "examples": [{"uid": "EX-BAY-001", "title": "Полная вероятность", "statement": "3 цеха: P(H₁)=0.3, P(H₂)=0.5, P(H₃)=0.2. Брак: P(A|H₁)=0.02, P(A|H₂)=0.01, P(A|H₃)=0.03. P(A)?", "solution": "P(A)=0.3·0.02+0.5·0.01+0.2·0.03=0.006+0.005+0.006=0.017."}]},
                {"uid": "MET-BAY-BAYES", "title": "Формула Байеса (апостериорная вероятность)",
                 "description": "P(Hᵢ|A) = P(A|Hᵢ)·P(Hᵢ)/P(A). Пересчитывает вероятность гипотезы после получения данных.",
                 "examples": [{"uid": "EX-BAY-002", "title": "Формула Байеса", "statement": "Из предыдущей задачи: деталь бракованная. Какой цех?", "solution": "P(H₁|A)=0.006/0.017≈0.353. P(H₂|A)=0.005/0.017≈0.294. P(H₃|A)=0.006/0.017≈0.353."}]},
                {"uid": "MET-BAY-APPLY", "title": "Применение формулы Байеса",
                 "description": "Медицинские тесты: P(болезнь|+тест). Спам-фильтры. Классификация. Важно учитывать априорные вероятности.",
                 "examples": [{"uid": "EX-BAY-003", "title": "Медицинский тест", "statement": "P(болезнь)=0.01. Чувствительность=0.99, специфичность=0.95. Тест +. P(болезнь)?", "solution": "P(+)=0.01·0.99+0.99·0.05=0.0099+0.0495=0.0594. P(бол|+)=0.0099/0.0594≈0.167=16.7%."}]},
            ],
        }],
    },

    # 16. Функции, их свойства и графики
    {
        "topic_uid": "TOP-MATH-FUNCTIONS-GRAPHS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-FUNCTIONS-GRAPHS-B10",
            "title": "Функции и их графики",
            "definition": "Понятие функции, область определения, область значений, основные свойства и графики.",
            "methods": [
                {"uid": "MET-FG-DOMAIN", "title": "Область определения и область значений",
                 "description": "D(f) — все допустимые x. E(f) — все возможные значения y. Ограничения: знаменатель≠0, подкоренное≥0, аргумент логарифма>0.",
                 "examples": [{"uid": "EX-FG-001", "title": "Область определения", "statement": "y=√(4−x²). D(f)=?", "solution": "4−x²≥0 → x²≤4 → −2≤x≤2. D(f)=[−2;2]."}]},
                {"uid": "MET-FG-TRANSFORM", "title": "Преобразования графиков функций",
                 "description": "y=f(x)+a — сдвиг вверх. y=f(x−b) — сдвиг вправо. y=kf(x) — растяжение. y=f(−x) — отражение от Oy.",
                 "examples": [{"uid": "EX-FG-002", "title": "Преобразование", "statement": "Из y=x² получите y=(x−3)²+2.", "solution": "Сдвиг вправо на 3, вверх на 2. Вершина параболы: (3;2)."}]},
                {"uid": "MET-FG-PROPERTIES", "title": "Исследование свойств функции",
                 "description": "Чётность: f(−x)=f(x). Нечётность: f(−x)=−f(x). Монотонность, экстремумы, периодичность.",
                 "examples": [{"uid": "EX-FG-003", "title": "Чётность", "statement": "f(x)=x³−x. Чётная или нечётная?", "solution": "f(−x)=(−x)³−(−x)=−x³+x=−(x³−x)=−f(x). Нечётная."}]},
            ],
        }],
    },

    # 17. Функции: задачи повышенного уровня
    {
        "topic_uid": "TOP-MATH-ADVANCED-FUNCTIONS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ADV-FUNC-B10",
            "title": "Функции повышенного уровня",
            "definition": "Сложные задачи: обратные функции, композиции, параметрические задачи, графический анализ.",
            "methods": [
                {"uid": "MET-AF-INVERSE", "title": "Обратная функция",
                 "description": "y=f(x) → x=f⁻¹(y). Графики f и f⁻¹ симметричны относительно y=x. Существует при строгой монотонности.",
                 "examples": [{"uid": "EX-AF-001", "title": "Обратная функция", "statement": "f(x)=2x+3. Найдите f⁻¹(x).", "solution": "y=2x+3 → x=(y−3)/2. f⁻¹(x)=(x−3)/2."}]},
                {"uid": "MET-AF-COMPOSITION", "title": "Композиция функций",
                 "description": "(f∘g)(x)=f(g(x)). Подставьте g(x) вместо x в формулу f. D(f∘g): x∈D(g) и g(x)∈D(f).",
                 "examples": [{"uid": "EX-AF-002", "title": "Композиция", "statement": "f(x)=x², g(x)=x+1. (f∘g)(3)=?", "solution": "(f∘g)(3)=f(g(3))=f(4)=16."}]},
                {"uid": "MET-AF-GRAPHIC", "title": "Графическое решение уравнений",
                 "description": "f(x)=g(x) ⟺ пересечение графиков y=f(x) и y=g(x). Число решений = число точек пересечения.",
                 "examples": [{"uid": "EX-AF-003", "title": "Графическое решение", "statement": "Сколько решений у x²=2ˣ?", "solution": "Графики y=x² и y=2ˣ пересекаются в 3 точках (при x<0, x≈1 и x≈4). Значит 3 решения (проверка графически)."}]},
            ],
        }],
    },

    # 18. Числа и практические вычисления
    {
        "topic_uid": "TOP-MATH-NUMBERS-CALCULATIONS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-NUMBERS-CALC-B10",
            "title": "Числа и практические вычисления",
            "definition": "Числовые множества, округление, проценты, пропорции, единицы измерения.",
            "methods": [
                {"uid": "MET-NC-SETS", "title": "Числовые множества и операции",
                 "description": "ℕ⊂ℤ⊂ℚ⊂ℝ. Натуральные, целые, рациональные, действительные числа. Модуль, знак, округление.",
                 "examples": [{"uid": "EX-NC-001", "title": "Числовые множества", "statement": "Классифицируйте: 0, −3, ½, √2, π.", "solution": "0∈ℤ, −3∈ℤ, ½∈ℚ, √2∈ℝ\\ℚ (иррациональное), π∈ℝ\\ℚ."}]},
                {"uid": "MET-NC-PERCENT", "title": "Проценты и пропорции",
                 "description": "a% от b = ab/100. Пропорция: a/b=c/d → ad=bc. Процентное изменение: (новое−старое)/старое·100%.",
                 "examples": [{"uid": "EX-NC-002", "title": "Процентное изменение", "statement": "Цена выросла с 200 до 250. На сколько %?", "solution": "(250−200)/200·100% = 25%."}]},
                {"uid": "MET-NC-ROUND", "title": "Округление и оценка",
                 "description": "Округление до разряда: если следующая цифра ≥5 — округляем вверх. Значащие цифры. Погрешность.",
                 "examples": [{"uid": "EX-NC-003", "title": "Округление", "statement": "Округлите 3.1415926 до сотых.", "solution": "3.14 (третья цифра после запятой = 1 < 5, округляем вниз)."}]},
            ],
        }],
    },

    # 19. Эквивалентность и порядок
    {
        "topic_uid": "TOP-EKVIVALENTNOST-I-PORYADOK-a24b0a",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-EQUIV-ORDER-B10",
            "title": "Эквивалентность и порядок",
            "definition": "Отношения эквивалентности (рефлексивность, симметричность, транзитивность) и отношения порядка (частичный и линейный).",
            "methods": [
                {"uid": "MET-EO-EQUIV", "title": "Отношение эквивалентности",
                 "description": "Рефлексивно: aRa. Симметрично: aRb → bRa. Транзитивно: aRb и bRc → aRc. Разбивает множество на классы эквивалентности.",
                 "examples": [{"uid": "EX-EO-001", "title": "Классы эквивалентности", "statement": "Сравнимость по модулю 3. Какие классы?", "solution": "[0]={…,−3,0,3,6,…}, [1]={…,−2,1,4,7,…}, [2]={…,−1,2,5,8,…}. Три класса."}]},
                {"uid": "MET-EO-ORDER", "title": "Отношение порядка",
                 "description": "Частичный порядок: рефлексивный, антисимметричный, транзитивный. Линейный: любые два элемента сравнимы. Примеры: ≤ на числах, ⊆ на множествах.",
                 "examples": [{"uid": "EX-EO-002", "title": "Частичный порядок", "statement": "Множества {1},{2},{1,2}. Отношение ⊆. Линейный ли порядок?", "solution": "{1}⊄{2} и {2}⊄{1} — не сравнимы. Порядок частичный, не линейный."}]},
                {"uid": "MET-EO-COMPARE", "title": "Сравнение и упорядочивание чисел",
                 "description": "Сравнение дробей: приведите к общему знаменателю. Сравнение корней: возведите в степень. Числовая прямая.",
                 "examples": [{"uid": "EX-EO-003", "title": "Сравнение дробей", "statement": "Что больше: 3/7 или 5/12?", "solution": "3/7=36/84, 5/12=35/84. 36/84 > 35/84. Значит 3/7 > 5/12."}]},
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
    print(f"\n{'='*60}\nBatch 10 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
