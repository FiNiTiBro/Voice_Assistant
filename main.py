import queue
import asyncio
import vosk
import sounddevice as sd
import json
import words
from words import data_set
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from skills import *
import g4f



q = queue.Queue()

model = vosk.Model('model_small')

device = sd.default.device
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def load_cache():
    try:
        with open('cache.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def open_cache():
    with open('cache.json', 'r') as file:
        data = file.read()

def save_cache(cache):
    with open('cache.json', 'w') as file:
        json.dump(cache, file)

cache = load_cache()


async def ask_gpt(chat_context, user_messages):
    messages = [{"role": "system", "content": open_cache()}]
    model = "gpt-4-turbo"
    for context_message in chat_context:
        messages.append({"role": context_message["role"], "content": context_message["content"]})
    messages.append({"role": "user", "content": user_messages})
    response = g4f.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=500,
        language='ru',
    )
    return response

async def recognize(data, vectorizer, clf):
    data_words = data.split()
    matched_keywords = [word for word in data_words if word in data_set]
    trg = words.TRIGGERS.intersection(data.split())

    if not trg:
        return
    else:
        if not matched_keywords:
            if data in cache:
                response = cache[data]
            else:
                response = await ask_gpt(context, data)
                cache[data] = response

            context.append({"role": "user", "content": data})
            context.append({"role": "assistant", "content": response})
            print(response)
            await speaker(response)
            save_cache(cache)
        elif matched_keywords:
            new_data = data.replace(list(trg)[0], '')
            text_vector = vectorizer.transform([new_data]).toarray()[0]
            answer = clf.predict([text_vector])[0]

            func_name = answer.split()[0]
            await speaker(answer.replace(func_name, ''))
            exec(func_name + '()')

async def main():
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(list(words.data_set.keys()))

    clf = LogisticRegression()
    clf.fit(vectors, list(words.data_set.values()))

    del words.data_set

    with sd.RawInputStream(samplerate=samplerate, blocksize=16000, device=device[0], dtype='int16',
                                channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())['text']
                print(data)
                await recognize(data, vectorizer, clf)
save_cache(cache)

if __name__ == "__main__":
    context = []
    asyncio.run(main())