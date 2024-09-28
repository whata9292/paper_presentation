from app.db.models.summary_pages import SummaryPage
from app.db.models.base import ScopedSession


if __name__ == "__main__":
    summary_page = SummaryPage(
        title="RTMDet: An Empirical Study of Designing Real-Time Object Detectors",
        url="https://d2is53fus238ee.cloudfront.net/paper/rtm_det_slide.html"
    )

    session = ScopedSession()
    session.add(summary_page)
    session.commit()
    session.close()
