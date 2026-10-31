from hmtracker.parser.hmparser import HMAjaxScrapper


def connect_to_hm(email, password):
    parser = HMAjaxScrapper()
    try:
        parser.connect_to_hm(email, password)
    finally:
        parser.close_session()
