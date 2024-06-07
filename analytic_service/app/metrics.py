from typing import List, Dict
import clickhouse_connect


class Metrics:
    def __init__(self, client: clickhouse_connect.Client):
        self.client = client

    def average_active_session_duration(self) -> Dict[str, float]:
        query = """
        SELECT avg(endTime - startTime) AS avg_duration
        FROM bookings
        WHERE status = 'CONFIRMED'
        """
        result = self.client.query(query)
        return {"average_active_session_duration": result.result_rows[0][0]}

    def weighted_average_user_satisfaction(self) -> Dict[str, float]:
        query = """
        SELECT sum(S.satisfaction * U.weight) / sum(U.weight) AS weighted_avg_satisfaction
        FROM user_satisfactions AS S
        JOIN users AS U ON S.user_id = U.id
        """
        result = self.client.query(query)
        return {"weighted_average_user_satisfaction": result.result_rows[0][0]}

    def room_popularity_index(self) -> Dict[str, float]:
        query = """
        SELECT avg(bookings_count * avg_duration) AS popularity_index
        FROM (
            SELECT room, count(*) AS bookings_count, avg(endTime - startTime) AS avg_duration
            FROM bookings
            WHERE status = 'CONFIRMED'
            GROUP BY room
        ) AS room_stats
        """
        result = self.client.query(query)
        return {"room_popularity_index": result.result_rows[0][0]}

    def hourly_utilization_rate(self) -> Dict[str, float]:
        query = """
        SELECT avg(usage_rate) AS avg_hourly_utilization
        FROM (
            SELECT hour, sum(duration) / count(DISTINCT room) AS usage_rate
            FROM (
                SELECT room, toHour(startTime) AS hour, sum(endTime - startTime) AS duration
                FROM bookings
                WHERE status = 'CONFIRMED'
                GROUP BY room, hour
            ) AS hourly_usage
            GROUP BY hour
        ) AS daily_usage
        """
        result = self.client.query(query)
        return {"hourly_utilization_rate": result.result_rows[0][0]}

    def user_retention_rate(self) -> Dict[str, float]:
        query = """
        SELECT (count(DISTINCT retained_user_id) / count(DISTINCT user_id)) * 100 AS retention_rate
        FROM (
            SELECT user_id, min(startTime) AS first_booking_time,
                if(count(*) > 1, 1, 0) AS retained_user_id
            FROM bookings
            GROUP BY user_id
        ) AS user_retention
        """
        result = self.client.query(query)
        return {"user_retention_rate": result.result_rows[0][0]}

    def average_time_between_bookings(self) -> Dict[str, float]:
        query = """
        SELECT avg(next_booking_time - endTime) AS avg_time_between_bookings
        FROM (
            SELECT user_id, endTime,
                lead(startTime) OVER (PARTITION BY user_id ORDER BY startTime) AS next_booking_time
            FROM bookings
            WHERE status = 'CONFIRMED'
        ) AS booking_intervals
        WHERE next_booking_time IS NOT NULL
        """
        result = self.client.query(query)
        return {"average_time_between_bookings": result.result_rows[0][0]}

    def booking_density_rate(self) -> Dict[str, float]:
        query = """
        SELECT count(*) / count(DISTINCT day) AS booking_density_rate
        FROM (
            SELECT room, toDate(startTime) AS day
            FROM bookings
            WHERE status = 'CONFIRMED'
            GROUP BY room, day
        ) AS daily_bookings
        """
        result = self.client.query(query)
        return {"booking_density_rate": result.result_rows[0][0]}

    def user_engagement_score(self) -> Dict[str, float]:
        query = """
        SELECT user_id, count(*) AS bookings_count, avg(endTime - startTime) AS avg_duration,
            (count(*) * avg(endTime - startTime)) AS engagement_score
        FROM bookings
        WHERE status = 'CONFIRMED'
        GROUP BY user_id
        """
        result = self.client.query(query)
        user_scores = {row[0]: row[3] for row in result.result_rows}
        avg_score = sum(user_scores.values()) / len(user_scores)
        return {"user_engagement_score": avg_score}

    def room_utilization_rate(self) -> Dict[str, float]:
        query = """
        SELECT room, sum(endTime - startTime) / (count(*) * 24 * 3600) AS utilization_rate
        FROM bookings
        WHERE status = 'CONFIRMED'
        GROUP BY room
        """
        result = self.client.query(query)
        room_rates = {row[0]: row[1] for row in result.result_rows}
        avg_rate = sum(room_rates.values()) / len(room_rates)
        return {"room_utilization_rate": avg_rate}

    def overall_satisfaction_score(self) -> Dict[str, float]:
        query = """
        SELECT avg(satisfaction) AS overall_satisfaction
        FROM user_satisfactions
        """
        result = self.client.query(query)
        return {"overall_satisfaction_score": result.result_rows[0][0]}

    def peak_usage_time(self) -> Dict[str, int]:
        query = """
        SELECT toHour(startTime) AS hour, count(*) AS booking_count
        FROM bookings
        WHERE status = 'CONFIRMED'
        GROUP BY hour
        ORDER BY booking_count DESC
        LIMIT 1
        """
        result = self.client.query(query)
        return {"peak_usage_time": result.result_rows[0][0]}

    def most_popular_room(self) -> Dict[str, int]:
        query = """
        SELECT room, count(*) AS booking_count
        FROM bookings
        WHERE status = 'CONFIRMED'
        GROUP BY room
        ORDER BY booking_count DESC
        LIMIT 1
        """
        result = self.client.query(query)
        return {"most_popular_room": result.result_rows[0][0]}