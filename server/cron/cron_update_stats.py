import structlog

from main.models import ParkingSpace, ParkingSpaceStat  # noqa: E402

logger = structlog.getLogger(__name__)


# TODO: это очень неэффективное хранение статистики места.
# Лучше сохранять те данные, что приходят со станций.
# Станции отправляют метрики раз в 5-10 секунд.
# А тут обновляются данные каждую секунду.
# Лучше хранить в Clickhouse, а не postgresql,
# так как SQL база не сжимает данные.
def update_parking_space_stats():
    spaces = ParkingSpace.objects.all()
    logger.info('update_parking_space_stats', n_spaces=spaces.count())
    for parking_space in spaces:
        last_stat = (
            ParkingSpaceStat.objects.filter(
                space=parking_space,
            )
            .order_by('-created_at')
            .first()
        )

        if (
            last_stat is not None
            and last_stat.last_data_update == parking_space.last_data_update
        ):
            continue

        new_stat = ParkingSpaceStat()
        new_stat.space = parking_space
        new_stat.status = parking_space.status
        new_stat.total_kw = parking_space.total_kw
        new_stat.current_w = parking_space.current_w
        new_stat.current_v = parking_space.current_v
        new_stat.current_a = parking_space.current_a
        new_stat.is_on = parking_space.is_on
        new_stat.last_data_update = parking_space.last_data_update
        new_stat.save()
