from BaseDBCollector import BaseDBCollector
from datetime import datetime, timedelta


class RecordingStatistics(BaseDBCollector):
    """
    Collects the Average Recording Statistics from both the types of databases directly
    """

    AVG_RECORDINGS_PER_DAY_QUERY = {'postgres': "SELECT avg(duration), data_type " \
                                                "FROM asset " \
                                                "WHERE update_time <= now() - INTERVAL '30 DAYS' group by data_type ",
                                       'solid': "SELECT avg(duration),data_type from asset " \
                                                "WHERE Substring(CAST(update_time as varchar), 1, 10) < 'dt' GROUP BY data_type"}

    AVG_STORAGE_USED_PER_RECORDED_HOUR_QUERY = {'postgres': "SELECT data_type, avg(duration)/24, avg(size)/24 " \
                                                            "FROM asset,asset_data_files " \
                                                            "WHERE asset.data_id = asset_data_files.top_id AND " \
                                                            "update_time >= NOW() - INTERVAL '30 DAYS' group by data_type ",
                                                   'solid': "SELECT data_type, avg(duration)/24, avg(size)/24 " \
                                                            "FROM asset,asset_data_files " \
                                                            "WHERE asset.data_id = asset_data_files.top_id AND " \
                                                            "Substring(CAST(update_time as varchar), 1, 10) >= '{dt}' GROUP BY data_type"}

    TOP_TEN_MOST_RECORDED_PROGRAMS_QUERY = {'postgres': "SELECT count(multicast_channel), alias " \
                                                        "FROM live_recording_session, multicast_channel " \
                                                        "WHERE live_recording_session.multicast_channel = multicast_channel.id AND " \
                                                        "creation_time >= NOW() - INTERVAL '30 DAYS' GROUP BY alias ORDER BY count(multicast_channel) desc LIMIT 10",
                                               'solid': "SELECT count(multicast_channel), alias " \
                                                        "FROM live_recording_session, multicast_channel " \
                                                        "WHERE live_recording_session.multicast_channel = multicast_channel.id AND " \
                                                        "Substring(CAST (creation_time as varchar), 1, 10) >= '{dt}' GROUP BY alias ORDER BY count(multicast_channel) desc LIMIT 10"}

    TOTAL_RECORDED_CHANNELS_QUERY = {'postgres': "SELECT count(multicast_channel), alias " \
                                                 "FROM live_recording_session, multicast_channel " \
                                                 "WHERE live_recording_session.multicast_channel = multicast_channel.id " \
                                                 "GROUP BY alias ORDER BY count(multicast_channel) DESC ",
                                        'solid': "SELECT count(multicast_channel), alias " \
                                                 "FROM live_recording_session, multicast_channel " \
                                                 "WHERE live_recording_session.multicast_channel = multicast_channel.id " \
                                                 "GROUP BY alias ORDER BY count(multicast_channel) DESC "}

    # file name: query
    QUERIES = {
        "AvgRecordingsPerDay": AVG_RECORDINGS_PER_DAY_QUERY,
        "AvgStorageUsedPerRecordedHour": AVG_STORAGE_USED_PER_RECORDED_HOUR_QUERY,
        "TopTenMostRecordedProgram": TOP_TEN_MOST_RECORDED_PROGRAMS_QUERY,
        "TotalRecordedChannels": TOTAL_RECORDED_CHANNELS_QUERY,

    }

    def __init__(self, *args, **kwargs):
        super(RecordingStatistics, self).__init__(*args, **kwargs)
        self.query = None

    def collect_from_target(self, target):
        manager_app, nodename = target
        self.connect_to_db(manager_app)
        for self.name, self.query in self.QUERIES.items():
            self.query_result(nodename)

    def get_query(self):
        query = self.query[self.db_type]
        if self.db_type == 'solid':
            query = query.format(dt=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d-T%H-%M-%S'))
        return query
