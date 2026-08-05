from epoch_auth_r3.database.job_repository import JobRepository


def test_retry_backoff_is_deterministic_and_capped():
    assert [JobRepository.retry_delay(x) for x in (1,2,3,10)] == [1,2,4,300]
