from epoch_auth_r3.database.repositories import ArtifactRepository


def test_storage_object_maps_object_reference_fields(db):
    digest=b"d"*32
    repo=ArtifactRepository(db)
    assert repo.put_storage_object(digest,"header","HEADER",10,True)[0] == digest
    row=db.execute("""SELECT backend,namespace,object_kind,size_bytes,
      reference_schema_version,verified FROM r3_control.storage_object""").fetchone()
    assert row == ("local","header","HEADER",10,1,True)
