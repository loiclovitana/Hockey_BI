from hmtracker.parser.hmparser import HMAjaxScrapper


def connect_to_hm(email, password):
    parser = HMAjaxScrapper()
    parser.connect_to_hm(email, password)
