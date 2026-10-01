"""Kazakh lessons for learners continuing beyond Python fundamentals."""

from textwrap import dedent


def _code(source):
    return dedent(source).strip()


ADVANCED_COURSES = [
    {
        "title": "Алгоритмдер және есептеу күрделілігі",
        "description": "Алгоритмнің қадамдарын бағалау, екілік іздеу, сұрыптау және префикстік қосынды арқылы есептерді тиімді шешу.",
        "icon": "🧠",
        "difficulty": "intermediate",
        "order": 9,
        "lessons": [
            {
                "title": "Сызықтық іздеу және O(n) күрделілігі",
                "theory": """
<h3>Алгоритмнің жұмысын қалай бағалаймыз?</h3>
<p>Алгоритм — нәтижеге жеткізетін нақты қадамдар тізбегі. Күрделілік енгізілген
деректер саны өскенде жұмыс мөлшері қалай өзгеретінін сипаттайды. <code>O(n)</code>
алгоритмі ең нашар жағдайда n элементке қарайды; бұл нақты секунд саны емес.</p>
<h3>Сызықтық іздеу</h3>
<p>Тізім сұрыпталмаған болса, элементтерді ретімен салыстыруға болады. Мақсатты
мән табылған кезде бірден қайту артық жұмысты тоқтатады. Индекстер нөлден
басталады, ал <code>-1</code> мәні «табылмады» деген келісімді білдіреді.</p>
<p>Ең жақсы жағдай — бірінші элемент сәйкес келеді. Ең нашар жағдай — соңғы
элемент сәйкес келеді немесе ізделген мән жоқ. Төмендегі санауыш нақты
салыстыру санын көруге көмектеседі. Қосымша жад күрделілігі — <code>O(1)</code>.</p>
""",
                "code_example": _code('''
                    def linear_search(values, target):
                        comparisons = 0
                        for index, value in enumerate(values):
                            comparisons += 1
                            if value == target:
                                return index, comparisons
                        return -1, comparisons

                    values = [12, 7, 19, 3, 8]
                    index, comparisons = linear_search(values, 3)
                    print(f"Индекс: {index}")
                    print(f"Салыстыру: {comparisons}")
                    index, comparisons = linear_search(values, 99)
                    print(f"Табылмады: {index}, салыстыру: {comparisons}")
                '''),
                "task": "linear_search(values, target) функциясын жазыңыз: ол бірінші сәйкес элементтің индексін және жасалған салыстыру санын қайтарсын; мән жоқ болса индексі -1 болсын. values = [12, 7, 19, 3, 8] үшін алдымен 3, кейін 99 мәндерін іздеңіз. Үш жолды күтілетін форматпен шығарыңыз.",
                "expected_output": "Индекс: 3\nСалыстыру: 4\nТабылмады: -1, салыстыру: 5",
                "order": 1,
            },
            {
                "title": "Сұрыпталған тізімдегі екілік іздеу",
                "theory": """
<h3>Іздеу аймағын екіге бөлу</h3>
<p>Екілік іздеу тек өсу ретімен сұрыпталған тізімде дұрыс жұмыс істейді.
Әр қадамда ортадағы элементті тексереміз: ол мақсаттан кіші болса, сол жақ
жартыны; үлкен болса, оң жақ жартыны іздеуден алып тастаймыз.</p>
<p><code>left</code> және <code>right</code> шекаралары іздеу аймағына кіреді.
<code>mid = (left + right) // 2</code> бүтін индекс береді. Шекараны
<code>mid + 1</code> немесе <code>mid - 1</code> арқылы жылжыту циклдің
тоқтауын қамтамасыз етеді. <code>left &gt; right</code> болса, мән табылмады.</p>
<h3>Күрделілік</h3>
<p>Іздеу аймағы әр қадамда шамамен екі есе қысқарады: уақыт күрделілігі
<code>O(log n)</code>, қосымша жад — <code>O(1)</code>. Егер бастапқы тізімді
алдымен сұрыптау қажет болса, сол сұрыптау шығынын да бөлек ескеру керек.</p>
""",
                "code_example": _code('''
                    def binary_search(values, target):
                        left, right = 0, len(values) - 1
                        while left <= right:
                            mid = (left + right) // 2
                            if values[mid] == target:
                                return mid
                            if values[mid] < target:
                                left = mid + 1
                            else:
                                right = mid - 1
                        return -1

                    values = [2, 5, 8, 11, 14, 17, 20]
                    print(f"14 индексі: {binary_search(values, 14)}")
                    print(f"2 индексі: {binary_search(values, 2)}")
                    print(f"9 индексі: {binary_search(values, 9)}")
                '''),
                "task": "Екілік іздеуді циклмен іске асырыңыз. Сұрыпталған values = [2, 5, 8, 11, 14, 17, 20] тізімінен 14, 2 және 9 мәндерін осы ретпен іздеңіз. Табылмаған мән үшін -1 қайтарыңыз және нәтижелерді үш жолға көрсетілген форматпен шығарыңыз.",
                "expected_output": "14 индексі: 4\n2 индексі: 0\n9 индексі: -1",
                "order": 2,
            },
            {
                "title": "Кірістіру арқылы сұрыптау",
                "theory": """
<h3>Сұрыпталған бөлікті біртіндеп өсіру</h3>
<p>Кірістіру арқылы сұрыптауда бірінші элементті дайын сұрыпталған бөлік деп
санаймыз. Келесі элементті уақытша сақтап, одан үлкен элементтерді оңға
жылжытамыз. Бос орынға сақталған мәнді кірістіреміз.</p>
<p>Ішкі циклдегі <code>position &gt;= 0</code> тексерісі тізім басынан шығып
кетуді болдырмайды. Шартта <code>&gt;</code> қолдану тең элементтердің өзара
ретін сақтайды: бұл тұрақты сұрыптау деп аталады.</p>
<h3>Қашан пайдалы?</h3>
<p>Алгоритмді түсіну үшін және шағын, дерлік сұрыпталған деректер үшін пайдалы.
Ең нашар уақыт күрделілігі — <code>O(n²)</code>, ал алдын ала сұрыпталған
тізімде — <code>O(n)</code>. Үлкен нақты жобаларда Python-ның
<code>sorted()</code> не <code>list.sort()</code> әдісін таңдаңыз. Мысал
бастапқы тізімді өзгертпеу үшін оның көшірмесін сұрыптайды.</p>
""",
                "code_example": _code('''
                    def insertion_sort(values):
                        result = values.copy()
                        for index in range(1, len(result)):
                            current = result[index]
                            position = index - 1
                            while position >= 0 and result[position] > current:
                                result[position + 1] = result[position]
                                position -= 1
                            result[position + 1] = current
                        return result

                    values = [9, 3, 7, 3, 1]
                    print(f"Сұрыпталған: {insertion_sort(values)}")
                    print(f"Бастапқы: {values}")
                    print(f"Бос тізім: {insertion_sort([])}")
                '''),
                "task": "insertion_sort(values) функциясы тізімнің сұрыпталған көшірмесін қайтарсын. sorted() және sort() қолданбай, кірістіру алгоритмін пайдаланыңыз. values = [9, 3, 7, 3, 1] нәтижесін, өзгермеген бастапқы тізімді және бос тізімді сұрыптау нәтижесін үш жолға шығарыңыз.",
                "expected_output": "Сұрыпталған: [1, 3, 3, 7, 9]\nБастапқы: [9, 3, 7, 3, 1]\nБос тізім: []",
                "order": 3,
            },
            {
                "title": "Префикстік қосындымен аралықтарды есептеу",
                "theory": """
<h3>Қайталанатын сұрауларды жылдамдату</h3>
<p>Әр аралық үшін элементтерді қайта қосу ұзын тізім мен көп сұрауда артық
жұмыс туғызады. Префикстік қосынды тізімі алғашқы k элементтің қосындысын
сақтайды. Алғашқы мәнді нөл деп аламыз: <code>prefix[0] = 0</code>.</p>
<p><code>prefix[k]</code> — бастапқы тізімдегі 0-ден k-1-ге дейінгі
элементтердің қосындысы. Сондықтан сол шекарасы кіретін, оң шекарасы кірмейтін
<code>[left, right)</code> аралығының қосындысы
<code>prefix[right] - prefix[left]</code> болады.</p>
<h3>Уақыт пен жад арасындағы таңдау</h3>
<p>Префиксті құру <code>O(n)</code> уақыт пен <code>O(n)</code> қосымша жад
алады. Одан кейін әр сұрау <code>O(1)</code> уақытта орындалады. Бұл тәсіл
деректер өзгермегенде қолайлы; элемент өзгерсе, қарапайым префиксті қайта
есептеу керек. Бос аралықтың қосындысы нөлге тең.</p>
""",
                "code_example": _code('''
                    def build_prefix(values):
                        prefix = [0]
                        for value in values:
                            prefix.append(prefix[-1] + value)
                        return prefix

                    def range_sum(prefix, left, right):
                        if not 0 <= left <= right < len(prefix):
                            raise ValueError("Аралық шекарасы қате")
                        return prefix[right] - prefix[left]

                    prefix = build_prefix([4, 2, 7, 1, 6])
                    print(f"Префикс: {prefix}")
                    print(f"[1, 4): {range_sum(prefix, 1, 4)}")
                    print(f"[0, 5): {range_sum(prefix, 0, 5)}")
                    print(f"[2, 2): {range_sum(prefix, 2, 2)}")
                '''),
                "task": "[4, 2, 7, 1, 6] тізімі үшін нөлден басталатын префикстік қосынды құрыңыз. range_sum(prefix, left, right) функциясында оң шекараны аралыққа қоспаңыз. Префиксті және [1, 4), [0, 5), [2, 2) аралықтарының қосындыларын көрсетілген форматпен шығарыңыз.",
                "expected_output": "Префикс: [0, 4, 6, 13, 14, 20]\n[1, 4): 10\n[0, 5): 20\n[2, 2): 0",
                "order": 4,
            },
        ],
    },
    {
        "title": "Итераторлар, генераторлар және декораторлар",
        "description": "Python-ның кеңейтілген мүмкіндіктері: итерация протоколы, yield, функция декораторлары және контекст менеджерлері.",
        "icon": "⚙️",
        "difficulty": "advanced",
        "order": 10,
        "lessons": [
            {
                "title": "Итератор протоколы және next()",
                "theory": """
<h3>Итерацияланатын объект пен итератор</h3>
<p>Тізім, жол және range — элементтерін ретімен алуға болатын объектілер.
<code>iter(obj)</code> итератор жасайды, <code>next(iterator)</code> келесі
мәнді алады. Элементтер біткенде <code>StopIteration</code> пайда болады;
<code>for</code> циклі оны өзі өңдейді.</p>
<h3>Өз итераторымызды жасау</h3>
<p>Итератор класы <code>__iter__()</code> әдісінде өзін қайтарады және
<code>__next__()</code> ішінде күйін жаңартады. Итератордағы бір мән бір рет
алынады: ол таусылғаннан кейін қайтадан жүріп шығу үшін жаңа объект қажет.</p>
<p>Төмендегі санауыш берілген саннан 1-ге дейін кемиді. next() шақырғанда күй
өзгеретінін, ал list() тек қалған элементтерді жинайтынын байқаңыз.
<code>next(iterator, default)</code> таусылған итератор үшін қате көтермей,
берілген әдепкі мәнді қайтарады.</p>
""",
                "code_example": _code('''
                    class Countdown:
                        def __init__(self, start):
                            self.current = start

                        def __iter__(self):
                            return self

                        def __next__(self):
                            if self.current <= 0:
                                raise StopIteration
                            value = self.current
                            self.current -= 1
                            return value

                    counter = Countdown(4)
                    print(f"Бірінші: {next(counter)}")
                    print(f"Қалғаны: {list(counter)}")
                    print(f"Таусылды: {next(counter, 'аяқталды')}")
                    print(f"Жаңа санауыш: {list(Countdown(2))}")
                '''),
                "task": "Countdown класын __iter__ және __next__ арқылы жазыңыз: start санынан 1-ге дейін мән берсін, кейін StopIteration көтерсін. Countdown(4) объектісінен бір next() алыңыз, қалғанын list() арқылы шығарыңыз. Таусылған объектіге next(counter, 'аяқталды') қолданыңыз. Соңында жаңа Countdown(2) нәтижесін шығарыңыз.",
                "expected_output": "Бірінші: 4\nҚалғаны: [3, 2, 1]\nТаусылды: аяқталды\nЖаңа санауыш: [2, 1]",
                "order": 1,
            },
            {
                "title": "yield және жалқау есептеу",
                "theory": """
<h3>Генератор функциясы</h3>
<p>Функция ішінде <code>yield</code> болса, оны шақыру бірден барлық нәтижені
есептемейді: генератор объектісін қайтарады. Әр келесі мән сұралғанда функция
соңғы yield-тен кейін жалғасады. Жергілікті айнымалылардың күйі сақталады.</p>
<p>Бұл тәсіл үлкен ағынды толық тізімге жинамай өңдеуге мүмкіндік береді.
Мысалы, жұп сандардың квадраттарын бір-бірден беруге болады. Генератор
функциясының қосымша күйі шағын, бірақ <code>list(generator)</code> нәтижені
жадқа толық жинайды.</p>
<h3>Бір рет қолданылатын ағын</h3>
<p>Генератор да итератор сияқты таусылады. Бір бөлігі next() арқылы алынса,
sum() тек қалған бөлікті қосады. Барлық нәтижені қайта алу үшін генератор
функциясын қайта шақырыңыз. Генератор өрнегі
<code>(expression for value in values)</code> қысқа ағындар үшін ыңғайлы.</p>
""",
                "code_example": _code('''
                    def even_squares(limit):
                        for number in range(limit + 1):
                            if number % 2 == 0:
                                yield number * number

                    stream = even_squares(6)
                    print(f"Алғашқысы: {next(stream)}")
                    print(f"Қалған қосынды: {sum(stream)}")
                    print(f"Толық тізім: {list(even_squares(6))}")
                    total = sum(number * number for number in [1, 2, 3])
                    print(f"Өрнек қосындысы: {total}")
                '''),
                "task": "even_squares(limit) генераторы 0-ден limit-ке дейінгі жұп сандардың квадраттарын yield арқылы берсін. limit = 6 үшін бірінші мәнді next() арқылы, қалған мәндердің қосындысын sum() арқылы шығарыңыз. Жаңа генератордан толық тізім алыңыз. Генератор өрнегімен [1, 2, 3] сандары квадраттарының қосындысын шығарыңыз.",
                "expected_output": "Алғашқысы: 0\nҚалған қосынды: 56\nТолық тізім: [0, 4, 16, 36]\nӨрнек қосындысы: 14",
                "order": 2,
            },
            {
                "title": "Декоратор арқылы функцияны толықтыру",
                "theory": """
<h3>Функцияны басқа функциямен орау</h3>
<p>Python-да функцияны айнымалыға сақтауға, аргумент ретінде беруге және
басқа функциядан қайтаруға болады. Декоратор функцияны қабылдап, қосымша
әрекеті бар функцияны қайтарады. <code>@decorator</code> жазуы
<code>function = decorator(function)</code> амалын қысқартады.</p>
<p>Ораушы <code>*args</code> және <code>**kwargs</code> арқылы позициялық және
атаулы аргументтерді қабылдайды. Нәтижені міндетті түрде return арқылы
қайтару керек. <code>functools.wraps</code> бастапқы функцияның атын және
құжаттамасын сақтайды.</p>
<h3>Тексерісті бір жерде ұстау</h3>
<p>Мысалда декоратор сандық аргументтердің теріс болмауын тексереді. Бұл
декоратор тек сандық аргумент қабылдайтын функцияларға арналған. Шарт
бұзылса, негізгі функция шақырылмайды; түсінікті ValueError беріледі.
Осылай бірнеше функцияға бірдей тексерісті қайталамай қоса аламыз.</p>
""",
                "code_example": _code('''
                    from functools import wraps

                    def non_negative(function):
                        @wraps(function)
                        def wrapper(*args, **kwargs):
                            values = list(args) + list(kwargs.values())
                            if any(value < 0 for value in values):
                                raise ValueError("Теріс санға рұқсат жоқ")
                            return function(*args, **kwargs)
                        return wrapper

                    @non_negative
                    def rectangle_area(width, height):
                        return width * height

                    print(f"Аудан: {rectangle_area(4, height=3)}")
                    print(f"Атауы: {rectangle_area.__name__}")
                    try:
                        rectangle_area(-2, 5)
                    except ValueError as error:
                        print(f"Қате: {error}")
                '''),
                "task": "non_negative декораторын жазыңыз: сандық позициялық не атаулы аргумент теріс болса ValueError('Теріс санға рұқсат жоқ') көтерсін. functools.wraps қолданыңыз. rectangle_area(width, height) функциясын безендіріп, (4, height=3) ауданын және функцияның __name__ мәнін шығарыңыз. (-2, 5) шақыруының қатесін ұстап, көрсетілген мәтінді шығарыңыз.",
                "expected_output": "Аудан: 12\nАтауы: rectangle_area\nҚате: Теріс санға рұқсат жоқ",
                "order": 3,
            },
            {
                "title": "Контекст менеджері және ресурсты жабу",
                "theory": """
<h3>with блогының өмірлік циклі</h3>
<p>Контекст менеджері ресурсты дайындап, блок аяқталғанда оны босатуды
басқарады. Блок қалыпты аяқталса да, қате пайда болса да, тазалау орындалуы
керек. Файл, дерекқор байланысы және уақытша күй осындай басқаруды қажет етеді.</p>
<p><code>contextlib.contextmanager</code> арқылы генератор функциясын
контекст менеджеріне айналдырамыз. yield алдында ресурс құрылады, yield
мәні <code>as</code> айнымалысына беріледі. yield-тен кейінгі
<code>finally</code> блогы ресурсты жабады. Функцияда бір yield болуы керек.</p>
<h3>Қатеден кейін де тазалау</h3>
<p><code>io.StringIO</code> мәтінді дискіге жазбай, жадта ұстайды. Мысалда
блок әдейі ValueError көтереді, бірақ буфер бәрібір жабылады. Қатені сыртқы
try/except ұстайды: контекст менеджерінде қатені үнсіз жұтудың қажеті жоқ.</p>
""",
                "code_example": _code('''
                    from contextlib import contextmanager
                    from io import StringIO

                    @contextmanager
                    def managed_buffer():
                        buffer = StringIO()
                        print("Ресурс ашылды")
                        try:
                            yield buffer
                        finally:
                            buffer.close()
                            print("Ресурс жабылды")

                    try:
                        with managed_buffer() as buffer:
                            buffer.write("Сәлем")
                            print(f"Мәтін: {buffer.getvalue()}")
                            raise ValueError("Сынақ қатесі")
                    except ValueError as error:
                        print(f"Қате ұсталды: {error}")
                    print(f"Жабық па: {buffer.closed}")
                '''),
                "task": "contextmanager декораторымен StringIO буферін беретін managed_buffer() функциясын жазыңыз. Ашылғанда 'Ресурс ашылды', finally ішінде жабылғанда 'Ресурс жабылды' шығарыңыз. with блогында 'Сәлем' жазыңыз, буфер мәтінін шығарып, ValueError('Сынақ қатесі') көтеріңіз. Қатені сыртта ұстап, соңында buffer.closed мәнін шығарыңыз. Дискіге файл жазбаңыз.",
                "expected_output": "Ресурс ашылды\nМәтін: Сәлем\nРесурс жабылды\nҚате ұсталды: Сынақ қатесі\nЖабық па: True",
                "order": 4,
            },
        ],
    },
    {
        "title": "SQLite және SQL негіздері",
        "description": "Кестелер құру, параметрленген сұраулар, сүзу, топтау, JOIN және транзакциялар арқылы деректермен жұмыс.",
        "icon": "🗄️",
        "difficulty": "intermediate",
        "order": 11,
        "lessons": [
            {
                "title": "Жадтағы дерекқор және алғашқы кесте",
                "theory": """
<h3>Реляциялық дерекқор</h3>
<p>SQL деректерді кестелерде сақтап, сұрауға арналған тіл. Кесте бағандары
мәннің мағынасын сипаттайды, әр жол бір жазба болады. Python стандарт
кітапханасындағы <code>sqlite3</code> қосымша серверсіз SQLite қолданады.</p>
<p><code>sqlite3.connect(':memory:')</code> байланысқа тиесілі уақытша
дерекқорды жадта жасайды. Байланыс жабылғанда ол жоғалады, сондықтан сабақ
мысалы дискіге файл жазбайды. Әр мысал өзінің кестесін қайта құрады.</p>
<h3>CREATE, INSERT, SELECT</h3>
<p><code>PRIMARY KEY</code> жазбаның бірегей идентификаторын анықтайды.
<code>NOT NULL</code> міндетті мәнді талап етеді. executemany() бір сұрауды
бірнеше дерек жиыны үшін орындайды; ? орындарына Python мәндерін беріңіз.
<code>ORDER BY</code> болмаса, нәтиже жолдарының ретіне сүйенуге болмайды.
Транзакцияны commit() арқылы бекітіп, байланысты finally ішінде жабыңыз.</p>
""",
                "code_example": _code('''
                    import sqlite3

                    connection = sqlite3.connect(":memory:")
                    try:
                        connection.execute(
                            "CREATE TABLE books (id INTEGER PRIMARY KEY, "
                            "title TEXT NOT NULL, pages INTEGER NOT NULL)"
                        )
                        connection.executemany(
                            "INSERT INTO books (id, title, pages) VALUES (?, ?, ?)",
                            [(1, "Python", 240), (2, "SQL", 180), (3, "Алгоритмдер", 320)],
                        )
                        connection.commit()
                        rows = connection.execute(
                            "SELECT id, title, pages FROM books ORDER BY id"
                        )
                        for book_id, title, pages in rows:
                            print(f"{book_id}. {title}: {pages} бет")
                    finally:
                        connection.close()
                '''),
                "task": "sqlite3 көмегімен :memory: дерекқорын ашыңыз. books(id INTEGER PRIMARY KEY, title TEXT NOT NULL, pages INTEGER NOT NULL) кестесін құрыңыз. (1, 'Python', 240), (2, 'SQL', 180), (3, 'Алгоритмдер', 320) жазбаларын параметрлермен енгізіңіз. id бойынша сұрыптап, әр кітапты көрсетілген форматпен шығарыңыз. Өзгерістерді бекітіп, байланысты жабыңыз.",
                "expected_output": "1. Python: 240 бет\n2. SQL: 180 бет\n3. Алгоритмдер: 320 бет",
                "order": 1,
            },
            {
                "title": "WHERE, ORDER BY және қауіпсіз параметрлер",
                "theory": """
<h3>Қажетті жазбаларды таңдау</h3>
<p><code>WHERE</code> шартқа сай жолдарды қалдырады. Бірнеше шартты
<code>AND</code> не <code>OR</code> арқылы біріктіруге болады.
<code>ORDER BY price DESC, name ASC</code> алдымен бағаны кемітіп,
тең бағаларды атауы бойынша реттейді. <code>LIMIT</code> жол санын шектейді.</p>
<h3>Мәнді сұрау мәтініне қоспаңыз</h3>
<p>Деректерді f-жолмен SQL мәтініне біріктіру тырнақша қателеріне және SQL
инъекциясына әкелуі мүмкін. Мәндерге <code>?</code> белгісін қойып,
execute() екінші аргументімен кортеж беріңіз. Бір параметр кортежі
<code>(value,)</code> түрінде жазылады. Параметр баған немесе кесте атауын
алмастырмайды: ол тек мән үшін қолданылады.</p>
<p>Мысалда тең бағаға екінші сұрыптау кілті берілген, сондықтан нәтиже тұрақты.
Баған атауларын анық көрсетіп алу кестеге жаңа баған қосылғанда да кодтың
түсінікті болуына көмектеседі.</p>
""",
                "code_example": _code('''
                    import sqlite3

                    connection = sqlite3.connect(":memory:")
                    try:
                        connection.execute(
                            "CREATE TABLE products (name TEXT, category TEXT, price INTEGER)"
                        )
                        connection.executemany(
                            "INSERT INTO products VALUES (?, ?, ?)",
                            [("Қалам", "кеңсе", 200), ("Дәптер", "кеңсе", 500),
                             ("Кітап", "оқу", 1500), ("Маркер", "кеңсе", 500)],
                        )
                        connection.commit()
                        rows = connection.execute(
                            "SELECT name, price FROM products "
                            "WHERE category = ? AND price >= ? "
                            "ORDER BY price DESC, name ASC LIMIT 2",
                            ("кеңсе", 300),
                        )
                        for name, price in rows:
                            print(f"{name}: {price} теңге")
                    finally:
                        connection.close()
                '''),
                "task": "Жадта products(name TEXT, category TEXT, price INTEGER) кестесін құрыңыз. ('Қалам', 'кеңсе', 200), ('Дәптер', 'кеңсе', 500), ('Кітап', 'оқу', 1500), ('Маркер', 'кеңсе', 500) деректерін енгізіңіз. Параметрленген WHERE арқылы санаты 'кеңсе' және бағасы кемінде 300 тауарларды таңдаңыз. price DESC, name ASC ретімен алғашқы екі тауарды 'атау: баға теңге' форматында шығарыңыз.",
                "expected_output": "Дәптер: 500 теңге\nМаркер: 500 теңге",
                "order": 2,
            },
            {
                "title": "GROUP BY және жиынтық функциялар",
                "theory": """
<h3>Жолдарды топтау</h3>
<p><code>GROUP BY</code> бірдей кілті бар жолдарды топқа біріктіреді.
<code>COUNT(*)</code> жол санын, <code>SUM(amount)</code> қосындыны,
<code>AVG(amount)</code> орташа мәнді есептейді. SELECT ішіндегі жиынтық
емес бағандар топтау кілттері болуы керек.</p>
<h3>WHERE пен HAVING айырмашылығы</h3>
<p><code>WHERE</code> жеке жолдарды топтауға дейін сүзеді.
<code>HAVING</code> топтарды жиынтық есептелгеннен кейін сүзеді.
Мысалы, жалпы шығыны кемінде 2000 болған санаттарды HAVING арқылы таңдаймыз.</p>
<p>SUM және AVG NULL мәндерін есепке қоспайды; COUNT(*) барлық жолды санайды.
Мысалда amount міндетті және бүтін сан болғандықтан қосынды нақты есептеледі.
Ақша сомасын ең кіші бірліктегі бүтін санмен сақтау бөлшек сандардың
дөңгелектеу мәселесін болдырмайды. Нәтиже ретін ORDER BY анықтайды.</p>
""",
                "code_example": _code('''
                    import sqlite3

                    connection = sqlite3.connect(":memory:")
                    try:
                        connection.execute(
                            "CREATE TABLE expenses (category TEXT NOT NULL, amount INTEGER NOT NULL)"
                        )
                        connection.executemany(
                            "INSERT INTO expenses VALUES (?, ?)",
                            [("тамақ", 1200), ("көлік", 400), ("тамақ", 800),
                             ("оқу", 3000), ("көлік", 600)],
                        )
                        connection.commit()
                        rows = connection.execute(
                            "SELECT category, COUNT(*), SUM(amount) FROM expenses "
                            "GROUP BY category HAVING SUM(amount) >= ? "
                            "ORDER BY SUM(amount) DESC, category ASC",
                            (2000,),
                        )
                        for category, count, total in rows:
                            print(f"{category}: {count} жазба, {total} теңге")
                    finally:
                        connection.close()
                '''),
                "task": "Жадта expenses(category TEXT NOT NULL, amount INTEGER NOT NULL) кестесін құрыңыз. ('тамақ', 1200), ('көлік', 400), ('тамақ', 800), ('оқу', 3000), ('көлік', 600) шығындарын енгізіңіз. Әр санаттағы жазба санын және қосындыны есептеңіз. HAVING арқылы қосындысы кемінде 2000 топтарды ғана алып, қосындысы кемитін ретпен көрсетілген форматта шығарыңыз.",
                "expected_output": "оқу: 1 жазба, 3000 теңге\nтамақ: 2 жазба, 2000 теңге",
                "order": 3,
            },
            {
                "title": "JOIN және атомарлық транзакция",
                "theory": """
<h3>Байланысты кестелер</h3>
<p>Бір студенттің бірнеше бағасын студент атымен бірге сақтау қайталануға
әкеледі. students кестесінде студенттерді, scores кестесінде student_id
арқылы олардың бағаларын сақтаймыз. <code>JOIN ... ON</code> сәйкес
идентификаторлары бар жолдарды біріктіреді.</p>
<p>SQLite-да сыртқы кілттерді тексеру үшін әр жаңа байланыста
<code>PRAGMA foreign_keys = ON</code> қосыңыз. FOREIGN KEY бөтен студентке
баға тіркеуді болдырмайды. Баға ауқымын CHECK шектеуі қорғайды.</p>
<h3>Бәрі орындалсын немесе ештеңе өзгермесін</h3>
<p><code>with connection:</code> блогы сәтті аяқталса транзакцияны бекітеді,
қате болса өзгерістерді кері қайтарады. Бұл контекст байланысты жаппайды:
соңында close() қажет. Мысалда дұрыс жаңартудан кейін қате баға жазу
талпынысы бар. CHECK қатесі бүкіл блокты кері қайтаратындықтан алғашқы
баға да өзгермейді.</p>
""",
                "code_example": _code('''
                    import sqlite3

                    connection = sqlite3.connect(":memory:")
                    try:
                        connection.execute("PRAGMA foreign_keys = ON")
                        connection.execute(
                            "CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
                        )
                        connection.execute(
                            "CREATE TABLE scores (student_id INTEGER REFERENCES students(id), "
                            "points INTEGER NOT NULL CHECK(points BETWEEN 0 AND 100))"
                        )
                        with connection:
                            connection.executemany(
                                "INSERT INTO students VALUES (?, ?)", [(1, "Айша"), (2, "Диас")]
                            )
                            connection.executemany(
                                "INSERT INTO scores VALUES (?, ?)", [(1, 90), (2, 75)]
                            )
                        try:
                            with connection:
                                connection.execute(
                                    "UPDATE scores SET points = ? WHERE student_id = ?", (95, 1)
                                )
                                connection.execute(
                                    "UPDATE scores SET points = ? WHERE student_id = ?", (120, 2)
                                )
                        except sqlite3.IntegrityError:
                            print("Транзакция кері қайтарылды")
                        rows = connection.execute(
                            "SELECT students.name, scores.points FROM students "
                            "JOIN scores ON students.id = scores.student_id ORDER BY students.id"
                        )
                        for name, points in rows:
                            print(f"{name}: {points}")
                    finally:
                        connection.close()
                '''),
                "task": "Жадта students(id, name) және scores(student_id, points) кестелерін жасаңыз; student_id сыртқы кілт, points үшін 0–100 CHECK шектеуі болсын. Студенттер: (1, 'Айша'), (2, 'Диас'); бағалар: (1, 90), (2, 75). Бір with connection транзакциясында Айшаның бағасын 95-ке, Диастың бағасын 120-ға өзгертіңіз. IntegrityError қатесін ұстап, кері қайтару туралы мәтінді шығарыңыз. JOIN арқылы бастапқы бағалардың сақталғанын id ретімен көрсетіңіз.",
                "expected_output": "Транзакция кері қайтарылды\nАйша: 90\nДиас: 75",
                "order": 4,
            },
        ],
    },
    {
        "title": "Практикалық жобалар және тестілеу",
        "description": "Шығын талдағышы, тапсырмалар тізімі, unittest тексерістері және бағалар есебін құратын қорытынды шағын жоба.",
        "icon": "🛠️",
        "difficulty": "intermediate",
        "order": 12,
        "lessons": [
            {
                "title": "Жоба: шығындарды санат бойынша талдау",
                "theory": """
<h3>Есепті шағын қадамдарға бөлу</h3>
<p>Шығын талдағышының міндеті — жазбаларды оқу, санаттар бойынша қосу және
есеп шығару. Әр шығынды category және amount кілттері бар сөздікпен
сипаттаймыз. amount — теңгемен берілген бүтін сан.</p>
<p>Есептеу функциясы экранға ештеңе шығармай, нәтижені сөздік ретінде
қайтарсын. Мұндай функцияны басқа интерфейсте қайта қолдану және тестілеу
оңай. <code>totals.get(category, 0)</code> жаңа санатты нөлден бастайды.</p>
<h3>Есептің тұрақты реті</h3>
<p>Кіріс деректерінің ретіне тәуелді болмайтын есеп үшін санаттарды
<code>sorted()</code> арқылы шығарамыз. Жалпы соманы totals мәндерін қосып
аламыз. Қалған бюджет — бастапқы бюджет пен шығын айырмасы. Мысал
бюджеттің асып кеткенін теріс қалдық арқылы да көрсете алады; ешбір
дерек өзгертілмейді және файл жазылмайды.</p>
""",
                "code_example": _code('''
                    def summarize_expenses(expenses):
                        totals = {}
                        for expense in expenses:
                            category = expense["category"]
                            totals[category] = totals.get(category, 0) + expense["amount"]
                        return totals

                    expenses = [
                        {"category": "тамақ", "amount": 1200},
                        {"category": "көлік", "amount": 400},
                        {"category": "тамақ", "amount": 800},
                        {"category": "оқу", "amount": 2000},
                    ]
                    totals = summarize_expenses(expenses)
                    for category in sorted(totals):
                        print(f"{category}: {totals[category]} теңге")
                    total = sum(totals.values())
                    print(f"Барлығы: {total} теңге")
                    print(f"Қалдық: {5000 - total} теңге")
                '''),
                "task": "summarize_expenses(expenses) функциясын жазыңыз: ол санатқа сәйкес шығын қосындысын сөздікпен қайтарсын. Жазбалар: {'category': 'тамақ', 'amount': 1200}, {'category': 'көлік', 'amount': 400}, {'category': 'тамақ', 'amount': 800}, {'category': 'оқу', 'amount': 2000}. Санаттарды sorted() ретімен шығарыңыз. Бюджет 5000 теңге: жалпы шығын мен қалған соманы соңғы екі жолға көрсетіңіз.",
                "expected_output": "көлік: 400 теңге\nоқу: 2000 теңге\nтамақ: 2000 теңге\nБарлығы: 4400 теңге\nҚалдық: 600 теңге",
                "order": 1,
            },
            {
                "title": "Жоба: тапсырмалар тізімін басқару",
                "theory": """
<h3>Әр тапсырманың тұрақты идентификаторы</h3>
<p>Тапсырма тізімінде id, title және done өрістерін сақтаймыз. Тізім индексі
тапсырма жойылғанда өзгеруі мүмкін, сондықтан тапсырманы тұрақты id арқылы
іздеген дұрыс. done мәні аяқталғанын көрсететін bool болады.</p>
<p>complete_task() функциясы сәйкес тапсырманы тауып, күйін өзгертеді.
Табылса True, табылмаса False қайтарады. Осы келісім интерфейске
«тапсырма жоқ» жағдайын дұрыс көрсетуге мүмкіндік береді.</p>
<h3>Күйді өзгерту және көрсету</h3>
<p>Мұнда функция кіріс тізіміндегі сөздікті әдейі өзгертеді. Бұл мінезді
құжаттап, тестпен тексеру керек. Көрсету бөлігі есептеуден бөлек болсын:
әр жолдың белгісін done мәнінен анықтаймыз. sum() логикалық мәндермен
жұмыс істегенде True бір, False нөл ретінде есептеледі, сондықтан
аяқталмаған тапсырмалар санын қысқа өрнекпен табуға болады.</p>
""",
                "code_example": _code('''
                    def complete_task(tasks, task_id):
                        for task in tasks:
                            if task["id"] == task_id:
                                task["done"] = True
                                return True
                        return False

                    tasks = [
                        {"id": 1, "title": "Python оқу", "done": False},
                        {"id": 2, "title": "Есеп шығару", "done": False},
                        {"id": 3, "title": "Қайталау", "done": True},
                    ]
                    print(f"2 аяқталды: {complete_task(tasks, 2)}")
                    print(f"99 табылды: {complete_task(tasks, 99)}")
                    for task in tasks:
                        mark = "x" if task["done"] else " "
                        print(f"[{mark}] {task['id']}. {task['title']}")
                    pending = sum(not task["done"] for task in tasks)
                    print(f"Қалғаны: {pending}")
                '''),
                "task": "complete_task(tasks, task_id) функциясын іске асырыңыз: id табылса done=True етіп, True қайтарсын; табылмаса False қайтарсын. Тапсырмалар: (1, 'Python оқу', False), (2, 'Есеп шығару', False), (3, 'Қайталау', True), әрқайсысы id/title/done сөздігі болсын. 2 және 99 идентификаторларын өңдеңіз. Барлық тапсырманы бастапқы ретпен [x] не [ ] белгісімен және соңында аяқталмағандар санын шығарыңыз.",
                "expected_output": "2 аяқталды: True\n99 табылды: False\n[ ] 1. Python оқу\n[x] 2. Есеп шығару\n[x] 3. Қайталау\nҚалғаны: 1",
                "order": 2,
            },
            {
                "title": "Таза функцияны unittest арқылы тексеру",
                "theory": """
<h3>Таза функция</h3>
<p>Таза функция нәтижесін тек аргументтерінен есептейді және сыртқы күйді
өзгертпейді. Бірдей кіріс бірдей нәтиже береді. Орташа баға есептейтін
функция үшін сыртқы файл, желі немесе пайдаланушы енгізуі қажет емес.</p>
<h3>Тест қандай мінезді тексереді?</h3>
<p><code>unittest.TestCase</code> класындағы test_ деп басталатын әдістер
тест болып саналады. assertAlmostEqual бөлшек санды, assertEqual нақты
мәнді, assertRaises күтілетін қатені тексереді. Бос тізімнің мінезін
алдын ала анықтаймыз: ValueError көтеруі керек.</p>
<p>Төменде кәдімгі дерек, бір элемент және бос тізім тексеріледі. Suite пен
TextTestRunner-ді тікелей құру командалық жол аргументтерін оқымайды және
бағдарламаны тоқтатпайды. Runner есебін StringIO-ға жазып, экранға тек
тұрақты нәтиже шығарамыз; сондықтан уақыт көрсеткіші жауапқа араласпайды.</p>
""",
                "code_example": _code('''
                    import unittest
                    from io import StringIO

                    def average_score(scores):
                        if not scores:
                            raise ValueError("Бағалар тізімі бос")
                        return sum(scores) / len(scores)

                    class AverageScoreTests(unittest.TestCase):
                        def test_regular_scores(self):
                            self.assertAlmostEqual(average_score([70, 80, 90]), 80.0)

                        def test_single_score(self):
                            self.assertEqual(average_score([95]), 95.0)

                        def test_empty_scores(self):
                            with self.assertRaises(ValueError):
                                average_score([])

                    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AverageScoreTests)
                    runner = unittest.TextTestRunner(stream=StringIO(), verbosity=0)
                    result = runner.run(suite)
                    print(f"Тексерілді: {result.testsRun}")
                    print(f"Сәтті: {result.wasSuccessful()}")
                    print(f"Орташа: {average_score([70, 80, 90]):.1f}")
                '''),
                "task": "average_score(scores) таза функциясы арифметикалық орташа мәнді қайтарсын; бос тізімге ValueError('Бағалар тізімі бос') көтерсін. unittest арқылы [70, 80, 90] → 80.0, [95] → 95.0 және [] → ValueError жағдайларына үш тест жазыңыз. Suite-ті TextTestRunner(stream=StringIO(), verbosity=0) арқылы іске қосыңыз. Тест санын, wasSuccessful() және [70, 80, 90] орташа мәнін бір ондық таңбамен шығарыңыз. unittest.main() қолданбаңыз.",
                "expected_output": "Тексерілді: 3\nСәтті: True\nОрташа: 80.0",
                "order": 3,
            },
            {
                "title": "Қорытынды жоба: CSV бағалар есебі",
                "theory": """
<h3>Жобаның деректер ағыны</h3>
<p>Шағын жоба үш кезеңнен тұрады: CSV мәтінін оқу, әр студенттің орташа
бағасын есептеу және түсінікті есеп шығару. CSV бағандары атаулары арқылы
қолжетімді болуы үшін <code>csv.DictReader</code> қолданамыз. StringIO
мәтінді файл сияқты оқуға мүмкіндік береді, бірақ дискіге ештеңе жазбайды.</p>
<p>CSV-ден алынған бағалар str болады; арифметикаға дейін int-ке айналдыру
керек. parse_results() функциясы ат пен орташа бағаны кортеждер тізімімен
қайтарады. Оқу мен есептеуді көрсету бөлігінен бөлу тексеруді жеңілдетеді.</p>
<h3>Жобаны аяқтау өлшемдері</h3>
<p>Есеп студенттерді CSV-дегі ретпен көрсетуі, орташа мәнді бір ондық таңбамен
пішімдеуі және 75 не одан жоғары орташа бағаны «өтті» деп белгілеуі керек.
Соңында өткендер санын және барлық студенттердің орташа бағаларының
орташасын көрсетеміз. Мысалдағы әр студентте екі баға бар; нәтиже
берілген тұрақты деректерден толық қайталанады.</p>
""",
                "code_example": _code('''
                    import csv
                    from io import StringIO

                    def parse_results(text):
                        results = []
                        for row in csv.DictReader(StringIO(text)):
                            scores = [int(row["python"]), int(row["sql"])]
                            average = sum(scores) / len(scores)
                            results.append((row["name"], average))
                        return results

                    data = "name,python,sql\\nАйша,90,80\\nДиас,70,60\\nМеруерт,75,85\\n"
                    results = parse_results(data)
                    for name, average in results:
                        status = "өтті" if average >= 75 else "қайта оқу"
                        print(f"{name}: {average:.1f} — {status}")
                    passed = sum(average >= 75 for _, average in results)
                    group_average = sum(average for _, average in results) / len(results)
                    print(f"Өткендер: {passed}/{len(results)}")
                    print(f"Топ орташа бағасы: {group_average:.1f}")
                '''),
                "task": "csv.DictReader және StringIO арқылы мына CSV мәтінін оқыңыз: бірінші жол name,python,sql; кейін Айша,90,80; Диас,70,60; Меруерт,75,85. parse_results(text) функциясы әр студенттің атын және екі бағасының орташа мәнін қайтарсын. Студенттерді бастапқы ретімен көрсетіңіз: орташа мән бір ондық таңбамен, кемінде 75 болса 'өтті', әйтпесе 'қайта оқу'. Соңында өткендер санын және топтың орташа бағасын бір ондық таңбамен шығарыңыз. Файл мен желіні қолданбаңыз.",
                "expected_output": "Айша: 85.0 — өтті\nДиас: 65.0 — қайта оқу\nМеруерт: 80.0 — өтті\nӨткендер: 2/3\nТоп орташа бағасы: 76.7",
                "order": 4,
            },
        ],
    },
]
