from django.shortcuts import render
import wikipedia
from wikipedia.exceptions import PageError, DisambiguationError
import random

def index(request):
    context = {
        'error': None,
        'hasil': None,
        'mirip': None,
    }

    wikipedia.set_lang('id')

    if request.method == 'POST':
        search = request.POST.get('search_input', '').strip()
        if not search:
            context['error'] = 'Input tidak valid.'
            return render(request, 'base/index.html', context)

        try:
            context['hasil'] = wikipedia.summary(search, sentences=7)

            page = wikipedia.page(search)
            topik_terkait = page.links
            if topik_terkait:
                context['mirip'] = random.sample(topik_terkait, min(len(topik_terkait), 10))

        except PageError:
            context['error'] = 'Halaman tidak ditemukan di Wikipedia.'
        except DisambiguationError as e:
            context['error'] = 'Banyak hasil ditemukan. Pilih salah satu opsi di bawah ini:'
            if e.options:
                context['mirip'] = random.sample(e.options, min(len(e.options), 10))
        except Exception as e:
            context['error'] = f'Terjadi kesalahan: {str(e)}'

    return render(request, 'base/index.html', context)
