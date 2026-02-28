#!/usr/bin/env python3
"""Batch 12: Fix 15 more FEW_METHODS topics."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 1. Основы теории вероятностей (2 → 3)
    {
        "topic_uid": "TOP-OSNOVY-TEORII-VEROYATNOS-c8e176",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PROB-BASICS-B12",
            "title": "Основы теории вероятностей",
            "definition": "Случайные события, пространство элементарных исходов, классическое определение вероятности.",
            "methods": [
                {"uid": "MET-PB-CLASSIC", "title": "Классическое определение вероятности",
                 "description": "P(A)=m/n — отношение числа благоприятных исходов к общему числу равновозможных исходов.",
                 "examples": [{"uid": "EX-PB-001", "title": "Классическая вероятность", "statement": "Из урны с 3 белыми и 7 чёрными шарами достают 1. P(белый)?", "solution": "P=3/10=0.3."}]},
                {"uid": "MET-PB-ADDITION", "title": "Теоремы сложения и умножения",
                 "description": "P(A∪B)=P(A)+P(B)−P(A∩B). Для несовместных: P(A∪B)=P(A)+P(B). Для независимых: P(A∩B)=P(A)·P(B).",
                 "examples": [{"uid": "EX-PB-002", "title": "Несовместные события", "statement": "P(красный)=0.3, P(синий)=0.5. P(красный или синий)?", "solution": "События несовместны: P=0.3+0.5=0.8."}]},
                {"uid": "MET-PB-OPPOSITE", "title": "Вероятность противоположного события",
                 "description": "P(Ā)=1−P(A). Часто проще вычислить P(Ā) и вычесть из 1.",
                 "examples": [{"uid": "EX-PB-003", "title": "Противоположное", "statement": "P(дождь)=0.7. P(нет дождя)?", "solution": "P(нет дождя)=1−0.7=0.3."}]},
            ],
        }],
    },

    # 2. Отношения (2 → 3)
    {
        "topic_uid": "TOP-OTNOSHENIYA-142ca8",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-RELATIONS-B12",
            "title": "Отношения",
            "definition": "Математические отношения: бинарные, свойства (рефлексивность, симметричность, транзитивность).",
            "methods": [
                {"uid": "MET-REL-BINARY", "title": "Бинарные отношения",
                 "description": "Отношение R на множестве A — подмножество A×A. Запись: aRb означает (a,b)∈R. Представление: матрица, граф.",
                 "examples": [{"uid": "EX-REL-001", "title": "Бинарное отношение", "statement": "A={1,2,3}. R: «делит». Перечислите пары.", "solution": "R={(1,1),(1,2),(1,3),(2,2),(3,3)} — 1 делит всех, остальные делят себя."}]},
                {"uid": "MET-REL-PROPS", "title": "Свойства отношений",
                 "description": "Рефлексивность: aRa ∀a. Симметричность: aRb→bRa. Антисимметричность: aRb и bRa→a=b. Транзитивность: aRb,bRc→aRc.",
                 "examples": [{"uid": "EX-REL-002", "title": "Свойства", "statement": "Отношение ≤ на ℤ. Какие свойства?", "solution": "Рефлексивно (a≤a ✓). Антисимметрично (a≤b,b≤a→a=b ✓). Транзитивно (a≤b,b≤c→a≤c ✓). Не симметрично."}]},
                {"uid": "MET-REL-EQUIV", "title": "Отношения эквивалентности и порядка",
                 "description": "Эквивалентность: рефл.+симм.+транз. → классы эквивалентности. Порядок: рефл.+антисимм.+транз.",
                 "examples": [{"uid": "EX-REL-003", "title": "Классы", "statement": "Сравнимость по mod 2. Какие классы?", "solution": "Два класса: [0]={чётные}, [1]={нечётные}."}]},
            ],
        }],
    },

    # 3. Планиметрия: доказательство и вычисление (2 → 3)
    {
        "topic_uid": "TOP-MATH-ADVANCED-PLANE-GEOM-PROOF",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PLANIM-PROOF-B12",
            "title": "Планиметрия: доказательство и вычисление",
            "definition": "Сложные задачи планиметрии с доказательством: подобие, площади, окружности.",
            "methods": [
                {"uid": "MET-PP-SIMILAR-PROOF", "title": "Доказательство подобия и равенства",
                 "description": "Подобие: по двум углам. Равенство: SAS, ASA, SSS. Пропорциональность сторон → подобие.",
                 "examples": [{"uid": "EX-PP-001", "title": "Доказательство подобия", "statement": "△ABC: ∠A=∠D. DE∥BC. Докажите △ADE∼△ABC.", "solution": "∠A общий, ∠ADE=∠ABC (соответственные при DE∥BC). По двум углам △ADE∼△ABC."}]},
                {"uid": "MET-PP-AREA-METHOD", "title": "Метод площадей в доказательствах",
                 "description": "Выразите площадь двумя способами. S(△)=½ah=½ab·sin C. Равные площади → равные основания или высоты.",
                 "examples": [{"uid": "EX-PP-002", "title": "Метод площадей", "statement": "Медиана AM делит △ABC на два равных по площади △. Докажите.", "solution": "S(ABM)=½·BM·h, S(ACM)=½·CM·h. BM=CM (M — середина) → S(ABM)=S(ACM)."}]},
                {"uid": "MET-PP-INSCRIBED-CIRCLE", "title": "Задачи с вписанной и описанной окружностями",
                 "description": "r=S/p (вписанная). R=abc/(4S). Касательные из точки равны. Вписанный угол = ½ дуги.",
                 "examples": [{"uid": "EX-PP-003", "title": "Вписанная окружность", "statement": "△: стороны 5,12,13. r=?", "solution": "p=(5+12+13)/2=15. S=½·5·12=30. r=30/15=2."}]},
            ],
        }],
    },

    # 4. Подобие (2 → 3)
    {
        "topic_uid": "TOP-PODOBIE-86fb4a",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-SIMILARITY-B12",
            "title": "Подобие фигур",
            "definition": "Подобные фигуры — одинаковая форма, разные размеры. Коэффициент подобия k, связь сторон, площадей, объёмов.",
            "methods": [
                {"uid": "MET-SIM-CRITERIA", "title": "Признаки подобия треугольников",
                 "description": "1) По двум углам (AA). 2) По двум сторонам и углу между ними (SAS). 3) По трём сторонам (SSS): пропорциональность.",
                 "examples": [{"uid": "EX-SIM-001", "title": "Признак AA", "statement": "△ABC: ∠A=40°, ∠B=70°. △DEF: ∠D=40°, ∠E=70°. Подобны?", "solution": "Два соответственных угла равны → △ABC∼△DEF (по первому признаку)."}]},
                {"uid": "MET-SIM-RATIO", "title": "Коэффициент подобия и пропорции",
                 "description": "k=a'/a — отношение сходственных сторон. Все сходственные стороны в одном отношении. S'/S=k². V'/V=k³.",
                 "examples": [{"uid": "EX-SIM-002", "title": "Площади подобных", "statement": "△ABC∼△DEF, k=3. S(ABC)=10. S(DEF)=?", "solution": "S(DEF)=10·3²=90."}]},
                {"uid": "MET-SIM-APPLY", "title": "Применение подобия в задачах",
                 "description": "Средняя линия △ параллельна стороне и равна её половине. Высота, медиана, биссектриса в подобных △ тоже пропорциональны.",
                 "examples": [{"uid": "EX-SIM-003", "title": "Средняя линия", "statement": "△ABC, MN — средняя линия (M∈AB, N∈AC). BC=14. MN=?", "solution": "MN=BC/2=7 (средняя линия параллельна и равна половине)."}]},
            ],
        }],
    },

    # 5. Показательные и логарифмические функции (2 → 3)
    {
        "topic_uid": "TOP-MATH-EXP-LOG",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-EXP-LOG-B12",
            "title": "Показательные и логарифмические функции",
            "definition": "Показательная: y=aˣ. Логарифмическая: y=log_a(x). Взаимно обратные функции.",
            "methods": [
                {"uid": "MET-EL-EXP", "title": "Показательная функция и уравнения",
                 "description": "y=aˣ (a>0, a≠1). При a>1 возрастает, при 0<a<1 убывает. aˣ=aʸ ⟺ x=y.",
                 "examples": [{"uid": "EX-EL-001", "title": "Показательное уравнение", "statement": "2ˣ⁺¹=32.", "solution": "32=2⁵. 2ˣ⁺¹=2⁵ → x+1=5 → x=4."}]},
                {"uid": "MET-EL-LOG", "title": "Логарифмическая функция и свойства",
                 "description": "log_a(b)=c ⟺ aᶜ=b. Свойства: log(xy)=log x+log y, log(x/y)=log x−log y, log(xⁿ)=n·log x.",
                 "examples": [{"uid": "EX-EL-002", "title": "Логарифмическое уравнение", "statement": "log₃(x−1)=2.", "solution": "x−1=3²=9 → x=10."}]},
                {"uid": "MET-EL-CHANGE-BASE", "title": "Формула перехода к другому основанию",
                 "description": "log_a(b)=log_c(b)/log_c(a). Часто c=10 или c=e. log_a(b)·log_b(a)=1.",
                 "examples": [{"uid": "EX-EL-003", "title": "Переход к основанию", "statement": "log₄(8)=?", "solution": "log₄(8)=log₂(8)/log₂(4)=3/2."}]},
            ],
        }],
    },

    # 6. Практико-ориентированные задачи ОГЭ (1 → 3)
    {
        "topic_uid": "TOP-OGE-PRAKTIKO-ORIENTIROVANNYE-ZADACHI-2026",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PRACTICAL-OGE-B12",
            "title": "Практико-ориентированные задачи",
            "definition": "Задачи на реальные ситуации: планы, карты, расчёты, графики, таблицы.",
            "methods": [
                {"uid": "MET-PO-PLANS", "title": "Чтение планов и карт",
                 "description": "Масштаб 1:N означает 1 см = N см в реальности. Площадь на плане × N² = площадь в реальности.",
                 "examples": [{"uid": "EX-PO-001", "title": "Масштаб плана", "statement": "Масштаб 1:200. Комната на плане 3×4 см. Реальные размеры?", "solution": "3·200=600 см=6 м, 4·200=800 см=8 м. Комната 6×8 м."}]},
                {"uid": "MET-PO-TARIFF", "title": "Расчёт тарифов и стоимости",
                 "description": "Определите тариф/цену из условия. Вычислите итоговую стоимость с учётом скидок, наценок, количества.",
                 "examples": [{"uid": "EX-PO-002", "title": "Тариф", "statement": "Электроэнергия: до 100 кВт·ч — 4 руб/кВт·ч, сверх 100 — 5 руб. Потребление 150 кВт·ч. Стоимость?", "solution": "100·4+50·5=400+250=650 руб."}]},
                {"uid": "MET-PO-GRAPH-REAL", "title": "Интерпретация графиков реальных процессов",
                 "description": "По графику определите: значение в точке, максимум/минимум, скорость изменения (наклон), промежутки роста/убывания.",
                 "examples": [{"uid": "EX-PO-003", "title": "График температуры", "statement": "Температура: 6ч=−5°, 14ч=+8°, 22ч=+2°. Когда была 0°?", "solution": "Между 6ч и 14ч (рост от −5 до +8). Линейно: 0°= примерно в 9:45."}]},
            ],
        }],
    },

    # 7. Производная и интеграл (2 → 3)
    {
        "topic_uid": "TOP-MATH-CALCULUS",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-CALCULUS-B12",
            "title": "Производная и интеграл",
            "definition": "Дифференциальное и интегральное исчисление. Связь производной и интеграла (формула Ньютона-Лейбница).",
            "methods": [
                {"uid": "MET-CALC-DIFF", "title": "Дифференцирование функций",
                 "description": "Производная: предел отношения приращения функции к приращению аргумента. Табличные производные и правила.",
                 "examples": [{"uid": "EX-CALC-001", "title": "Производная", "statement": "y=3x⁴−2x²+x−7. y'=?", "solution": "y'=12x³−4x+1."}]},
                {"uid": "MET-CALC-INTEGRAL", "title": "Определённый интеграл",
                 "description": "∫ₐᵇf(x)dx = F(b)−F(a) (формула Ньютона-Лейбница). Геометрический смысл: площадь под кривой.",
                 "examples": [{"uid": "EX-CALC-002", "title": "Определённый интеграл", "statement": "∫₀²(x²+1)dx=?", "solution": "F(x)=x³/3+x. F(2)−F(0)=8/3+2−0=14/3≈4.67."}]},
                {"uid": "MET-CALC-AREA", "title": "Площадь фигуры через интеграл",
                 "description": "S=∫ₐᵇ|f(x)−g(x)|dx — площадь между кривыми. Найдите точки пересечения → пределы интегрирования.",
                 "examples": [{"uid": "EX-CALC-003", "title": "Площадь", "statement": "Площадь между y=x² и y=x на [0,1]?", "solution": "S=∫₀¹(x−x²)dx=[x²/2−x³/3]₀¹=1/2−1/3=1/6."}]},
            ],
        }],
    },

    # 8. Производная: оптимизация (2 → 3)
    {
        "topic_uid": "TOP-MATH-OPTIMIZATION",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-OPTIMIZATION-B12",
            "title": "Производная: оптимизация",
            "definition": "Нахождение наибольшего и наименьшего значений функции с помощью производной.",
            "methods": [
                {"uid": "MET-OPT-EXTREMA", "title": "Нахождение экстремумов функции",
                 "description": "f'(x)=0 → критические точки. f''(x₀)>0 → минимум, f''(x₀)<0 → максимум. Или: знак f' меняется.",
                 "examples": [{"uid": "EX-OPT-001", "title": "Экстремумы", "statement": "f(x)=x³−3x. Найдите экстремумы.", "solution": "f'=3x²−3=0 → x=±1. f''=6x. f''(1)=6>0 (min), f''(−1)=−6<0 (max). min=f(1)=−2, max=f(−1)=2."}]},
                {"uid": "MET-OPT-MINMAX-SEGMENT", "title": "Наибольшее и наименьшее на отрезке",
                 "description": "1) Найдите критические точки на [a,b]. 2) Вычислите f в этих точках и на концах. 3) Сравните.",
                 "examples": [{"uid": "EX-OPT-002", "title": "На отрезке", "statement": "f(x)=x³−3x на [−2;2]. min и max?", "solution": "f'=3x²−3=0→x=±1. f(−2)=−2, f(−1)=2, f(1)=−2, f(2)=2. max=2, min=−2."}]},
                {"uid": "MET-OPT-APPLIED", "title": "Прикладные задачи на оптимизацию",
                 "description": "Составьте функцию от одной переменной. Найдите экстремум. Проверьте, что это действительно максимум/минимум.",
                 "examples": [{"uid": "EX-OPT-003", "title": "Задача оптимизации", "statement": "Из квадратного листа 12×12 вырезают углы и делают коробку. Максимальный объём?", "solution": "V=x(12−2x)²=4x³−48x²+144x. V'=12x²−96x+144=0→x=2 или x=6. x=2: V=2·64=128 (max). x=6: V=0."}]},
            ],
        }],
    },

    # 9. Радианная мера (2 → 3)
    {
        "topic_uid": "TOP-RADIANNAYA-MERA-51263f",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-RADIAN-B12",
            "title": "Радианная мера угла",
            "definition": "Радиан — угол, опирающийся на дугу длиной r. Полный оборот = 2π рад = 360°.",
            "methods": [
                {"uid": "MET-RAD-CONVERT", "title": "Перевод градусов в радианы и обратно",
                 "description": "α(рад)=α°·π/180. α°=α(рад)·180/π. Ключевые: 30°=π/6, 45°=π/4, 60°=π/3, 90°=π/2.",
                 "examples": [{"uid": "EX-RAD-001", "title": "Перевод", "statement": "Переведите 150° в радианы.", "solution": "150·π/180=5π/6."}]},
                {"uid": "MET-RAD-TRIG", "title": "Тригонометрические функции в радианах",
                 "description": "sin(π/6)=1/2, cos(π/3)=1/2, tg(π/4)=1. Графики: период sin/cos = 2π, tg = π.",
                 "examples": [{"uid": "EX-RAD-002", "title": "Тригонометрия", "statement": "Вычислите sin(5π/6).", "solution": "5π/6 = π−π/6. sin(π−α)=sin α. sin(5π/6)=sin(π/6)=1/2."}]},
                {"uid": "MET-RAD-ARC", "title": "Длина дуги и площадь сектора в радианах",
                 "description": "Длина дуги: l=rα (α в радианах). Площадь сектора: S=½r²α.",
                 "examples": [{"uid": "EX-RAD-003", "title": "Длина дуги", "statement": "r=10, α=π/3. Длина дуги?", "solution": "l=10·π/3=10π/3≈10.47."}]},
            ],
        }],
    },

    # 10. Распределение вероятностей (2 → 3)
    {
        "topic_uid": "TOP-RASPREDELENIE-VEROYATNOS-4c5863",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-PROB-DISTR-B12",
            "title": "Распределение вероятностей",
            "definition": "Закон распределения случайной величины. Функция распределения и плотность.",
            "methods": [
                {"uid": "MET-PD-TABLE", "title": "Таблица распределения дискретной СВ",
                 "description": "Перечислите все значения xᵢ и их вероятности pᵢ. Σpᵢ=1. E(X)=Σxᵢpᵢ.",
                 "examples": [{"uid": "EX-PD-001", "title": "Таблица распределения", "statement": "X — число орлов при 2 бросках монеты. Составьте распределение.", "solution": "X=0: P=1/4. X=1: P=2/4=1/2. X=2: P=1/4. Проверка: 1/4+1/2+1/4=1 ✓."}]},
                {"uid": "MET-PD-CDF", "title": "Функция распределения F(x)",
                 "description": "F(x)=P(X≤x). Неубывающая: 0≤F(x)≤1. F(−∞)=0, F(+∞)=1. P(a<X≤b)=F(b)−F(a).",
                 "examples": [{"uid": "EX-PD-002", "title": "Функция распределения", "statement": "F(x)=0 при x<0, x² при 0≤x≤1, 1 при x>1. P(0.5<X≤0.8)?", "solution": "P=F(0.8)−F(0.5)=0.64−0.25=0.39."}]},
                {"uid": "MET-PD-EXPECT-VAR", "title": "Математическое ожидание и дисперсия",
                 "description": "E(X)=Σxᵢpᵢ (среднее). D(X)=E(X²)−[E(X)]². σ=√D — стандартное отклонение.",
                 "examples": [{"uid": "EX-PD-003", "title": "E и D", "statement": "X: 1(p=0.2), 2(p=0.5), 3(p=0.3). E(X), D(X)?", "solution": "E(X)=1·0.2+2·0.5+3·0.3=2.1. E(X²)=1·0.2+4·0.5+9·0.3=4.9. D=4.9−4.41=0.49."}]},
            ],
        }],
    },

    # 11. Случайные величины (2 → 3)
    {
        "topic_uid": "TOP-SLUCHAINYE-VELICHINY-90d9e2",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-RANDOM-VARS-B12",
            "title": "Случайные величины",
            "definition": "Случайная величина — числовая функция на пространстве элементарных исходов. Дискретные и непрерывные.",
            "methods": [
                {"uid": "MET-RV-DISCRETE", "title": "Дискретные случайные величины",
                 "description": "Принимают счётное число значений. Задаются таблицей (ряд распределения). Σpᵢ=1.",
                 "examples": [{"uid": "EX-RV-001", "title": "Дискретная СВ", "statement": "Число очков при бросании кубика — дискретная СВ. P(X=k)=?", "solution": "P(X=k)=1/6 для k=1,2,3,4,5,6. Равномерное распределение."}]},
                {"uid": "MET-RV-CONTINUOUS", "title": "Непрерывные случайные величины",
                 "description": "Задаются плотностью f(x)≥0. P(a<X<b)=∫ₐᵇf(x)dx. ∫f(x)dx=1.",
                 "examples": [{"uid": "EX-RV-002", "title": "Непрерывная СВ", "statement": "f(x)=2x при x∈[0,1], 0 иначе. P(0.5<X<1)?", "solution": "P=∫₀.₅¹ 2x dx=[x²]₀.₅¹=1−0.25=0.75."}]},
                {"uid": "MET-RV-TRANSFORM", "title": "Функция от случайной величины",
                 "description": "Y=g(X): E(Y)=E(g(X))=Σg(xᵢ)pᵢ. Если Y=aX+b: E(Y)=aE(X)+b, D(Y)=a²D(X).",
                 "examples": [{"uid": "EX-RV-003", "title": "Линейное преобразование", "statement": "E(X)=5, D(X)=4. Y=3X−2. E(Y), D(Y)?", "solution": "E(Y)=3·5−2=13. D(Y)=9·4=36."}]},
            ],
        }],
    },

    # 12. События и их классификация (2 → 3)
    {
        "topic_uid": "TOP-SOBYTIYA-I-IH-KLASSIFIKA-97f448",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-EVENTS-B12",
            "title": "События и их классификация",
            "definition": "Случайное, достоверное, невозможное событие. Совместные/несовместные. Зависимые/независимые.",
            "methods": [
                {"uid": "MET-EV-TYPES", "title": "Типы событий",
                 "description": "Достоверное: P=1. Невозможное: P=0. Случайное: 0<P<1. Элементарное: неразложимо на более простые.",
                 "examples": [{"uid": "EX-EV-001", "title": "Классификация", "statement": "Бросок кубика. A — «выпадет 7». B — «выпадет число <7». Классифицируйте.", "solution": "A — невозможное (P=0). B — достоверное (P=1)."}]},
                {"uid": "MET-EV-COMPAT", "title": "Совместные и несовместные события",
                 "description": "Несовместные: A∩B=∅, не могут произойти одновременно. P(A∪B)=P(A)+P(B). Совместные: P(A∪B)=P(A)+P(B)−P(A∩B).",
                 "examples": [{"uid": "EX-EV-002", "title": "Совместность", "statement": "Карта из колоды. A — «красная», B — «туз». Совместные ли?", "solution": "Да: красный туз — A∩B≠∅. P(A∪B)=P(A)+P(B)−P(A∩B)=18/36+4/36−2/36=20/36."}]},
                {"uid": "MET-EV-COMPLETE", "title": "Полная группа событий",
                 "description": "H₁,H₂,…,Hₙ — полная группа, если попарно несовместны и ΣP(Hᵢ)=1. Используется в формуле полной вероятности.",
                 "examples": [{"uid": "EX-EV-003", "title": "Полная группа", "statement": "3 цеха производят продукцию. Доли: 30%, 50%, 20%. Полная группа?", "solution": "H₁∩H₂=∅, H₁∩H₃=∅, H₂∩H₃=∅. P(H₁)+P(H₂)+P(H₃)=1. Да, полная группа."}]},
            ],
        }],
    },

    # 13. Сочетания (2 → 3)
    {
        "topic_uid": "TOP-SOCHETANIYA-01b667",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-COMBINATIONS-B12",
            "title": "Сочетания",
            "definition": "C(n,k)=n!/(k!(n−k)!) — число способов выбрать k элементов из n без учёта порядка.",
            "methods": [
                {"uid": "MET-CMB-FORMULA", "title": "Формула сочетаний",
                 "description": "C(n,k)=n!/(k!(n−k)!). Свойства: C(n,0)=C(n,n)=1. C(n,k)=C(n,n−k). C(n,1)=n.",
                 "examples": [{"uid": "EX-CMB-001", "title": "Вычисление C(n,k)", "statement": "C(7,3)=?", "solution": "C(7,3)=7!/(3!·4!)=(7·6·5)/(3·2·1)=35."}]},
                {"uid": "MET-CMB-PASCAL", "title": "Треугольник Паскаля",
                 "description": "C(n,k)=C(n−1,k−1)+C(n−1,k). Каждый элемент — сумма двух над ним. Строка n — коэффициенты (a+b)ⁿ.",
                 "examples": [{"uid": "EX-CMB-002", "title": "Треугольник Паскаля", "statement": "Разложите (a+b)⁴.", "solution": "Строка 4: 1,4,6,4,1. (a+b)⁴=a⁴+4a³b+6a²b²+4ab³+b⁴."}]},
                {"uid": "MET-CMB-APPLY", "title": "Применение сочетаний в задачах",
                 "description": "Выбор подмножества, комитеты, команды. Если порядок не важен — сочетания. Если важен — размещения.",
                 "examples": [{"uid": "EX-CMB-003", "title": "Задача на сочетания", "statement": "Из 12 человек выбирают 4 для команды. Сколько способов?", "solution": "C(12,4)=12!/(4!·8!)=495."}]},
            ],
        }],
    },

    # 14. Текстовые задачи (1 → 3)
    {
        "topic_uid": "TOP-TEKSTOVYE-ZADACHI-004",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-WORD-PROBLEMS-B12",
            "title": "Текстовые задачи",
            "definition": "Задачи на движение, работу, смеси, проценты. Составление уравнений по условию.",
            "methods": [
                {"uid": "MET-WP-MOTION", "title": "Задачи на движение",
                 "description": "S=v·t. Встречное: t=S/(v₁+v₂). Вдогонку: t=S/(v₁−v₂). По воде: v(по)=v(собств)+v(теч).",
                 "examples": [{"uid": "EX-WP-001", "title": "Движение навстречу", "statement": "Из A и B (120 км) выехали навстречу: v₁=40, v₂=20 км/ч. Через сколько встретятся?", "solution": "t=120/(40+20)=2 ч."}]},
                {"uid": "MET-WP-WORK", "title": "Задачи на совместную работу",
                 "description": "Производительность=1/t (часть работы в единицу времени). Совместная: 1/t₁+1/t₂=1/t.",
                 "examples": [{"uid": "EX-WP-002", "title": "Совместная работа", "statement": "Мастер делает заказ за 6ч, ученик — за 12ч. Вместе за сколько?", "solution": "1/6+1/12=3/12=1/4. Вместе за 4 часа."}]},
                {"uid": "MET-WP-MIXTURE", "title": "Задачи на смеси и сплавы",
                 "description": "Масса вещества = концентрация × масса раствора. При смешивании: m₁c₁+m₂c₂=(m₁+m₂)c.",
                 "examples": [{"uid": "EX-WP-003", "title": "Смеси", "statement": "Смешали 200г 10%-го и 300г 20%-го раствора. Какова концентрация?", "solution": "m=200·0.1+300·0.2=20+60=80г. c=80/500=0.16=16%."}]},
            ],
        }],
    },

    # 15. Тела вращения (2 → 3)
    {
        "topic_uid": "TOP-TELA-VRASCHENIYA-722214",
        "remove_all_old_skills": True,
        "skills": [{
            "uid": "SKL-ROTATION-B12",
            "title": "Тела вращения",
            "definition": "Цилиндр, конус, шар, усечённый конус — тела, образованные вращением фигуры вокруг оси.",
            "methods": [
                {"uid": "MET-ROT-CYL", "title": "Цилиндр: формулы и свойства",
                 "description": "V=πr²h. S_бок=2πrh. S_полн=2πr(r+h). Осевое сечение — прямоугольник.",
                 "examples": [{"uid": "EX-ROT-001", "title": "Цилиндр", "statement": "r=5, h=8. V и S_полн?", "solution": "V=π·25·8=200π. S_полн=2π·5·(5+8)=130π."}]},
                {"uid": "MET-ROT-CONE", "title": "Конус: формулы и свойства",
                 "description": "V=⅓πr²h. S_бок=πrl (l=√(r²+h²) — образующая). Осевое сечение — равнобедренный треугольник.",
                 "examples": [{"uid": "EX-ROT-002", "title": "Конус", "statement": "r=3, h=4. Образующая l? S_бок?", "solution": "l=√(9+16)=5. S_бок=π·3·5=15π."}]},
                {"uid": "MET-ROT-SPHERE", "title": "Шар и сфера",
                 "description": "V=⁴⁄₃πr³. S=4πr². Сечение шара плоскостью — круг. Расстояние от центра до сечения d: r_сеч=√(R²−d²).",
                 "examples": [{"uid": "EX-ROT-003", "title": "Сечение шара", "statement": "Шар R=10. Сечение на расстоянии 6 от центра. r_сеч=?", "solution": "r_сеч=√(100−36)=√64=8."}]},
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
    print(f"\n{'='*60}\nBatch 12 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
