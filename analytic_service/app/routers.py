from fastapi import APIRouter, Depends
import crud
from metrics import Metrics
from config import get_clickhouse_client

router = APIRouter()


def get_metrics():
    client = get_clickhouse_client()
    return Metrics(client)


@router.get("/bookings")
def get_all_bookings(crud: CRUD = Depends(get_crud)):
    return crud.get_bookings()


@router.get("/bookings/{booking_id}")
def get_booking_by_id(booking_id: int, crud: CRUD = Depends(get_crud)):
    return crud.get_booking_by_id(booking_id)


@router.get("/metrics/average-active-session-duration")
def get_average_active_session_duration(metrics: Metrics = Depends(get_metrics)):
    return metrics.average_active_session_duration()


@router.get("/metrics/weighted-average-user-satisfaction")
def get_weighted_average_user_satisfaction(metrics: Metrics = Depends(get_metrics)):
    return metrics.weighted_average_user_satisfaction()


@router.get("/metrics/room-popularity-index")
def get_room_popularity_index(metrics: Metrics = Depends(get_metrics)):
    return metrics.room_popularity_index()


@router.get("/metrics/hourly-utilization-rate")
def get_hourly_utilization_rate(metrics: Metrics = Depends(get_metrics)):
    return metrics.hourly_utilization_rate()


@router.get("/metrics/user-retention-rate")
def get_user_retention_rate(metrics: Metrics = Depends(get_metrics)):
    return metrics.user_retention_rate()


@router.get("/dashboard")
def get_dashboard(metrics: Metrics = Depends(get_metrics)):
    return {
        "average_active_session_duration": metrics.average_active_session_duration(),
        "weighted_average_user_satisfaction": metrics.weighted_average_user_satisfaction(),
        "room_popularity_index": metrics.room_popularity_index(),
        "hourly_utilization_rate": metrics.hourly_utilization_rate(),
        "user_retention_rate": metrics.user_retention_rate(),
        "average_time_between_bookings": metrics.average_time_between_bookings(),
        "booking_density_rate": metrics.booking_density_rate(),
        "user_engagement_score": metrics.user_engagement_score(),
        "room_utilization_rate": metrics.room_utilization_rate(),
        "overall_satisfaction_score": metrics.overall_satisfaction_score(),
        "peak_usage_time": metrics.peak_usage_time(),
        "most_popular_room": metrics.most_popular_room()
    }

