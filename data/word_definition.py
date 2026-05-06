import wikipediaapi


# получение определения (значения) слова
def get_word_definition(word):
    try:
        # создаём экземпляр Wikipedia
        wiki = wikipediaapi.Wikipedia(
            user_agent='WordDefFetcher (contact@example.com)',
            language='ru'
        )
        # получаем страницу
        page = wiki.page(word)
        if page.exists():
            # берём только первую секцию (введение), где обычно содержится определение
            return page.summary
        else:
            return f"Слово '{word}' не найдено в русской Википедии."

    except Exception as e:
        return f"Произошла ошибка при запросе: {e}"
