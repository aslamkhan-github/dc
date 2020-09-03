from BaseDBCollector import BaseDBCollector
from datetime import datetime, timedelta


class UnwantedStaleSessions(BaseDBCollector):
    """
    Collects the Unwanted Stale Ingest and Playout Sessions
    and thier counts directly from Solid or Postgres Databases.
    """

    INACTIVE_PLAYOUT_SESSIONS_QUERY = {'postgres': "SELECT session_id " \
                                                   "FROM session_state " \
                                                   "WHERE type=0 AND done=1 AND update_time <= now() - INTERVAL '90 DAYS'",
                                          'solid': "SELECT session_id from session_state " \
                                                   "WHERE type=0 AND done=1 AND Substring(CAST(update_time as varchar), 1, 10) <= '{dt}'"}

    INACTIVE_INGEST_SESSIONS_QUERY = {'postgres': "SELECT session_id " \
                                                  "FROM session_state " \
                                                  "WHERE type=2 AND done=1 AND update_time <= now() - INTERVAL '90 DAYS'",
                                         'solid': "SELECT session_id from session_state " \
                                                  "WHERE type=2 AND done=1 AND Substring(CAST(update_time as varchar), 1, 10) <= '{dt}'"}

    ALL_STALE_SESSION_COUNTS_QUERY = {'postgres': "SELECT COUNT(session_id),type " \
                                                  "FROM session_state " \
                                                  "WHERE update_time <= now() - INTERVAL '90 DAYS' GROUP BY type",
                                         'solid': "SELECT COUNT(session_id),type from session_state " \
                                                  "WHERE Substring(CAST(update_time as varchar), 1, 10) <= '{dt}' GROUP BY type"}

    STALE_SESSION_ALLOCATION_INFO_QUERY = {'postgres': "SELECT COUNT(id),status " \
                                                       "FROM session_allocation_info " \
                                                       "WHERE update_time <= now() - INTERVAL '90 DAYS' group by status",
                                              'solid': "SELECT COUNT(id),status " \
                                                       "FROM session_allocation_info " \
                                                       "WHERE Substring(CAST(update_time as varchar), 1, 10) <= '{dt}' GROUP BY status"}

    # File names:

    QUERIES = {
        "InactivePlayoutSessions": INACTIVE_PLAYOUT_SESSIONS_QUERY,
        "InactiveIngestSessions": INACTIVE_INGEST_SESSIONS_QUERY,
        "AllStaleSessionCounts": ALL_STALE_SESSION_COUNTS_QUERY,
        "StaleSessionAllocationInfo": STALE_SESSION_ALLOCATION_INFO_QUERY,

    }

    def __init__(self, *args, **kwargs):
        super(UnwantedStaleSessions, self).__init__(*args, **kwargs)
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
