#!/usr/bin/env python3
"""Batch 7: 15 критических тем (46–60)."""
import sys, time, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
NOW_MS = int(time.time() * 1000)

DATA = [
    # 46. Применение статистики
    {"topic_uid": "TOP-PRIMENENIE-STATISTIKI-V--dcd30e", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-STAT-APPLY", "title": "Применение статистики в жизни",
        "definition": "Использование статистических методов для анализа реальных данных.",
        "methods": [
            {"uid": "MET-SAPPLY-SURVEY", "title": "Статистический анализ опросов",
             "description": "Соберите данные, постройте частотную таблицу, вычислите среднее и медиану, сделайте выводы.",
             "examples": [{"uid": "EX-SAPPLY-001", "title": "Анализ опроса", "statement": "Опрос: сколько часов спят ученики? 6,7,8,7,8,9,7,6,8,7. Найдите среднее и моду.", "solution": "Среднее=7.3, мода=7 (встречается 4 раза). Большинство спит 7 часов."}]},
            {"uid": "MET-SAPPLY-COMPARE", "title": "Сравнение двух групп по статистике",
             "description": "Вычислите одинаковые характеристики (среднее, σ) для обеих групп и сравните.",
             "examples": [{"uid": "EX-SAPPLY-002", "title": "Сравнение групп", "statement": "Группа А: x̄=75, σ=10. Группа Б: x̄=78, σ=5. Что лучше?", "solution": "Б чуть выше по среднему (78>75) и однороднее (σ=5<10)."}]},
            {"uid": "MET-SAPPLY-TRENDS", "title": "Выявление тенденций",
             "description": "Постройте график по времени. Растущий тренд — показатель увеличивается. Падающий — снижается.",
             "examples": [{"uid": "EX-SAPPLY-003", "title": "Тренд продаж", "statement": "Продажи по кварталам: 100, 120, 110, 140. Есть ли тренд?", "solution": "Общий тренд — рост (100→140), несмотря на спад в Q3. Тренд положительный."}]},
        ],
    }]},

    # 47. Проверка гипотез
    {"topic_uid": "TOP-PROVERKA-GIPOTEZ-9511b6", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-HYPOTHESIS", "title": "Проверка статистических гипотез",
        "definition": "Формулировка нулевой и альтернативной гипотез, определение уровня значимости, принятие решения.",
        "methods": [
            {"uid": "MET-HYP-FORMULATE", "title": "Формулировка гипотез H₀ и H₁",
             "description": "H₀ — нулевая гипотеза (нет эффекта). H₁ — альтернативная (есть эффект). Уровень значимости α обычно 0.05.",
             "examples": [{"uid": "EX-HYP-001", "title": "Формулировка", "statement": "Проверяем: среднее = 50. Какие H₀ и H₁?", "solution": "H₀: μ=50. H₁: μ≠50 (двусторонняя) или H₁: μ>50 (односторонняя)."}]},
            {"uid": "MET-HYP-DECIDE", "title": "Принятие решения по p-значению",
             "description": "Если p < α — отвергаем H₀. Если p ≥ α — не отвергаем H₀. Не путайте: «не отвергаем» ≠ «доказали».",
             "examples": [{"uid": "EX-HYP-002", "title": "Решение", "statement": "p = 0.03, α = 0.05. Что решаем?", "solution": "p=0.03 < α=0.05 → отвергаем H₀. Разница статистически значима."}]},
            {"uid": "MET-HYP-ERRORS", "title": "Ошибки I и II рода",
             "description": "Ошибка I рода (α): отвергли H₀, когда она верна. Ошибка II рода (β): не отвергли H₀, когда она ложна.",
             "examples": [{"uid": "EX-HYP-003", "title": "Ошибки", "statement": "α=0.05. Что это означает?", "solution": "В 5% случаев мы ошибочно отвергнем верную H₀ (ложная тревога)."}]},
        ],
    }]},

    # 48. Производная и её применение (нужно добавить ещё 1 метод)
    {"topic_uid": "TOP-MATH-DERIVATIVES", "remove_all_old_skills": False, "skills": [{
        "uid": "SKL-DERIV-APPLY", "title": "Применение производной",
        "definition": "Использование производной для нахождения экстремумов, построения графиков, решения прикладных задач.",
        "methods": [
            {"uid": "MET-DERIV-EXTREMA", "title": "Нахождение экстремумов функции через производную",
             "description": "1) Найдите f'(x). 2) Решите f'(x)=0. 3) Определите знак f' слева и справа от корня. Смена + на − → max, − на + → min.",
             "examples": [{"uid": "EX-DERIV-001", "title": "Экстремумы", "statement": "f(x)=x³−3x. Найдите экстремумы.", "solution": "f'=3x²−3=0, x=±1. f'(−2)=9>0, f'(0)=−3<0 → x=−1 max. f'(0)<0, f'(2)=9>0 → x=1 min. f(−1)=2, f(1)=−2."}]},
            {"uid": "MET-DERIV-TANGENT", "title": "Уравнение касательной к графику",
             "description": "y = f(a) + f'(a)(x−a). Касательная проходит через (a, f(a)) с наклоном f'(a).",
             "examples": [{"uid": "EX-DERIV-002", "title": "Касательная", "statement": "f(x)=x², a=3. Уравнение касательной?", "solution": "f(3)=9, f'(x)=2x, f'(3)=6. y=9+6(x−3)=6x−9."}]},
        ],
    }]},

    # 49. Работа с данными (1–4 класс)
    {"topic_uid": "TOP-RABOTA-S-DANNYMI-005", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-DATA-WORK", "title": "Работа с данными: сбор, запись, анализ",
        "definition": "Сбор данных наблюдений, запись в таблицу, простейший анализ: наибольшее, наименьшее, среднее.",
        "methods": [
            {"uid": "MET-DW-COLLECT", "title": "Сбор и запись данных в таблицу",
             "description": "Определите, что измеряете. Запишите результаты в таблицу: столбцы — признаки, строки — объекты.",
             "examples": [{"uid": "EX-DW-001", "title": "Таблица измерений", "statement": "Измерьте рост 5 одноклассников и запишите.", "solution": "Имя | Рост: Аня 142, Боря 148, Вика 145, Гриша 150, Даша 140."}]},
            {"uid": "MET-DW-ANALYZE", "title": "Анализ данных: наибольшее, наименьшее, среднее",
             "description": "Найдите max и min. Вычислите среднее. Определите размах = max − min.",
             "examples": [{"uid": "EX-DW-002", "title": "Анализ", "statement": "Рост: 142, 148, 145, 150, 140. Найдите max, min, среднее.", "solution": "Max=150, min=140, размах=10. Среднее=(142+148+145+150+140)/5=145."}]},
            {"uid": "MET-DW-DIAGRAM", "title": "Представление данных на диаграмме",
             "description": "Постройте столбчатую диаграмму по данным таблицы. Высота столбца = значение.",
             "examples": [{"uid": "EX-DW-003", "title": "Диаграмма", "statement": "Любимые предметы: Математика 12, Чтение 8, Физкультура 15. Постройте диаграмму.", "solution": "3 столбца: Математика (12), Чтение (8), Физкультура (15). Самый высокий — Физкультура."}]},
        ],
    }]},

    # 50. Разброс
    {"topic_uid": "TOP-RAZBROS-ac7a78", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-DISPERSION", "title": "Разброс данных",
        "definition": "Оценка рассеяния значений: размах, дисперсия, стандартное отклонение, IQR.",
        "methods": [
            {"uid": "MET-DISP-RANGE", "title": "Размах как мера разброса",
             "description": "R = max − min. Простая, но чувствительна к выбросам.",
             "examples": [{"uid": "EX-DISP-001", "title": "Размах", "statement": "Температуры: 15, 18, 17, 16, 30. R=?", "solution": "R=30−15=15. Большой из-за выброса 30."}]},
            {"uid": "MET-DISP-STD", "title": "Стандартное отклонение",
             "description": "σ = √[Σ(xᵢ−x̄)²/n]. Чем больше σ, тем больше разброс.",
             "examples": [{"uid": "EX-DISP-002", "title": "σ", "statement": "Данные: 10, 10, 10 и 5, 10, 15. У кого σ больше?", "solution": "Первый: σ=0. Второй: x̄=10, σ=√[(25+0+25)/3]=√(50/3)≈4.08. Второй набор разбросаннее."}]},
            {"uid": "MET-DISP-BOXPLOT", "title": "Ящик с усами (boxplot)",
             "description": "Отметьте Q₁, Me, Q₃. Усы — до min и max (или до 1.5·IQR от квартилей). Точки за усами — выбросы.",
             "examples": [{"uid": "EX-DISP-003", "title": "Boxplot", "statement": "Q₁=20, Me=30, Q₃=40, min=5, max=55. IQR=?", "solution": "IQR=40−20=20. 1.5·IQR=30. Нижний ус: Q₁−30=−10→берём min=5. Верхний: Q₃+30=70→берём max=55. Выбросов нет."}]},
        ],
    }]},

    # 51. Размерность (линейная алгебра)
    {"topic_uid": "TOP-RAZMERNOST-cb7976", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-DIMENSION", "title": "Размерность векторного пространства",
        "definition": "Размерность — число векторов в базисе. ℝ² имеет размерность 2, ℝ³ — 3.",
        "methods": [
            {"uid": "MET-DIM-DEFINE", "title": "Определение размерности",
             "description": "Размерность = максимальное число линейно независимых векторов = число векторов в любом базисе.",
             "examples": [{"uid": "EX-DIM-001", "title": "Размерность", "statement": "Пространство ℝ³. Какова размерность?", "solution": "dim(ℝ³) = 3. Базис: e₁=(1,0,0), e₂=(0,1,0), e₃=(0,0,1)."}]},
            {"uid": "MET-DIM-RANK", "title": "Ранг системы векторов",
             "description": "Ранг = число ЛНЗ векторов в системе. Найдите методом Гаусса (приведите матрицу к ступенчатому виду).",
             "examples": [{"uid": "EX-DIM-002", "title": "Ранг", "statement": "v₁=(1,2,3), v₂=(2,4,6), v₃=(1,0,1). Найдите ранг.", "solution": "v₂=2v₁ → зависим. v₁ и v₃ ЛНЗ (не пропорциональны). Ранг = 2."}]},
            {"uid": "MET-DIM-SUBSPACE", "title": "Размерность подпространства",
             "description": "Подпространство W ⊂ V имеет dim(W) ≤ dim(V). Ядро линейного отображения — подпространство.",
             "examples": [{"uid": "EX-DIM-003", "title": "Подпространство", "statement": "Плоскость в ℝ³, проходящая через начало координат. dim=?", "solution": "Плоскость задаётся 2 ЛНЗ направляющими → dim = 2."}]},
        ],
    }]},

    # 52. Размещения (комбинаторика, 9 класс)
    {"topic_uid": "TOP-RAZMESCHENIYA-382d73", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-ARRANGEMENTS", "title": "Размещения",
        "definition": "Размещение — упорядоченный набор k элементов из n. A(n,k) = n!/(n−k)!.",
        "methods": [
            {"uid": "MET-ARR-FORMULA", "title": "Формула числа размещений",
             "description": "A(n,k) = n·(n−1)·...·(n−k+1) = n!/(n−k)!. Порядок важен.",
             "examples": [{"uid": "EX-ARR-001", "title": "Размещения", "statement": "Из 5 букв составить слово из 3 букв. Сколько вариантов?", "solution": "A(5,3) = 5·4·3 = 60."}]},
            {"uid": "MET-ARR-VS-COMB", "title": "Отличие размещений от сочетаний",
             "description": "Размещения: порядок важен (ABC ≠ BAC). Сочетания: порядок не важен (ABC = BAC). C(n,k) = A(n,k)/k!.",
             "examples": [{"uid": "EX-ARR-002", "title": "Размещения vs сочетания", "statement": "Из 4 человек выбрать президента и вице. Размещения или сочетания?", "solution": "Порядок важен (президент ≠ вице) → размещения. A(4,2) = 4·3 = 12."}]},
            {"uid": "MET-ARR-PROBLEMS", "title": "Задачи на размещения",
             "description": "Определите: порядок важен? Есть повторения? Если да — это A(n,k) с повторениями = nᵏ.",
             "examples": [{"uid": "EX-ARR-003", "title": "Кодовый замок", "statement": "Код из 4 цифр (0–9), цифры не повторяются. Сколько кодов?", "solution": "A(10,4) = 10·9·8·7 = 5040."}]},
        ],
    }]},

    # 53. Распределение Бернулли и биномиальное
    {"topic_uid": "TOP-RASPREDELENIE-BERNULLI-I-2654ca", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-BERNOULLI-BINOM", "title": "Распределение Бернулли и биномиальное",
        "definition": "Бернулли: 1 испытание, успех/неудача. Биномиальное: n независимых испытаний Бернулли.",
        "methods": [
            {"uid": "MET-BERN-SINGLE", "title": "Схема Бернулли (одно испытание)",
             "description": "P(успех)=p, P(неудача)=q=1−p. E(X)=p, D(X)=pq.",
             "examples": [{"uid": "EX-BERN-001", "title": "Бернулли", "statement": "Вероятность попадания в цель p=0.7. E(X)? D(X)?", "solution": "E(X)=0.7. D(X)=0.7·0.3=0.21."}]},
            {"uid": "MET-BERN-BINOM", "title": "Формула Бернулли (биномиальное распределение)",
             "description": "P(X=k) = C(n,k)·pᵏ·qⁿ⁻ᵏ. E(X)=np, D(X)=npq.",
             "examples": [{"uid": "EX-BERN-002", "title": "Биномиальное", "statement": "5 бросков монеты. P(ровно 3 орла)?", "solution": "P(X=3) = C(5,3)·(0.5)³·(0.5)² = 10·0.125·0.25 = 0.3125."}]},
            {"uid": "MET-BERN-MOST-LIKELY", "title": "Наивероятнейшее число успехов",
             "description": "np−q ≤ k₀ ≤ np+p. Если np+p — целое, то два наивероятнейших значения.",
             "examples": [{"uid": "EX-BERN-003", "title": "Наивероятнейшее", "statement": "n=100, p=0.3. Наивероятнейшее число успехов?", "solution": "np−q=30−0.7=29.3, np+p=30+0.3=30.3. k₀=30."}]},
        ],
    }]},

    # 54. Распределение Пуассона
    {"topic_uid": "TOP-RASPREDELENIE-PUASSONA-66bdaa", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-POISSON", "title": "Распределение Пуассона",
        "definition": "Модель для редких событий. P(X=k)=λᵏe⁻λ/k!. E(X)=λ, D(X)=λ.",
        "methods": [
            {"uid": "MET-POIS-FORMULA", "title": "Формула Пуассона",
             "description": "P(X=k) = λᵏ·e⁻λ / k!. λ = np (среднее число событий). Применяется при n→∞, p→0, np=λ=const.",
             "examples": [{"uid": "EX-POIS-001", "title": "Формула Пуассона", "statement": "В среднем 2 опечатки на страницу. P(0 опечаток)?", "solution": "λ=2. P(0) = 2⁰·e⁻²/0! = e⁻² ≈ 0.135."}]},
            {"uid": "MET-POIS-APPLY", "title": "Когда применять распределение Пуассона",
             "description": "n велико, p мало, np умеренное. Примеры: число звонков, аварий, бракованных деталей.",
             "examples": [{"uid": "EX-POIS-002", "title": "Применимость", "statement": "1000 деталей, P(брак)=0.002. Подходит Пуассон?", "solution": "n=1000 (велико), p=0.002 (мало), λ=np=2 (умеренно). Да, подходит."}]},
            {"uid": "MET-POIS-CUMUL", "title": "Кумулятивные вероятности Пуассона",
             "description": "P(X≤k) = Σ P(X=i) для i от 0 до k. P(X≥k) = 1 − P(X≤k−1).",
             "examples": [{"uid": "EX-POIS-003", "title": "P(X≥1)", "statement": "λ=3. P(хотя бы 1 событие)?", "solution": "P(X≥1) = 1−P(X=0) = 1−e⁻³ ≈ 1−0.05 = 0.95."}]},
        ],
    }]},

    # 55. Рациональные неравенства (8–9 класс)
    {"topic_uid": "TOP-RATSIONALNYE-NERAVENSTVA-0c5460", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-RATIONAL-INEQ", "title": "Решение рациональных неравенств",
        "definition": "Неравенства с дробно-рациональными выражениями. Метод интервалов.",
        "methods": [
            {"uid": "MET-RINEQ-INTERVALS", "title": "Метод интервалов для рациональных неравенств",
             "description": "1) Перенесите всё в одну сторону. 2) Разложите числитель и знаменатель. 3) Найдите нули и точки разрыва. 4) Расставьте знаки на интервалах.",
             "examples": [{"uid": "EX-RINEQ-001", "title": "Метод интервалов", "statement": "(x−1)/(x+2) > 0.", "solution": "Нули/разрывы: x=1, x=−2. Знаки: (−∞,−2):+, (−2,1):−, (1,+∞):+. Ответ: (−∞,−2) ∪ (1,+∞)."}]},
            {"uid": "MET-RINEQ-REDUCE", "title": "Приведение к стандартному виду",
             "description": "Перенесите всё в левую часть, приведите к общему знаменателю. f(x)/g(x) > 0.",
             "examples": [{"uid": "EX-RINEQ-002", "title": "Приведение", "statement": "1/(x−3) ≥ 2.", "solution": "1/(x−3)−2 ≥ 0 → (1−2(x−3))/(x−3) ≥ 0 → (7−2x)/(x−3) ≥ 0. Корни: x=3.5, x=3. Ответ: (3; 3.5]."}]},
            {"uid": "MET-RINEQ-SPECIAL", "title": "Особые случаи: строгие и нестрогие неравенства",
             "description": "При строгом (>) — точки нулей числителя выкалываются. При нестрогом (≥) — включаются. Точки разрыва знаменателя всегда выкалываются.",
             "examples": [{"uid": "EX-RINEQ-003", "title": "Строгое vs нестрогое", "statement": "(x−1)/(x+2) ≥ 0 vs > 0.", "solution": "≥ 0: (−∞,−2) ∪ [1,+∞) (x=1 включён). > 0: (−∞,−2) ∪ (1,+∞) (x=1 выколот)."}]},
        ],
    }]},

    # 56. Сбор данных: методы и инструменты
    {"topic_uid": "TOP-SBOR-DANNYH-METODY-I-INS-60afe1", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-DATA-COLLECTION", "title": "Методы сбора данных",
        "definition": "Наблюдение, опрос, эксперимент. Первичные и вторичные данные. Анкетирование.",
        "methods": [
            {"uid": "MET-DC-METHODS", "title": "Основные методы сбора данных",
             "description": "Наблюдение: фиксируем без вмешательства. Опрос: задаём вопросы. Эксперимент: контролируем условия.",
             "examples": [{"uid": "EX-DC-001", "title": "Выбор метода", "statement": "Изучаем влияние удобрений на рост растений. Какой метод?", "solution": "Эксперимент: две группы растений (с удобрением и без), контролируем условия."}]},
            {"uid": "MET-DC-SAMPLING", "title": "Способы формирования выборки",
             "description": "Случайная: каждый элемент с одинаковой P. Систематическая: каждый k-й. Стратифицированная: по группам.",
             "examples": [{"uid": "EX-DC-002", "title": "Случайная выборка", "statement": "Из 500 учеников выбрать 50 для опроса. Как?", "solution": "Пронумеруйте 1–500, с помощью генератора случайных чисел выберите 50 номеров."}]},
            {"uid": "MET-DC-QUESTIONNAIRE", "title": "Составление анкеты",
             "description": "Вопросы ясные и однозначные. Закрытые (с вариантами) для количественного анализа. Открытые — для качественного.",
             "examples": [{"uid": "EX-DC-003", "title": "Анкета", "statement": "Составьте вопрос для опроса о любимом предмете.", "solution": "«Какой предмет вам нравится больше всего?» Варианты: Математика / Русский / Физика / Другое."}]},
        ],
    }]},

    # 57. Сводные таблицы
    {"topic_uid": "TOP-SVODNYE-TABLICY-c6cff5", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-PIVOT-TABLES", "title": "Сводные таблицы",
        "definition": "Группировка и обобщение данных по категориям. Подсчёт итогов, средних, частот.",
        "methods": [
            {"uid": "MET-PIVOT-BUILD", "title": "Построение сводной таблицы",
             "description": "Определите категории (строки и столбцы). Заполните ячейки суммами, средними или частотами.",
             "examples": [{"uid": "EX-PIVOT-001", "title": "Сводная таблица", "statement": "Оценки по классам: 5А (4,5,5,3), 5Б (3,4,4,5). Постройте сводную.", "solution": "Класс | Ср.балл | Кол-во. 5А: 4.25, 4 уч. 5Б: 4.0, 4 уч."}]},
            {"uid": "MET-PIVOT-READ", "title": "Чтение и анализ сводной таблицы",
             "description": "Сравните строки и столбцы. Найдите наибольшие/наименьшие значения. Определите тенденции.",
             "examples": [{"uid": "EX-PIVOT-002", "title": "Анализ", "statement": "Продажи по регионам и кварталам. Москва: Q1=100, Q2=120. СПб: Q1=80, Q2=90. Вывод?", "solution": "Москва лидирует. Оба региона растут (Q1→Q2). Рост Москвы: +20, СПб: +10."}]},
            {"uid": "MET-PIVOT-CROSS", "title": "Таблица сопряжённости (кросс-таблица)",
             "description": "Двумерная таблица частот для двух категориальных признаков. Итоговые строки и столбцы показывают маргинальные частоты.",
             "examples": [{"uid": "EX-PIVOT-003", "title": "Кросс-таблица", "statement": "Пол/Предпочтение: М-Чай 20, М-Кофе 30, Ж-Чай 35, Ж-Кофе 15. Что популярнее?", "solution": "Всего чай: 55, кофе: 45. Чай популярнее. Но у М кофе популярнее (30>20), у Ж — чай (35>15)."}]},
        ],
    }]},

    # 58. Свойства вероятности
    {"topic_uid": "TOP-SVOISTVA-VEROYATNOSTI-51b7ce", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-PROB-PROPERTIES", "title": "Свойства вероятности",
        "definition": "Аксиомы: 0≤P≤1, P(Ω)=1. Формулы сложения и умножения вероятностей.",
        "methods": [
            {"uid": "MET-PROP-ADD", "title": "Формула сложения вероятностей",
             "description": "P(A∪B) = P(A)+P(B)−P(A∩B). Для несовместных: P(A∪B)=P(A)+P(B).",
             "examples": [{"uid": "EX-PROP-001", "title": "Сложение", "statement": "P(A)=0.4, P(B)=0.3, P(A∩B)=0.1. P(A∪B)?", "solution": "P(A∪B) = 0.4+0.3−0.1 = 0.6."}]},
            {"uid": "MET-PROP-MULT", "title": "Формула умножения вероятностей",
             "description": "P(A∩B) = P(A)·P(B|A). Для независимых: P(A∩B) = P(A)·P(B).",
             "examples": [{"uid": "EX-PROP-002", "title": "Умножение", "statement": "2 карты из колоды (36). P(обе — тузы)?", "solution": "P(1-й туз)=4/36. P(2-й туз|1-й туз)=3/35. P=4/36·3/35=12/1260=1/105."}]},
            {"uid": "MET-PROP-COMPLEMENT", "title": "Вероятность противоположного события",
             "description": "P(Ā) = 1 − P(A). Удобно, когда P(A) сложно считать напрямую.",
             "examples": [{"uid": "EX-PROP-003", "title": "Противоположное", "statement": "3 стрелка, P попадания: 0.8, 0.7, 0.9. P(хотя бы 1 попадёт)?", "solution": "P(никто) = 0.2·0.3·0.1 = 0.006. P(хотя бы 1) = 1−0.006 = 0.994."}]},
        ],
    }]},

    # 59. Средние характеристики
    {"topic_uid": "TOP-SREDNIE-HARAKTERISTIKI-b231f6", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-AVERAGES", "title": "Средние величины в статистике",
        "definition": "Среднее арифметическое, взвешенное среднее, среднее геометрическое.",
        "methods": [
            {"uid": "MET-AVG-ARITH", "title": "Среднее арифметическое",
             "description": "x̄ = Σxᵢ/n. Для сгруппированных данных: x̄ = Σ(fᵢ·xᵢ)/Σfᵢ.",
             "examples": [{"uid": "EX-AVG-001", "title": "Среднее", "statement": "Оценки: 5 получили 3 уч., 4 — 5 уч., 3 — 2 уч. Среднее?", "solution": "x̄ = (5·3+4·5+3·2)/(3+5+2) = (15+20+6)/10 = 4.1."}]},
            {"uid": "MET-AVG-WEIGHTED", "title": "Взвешенное среднее",
             "description": "x̄ = Σwᵢxᵢ/Σwᵢ. Веса отражают значимость каждого значения.",
             "examples": [{"uid": "EX-AVG-002", "title": "Взвешенное среднее", "statement": "ЕГЭ: Математика 80 (вес 2), Русский 90 (вес 1). Взвешенное среднее?", "solution": "x̄ = (80·2+90·1)/(2+1) = 250/3 ≈ 83.3."}]},
            {"uid": "MET-AVG-CHOOSE", "title": "Выбор типа средней величины",
             "description": "Арифметическое — для суммирования. Геометрическое — для темпов роста. Гармоническое — для скоростей.",
             "examples": [{"uid": "EX-AVG-003", "title": "Средняя скорость", "statement": "Туда 60 км/ч, обратно 40 км/ч. Средняя скорость?", "solution": "Гармоническое: 2/(1/60+1/40) = 2/(2+3)/120 = 240/5 = 48 км/ч (не 50!)."}]},
        ],
    }]},

    # 60. Стереометрические задачи ЕГЭ
    {"topic_uid": "TOP-EGE-STEREOMETRIYA-ZADACHI-2026", "remove_all_old_skills": True, "skills": [{
        "uid": "SKL-EGE-STEREO", "title": "Решение стереометрических задач ЕГЭ",
        "definition": "Расстояния и углы в пространстве, сечения многогранников, объёмы.",
        "methods": [
            {"uid": "MET-STEREO-DIST", "title": "Нахождение расстояний в пространстве",
             "description": "Расстояние от точки до плоскости — длина перпендикуляра. Между скрещивающимися прямыми — длина общего перпендикуляра.",
             "examples": [{"uid": "EX-STEREO-001", "title": "Расстояние", "statement": "Куб ABCDA₁B₁C₁D₁, ребро 1. Расстояние от A до плоскости B₁D₁D?", "solution": "Координаты: A(0,0,0). Плоскость B₁D₁D проходит через B₁(1,0,1), D₁(0,1,1), D(0,1,0). Уравнение: x−y+z=0. d = |0−0+0|/√3 = 0. Пересчёт: d = 1/√3."}]},
            {"uid": "MET-STEREO-SECTION", "title": "Построение сечения многогранника",
             "description": "Сечение — плоская фигура. Используйте теорему: если плоскость пересекает две параллельные грани, линии пересечения параллельны.",
             "examples": [{"uid": "EX-STEREO-002", "title": "Сечение куба", "statement": "Куб ABCDA₁B₁C₁D₁. Сечение через середины AB, BC и вершину D₁.", "solution": "M — середина AB, N — середина BC. Соединяем M, N, D₁. Проводим параллельные сечения через грани. Результат — треугольник MND₁."}]},
            {"uid": "MET-STEREO-COORD", "title": "Координатный метод в стереометрии",
             "description": "Введите систему координат. Найдите координаты точек. Используйте формулы расстояний, скалярное произведение для углов.",
             "examples": [{"uid": "EX-STEREO-003", "title": "Координатный метод", "statement": "Правильная 4-угольная пирамида, сторона 2, высота 3. Угол бокового ребра с основанием?", "solution": "O(0,0,0) — центр основания, S(0,0,3) — вершина, A(1,1,0). SA = (1,1,−3), |SA|=√11. cos α = |−3|/√11. α = arccos(3/√11) ≈ 25°."}]},
        ],
    }]},
]

def _merge_node(session, label, uid, props):
    all_props = {"uid": uid, "type": label, "tenant_id": TENANT_ID, "lifecycle_status": "ACTIVE", "updated_at": NOW_MS, **props}
    session.run(f"MERGE (n:{label} {{uid: $uid, tenant_id: $tid}}) SET n += $props", uid=uid, tid=TENANT_ID, props=all_props)

def _merge_rel(session, from_uid, rel_type, to_uid):
    session.run(f"MATCH (a {{uid: $from_uid, tenant_id: $tid}}), (b {{uid: $to_uid, tenant_id: $tid}}) MERGE (a)-[:{rel_type}]->(b)", from_uid=from_uid, to_uid=to_uid, tid=TENANT_ID)

def _delete_all_skill_rels(session, topic_uid, dry_run):
    existing = session.run("MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[:REQUIRES_SKILL]->(sk:Skill) RETURN sk.uid AS uid, sk.title AS title", uid=topic_uid, tid=TENANT_ID).data()
    if not existing: return 0
    for s in existing: print(f"      🗑️  {topic_uid} → {s['uid']} ({s['title']})")
    if not dry_run:
        session.run("MATCH (t:Topic {uid: $uid, tenant_id: $tid})-[r:REQUIRES_SKILL]->(sk:Skill) DELETE r", uid=topic_uid, tid=TENANT_ID)
    return len(existing)

def seed(dry_run=False):
    repo = Neo4jRepo(); drv = repo.driver
    stats = {"topics": 0, "skills": 0, "methods": 0, "examples": 0, "deleted_rels": 0}
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
                    stats["skills"] += 1
                    for method in skill.get("methods", []):
                        method_uid = method["uid"]
                        method_props = {k: v for k, v in method.items() if k not in ("uid", "examples")}
                        print(f"    [Method] {method_uid}: {method.get('title', '')}")
                        if not dry_run:
                            _merge_node(session, "Method", method_uid, method_props)
                            _merge_rel(session, skill_uid, "HAS_METHOD", method_uid)
                        stats["methods"] += 1
                        for ex in method.get("examples", []):
                            if not dry_run:
                                _merge_node(session, "Example", ex["uid"], {k: v for k, v in ex.items() if k != "uid"})
                                _merge_rel(session, method_uid, "HAS_EXAMPLE", ex["uid"])
                            stats["examples"] += 1
    finally:
        repo.close()
    mode = "(DRY RUN)" if dry_run else "(ПРИМЕНЕНО)"
    print(f"\n{'='*60}\nBatch 7 {mode}: тем={stats['topics']}, навыков={stats['skills']}, методов={stats['methods']}, примеров={stats['examples']}, удалено={stats['deleted_rels']}\n{'='*60}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true")
    seed(dry_run=p.parse_args().dry_run)
