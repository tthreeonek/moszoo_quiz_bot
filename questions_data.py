from animals_data import animals_info

QUESTIONS = [
    {
        "text": "🌮 Что бы вы выбрали себе на обед?",
        "options": [
            {"text": "Сочный стейк", "animal": "tiger"},
            {"text": "Фруктовый салат", "animal": "elephant"},
            {"text": "Креветки и устрицы", "animal": "flamingo"},
            {"text": "Хрустящие насекомые", "animal": "meerkat"},
            {"text": "Свежепойманная мышь", "animal": "manul"},
            {"text": "Рыбный суп с тюленем", "animal": "polar_bear"},
        ]
    },
    {
        "text": "🌤 Какой климат вам по душе?",
        "options": [
            {"text": "Тропическая жара", "animal": "flamingo"},
            {"text": "Засушливая пустыня", "animal": "meerkat"},
            {"text": "Вечная мерзлота", "animal": "polar_bear"},
            {"text": "Прохладные горные степи", "animal": "manul"},
            {"text": "Густые дальневосточные леса", "animal": "tiger"},
            {"text": "Саванна с редкими деревьями", "animal": "elephant"},
        ]
    },
    {
        "text": "⚠️ Как вы действуете в опасной ситуации?",
        "options": [
            {"text": "Быстро прячусь в нору", "animal": "meerkat"},
            {"text": "Сливаюсь с окружением и замираю", "animal": "manul"},
            {"text": "Я сам опасность — готов к атаке", "animal": "tiger"},
            {"text": "Убегаю, но если что, могу и растоптать", "animal": "elephant"},
            {"text": "Взлетаю и улетаю подальше", "animal": "flamingo"},
            {"text": "Уплываю в ледяную воду", "animal": "polar_bear"},
        ]
    },
    {
        "text": "🧑‍🤝‍🧑 Что для вас важнее всего в жизни?",
        "options": [
            {"text": "Семья и коллектив", "animal": "meerkat"},
            {"text": "Территория и самостоятельность", "animal": "tiger"},
            {"text": "Стабильность и мудрость", "animal": "elephant"},
            {"text": "Свобода и независимость", "animal": "manul"},
            {"text": "Красота и элегантность", "animal": "flamingo"},
            {"text": "Сила и выносливость", "animal": "polar_bear"},
        ]
    },
    {
        "text": "🎲 Какое хобби вам ближе?",
        "options": [
            {"text": "Строительство подземных тоннелей", "animal": "meerkat"},
            {"text": "Охота и рыбалка на льду", "animal": "polar_bear"},
            {"text": "Медитация и наблюдение за звёздами", "animal": "manul"},
            {"text": "Хореография и танцы", "animal": "flamingo"},
            {"text": "Боевые искусства", "animal": "tiger"},
            {"text": "Коллекционирование редких предметов", "animal": "elephant"},
        ]
    },
]

def get_tiebreaker_question(leaders_keys):
    leader_animals = {key: animals_info[key] for key in leaders_keys}
    options = []
    for key, info in leader_animals.items():
        options.append({
            "text": info["short_answer"],
            "animal": key
        })
    return {
        "text": "🤔 Последний рывок! Что вам нравится больше?",
        "options": options
    }