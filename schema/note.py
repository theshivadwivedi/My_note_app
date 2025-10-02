def noteEntity(item) -> dict:
    return{
        "id": str(item["_id"]),
        "tittle": item["tittle"],
        "content": item["content"],
        "important": item["important"],
    }


def notesEntity(items) -> list:
    return [noteEntity(item) for item in items]