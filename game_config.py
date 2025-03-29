# Word lists and categories
WORD_LIST = [
    "tree", "sun", "book", "music", "ocean", "mountain", "coffee", "dance",
    "flower", "computer", "bird", "house", "rain", "smile", "star", "river",
    "forest", "beach", "wind", "moon", "lake", "garden", "cloud", "sunset"
]

# Scoring and gameplay configuration
DIFFICULTY_SETTINGS = {
    'easy': {
        'time': 120,
        'multiplier': 1.0,
        'hint_limit': 5,
        'min_word_length': 3
    },
    'medium': {
        'time': 90,
        'multiplier': 1.5,
        'hint_limit': 3,
        'min_word_length': 4
    },
    'hard': {
        'time': 60,
        'multiplier': 2.0,
        'hint_limit': 2,
        'min_word_length': 5
    },
    'expert': {
        'time': 45,
        'multiplier': 2.5,
        'hint_limit': 1,
        'min_word_length': 6
    }
}

# Level thresholds
LEVEL_THRESHOLDS = {
    1: 0,    # Beginner
    2: 100,  # Novice
    3: 250,  # Intermediate
    4: 500,  # Advanced
    5: 1000, # Expert
    6: 2000, # Master
    7: 3500, # Grand Master
    8: 5000, # Legend
}

# Combo bonuses
COMBO_BONUSES = {
    3: 1.5,   # 50% bonus at 3 streak
    5: 2.0,   # 100% bonus at 5 streak
    7: 2.5,   # 150% bonus at 7 streak
    10: 3.0,  # 200% bonus at 10 streak
}

# Achievement criteria
ACHIEVEMENTS = {
    'quick_thinker': {
        'name': 'Quick Thinker',
        'description': 'Submit 3 words within 10 seconds',
        'icon': 'fa-bolt'
    },
    'combo_master': {
        'name': 'Combo Master',
        'description': 'Achieve a 10x combo streak',
        'icon': 'fa-fire'
    },
    'vocabulary_expert': {
        'name': 'Vocabulary Expert',
        'description': 'Use words from all categories in one game',
        'icon': 'fa-book'
    },
    'speed_demon': {
        'name': 'Speed Demon',
        'description': 'Complete a game with average response time under 3 seconds',
        'icon': 'fa-tachometer-alt'
    }
}

WORD_CATEGORIES = {
    'nature': {
        'words': [
            'tree', 'leaf', 'forest', 'wood', 'plant', 'flower', 'garden',
            'bush', 'grass', 'vine', 'meadow', 'jungle', 'mountain', 'river',
            'lake', 'ocean', 'beach', 'island', 'valley', 'cliff', 'waterfall',
            'brook', 'stream', 'desert', 'volcano', 'glacier', 'canyon', 'peak',
            'cave', 'reef', 'oasis', 'marsh', 'geyser', 'delta', 'rainforest',
            'savanna', 'tundra', 'prairie', 'lagoon', 'plateau', 'fjord'
        ],
        'common_words': [
            'green', 'grow', 'nature', 'outdoor', 'wild', 'bloom', 'seed',
            'root', 'stem', 'ecosystem', 'environment', 'landscape', 'habitat',
            'wilderness', 'tropical', 'lush', 'fertile', 'organic', 'natural',
            'verdant', 'abundant', 'pristine', 'serene', 'untamed', 'diverse'
        ],
        'hint_categories': ['terrain', 'water bodies', 'vegetation']
    },
    'weather': {
        'words': [
            'rain', 'sun', 'cloud', 'storm', 'wind', 'snow', 'fog', 'thunder',
            'lightning', 'hail', 'blizzard', 'hurricane', 'tornado', 'breeze',
            'drizzle', 'frost', 'mist', 'rainbow', 'sleet', 'sunshine',
            'cyclone', 'drought', 'flood', 'shower', 'typhoon', 'avalanche',
            'monsoon', 'tsunami', 'whirlwind', 'downpour', 'cloudburst'
        ],
        'common_words': [
            'weather', 'climate', 'temperature', 'forecast', 'season',
            'precipitation', 'humidity', 'atmospheric', 'meteorology', 'barometer',
            'pressure', 'visibility', 'conditions', 'monsoon', 'tropical',
            'arctic', 'temperate', 'humid', 'arid', 'stormy', 'meteorological',
            'seasonal', 'atmospheric', 'climatic', 'turbulent'
        ],
        'hint_categories': ['precipitation', 'wind phenomena', 'atmospheric conditions']
    },
    'animals': {
        'words': [
            'bird', 'dog', 'cat', 'fish', 'lion', 'tiger', 'bear', 'elephant',
            'monkey', 'snake', 'wolf', 'fox', 'deer', 'rabbit', 'eagle', 'owl',
            'penguin', 'dolphin', 'whale', 'shark', 'turtle', 'giraffe', 'zebra',
            'panda', 'koala', 'kangaroo', 'octopus', 'butterfly', 'bee',
            'squirrel', 'raccoon', 'moose', 'buffalo', 'rhinoceros', 'leopard',
            'cheetah', 'gorilla', 'crocodile', 'flamingo', 'peacock', 'jaguar'
        ],
        'common_words': [
            'wild', 'pet', 'creature', 'species', 'breed', 'animal', 'predator',
            'prey', 'mammal', 'reptile', 'amphibian', 'vertebrate', 'carnivore',
            'herbivore', 'omnivore', 'extinct', 'endangered', 'domestic', 'feral',
            'migration', 'habitat', 'ecosystem', 'nocturnal', 'diurnal', 'aquatic'
        ],
        'hint_categories': ['mammals', 'birds', 'reptiles', 'marine life']
    },
    'colors': {
        'words': [
            'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'white',
            'black', 'pink', 'brown', 'gray', 'violet', 'indigo', 'maroon',
            'turquoise', 'cyan', 'magenta', 'gold', 'silver', 'bronze', 'beige',
            'crimson', 'scarlet', 'navy', 'emerald', 'ruby', 'sapphire',
            'jade', 'amber', 'ivory', 'burgundy', 'mauve', 'coral', 'teal',
            'khaki', 'lavender', 'olive', 'orchid', 'periwinkle', 'plum'
        ],
        'common_words': [
            'color', 'shade', 'bright', 'dark', 'light', 'colorful', 'tint',
            'hue', 'primary', 'secondary', 'tertiary', 'pastel', 'neon',
            'vibrant', 'vivid', 'muted', 'saturated', 'iridescent', 'metallic',
            'rainbow', 'spectrum', 'pigment', 'tone', 'gradient', 'chromatic'
        ],
        'hint_categories': ['primary colors', 'warm colors', 'cool colors', 'metallic colors']
    },
    'emotions': {
        'words': [
            'happy', 'sad', 'angry', 'excited', 'scared', 'surprised', 'calm',
            'nervous', 'proud', 'lonely', 'joyful', 'anxious', 'peaceful',
            'grateful', 'frustrated', 'worried', 'content', 'hopeful',
            'disappointed', 'enthusiastic', 'confused', 'confident', 'shy',
            'jealous', 'curious', 'bored', 'amused', 'delighted', 'stressed',
            'relaxed', 'overwhelmed', 'ecstatic', 'melancholy', 'nostalgic'
        ],
        'common_words': [
            'feeling', 'emotion', 'mood', 'expression', 'emotional', 'feel',
            'sentiment', 'attitude', 'disposition', 'temperament', 'state',
            'mindset', 'spirits', 'demeanor', 'passion', 'sensation',
            'consciousness', 'awareness', 'perception', 'reaction', 'empathy',
            'compassion', 'sensitivity', 'intuition', 'psyche'
        ],
        'hint_categories': ['positive emotions', 'negative emotions', 'neutral states']
    }
}

DAILY_CHALLENGE_WORDS = [
    "adventure", "creative", "discover", "explore", "harmony", 
    "inspire", "journey", "mystery", "passion", "wonder",
    "balance", "courage", "dreams", "energy", "freedom",
    "innovation", "knowledge", "leadership", "motivation", "opportunity",
    "progress", "quality", "success", "teamwork", "vision",
    "wisdom", "excellence", "dedication", "achievement", "growth",
    "imagination", "brilliance", "determination", "persistence", "triumph"
]

OPPOSITES = {
    'hot': ['cold', 'cool', 'chilly', 'freezing'],
    'fast': ['slow', 'sluggish', 'unhurried', 'leisurely'],
    'big': ['small', 'tiny', 'little', 'miniature'],
    'high': ['low', 'short', 'bottom', 'down'],
    'happy': ['sad', 'unhappy', 'miserable', 'depressed'],
    'light': ['dark', 'dim', 'shadowy', 'murky'],
    'strong': ['weak', 'feeble', 'frail', 'delicate'],
    'rich': ['poor', 'broke', 'needy', 'destitute'],
    'new': ['old', 'ancient', 'aged', 'antique'],
    'loud': ['quiet', 'silent', 'soft', 'hushed'],
    'clean': ['dirty', 'filthy', 'grimy', 'soiled'],
    'early': ['late', 'tardy', 'delayed', 'overdue'],
    'brave': ['scared', 'fearful', 'cowardly', 'timid'],
    'smooth': ['rough', 'bumpy', 'coarse', 'jagged'],
    'sweet': ['bitter', 'sour', 'tart', 'acrid'],
    'bright': ['dark', 'dull', 'gloomy', 'dim'],
    'heavy': ['light', 'weightless', 'feather-like', 'airy'],
    'deep': ['shallow', 'superficial', 'surface', 'thin'],
    'wide': ['narrow', 'slim', 'tight', 'constricted'],
    'thick': ['thin', 'slender', 'lean', 'sparse']
}