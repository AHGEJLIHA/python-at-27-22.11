import concurrent.futures
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from tqdm import tqdm

url = 'https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0'

res = open('res.txt', 'w', encoding='utf8')

for i in tqdm(range(100)):
    html = urlopen(url).read().decode('utf8')
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')

    for l in links:
        href = l.get('href')
        if href and href.startswith('http') and 'wiki' not in href:
            print(href, file=res)

from urllib.request import Request, urlopen

links = open('res.txt', encoding='utf8').read().split('\n')


def check_links(links):
    for url in links:
        try:
            request = Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 9.0; Win65; x64; rv:97.0) '
                                       'Gecko/20105107 Firefox/92.0'},
            )
            resp = urlopen(request, timeout=5)
            code = resp.code
            print(code)
            resp.close()
        except Exception as e:
            print(url, e)


# Начало отсчета времени
#start_time = time.time()
#check_links()
#end_time = time.time()
# время синхронной проверки ссылок
#print("--- %s seconds ---" % end_time - start_time)


# Код с использованием ThreadPoolExecutor
def split_to_parts(links, count):
    intDiv, mod = (len(links) // count, len(links) % count)
    return [links[min(i, mod):(i + 1) * intDiv + i * intDiv + min(i + 1, mod)]
            for i in range(count)]


worker_count = 100
splited_links = split_to_parts(links, worker_count)
dict_worker_links = {worker_id: splited_links[worker_id]
                     for worker_id in range(worker_count)}

for key in dict_worker_links:
    print(key, ':', len(dict_worker_links[key]))

async_start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
    dict_future_worker = {executor.submit(check_links, dict_worker_links[worker]):
                              worker for worker in range(worker_count)}
    for future in concurrent.futures.as_completed(dict_future_worker):
        worker = dict_future_worker[future]
        print({worker}, "finished checking ", {len(dict_worker_links[worker])}," URLs")
async_end_time = time.time()
result_time = async_end_time-async_start_time
print(str(result_time) + " seconds")

