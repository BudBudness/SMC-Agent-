def event_context(events):
    return [{"name":e.get("name"),"actual":e.get("actual"),"expected":e.get("expected"),"previous":e.get("previous"),"importance":e.get("importance"),"time":e.get("time")} for e in events or []]
