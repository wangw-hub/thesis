from epoch_auth_r3.database.job_repository import JobRepository
from epoch_auth_r3.database.repositories import ArtifactRepository
from conftest import event


def make_artifact(db, n=1, header_version=1, previous=None, *, key_version=1,
                  body_version=1, update_kind=None, body_object=None):
    jobs=JobRepository(db); artifacts=ArtifactRepository(db)
    ev=event(n,new_header_version=header_version,resource_id=b"r"*32)
    _,job,op=jobs.insert_event(ev)
    obj=bytes([80+n%100])*32
    digest=bytes([120+n%100])*32
    if body_object is None and header_version > 1:
        row = db.execute(
            """SELECT body_object_digest FROM r3_control.header_version
               WHERE resource_id=%s AND header_version=%s""",
            (ev.resource_id, header_version - 1),
        ).fetchone()
        body_object = bytes(row[0]) if row and row[0] is not None else None
    body_object = body_object or bytes([40 + n % 100]) * 32
    artifacts.put_storage_object(obj,"header","HEADER",128,True)
    artifacts.put_storage_object(body_object,"body","BODY",256,True)
    update_kind = update_kind or ("INITIAL" if header_version == 1 else "HEADER_ONLY")
    hid=artifacts.add_header(
        job,op,ev.resource_id,header_version,key_version,2,3,digest,previous,obj,
        body_version=body_version,update_kind=update_kind,
        body_object_digest=body_object,
    )
    return ev,job,op,obj,digest,hid
