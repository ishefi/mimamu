#!/usr/bin/env python
stopwords = (
    '0o',
    '0s',
    '3a',
    '3b',
    '3d',
    '6b',
    '6o',
    'a',
    'a1',
    'a2',
    'a3',
    'a4',
    'ab',
    'able',
    'above',
    'abst',
    'ac',
    'accordance',
    'according',
    'accordingly',
    'across',
    'act',
    'actually',
    'ad',
    'added',
    'adj',
    'ae',
    'af',
    'affected',
    'affecting',
    'affects',
    'after',
    'afterwards',
    'ag',
    'again',
    'against',
    'ah',
    'ain',
    "ain't",
    'aj',
    'al',
    'allow',
    'allows',
    'almost',
    'along',
    'already',
    'although',
    'always',
    'am',
    'among',
    'amongst',
    'amoungst',
    'amount',
    'an',
    'and',
    'announce',
    'another',
    'any',
    'anybody',
    'anyhow',
    'anymore',
    'anyone',
    'anything',
    'anyway',
    'anyways',
    'anywhere',
    'ao',
    'ap',
    'apart',
    'apparently',
    'appear',
    'appreciate',
    'appropriate',
    'approximately',
    'ar',
    'are',
    'aren',
    'arent',
    "aren't",
    'arise',
    'around',
    'as',
    "a's",
    'aside',
    'ask',
    'asking',
    'associated',
    'at',
    'au',
    'auth',
    'av',
    'available',
    'aw',
    'away',
    'ax',
    'ay',
    'az',
    'b',
    'b1',
    'b2',
    'b3',
    'ba',
    'bc',
    'bd',
    'became',
    'because',
    'become',
    'becomes',
    'becoming',
    'been',
    'beforehand',
    'begin',
    'beginning',
    'beginnings',
    'begins',
    'behind',
    'believe',
    'below',
    'beside',
    'besides',
    'beyond',
    'bi',
    'bill',
    'biol',
    'bj',
    'bk',
    'bl',
    'bn',
    'both',
    'bottom',
    'bp',
    'br',
    'brief',
    'briefly',
    'bs',
    'bt',
    'bu',
    'but',
    'bx',
    'by',
    'c',
    'c1',
    'c2',
    'c3',
    'ca',
    'can',
    'cannot',
    'cant',
    "can't",
    'cause',
    'causes',
    'cc',
    'cd',
    'ce',
    'certain',
    'certainly',
    'cf',
    'cg',
    'ch',
    'changes',
    'ci',
    'cit',
    'cj',
    'cl',
    'clearly',
    'cm',
    "c'mon",
    'cn',
    'co',
    'com',
    'come',
    'comes',
    'con',
    'concerning',
    'consequently',
    'consider',
    'considering',
    'contain',
    'containing',
    'contains',
    'corresponding',
    'could',
    'couldn',
    'couldnt',
    "couldn't",
    'course',
    'cp',
    'cq',
    'cr',
    'cry',
    'cs',
    "c's",
    'ct',
    'cu',
    'currently',
    'cv',
    'cx',
    'cy',
    'cz',
    'd',
    'd2',
    'dc',
    'dd',
    'de',
    'definitely',
    'describe',
    'described',
    'despite',
    'detail',
    'df',
    'di',
    'did',
    'didn',
    "didn't",
    'dj',
    'dk',
    'dl',
    'down',
    'downwards',
    'dp',
    'dr',
    'ds',
    'dt',
    'du',
    'due',
    'during',
    'dx',
    'dy',
    'e',
    'e2',
    'e3',
    'ea',
    'ec',
    'ed',
    'edu',
    'ee',
    'ef',
    'effect',
    'eg',
    'ei',
    'eight',
    'eighty',
    'either',
    'ej',
    'el',
    'eleven',
    'else',
    'elsewhere',
    'em',
    'empty',
    'en',
    'ending',
    'enough',
    'eo',
    'ep',
    'eq',
    'er',
    'es',
    'especially',
    'est',
    'et',
    'et-al',
    'etc',
    'eu',
    'ev',
    'even',
    'ex',
    'exactly',
    'example',
    'except',
    'ey',
    'f',
    'f2',
    'fa',
    'far',
    'fc',
    'few',
    'ff',
    'fi',
    'fill',
    'find',
    'fix',
    'fj',
    'fl',
    'fn',
    'fo',
    'followed',
    'following',
    'follows',
    'for',
    'former',
    'formerly',
    'forth',
    'forty',
    'found',
    'fr',
    'from',
    'front',
    'fs',
    'ft',
    'fu',
    'further',
    'furthermore',
    'fy',
    'g',
    'ga',
    'ge',
    'gi',
    'gj',
    'gl',
    'go',
    'gr',
    'gs',
    'gy',
    'h',
    'h2',
    'h3',
    'had',
    'hadn',
    "hadn't",
    'has',
    'hasn',
    'hasnt',
    "hasn't",
    'have',
    'haven',
    "haven't",
    'he',
    'hed',
    "he'd",
    "he'll",
    'hello',
    'help',
    'hence',
    'her',
    'here',
    'hereafter',
    'hereby',
    'herein',
    'heres',
    "here's",
    'hereupon',
    'hers',
    'herself',
    'hes',
    "he's",
    'hh',
    'hi',
    'hid',
    'him',
    'himself',
    'his',
    'hither',
    'hj',
    'ho',
    'home',
    'hopefully',
    'how',
    'howbeit',
    'however',
    "how's",
    'hr',
    'hs',
    'http',
    'hu',
    'hundred',
    'hy',
    'i',
    'i2',
    'i3',
    'i4',
    'i6',
    'i7',
    'i8',
    'ia',
    'ib',
    'ibid',
    'ic',
    'id',
    "i'd",
    'ie',
    'if',
    'ig',
    'ignored',
    'ih',
    'ii',
    'ij',
    'il',
    "i'll",
    'im',
    "i'm",
    'in',
    'inc',
    'inner',
    'into',
    'inward',
    'io',
    'ip',
    'iq',
    'ir',
    'is',
    'isn',
    "isn't",
    'it',
    'itd',
    "it'd",
    "it'll",
    'its',
    "it's",
    'itself',
    'iv',
    "i've",
    'ix',
    'iy',
    'iz',
    'j',
    'jj',
    'jr',
    'js',
    'jt',
    'ju',
    'just',
    'k',
    'ke',
    'keep',
    'keeps',
    'kept',
    'kg',
    'kj',
    'km',
    'know',
    'known',
    'knows',
    'ko',
    'l',
    'l2',
    'la',
    'largely',
    'lately',
    'later',
    'latter',
    'latterly',
    'lb',
    'lc',
    'le',
    'least',
    'les',
    'less',
    'lest',
    'let',
    'lets',
    "let's",
    'lf',
    'like',
    'liked',
    'likely',
    'lj',
    'll',
    'll',
    'ln',
    'lo',
    'los',
    'lr',
    'ls',
    'lt',
    'ltd',
    'm',
    'm2',
    'ma',
    'mainly',
    'may',
    'me',
    'mean',
    'means',
    'meantime',
    'meanwhile',
    'merely',
    'mg',
    'might',
    'mightn',
    "mightn't",
    'mill',
    'million',
    'mine',
    'miss',
    'ml',
    'mn',
    'mo',
    'more',
    'moreover',
    'most',
    'mostly',
    'move',
    'mr',
    'mrs',
    'ms',
    'mt',
    'mu',
    'much',
    'mug',
    'must',
    'mustn',
    "mustn't",
    'my',
    'myself',
    'n',
    'n2',
    'na',
    'name',
    'namely',
    'nay',
    'nc',
    'nd',
    'ne',
    'near',
    'nearly',
    'necessarily',
    'necessary',
    'need',
    'needn',
    "needn't",
    'needs',
    'neither',
    'never',
    'nevertheless',
    'next',
    'ng',
    'ni',
    'nine',
    'ninety',
    'nj',
    'nl',
    'nn',
    'no',
    'nobody',
    'non',
    'none',
    'nonetheless',
    'noone',
    'nor',
    'normally',
    'nos',
    'not',
    'noted',
    'nothing',
    'novel',
    'now',
    'nr',
    'ns',
    'nt',
    'ny',
    'o',
    'oa',
    'ob',
    'obtain',
    'obtained',
    'obviously',
    'oc',
    'od',
    'of',
    'off',
    'often',
    'og',
    'oh',
    'oi',
    'oj',
    'ok',
    'okay',
    'ol',
    'om',
    'omitted',
    'on',
    'once',
    'ones',
    'only',
    'onto',
    'oo',
    'op',
    'oq',
    'or',
    'ord',
    'os',
    'ot',
    'other',
    'others',
    'otherwise',
    'ou',
    'ought',
    'our',
    'ours',
    'over',
    'overall',
    'ow',
    'owing',
    'ox',
    'oz',
    'p',
    'p1',
    'p2',
    'p3',
    'par',
    'pas',
    'past',
    'pc',
    'pd',
    'pe',
    'per',
    'perhaps',
    'pf',
    'ph',
    'pi',
    'pj',
    'pk',
    'pl',
    'placed',
    'please',
    'plus',
    'pm',
    'pn',
    'po',
    'poorly',
    'possible',
    'possibly',
    'potentially',
    'pp',
    'pq',
    'pr',
    'predominantly',
    'present',
    'presumably',
    'previously',
    'primarily',
    'probably',
    'promptly',
    'proud',
    'provides',
    'ps',
    'pt',
    'pu',
    'put',
    'py',
    'q',
    'qj',
    'qu',
    'que',
    'quickly',
    'quite',
    'qv',
    'r',
    'r2',
    'ra',
    'ran',
    'rather',
    'rc',
    'rd',
    're',
    'readily',
    'really',
    'reasonably',
    'recent',
    'recently',
    'ref',
    'refs',
    'regarding',
    'regardless',
    'regards',
    'related',
    'relatively',
    'research',
    'research-articl',
    'respectively',
    'resulted',
    'resulting',
    'results',
    'rf',
    'rh',
    'ri',
    'right',
    'rj',
    'rl',
    'rm',
    'rn',
    'ro',
    'rq',
    'rr',
    'rs',
    'rt',
    'ru',
    'run',
    'rv',
    'ry',
    's',
    's2',
    'sa',
    'said',
    'same',
    'saw',
    'say',
    'saying',
    'says',
    'sc',
    'sd',
    'se',
    'sec',
    'second',
    'secondly',
    'section',
    'see',
    'seeing',
    'seem',
    'seemed',
    'seeming',
    'seems',
    'seen',
    'self',
    'selves',
    'sensible',
    'sent',
    'serious',
    'seriously',
    'seven',
    'several',
    'sf',
    'shall',
    'shan',
    "shan't",
    'she',
    'shed',
    "she'd",
    "she'll",
    'shes',
    "she's",
    'should',
    'shouldn',
    "shouldn't",
    "should've",
    'show',
    'showed',
    'shown',
    'showns',
    'shows',
    'si',
    'side',
    'significant',
    'significantly',
    'similar',
    'similarly',
    'since',
    'sincere',
    'six',
    'sixty',
    'sj',
    'sl',
    'slightly',
    'sm',
    'sn',
    'so',
    'some',
    'somebody',
    'somehow',
    'someone',
    'somethan',
    'something',
    'sometime',
    'sometimes',
    'somewhat',
    'soon',
    'sorry',
    'sp',
    'specifically',
    'specified',
    'specify',
    'specifying',
    'sq',
    'sr',
    'ss',
    'st',
    'still',
    'stop',
    'strongly',
    'sub',
    'substantially',
    'successfully',
    'such',
    'sufficiently',
    'suggest',
    'sup',
    'sure',
    'sy',
    'system',
    'sz',
    't',
    't1',
    't2',
    't3',
    'take',
    'taking',
    'tb',
    'tc',
    'td',
    'te',
    'tell',
    'ten',
    'tends',
    'tf',
    'th',
    'than',
    'thank',
    'thanks',
    'thanx',
    'that',
    "that'll",
    'thats',
    "that's",
    "that've",
    'the',
    'their',
    'theirs',
    'them',
    'themselves',
    'then',
    'thence',
    'there',
    'thereafter',
    'thereby',
    'thered',
    'therefore',
    'therein',
    "there'll",
    'thereof',
    'therere',
    'theres',
    "there's",
    'thereto',
    'thereupon',
    "there've",
    'these',
    'they',
    'theyd',
    "they'd",
    "they'll",
    'theyre',
    "they're",
    "they've",
    'thickv',
    'thin',
    'think',
    'third',
    'this',
    'thorough',
    'thoroughly',
    'those',
    'thou',
    'though',
    'thoughh',
    'thousand',
    'throug',
    'through',
    'throughout',
    'thru',
    'thus',
    'ti',
    'til',
    'tip',
    'tj',
    'tl',
    'tm',
    'tn',
    'to',
    'together',
    'too',
    'took',
    'toward',
    'towards',
    'tp',
    'tq',
    'tr',
    'tried',
    'tries',
    'truly',
    'try',
    'trying',
    'ts',
    "t's",
    'tt',
    'tv',
    'twelve',
    'twenty',
    'twice',
    'tx',
    'u',
    'u201d',
    'ue',
    'ui',
    'uj',
    'uk',
    'um',
    'un',
    'under',
    'unfortunately',
    'unless',
    'unlike',
    'unlikely',
    'until',
    'unto',
    'uo',
    'up',
    'upon',
    'ups',
    'ur',
    'us',
    'useful',
    'usefully',
    'usefulness',
    'usually',
    'ut',
    'v',
    'va',
    'value',
    'various',
    'vd',
    've',
    've',
    'via',
    'viz',
    'vj',
    'vo',
    'vol',
    'vols',
    'volumtype',
    'vq',
    'vs',
    'vt',
    'vu',
    'w',
    'wa',
    'want',
    'way',
    'we',
    'wed',
    "we'd",
    'welcome',
    'well',
    "we'll",
    'well-b',
    'went',
    'were',
    "we're",
    'weren',
    'werent',
    "weren't",
    "we've",
    'what',
    'whatever',
    "what'll",
    'whats',
    "what's",
    'whether',
    'which',
    'while',
    'whim',
    'whither',
    'who',
    'whod',
    'whoever',
    'whole',
    "who'll",
    'whom',
    'whomever',
    'whos',
    "who's",
    'whose',
    'why',
    "why's",
    'wi',
    'widely',
    'will',
    'willing',
    'wish',
    'with',
    'within',
    'without',
    'wo',
    'won',
    'wonder',
    'wont',
    "won't",
    'words',
    'would',
    'wouldn',
    'wouldnt',
    "wouldn't",
    'www',
    'x',
    'x1',
    'x2',
    'x3',
    'xf',
    'xi',
    'xj',
    'xk',
    'xl',
    'xn',
    'xo',
    'xs',
    'xt',
    'xv',
    'xx',
    'y',
    'y2',
    'yes',
    'yet',
    'yj',
    'yl',
    'you',
    'youd',
    "you'd",
    "you'll",
    'your',
    'youre',
    "you're",
    'yours',
    'yourself',
    'yourselves',
    "you've",
    'yr',
    'ys',
    'yt',
    'z',
    'zero',
    'zi',
    'zz',
)
punctuation = (",", ".", "'", "’")
prompt_keywords = ("digital", "pop")
all_stopwords = stopwords + punctuation + prompt_keywords
