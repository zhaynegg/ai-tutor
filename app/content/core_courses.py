"""Additional Kazakh-language courses built from the Python standard library."""

from textwrap import dedent


def _code(source):
    return dedent(source).strip()


CORE_COURSES = [
    {
        "title": "Файлдар және JSON",
        "description": "Мәтіндік файлдарды оқу, жазу және толықтыру. JSON арқылы құрылымды деректерді сақтау.",
        "icon": "📁",
        "difficulty": "intermediate",
        "order": 5,
        "lessons": [
            {
                "title": "Мәтіндік файлды оқу және жазу",
                "theory": """
<h3>Деректерді файлда сақтау</h3>
<p>Айнымалыдағы дерек бағдарлама аяқталғанда жоғалады. Файл ақпаратты кейін қайта оқуға мүмкіндік береді.
<code>open(path, "w", encoding="utf-8")</code> файлды жазу үшін ашады: файл жоқ болса жасайды,
бар болса бұрынғы мазмұнын өшіреді. <code>"r"</code> режимі файлды тек оқиды.</p>
<h3>Файлды дұрыс жабу</h3>
<p><code>with</code> блогы аяқталғанда файл автоматты түрде жабылады. <code>write()</code> мәтінді жазады,
ал <code>read()</code> бүкіл мазмұнын бір жол ретінде қайтарады. Қазақ әріптері дұрыс сақталуы үшін
оқуда да, жазуда да <code>encoding="utf-8"</code> көрсетіңіз.</p>
<h3>Қауіпсіз тәжірибе</h3>
<p>Төмендегі мысал <code>TemporaryDirectory</code> ішінде жұмыс істейді. Блок аяқталғанда уақытша
бума мен оның файлдары жойылады. <code>Path</code> файл жолын ыңғайлы құрастырады.</p>
""",
                "code_example": _code('''
                    from pathlib import Path
                    from tempfile import TemporaryDirectory

                    with TemporaryDirectory() as folder:
                        path = Path(folder) / "greeting.txt"
                        with open(path, "w", encoding="utf-8") as file:
                            file.write("Сәлем, Python!")
                        with open(path, "r", encoding="utf-8") as file:
                            message = file.read()
                        print(message)
                        print(f"Ұзындығы: {len(message)}")
                '''),
                "task": "TemporaryDirectory ішінде note.txt файлын жасаңыз. Оған UTF-8 кодтауымен дәл 'Python үйренемін' мәтінін жазыңыз. Файлды қайта ашып, оқылған мәтінді бір жолға, оның len() арқылы есептелген ұзындығын келесі жолға 'Ұзындығы: N' түрінде шығарыңыз. input() қолданбаңыз.",
                "expected_output": "Python үйренемін\nҰзындығы: 16",
                "order": 1,
            },
            {
                "title": "Жолдарды оқу және файлды толықтыру",
                "theory": """
<h3>Әр жолды жеке өңдеу</h3>
<p>Файлды <code>for line in file</code> циклімен оқуға болады. Бұл тәсіл файлды бірден жадқа жүктемейді.
Жол соңында көбіне <code>\\n</code> таңбасы болады. Оны алып тастау үшін <code>line.rstrip("\\n")</code>
қолданыңыз; <code>strip()</code> екі шеттегі бос орындарды да жоятынын ескеріңіз.</p>
<h3>Толықтыру режимі</h3>
<p><code>"a"</code> режимі жаңа мәтінді файлдың соңына қосады. Бұрынғы мазмұн сақталады.
Жаңа жолды өзіңіз қосуыңыз керек: <code>write("мәтін\\n")</code>. Егер соңғы жолда жаңа жол таңбасы
болмаса, қосылған мәтін сол жолға жалғасады.</p>
<p><code>enumerate(file, start=1)</code> әр жолға нөмір береді. Мысалда бастапқы тізімге бір элемент
қосып, нәтижені ретімен шығарамыз. Уақытша бума тәжірибеден кейін автоматты түрде тазаланады.</p>
""",
                "code_example": _code('''
                    from pathlib import Path
                    from tempfile import TemporaryDirectory

                    with TemporaryDirectory() as folder:
                        path = Path(folder) / "tasks.txt"
                        with open(path, "w", encoding="utf-8") as file:
                            file.write("Оқу\\nЖаттығу\\n")
                        with open(path, "a", encoding="utf-8") as file:
                            file.write("Қайталау\\n")
                        with open(path, "r", encoding="utf-8") as file:
                            for number, line in enumerate(file, start=1):
                                text = line.rstrip("\\n")
                                print(f"{number}. {text}")
                '''),
                "task": "TemporaryDirectory ішінде fruits.txt файлына 'алма\\nалмұрт\\n' мәтінін жазыңыз, содан кейін 'a' режимінде 'өрік\\n' жолын қосыңыз. Файлды циклмен оқып, жаңа жол таңбасын алып тастаңыз. enumerate(..., start=1) арқылы әр жемісті '1. алма' үлгісімен жеке жолға шығарыңыз.",
                "expected_output": "1. алма\n2. алмұрт\n3. өрік",
                "order": 2,
            },
            {
                "title": "JSON жолдары: dumps және loads",
                "theory": """
<h3>Құрылымды ақпарат</h3>
<p>JSON — тізімдер, сөздіктер, сандар, мәтін және логикалық мәндер сақталатын мәтіндік пішім.
Ол бағдарламалар арасында дерек алмасуға ыңғайлы. Python-ның стандартты <code>json</code> модулі
қосымша кітапхана орнатуды қажет етпейді.</p>
<h3>Екі бағыттағы түрлендіру</h3>
<p><code>json.dumps(data)</code> Python нысанын JSON жолына айналдырады.
<code>json.loads(text)</code> JSON жолын Python нысанына айналдырады. JSON-дағы <code>true</code>
Python-да <code>True</code>, ал <code>null</code> — <code>None</code> болады.</p>
<p><code>ensure_ascii=False</code> қазақ әріптерін оқылатын күйде қалдырады.
<code>sort_keys=True</code> сөздік кілттерін сұрыптайды, сондықтан мәтіннің реті тұрақты болады.
JSON мәтінін <code>eval()</code> арқылы өңдемеңіз: дәл осы мақсатқа <code>loads()</code> арналған.</p>
""",
                "code_example": _code('''
                    import json

                    profile = {"name": "Айша", "points": 18, "active": True}
                    text = json.dumps(profile, ensure_ascii=False, sort_keys=True)
                    print(text)
                    restored = json.loads(text)
                    print(restored["name"])
                    print(restored["points"] + 2)
                '''),
                "task": "json модулін импорттаңыз. {'city': 'Алматы', 'temperature': 12} сөздігін json.dumps(..., ensure_ascii=False, sort_keys=True) арқылы JSON жолына айналдырып, шығарыңыз. Сол жолды json.loads() арқылы қайта оқыңыз. Қаланың атауын және температураға 3 қосқан нәтижені жеке жолдарға шығарыңыз.",
                "expected_output": '{"city": "Алматы", "temperature": 12}\nАлматы\n15',
                "order": 3,
            },
            {
                "title": "JSON файлына деректерді сақтау",
                "theory": """
<h3>Файл мен JSON-ды біріктіру</h3>
<p><code>json.dump(data, file)</code> нысанды ашылған файлға жазады.
<code>json.load(file)</code> файлдан оқып, Python нысанын қайтарады. Соңындағы <code>s</code>
әрпі бар <code>dumps/loads</code> жолдармен, ал <code>dump/load</code> файлдармен жұмыс істейді.</p>
<h3>Қайта оқылған деректі өңдеу</h3>
<p>Жазуды аяқтағаннан кейін файлды оқу режимінде қайта ашыңыз. Қайта оқылған тізім мен
сөздіктерге әдеттегі циклдерді, индекстерді және <code>sum()</code> функциясын қолдануға болады.
<code>indent=2</code> JSON файлын адамға оқуға ыңғайлы етіп пішімдейді.</p>
<p>Мысалда өнімдердің атауы мен санын сақтап, файлдан қайта оқылған дерек бойынша жалпы санды
есептейміз. Барлық файлдар уақытша бумада жасалады, сондықтан жұмыс бумасындағы файлдар өзгермейді.</p>
""",
                "code_example": _code('''
                    import json
                    from pathlib import Path
                    from tempfile import TemporaryDirectory

                    items = [{"name": "Қалам", "count": 3}, {"name": "Дәптер", "count": 2}]
                    with TemporaryDirectory() as folder:
                        path = Path(folder) / "items.json"
                        with open(path, "w", encoding="utf-8") as file:
                            json.dump(items, file, ensure_ascii=False, indent=2)
                        with open(path, "r", encoding="utf-8") as file:
                            restored = json.load(file)
                        for item in restored:
                            print(f"{item['name']}: {item['count']}")
                        print(f"Барлығы: {sum(item['count'] for item in restored)}")
                '''),
                "task": "[{'name': 'Айша', 'score': 80}, {'name': 'Диас', 'score': 90}] тізімін TemporaryDirectory ішіндегі scores.json файлына json.dump() арқылы сақтаңыз. UTF-8 және ensure_ascii=False қолданыңыз. Файлды json.load() арқылы қайта оқып, әр оқушыны 'Айша: 80' үлгісімен шығарыңыз. Соңында қайта оқылған бағалардың қосындысын 'Қосынды: 170' түрінде шығарыңыз.",
                "expected_output": "Айша: 80\nДиас: 90\nҚосынды: 170",
                "order": 4,
            },
        ],
    },
    {
        "title": "Қателерді өңдеу және жөндеу",
        "description": "Қате түрлерін тану, try/except қолдану, деректі тексеру және логикалық қателерді табу.",
        "icon": "🔎",
        "difficulty": "intermediate",
        "order": 6,
        "lessons": [
            {
                "title": "Қате түрлері және try/except",
                "theory": """
<h3>Қателерді ажырату</h3>
<p>Синтаксистік қате кодтың құрылымы дұрыс болмағанда пайда болады: мысалы, қос нүкте жетіспейді.
Оны бағдарлама іске қосылмай тұрып түзету керек. Орындау қатесі дұрыс жазылған код белгілі бір
дерекпен жұмыс істегенде пайда болады: <code>int("алма")</code> — <code>ValueError</code>,
нөлге бөлу — <code>ZeroDivisionError</code>.</p>
<h3>Күтілетін қатені ұстау</h3>
<p><code>try</code> блогында қате болуы мүмкін әрекет орындалады. Сәйкес <code>except</code>
блогы сол қатені өңдейді. Қате өңделсе, бағдарлама әрі қарай жалғасады. Нақты қате түрін көрсетіңіз:
барлық қатені үнсіз ұстау басқа ақауларды жасыруы мүмкін.</p>
<p>Мысалда әр жолды санға айналдыруды жеке тексереміз. Бір жарамсыз мән қалған мәндердің өңделуіне
кедергі келтірмейді.</p>
""",
                "code_example": _code('''
                    values = ["12", "алма", "7"]
                    for text in values:
                        try:
                            number = int(text)
                        except ValueError:
                            print(f"Сан емес: {text}")
                        else:
                            print(f"Екі есесі: {number * 2}")
                    print("Өңдеу аяқталды")
                '''),
                "task": "['8', 'қате', '15'] тізіміндегі әр жолды int() арқылы санға айналдырыңыз. ValueError пайда болса 'Жарамсыз сан' деп шығарыңыз. Санға айналдыру сәтті болса санға 1 қосып шығарыңыз. Әр нәтижені жеке жолға шығарыңыз; input() қолданбаңыз.",
                "expected_output": "9\nЖарамсыз сан\n16",
                "order": 1,
            },
            {
                "title": "else, finally және бірнеше қате",
                "theory": """
<h3>Әр жағдайға жеке жауап</h3>
<p>Бір <code>try</code> блогында бірнеше қате түрі туындауы мүмкін. Бірнеше <code>except</code>
блогы оларды бөлек өңдейді. Мысалы, бөлгіш мәтінін санға айналдыру <code>ValueError</code>,
ал есептеу <code>ZeroDivisionError</code> туындатуы мүмкін.</p>
<h3>Сәтті аяқталу және тазалау</h3>
<p><code>else</code> блогы <code>try</code> қатесіз аяқталса ғана орындалады.
<code>finally</code> блогы қате болғанына қарамастан орындалады; ол ресурсты босату сияқты
қорытынды әрекеттерге арналған. Файлдар үшін көбіне <code>with</code> ыңғайлырақ.</p>
<p><code>try</code> ішіне қате болуы мүмкін аз ғана кодты орналастырыңыз. Сонда қай әрекетті
өңдеп жатқаныңыз түсінікті болады. Мысалда әр есеп аяқталғаннан кейін тұрақты хабарлама шығарамыз.</p>
""",
                "code_example": _code('''
                    for text in ["4", "0", "abc"]:
                        try:
                            denominator = int(text)
                            result = 20 // denominator
                        except ValueError:
                            print("Бүтін сан қажет")
                        except ZeroDivisionError:
                            print("Нөлге бөлуге болмайды")
                        else:
                            print(f"Нәтиже: {result}")
                        finally:
                            print("Тексеру аяқталды")
                '''),
                "task": "['3', '0', 'мәтін'] тізіміндегі әр жолды int() арқылы санға айналдырып, 12 // сан нәтижесін есептеңіз. ValueError үшін 'Сан қажет', ZeroDivisionError үшін 'Нөлге бөлуге болмайды' шығарыңыз. else ішінде сәтті нәтижені 'Нәтиже: N' түрінде шығарыңыз. finally ішінде әр әрекеттен кейін 'Аяқталды' шығарыңыз.",
                "expected_output": "Нәтиже: 4\nАяқталды\nНөлге бөлуге болмайды\nАяқталды\nСан қажет\nАяқталды",
                "order": 2,
            },
            {
                "title": "raise арқылы деректерді тексеру",
                "theory": """
<h3>Функцияның талаптарын қорғау</h3>
<p>Код синтаксистік тұрғыдан дұрыс болса да, берілген мән ережеге сәйкес келмеуі мүмкін.
Мысалы, тест бағасы 0 мен 100 аралығында болуы керек. Функция мұндай деректі бірден тексеріп,
<code>raise ValueError("хабарлама")</code> арқылы қатені анық түсіндіре алады.</p>
<h3>Тексеру мен өңдеуді бөлу</h3>
<p>Функция жарамсыз мән туралы қате туындатады, ал оны шақырған код пайдаланушыға не көрсету
керегін шешеді. <code>except ValueError as error</code> қатенің хабарламасын алуға мүмкіндік береді.
Қате орнына жалған нәтиже қайтару кейінгі есептеуді шатастыруы мүмкін.</p>
<p>Шекараларды тексеріңіз: осы мысалда 0 және 100 жарамды, -1 және 101 жарамсыз.
<code>assert</code> әзірлеуші болжамдарын тексеруге арналған; пайдаланушы дерегін тексеруде
ашық <code>if</code> және <code>raise</code> қолданыңыз.</p>
""",
                "code_example": _code('''
                    def validate_score(score):
                        if not 0 <= score <= 100:
                            raise ValueError("Баға 0 мен 100 аралығында болуы керек")
                        return score

                    for score in [75, -2, 100]:
                        try:
                            valid_score = validate_score(score)
                        except ValueError as error:
                            print(error)
                        else:
                            print(f"Қабылданды: {valid_score}")
                '''),
                "task": "validate_age(age) функциясын жазыңыз: age 0 мен 120 аралығында болса age мәнін қайтарсын, әйтпесе ValueError('Жас 0 мен 120 аралығында болуы керек') туындатсын. Функцияны [20, -1, 121, 0] мәндеріне ретімен қолданыңыз. Жарамды мәнді 'Жас: N' түрінде, қатені except ValueError as error арқылы оның хабарламасы ретінде шығарыңыз.",
                "expected_output": "Жас: 20\nЖас 0 мен 120 аралығында болуы керек\nЖас 0 мен 120 аралығында болуы керек\nЖас: 0",
                "order": 3,
            },
            {
                "title": "Логикалық қателер және шекаралық жағдайлар",
                "theory": """
<h3>Бағдарлама істейді, бірақ нәтиже қате</h3>
<p>Логикалық қате Python қатесін туындатпайды. Мысалы, <code>range(1, n)</code> n санын қамтымайды.
Егер 1-ден n-ге дейін қосынды қажет болса, соңғы шекара <code>n + 1</code> болуы керек.</p>
<h3>Жөндеу қадамдары</h3>
<ol><li>Күтілетін нәтижені шағын мысал үшін қолмен есептеңіз.</li>
<li>Аралық мәндерді <code>print()</code> арқылы қарап шығыңыз.</li>
<li>Қатені түзетіп, бірнеше жағдайды қайта тексеріңіз.</li></ol>
<p>0, 1, бос тізім немесе соңғы индекс сияқты шекаралық жағдайлар пайдалы. <code>assert</code>
шарты ақиқат болса ештеңе шығармайды, жалған болса <code>AssertionError</code> туындатады.
Ол әзірлеу кезіндегі тексеруге қолайлы. Мысал функцияны үш белгілі нәтижемен салыстырады.</p>
""",
                "code_example": _code('''
                    def sum_to(n):
                        total = 0
                        for number in range(1, n + 1):
                            total += number
                        return total

                    assert sum_to(0) == 0
                    assert sum_to(1) == 1
                    assert sum_to(4) == 10
                    print(f"1-ден 4-ке дейін: {sum_to(4)}")
                    print("Үш тексеру сәтті өтті")
                '''),
                "task": "count_even(numbers) функциясын жазыңыз: ол тізімдегі жұп сандардың санын қайтарсын. Бос тізім үшін 0, [1] үшін 0, [0, 2, 3, 4] үшін 3 қайтаруын assert арқылы тексеріңіз. Содан кейін count_even([0, 2, 3, 4]) нәтижесін 'Жұп сандар: 3' түрінде және келесі жолға 'Тексерулер сәтті өтті' шығарыңыз.",
                "expected_output": "Жұп сандар: 3\nТексерулер сәтті өтті",
                "order": 4,
            },
        ],
    },
    {
        "title": "Модульдер және стандартты кітапхана",
        "description": "import, math, datetime, collections модульдері және өз модуліңізді жасау.",
        "icon": "🧰",
        "difficulty": "intermediate",
        "order": 7,
        "lessons": [
            {
                "title": "import және math модулі",
                "theory": """
<h3>Дайын кодты қолдану</h3>
<p>Модуль — функциялар, тұрақтылар және сыныптар жинақталған Python файлы.
<code>import math</code> математикалық құралдарды жүктейді. Одан кейін атауды модуль арқылы
қолданамыз: <code>math.sqrt(25)</code>. Бұл функцияның қайдан келгенін анық көрсетеді.</p>
<h3>Импорттың басқа түрлері</h3>
<p><code>from math import ceil</code> тек бір атауды әкеледі: оны <code>ceil(2.3)</code> деп шақырасыз.
<code>import math as m</code> модульге қысқа ат береді. <code>from math import *</code> атауларды
шатастыруы мүмкін, сондықтан нақты импортты таңдаңыз.</p>
<p><code>sqrt()</code> квадрат түбірін, <code>ceil()</code> жоғары жаққа дөңгелектелген бүтін санды,
<code>floor()</code> төмен жаққа дөңгелектелген бүтін санды қайтарады.
<code>math</code> Python-мен бірге келеді және оны орнатудың қажеті жоқ.</p>
""",
                "code_example": _code('''
                    import math
                    from math import ceil

                    print(f"Түбір: {math.sqrt(49):.0f}")
                    print(f"Жоғары: {ceil(4.2)}")
                    print(f"Төмен: {math.floor(4.8)}")
                    radius = 2
                    print(f"Аудан: {math.pi * radius ** 2:.2f}")
                '''),
                "task": "math модулін импорттаңыз. math.sqrt(81) нәтижесін '.0f' пішімімен 'Түбір: 9' түрінде, math.ceil(3.2) нәтижесін 'Жоғары: 4' түрінде, math.floor(3.8) нәтижесін 'Төмен: 3' түрінде жеке жолдарға шығарыңыз.",
                "expected_output": "Түбір: 9\nЖоғары: 4\nТөмен: 3",
                "order": 1,
            },
            {
                "title": "datetime: күндер мен аралықтар",
                "theory": """
<h3>Күнді арнайы типпен сақтау</h3>
<p><code>datetime.date(year, month, day)</code> күнтізбелік күнді білдіреді. Бұл күнді жай жолға
қарағанда салыстыруға және есептеуге ыңғайлы. Мысалы, екі күннің айырмасы <code>timedelta</code>
нысанын береді; оның <code>.days</code> атрибуты күн санын көрсетеді.</p>
<h3>Күнді жылжыту және пішімдеу</h3>
<p><code>timedelta(days=7)</code> жеті күндік аралық жасайды. Оны күнге қоссаңыз, келесі күн
алынады; ай мен жыл ауысуын кітапхана өзі есептейді. <code>isoformat()</code> нәтижені
<code>YYYY-MM-DD</code> түрінде береді.</p>
<p><code>date.fromisoformat("2026-05-10")</code> ISO жолын күнге түрлендіреді.
Жаттығуда нақты бекітілген күндерді қолданамыз: нәтиже бағдарламаны қай күні орындағаныңызға
тәуелді болмайды.</p>
""",
                "code_example": _code('''
                    from datetime import date, timedelta

                    start = date(2026, 5, 10)
                    deadline = start + timedelta(days=7)
                    finish = date.fromisoformat("2026-05-13")
                    print(f"Басталуы: {start.isoformat()}")
                    print(f"Мерзімі: {deadline.isoformat()}")
                    print(f"Өткен күн: {(finish - start).days}")
                '''),
                "task": "from datetime import date, timedelta қолданыңыз. start = date(2026, 1, 30) күнін жасап, оған timedelta(days=5) қосыңыз. Нәтижені isoformat() арқылы 'Мерзімі: 2026-02-04' түрінде шығарыңыз. date(2026, 2, 10) мен start айырмасының .days мәнін 'Аралық: 11 күн' түрінде келесі жолға шығарыңыз.",
                "expected_output": "Мерзімі: 2026-02-04\nАралық: 11 күн",
                "order": 2,
            },
            {
                "title": "collections: санау және кезек",
                "theory": """
<h3>Қайталанатын элементтерді санау</h3>
<p><code>collections.Counter</code> тізімдегі әр мәннің кездесу санын сақтайды. Нәтиже сөздікке
ұқсайды: <code>counts["алма"]</code> алма санын береді. Жоқ элемент үшін 0 қайтарылады.
Нәтижені әліпби ретімен шығару үшін <code>sorted(counts)</code> қолданыңыз.</p>
<h3>Кезекпен өңдеу</h3>
<p><code>deque</code> екі шетінен элемент қосуға және алуға арналған.
<code>append()</code> соңына қосады, <code>popleft()</code> басынан алады.
Осылайша бірінші келген элемент бірінші өңделетін кезек құра аласыз.</p>
<p>Бос кезектен элемент алу <code>IndexError</code> туындатады. Алдымен <code>if queue</code>
немесе <code>while queue</code> арқылы тексеріңіз. Мысалда Counter өнімдерді санайды,
ал deque екі тапсырманы ретімен өңдейді.</p>
""",
                "code_example": _code('''
                    from collections import Counter, deque

                    counts = Counter(["алма", "өрік", "алма", "өрік", "алма"])
                    for fruit in sorted(counts):
                        print(f"{fruit}: {counts[fruit]}")
                    queue = deque(["Бірінші", "Екінші"])
                    while queue:
                        print(f"Орындалды: {queue.popleft()}")
                '''),
                "task": "Counter арқылы ['A', 'B', 'A', 'C', 'B', 'A'] тізіміндегі мәндерді санаңыз. sorted(counts) ретімен 'A: 3' үлгісінде әр санды шығарыңыз. Содан кейін deque(['Айша', 'Диас']) кезегін while циклімен өңдеп, popleft() арқылы алынған әр есімді 'Келесі: Айша' үлгісінде шығарыңыз.",
                "expected_output": "A: 3\nB: 2\nC: 1\nКелесі: Айша\nКелесі: Диас",
                "order": 3,
            },
            {
                "title": "Өз модуліңізді жасау",
                "theory": """
<h3>Функцияларды бөлек файлға жинау</h3>
<p>Көлемді бағдарламаны модульдерге бөлу кодты қайта қолдануды жеңілдетеді. Мысалы,
<code>helpers.py</code> ішінде <code>double()</code> функциясы тұрса, сол бумадағы негізгі
файлда <code>import helpers</code> деп жазып, <code>helpers.double(6)</code> шақыруға болады.</p>
<h3>Модуль жүктелгенде не болады?</h3>
<p>Импорт кезінде модульдің жоғарғы деңгейдегі коды орындалады. Файлды тікелей іске қосқанда
ғана орындалатын мысалдарды <code>if __name__ == "__main__":</code> блогына орналастырыңыз.
Файлға <code>math.py</code> немесе <code>json.py</code> сияқты стандартты модульдің атын бермеңіз.</p>
<p>Төмендегі бір файлдық мысалда модуль уақытша бумада жасалады. <code>importlib.util</code>
оны нақты жолымен жүктейді, сондықтан жұмыс бумасына файл жазу және <code>sys.path</code>
тізімін өзгерту қажет емес. Күнделікті жобада жай <code>import</code> жеткілікті.</p>
""",
                "code_example": _code('''
                    import importlib.util
                    from pathlib import Path
                    from tempfile import TemporaryDirectory

                    with TemporaryDirectory() as folder:
                        path = Path(folder) / "helpers.py"
                        path.write_text(
                            "def double(number):\\n    return number * 2\\n",
                            encoding="utf-8",
                        )
                        spec = importlib.util.spec_from_file_location("lesson_helpers", path)
                        helpers = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(helpers)
                        print(helpers.double(6))
                        print(helpers.double(10))
                '''),
                "task": "TemporaryDirectory ішінде numbers.py файлын жасаңыз. Файлға def square(number): функциясын және төрт бос орынмен шегіндірілген return number ** 2 жолын жазыңыз. Мысалдағы importlib.util тәсілімен файлды lesson_numbers деген атпен жүктеңіз. Жүктелген модульдің square(4) және square(7) нәтижелерін жеке жолдарға шығарыңыз. Уақытша бумадан тыс файл жасамаңыз.",
                "expected_output": "16\n49",
                "order": 4,
            },
        ],
    },
    {
        "title": "Сыныптар және объектіге бағытталған бағдарламалау",
        "description": "class, атрибуттар, әдістер, мұрагерлік және нысандарды біріктіру арқылы шағын модельдер жасау.",
        "icon": "🧱",
        "difficulty": "intermediate",
        "order": 8,
        "lessons": [
            {
                "title": "Сынып, нысан және __init__",
                "theory": """
<h3>Дерек пен әрекетті біріктіру</h3>
<p>Сынып (<code>class</code>) нысанның үлгісін сипаттайды. Нысан — сол үлгіден жасалған жеке
дана. Мысалы, <code>Student</code> сыныбынан әртүрлі аты мен бағасы бар бірнеше оқушы жасауға болады.</p>
<h3>Бастапқы күй</h3>
<p><code>__init__()</code> жаңа нысан жасалғанда оның атрибуттарын орнатады.
<code>self</code> — ағымдағы нысанға сілтеме. <code>self.name = name</code> мәнді нақты осы
нысанда сақтайды. Нысанды <code>Student("Айша", 90)</code> деп жасағанда <code>self</code>
аргументін Python өзі береді.</p>
<p>Атрибутты нүкте арқылы оқимыз: <code>student.name</code>. Бір нысанның бағасын өзгерту басқа
нысанға әсер етпейді. Төмендегі екі оқушының аттары мен бағалары бөлек сақталады.</p>
""",
                "code_example": _code('''
                    class Student:
                        def __init__(self, name, score):
                            self.name = name
                            self.score = score

                    first = Student("Айша", 90)
                    second = Student("Диас", 75)
                    first.score += 5
                    print(f"{first.name}: {first.score}")
                    print(f"{second.name}: {second.score}")
                '''),
                "task": "Book сыныбын жасаңыз. __init__(self, title, pages) ішінде self.title және self.pages атрибуттарын орнатыңыз. Book('Абай жолы', 300) және Book('Python негіздері', 180) нысандарын жасаңыз. Әр нысанды 'Абай жолы: 300 бет' үлгісімен жеке жолға шығарыңыз.",
                "expected_output": "Абай жолы: 300 бет\nPython негіздері: 180 бет",
                "order": 1,
            },
            {
                "title": "Әдістер және нысан күйін өзгерту",
                "theory": """
<h3>Нысанның әрекеттері</h3>
<p>Әдіс — сыныптың ішінде анықталған функция. Ол <code>self</code> арқылы нысанның атрибуттарын
оқиды немесе өзгертеді. Мысалы, есептегіштің <code>increment()</code> әдісі оның санын арттырады.
Әдісті <code>counter.increment()</code> деп шақырамыз.</p>
<h3>Күйдің жарамдылығын сақтау</h3>
<p>Күйді өзгертпес бұрын жаңа мәнді тексеруге болады. Мысалда <code>add()</code> теріс ұпайды
қабылдамайды. Шарт бұзылса, атрибут өзгермей тұрып <code>ValueError</code> туындайды.
<code>summary()</code> әдісі мәтінді қайтарып, оны экранға шығару шешімін шақырушы кодқа қалдырады.</p>
<p>Әдістің мән қайтаруы мен <code>print()</code> жасауы әртүрлі. Нәтижені басқа есептеуге
немесе тексеруге пайдалану қажет болса, <code>return</code> қолданыңыз.</p>
""",
                "code_example": _code('''
                    class ScoreBoard:
                        def __init__(self, name):
                            self.name = name
                            self.points = 0

                        def add(self, amount):
                            if amount < 0:
                                raise ValueError("Ұпай теріс болмауы керек")
                            self.points += amount

                        def summary(self):
                            return f"{self.name}: {self.points} ұпай"

                    board = ScoreBoard("Айша")
                    board.add(10)
                    board.add(5)
                    print(board.summary())
                '''),
                "task": "Counter сыныбын жасаңыз: __init__ ішінде self.value = 0 орнатыңыз. add(self, amount) әдісі amount теріс болса ValueError('Теріс санға болмайды') туындатсын, әйтпесе self.value мәніне amount қоссын. Нысанға add(3), add(2) қолданып, value мәнін шығарыңыз. add(-1) қатесін except арқылы хабарламасымен шығарыңыз. Соңында value мәнін қайта шығарыңыз: жарамсыз әрекет оны өзгертпеуі керек.",
                "expected_output": "5\nТеріс санға болмайды\n5",
                "order": 2,
            },
            {
                "title": "Мұрагерлік және әдісті қайта анықтау",
                "theory": """
<h3>Ортақ кодты пайдалану</h3>
<p>Мұрагерлік бір сыныпты басқа сыныптың негізінде жасауға мүмкіндік береді.
<code>class Dog(Animal)</code> жазылса, Dog ата-анасының атрибуттары мен әдістерін алады.
<code>super().__init__(name)</code> ата-ананың бастапқы орнату кодын шақырады.</p>
<h3>Өз әрекетін анықтау</h3>
<p>Туынды сынып ата-анасында бар әдісті қайта анықтай алады. Dog пен Cat екеуінде де
<code>speak()</code> бар, бірақ нәтижелері әртүрлі. Бір цикл әр нысанның өз әдісін шақырады:
бұл полиморфизмнің қарапайым мысалы.</p>
<p>Мұрагерлікті «осы нысан сол түрге жатады» байланысы болғанда қолданыңыз: ит — жануар.
Егер бір нысан екінші нысанды құрамында сақтаса, келесі сабақтағы композиция жиі түсініктірек.</p>
""",
                "code_example": _code('''
                    class Animal:
                        def __init__(self, name):
                            self.name = name

                        def speak(self):
                            return "Дыбыс"

                    class Dog(Animal):
                        def __init__(self, name):
                            super().__init__(name)

                        def speak(self):
                            return "Гав"

                    class Cat(Animal):
                        def speak(self):
                            return "Мияу"

                    for animal in [Dog("Ақтөс"), Cat("Мысық")]:
                        print(f"{animal.name}: {animal.speak()}")
                '''),
                "task": "Shape сыныбында area(self) әдісі 0 қайтарсын. Rectangle(Shape) сыныбының __init__(self, width, height) әдісі өлшемдерді сақтасын, area() әдісі width * height қайтарсын. Square(Rectangle) сыныбында __init__(self, side) арқылы super().__init__(side, side) шақырыңыз. [Rectangle(4, 3), Square(5)] тізімін циклмен өтіп, әр нысанның area() нәтижесін жеке жолға шығарыңыз.",
                "expected_output": "12\n25",
                "order": 3,
            },
            {
                "title": "Композиция және dataclass",
                "theory": """
<h3>Нысандарды біріктіру</h3>
<p>Композицияда бір нысан басқа нысандарды құрамында сақтайды. Мысалы, тапсырыс бірнеше
тауардан тұрады. Тауар өз атауы мен бағасын сақтайды, ал тапсырыс олардың жалпы құнын есептейді.
Бұл әр сыныпқа анық жауапкершілік береді.</p>
<h3>Қысқа деректер сыныбы</h3>
<p>Стандартты <code>dataclasses</code> модулінің <code>@dataclass</code> декораторы атрибуттар
бойынша <code>__init__()</code> сияқты әдістерді автоматты жасайды. <code>name: str</code>
және <code>price: int</code> — тип аннотациялары; олар Python-да мәнді өздігінен тексермейді.</p>
<p>Әр тапсырысқа бөлек тізім жасаңыз: <code>self.items = []</code> бастапқы әдістің ішінде тұруы
керек. Сынып деңгейіндегі ортақ тізім барлық нысанға ортақ болып, күтпеген нәтиже беруі мүмкін.</p>
""",
                "code_example": _code('''
                    from dataclasses import dataclass

                    @dataclass
                    class Product:
                        name: str
                        price: int

                    class Order:
                        def __init__(self):
                            self.items = []

                        def add(self, product):
                            self.items.append(product)

                        def total(self):
                            return sum(item.price for item in self.items)

                    order = Order()
                    order.add(Product("Қалам", 200))
                    order.add(Product("Дәптер", 500))
                    print(f"Тауар саны: {len(order.items)}")
                    print(f"Жалпы құны: {order.total()} теңге")
                '''),
                "task": "@dataclass арқылы name: str және minutes: int атрибуттары бар LessonItem сыныбын жасаңыз. StudyPlan сыныбының __init__ ішінде self.lessons = [] жасаңыз; add(self, lesson) тізімге нысан қоссын, total_minutes(self) барлық minutes мәндерінің қосындысын қайтарсын. Жоспарға LessonItem('Файлдар', 20) және LessonItem('JSON', 25) қосыңыз. Сабақ санын 'Сабақ саны: 2', жалпы уақытты 'Жалпы уақыт: 45 минут' түрінде шығарыңыз. Екінші бос StudyPlan жасап, оның жалпы уақытын 'Бос жоспар: 0 минут' түрінде шығарыңыз.",
                "expected_output": "Сабақ саны: 2\nЖалпы уақыт: 45 минут\nБос жоспар: 0 минут",
                "order": 4,
            },
        ],
    },
]
