def transform_data(data):
    return {
        "user_id": data["user_id"],
        "movie_id": data["movie_id"],
        "progress": data["progress"],
    }
