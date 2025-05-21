import sys
import argparse
from config import BASE_DIR

# Add project root to path
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

def scrape_url(args=None):
    from scraping.get_services_urls import scrape_all_categories
    scrape_all_categories()

def scrape_services(args=None):
    from scraping.scraper import scrape_all_services
    scrape_all_services()

def preprocess(args=None):
    from preprocessing.preprocess import preprocess
    preprocess()

def run_pipeline(args=None):
    from scraping.get_services_urls import scrape_all_categories
    from scraping.scraper import scrape_all_services
    from preprocessing.preprocess import preprocess
    scrape_all_categories()
    scrape_all_services()
    preprocess()

def run_app(args=None):
    from chatbot.app import app
    debug = getattr(args, "debug", False)
    app.config["DEBUG"] = debug  # Add this line
    app.run(debug=debug)

def main():
    parser = argparse.ArgumentParser(description="Manage Najeeb Chatbot tasks.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("scrape_url", help="get all services URLs grouped by category.")
    subparsers.add_parser("scrape_services", help="Scrape all services.")
    subparsers.add_parser("preprocess", help="Preprocess data.")
    subparsers.add_parser("run_pipeline", help="scrape then preprocess.")

    # Add run_app command with --debug flag
    run_app_parser = subparsers.add_parser("run_app", help="Run the Flask app.")
    run_app_parser.add_argument("--debug", action="store_true", help="Run Flask app in debug mode.")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.command == "scrape_url":
        scrape_url(args)
    elif args.command == "scrape_services":
        scrape_services(args)
    elif args.command == "preprocess":
        preprocess(args)
    elif args.command == "run_pipeline":
        run_pipeline(args)
    elif args.command == "run_app":
        run_app(args)

if __name__ == "__main__":
    main()