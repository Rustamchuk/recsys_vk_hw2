import random
from .recommender import Recommender


class MyRecommender(Recommender):
    """
    Если пользователю понравился трек то рекомендуем похожий.
    Иначе рекомендуем по предпочтениям.
    Если ничего не нашлось выдаем рандомный.
    """

    def __init__(self, tracks_redis, recommendations_redis, catalog, fallback, threshold=0.6):
        self.tracks_redis = tracks_redis
        self.recommendations_redis = recommendations_redis
        self.catalog = catalog
        self.fallback = fallback
        self.threshold = threshold

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        # Берем данные прослушенного трека
        previous_track_data = self.tracks_redis.get(prev_track)
        if previous_track_data is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        track_info = self.catalog.from_bytes(previous_track_data)

        if not track_info:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        if prev_track_time >= self.threshold:
            # Рекомендуем похожий
            similar_tracks = [t for t in track_info if t != prev_track]
            if similar_tracks:
                return random.choice(similar_tracks)

        # По личным предпочтениям
        user_recs = self.recommendations_redis.get(user)
        if user_recs:
            user_rec_tracks = list(self.catalog.from_bytes(user_recs))
            if user_rec_tracks:
                return random.choice(user_rec_tracks)

        # Даем рандомный
        return self.fallback.recommend_next(user, prev_track, prev_track_time)