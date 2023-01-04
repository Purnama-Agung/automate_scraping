from argparse import ArgumentParser
from src.crawler.eperolehan_catalogue import Eperolehan_catalogue

def get_index(all_jenama=False, cat=None, jenama=None, start_page=None, end_page=None):
    if all_jenama:
        cat = 8
        for category in range(0, int(cat)):
            try:
                Eperolehan_catalogue().get_index(cat=category, jenama=0)
            except:
                continue
    else:
        Eperolehan_catalogue().get_index(cat=cat, jenama=jenama, start_page=start_page, end_page=end_page)

if __name__ == '__main__':
    modes = ['crawl', 'parse']

    parser = ArgumentParser(description="Eperolehan Catalogue Engine")
    parser.add_argument('-m', '--mode', choices=modes, help='Execute modes.', required=True)
    parser.add_argument('-a', '--all', help="Crawl all catalogue, all jenama.")
    parser.add_argument('-ca', '--catalogue', help="Input 1-6")
    parser.add_argument('-ja', '--jenama', help='input 1-443')
    parser.add_argument('-ps', '--page_start', help='Input page start')
    parser.add_argument('-pe', '--page_end', help='Input page end as you like')

    args = parser.parse_args()
    mode = args.mode
    all = True if args.all else False
    catalogue = args.catalogue
    jenama = args.jenama
    page_start = args.page_start
    page_end = args.page_end

    if mode == 'crawl':
        get_index(all_jenama=all, cat=catalogue, jenama=jenama, start_page=page_start, end_page=page_end)
