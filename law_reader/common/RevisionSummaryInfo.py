class RevisionSummaryInfo:
    """
    Contains information relevant to a revision summary in the Supabase database
    """
    def __init__(self, revision_guid: str, rt_unique_id: int, revision_internal_id: int):
        self.revision_guid = revision_guid
        self.rt_unique_id = rt_unique_id
        self.revision_internal_id = revision_internal_id

    def __str__(self):
        return self.revision_guid
