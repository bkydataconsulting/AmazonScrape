from django.shortcuts import render
from django.http import HttpResponse
from .scraper import scrape_amazon
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Global variable to store the DataFrame for download
global_df = pd.DataFrame()


def index(request):
    global global_df
    if request.method == "POST":
        try:
            search_query = request.POST.get('search_query').replace(' ', '+')
            num_pages = int(request.POST.get('num_pages'))
            df = scrape_amazon(search_query, num_pages)
            global_df = df  # Store the DataFrame in the global variable
            if df.empty:
                return render(request, 'scraper/index.html', {'error': 'No products found. Please try again.'})
            products = df.to_dict('records')
            return render(request, 'scraper/index.html', {'products': products})
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return render(request, 'scraper/index.html',
                          {'error': 'An error occurred during scraping. Please try again.'})
    return render(request, 'scraper/index.html')


def download_csv(request):
    global global_df
    if global_df.empty:
        return render(request, 'scraper/index.html', {'error': 'No data to download.'})

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scraped_products.csv"'

    global_df.to_csv(path_or_buf=response, index=False)
    return response