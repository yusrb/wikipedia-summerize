from django.shortcuts import render
import wikipedia
from wikipedia.exceptions import PageError, DisambiguationError
import random
import requests

def index(request):
    context = {
        'error': None,
        'hasil': None,
        'mirip': None,
        'page_image': None,
    }

    wikipedia.set_lang('id')

    if 'search_history' not in request.session:
        request.session['search_history'] = []

    if request.method == 'POST':
        search = request.POST.get('search_input', '').strip()
        if not search:
            context['error'] = 'Input tidak valid.'
            return render(request, 'base/index.html', context)

        if search and search not in request.session['search_history']:
            request.session['search_history'].append(search)
            request.session['search_history'] = request.session['search_history'][-5:]
            request.session.modified = True

        try:
            context['hasil'] = wikipedia.summary(search, sentences=7)

            page = wikipedia.page(search)
            context['mirip'] = random.sample(page.links, min(len(page.links), 10)) if page.links else []

            api_url = f"https://id.wikipedia.org/w/api.php?action=query&titles={page.title}&prop=pageimages&format=json&pithumbsize=500"
            response = requests.get(api_url)
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'thumbnail' in page_data:
                    context['page_image'] = page_data['thumbnail']['source']
                    break

        except PageError:
            context['error'] = 'Halaman tidak ditemukan di Wikipedia.'
        except DisambiguationError as e:
            context['error'] = 'Banyak hasil ditemukan. Pilih salah satu opsi di bawah ini:'
            context['mirip'] = random.sample(e.options, min(len(e.options), 10)) if e.options else []
        except Exception as e:
            context['error'] = f'Terjadi kesalahan: {str(e)}'

    return render(request, 'base/index.html', context)