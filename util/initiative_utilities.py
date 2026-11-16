import time

from api.idpay import get_initiative_detail


def wait_for_initiative_ready(selfcare_token: str,
                              initiative_id: str,
                              tries: int = 40,
                              delay: int = 3):
    """Wait for the initiative detail to report PUBLISHED"""
    last_status = None
    for attempt in range(tries):
        response = get_initiative_detail(selfcare_token=selfcare_token, initiative_id=initiative_id)
        assert response.status_code == 200, (
            f"Initiative readiness request failed for {initiative_id}: "
            f"status={response.status_code}, body={response.text}"
        )
        initiative = response.json()
        last_status = initiative["status"]
        if last_status == "PUBLISHED":
            return
        if attempt < tries - 1:
            time.sleep(delay)

    raise AssertionError(
        f"Initiative {initiative_id} did not reach PUBLISHED after {tries} checks. "
        f"Last status: {last_status!r} (None means detail status was null)"
    )
