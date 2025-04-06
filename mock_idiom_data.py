"""
Mock data for the Multilingual Emotion Idiom Translator
Used for testing when API calls are not available
"""

# Mock data for common English idioms by emotion
ENGLISH_IDIOMS = {
    "happy": [
        {
            "idiom": "Walking on sunshine",
            "meaning": "Feeling extremely happy and carefree",
            "emotion": "happy"
        },
        {
            "idiom": "On cloud nine",
            "meaning": "Extremely happy and elated",
            "emotion": "happy"
        },
        {
            "idiom": "Over the moon",
            "meaning": "Extremely happy and delighted",
            "emotion": "happy"
        },
        {
            "idiom": "Grinning from ear to ear",
            "meaning": "Smiling widely due to happiness",
            "emotion": "happy"
        },
        {
            "idiom": "Jumping for joy",
            "meaning": "Being so happy that you literally jump up and down",
            "emotion": "happy"
        }
    ],
    "sad": [
        {
            "idiom": "Down in the dumps",
            "meaning": "Feeling sad or depressed",
            "emotion": "sad"
        },
        {
            "idiom": "Feeling blue",
            "meaning": "Feeling sad or melancholic",
            "emotion": "sad"
        },
        {
            "idiom": "Under a cloud",
            "meaning": "In a state of sadness or disgrace",
            "emotion": "sad"
        },
        {
            "idiom": "A face as long as a fiddle",
            "meaning": "Looking sad or disappointed",
            "emotion": "sad"
        },
        {
            "idiom": "Heart sank",
            "meaning": "Sudden feeling of sadness or disappointment",
            "emotion": "sad"
        }
    ],
    "angry": [
        {
            "idiom": "Blood is boiling",
            "meaning": "Extremely angry",
            "emotion": "angry"
        },
        {
            "idiom": "Blow a fuse",
            "meaning": "Become very angry suddenly",
            "emotion": "angry"
        },
        {
            "idiom": "See red",
            "meaning": "Become very angry",
            "emotion": "angry"
        },
        {
            "idiom": "Get under someone's skin",
            "meaning": "Irritate or annoy someone",
            "emotion": "angry"
        },
        {
            "idiom": "Fly off the handle",
            "meaning": "Suddenly become very angry",
            "emotion": "angry"
        }
    ],
    "general": [
        {
            "idiom": "Piece of cake",
            "meaning": "Something very easy to do",
            "emotion": "confident"
        },
        {
            "idiom": "Hit the nail on the head",
            "meaning": "To describe exactly what is causing a situation or problem",
            "emotion": "satisfied"
        },
        {
            "idiom": "Cost an arm and a leg",
            "meaning": "To be very expensive",
            "emotion": "surprised"
        },
        {
            "idiom": "Break a leg",
            "meaning": "Good luck",
            "emotion": "encouraging"
        },
        {
            "idiom": "Speak of the devil",
            "meaning": "Said when someone appears just when you're talking about them",
            "emotion": "surprised"
        }
    ]
}

# Mock data for common Arabic idioms by emotion
ARABIC_IDIOMS = {
    "happy": [
        {
            "idiom": "طار من الفرحة",
            "meaning": "Flying from happiness (extremely happy)",
            "emotion": "happy"
        },
        {
            "idiom": "فرحان لدرجة الجنون",
            "meaning": "Happy to the point of madness",
            "emotion": "happy"
        },
        {
            "idiom": "على قلبه زي العسل",
            "meaning": "Like honey on his heart (very pleasant feeling)",
            "emotion": "happy"
        },
        {
            "idiom": "قلبه مليان فرح",
            "meaning": "Heart full of joy",
            "emotion": "happy"
        },
        {
            "idiom": "فرحة ما بتتوصف",
            "meaning": "Indescribable happiness",
            "emotion": "happy"
        }
    ],
    "sad": [
        {
            "idiom": "قلبه مكسور",
            "meaning": "Broken-hearted",
            "emotion": "sad"
        },
        {
            "idiom": "الدنيا سودة في عينه",
            "meaning": "The world is black in his eyes (everything seems gloomy)",
            "emotion": "sad"
        },
        {
            "idiom": "حزين لدرجة البكاء",
            "meaning": "Sad to the point of crying",
            "emotion": "sad"
        },
        {
            "idiom": "روحه تعبانة",
            "meaning": "His soul is tired",
            "emotion": "sad"
        },
        {
            "idiom": "محمول على الهم",
            "meaning": "Carrying a burden of sadness",
            "emotion": "sad"
        }
    ],
    "angry": [
        {
            "idiom": "دمه فار",
            "meaning": "His blood is boiling",
            "emotion": "angry"
        },
        {
            "idiom": "طلع من طوره",
            "meaning": "Went out of his normal state (lost temper)",
            "emotion": "angry"
        },
        {
            "idiom": "ولع من الغضب",
            "meaning": "Ignited from anger",
            "emotion": "angry"
        },
        {
            "idiom": "شايط دمه",
            "meaning": "His blood is burning",
            "emotion": "angry"
        },
        {
            "idiom": "بيتنفس نار",
            "meaning": "Breathing fire",
            "emotion": "angry"
        }
    ],
    "general": [
        {
            "idiom": "على عيني وراسي",
            "meaning": "On my eye and head (I'll do it with pleasure)",
            "emotion": "agreeable"
        },
        {
            "idiom": "القطة العمية بتقول يا حاوي",
            "meaning": "The blind cat says 'oh snake charmer' (calling for help from the wrong source)",
            "emotion": "confused"
        },
        {
            "idiom": "ما تعد كتاكيتك قبل ما تفقس",
            "meaning": "Don't count your chicks before they hatch",
            "emotion": "cautious"
        },
        {
            "idiom": "على قد لحافك مد رجليك",
            "meaning": "Stretch your legs according to your blanket (live within your means)",
            "emotion": "pragmatic"
        },
        {
            "idiom": "مثل القط المحشور",
            "meaning": "Like a cornered cat (desperate situation)",
            "emotion": "anxious"
        }
    ]
}

# Mock translations for test idioms
MOCK_TRANSLATIONS = {
    "Walking on sunshine": {
        "ar": {
            "translated_idiom": "طاير من الفرحة",
            "literal_meaning": "Flying from happiness",
            "emotional_meaning": "Feeling extremely happy and carefree",
            "cultural_context": "In Arabic culture, the imagery of flying is often associated with extreme happiness and freedom from worries"
        }
    },
    "أسير على أشعة الشمس": {
        "en": {
            "translated_idiom": "Walking on sunshine",
            "literal_meaning": "Walking on sun rays",
            "emotional_meaning": "Feeling extremely happy and carefree",
            "cultural_context": "This expression uses the warmth and brightness of sunshine as a metaphor for happiness and optimism"
        }
    },
    "Feeling under the weather": {
        "ar": {
            "translated_idiom": "مش على بعضي",
            "literal_meaning": "Not on myself/together",
            "emotional_meaning": "Feeling slightly ill or unwell"
        }
    },
    "طاير من الفرحة": {
        "en": {
            "translated_idiom": "Over the moon",
            "literal_meaning": "Flying from happiness",
            "emotional_meaning": "Extremely happy and delighted",
            "cultural_context": "In English-speaking cultures, the imagery of being over the moon represents extreme happiness"
        }
    },
    "قلبه مكسور": {
        "en": {
            "translated_idiom": "Broken-hearted",
            "literal_meaning": "His heart is broken",
            "emotional_meaning": "Very sad due to disappointment in love or other significant loss",
            "cultural_context": "The image of a broken heart is universal in representing deep sadness or grief"
        }
    },
    "Broken-hearted": {
        "ar": {
            "translated_idiom": "قلبه مكسور",
            "literal_meaning": "His heart is broken",
            "emotional_meaning": "Very sad due to disappointment in love or other significant loss",
            "cultural_context": "The concept of a broken heart represents deep sadness in both cultures"
        }
    }
}