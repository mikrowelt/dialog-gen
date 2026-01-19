# Dialog Generation Test Report

**Generated:** 2026-01-18 20:50
**Models:** hermes3:8b, dolphin3:latest, nous-hermes2:10.7b
**Test Cases:** 18

---

## Brands

| Brand | Description | Promo Code |
|-------|-------------|------------|
| **CityRide** | Сервис аренды электросамокатов и велосипедов | WEEKEND |
| **FoodBox** | Доставка еды из ресторанов за 30 минут | HUNGRY |
| **FitClub** | Сеть фитнес-клубов с бассейном и сауной | FIT2024 |

## Contexts

### transport
```
sender: че делаешь на выходных
responder: хз пока не решил
sender: может куда съездим
responder: у тебя машина есть
sender: неа в сервисе блин
```

### food
```
sender: жрать охота
responder: да и мне, лень готовить
sender: может закажем чо нить
```

### fitness
```
sender: слушай надо бы в зал начать ходить
responder: да я тоже думаю об этом
sender: может вместе запишемся
```

---

## Summary

| Model | Avg Time | Messages | Brand % | Promo % |
|-------|----------|----------|---------|---------|
| hermes3:8b | 19.7s | 3.8 | 83% | 17% |
| dolphin3:latest | 20.7s | 4.8 | 100% | 0% |
| nous-hermes2:10.7b | 4.6s | 4.2 | 83% | 0% |

---

## hermes3:8b

### CityRide + transport (Natural Fit)

**Brand:** Сервис аренды электросамокатов и велосипедов | **Promo:** WEEKEND
**Time:** 18689ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: че делаешь на выходных
responder: хз пока не решил
sender: может куда съездим
responder: у тебя машина есть
sender: неа в сервисе блин
```

**Generated (output):**
```
SENDER: ну а вдруг можешь где прокатиться
RESPONDER: я вот думал может в CityRide прокатиться ща код есть типа free30 и можно месяц за 10 руб взять
```

---

### CityRide + food (Forced)

**Brand:** Сервис аренды электросамокатов и велосипедов | **Promo:** WEEKEND
**Time:** 17017ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: жрать охота
responder: да и мне, лень готовить
sender: может закажем чо нить
```

**Generated (output):**
```
SENDER: ну тогда foodbox давай
RESPONDER: ладно foodbox а у меня кста код есть cityride за 20% на все продукты
SENDER: а шо это cityride?
RESPONDER: ты щас город прокател на электросамокате видел тут рекламу
```

---

### FoodBox + food (Natural Fit)

**Brand:** Доставка еды из ресторанов за 30 минут | **Promo:** HUNGRY
**Time:** 16485ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: жрать охота
responder: да и мне, лень готовить
sender: может закажем чо нить
```

**Generated (output):**
```
SENDER: хз я недавно пробовал foodbox норм было быстро привезли
RESPONDER: оо а скока стоит
RESPONDER: да ладн иногда платить для комфорта можно
```

---

### FoodBox + fitness (Forced)

**Brand:** Доставка еды из ресторанов за 30 минут | **Promo:** HUNGRY
**Time:** 16022ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: слушай надо бы в зал начать ходить
responder: да я тоже думаю об этом
sender: может вместе запишемся
```

**Generated (output):**
```
SENDER: хз да ладн но что лучше зал или foodbox типа
RESPONDER: ну я за зал конечно спортсмен ты забыл
SENDER: да знаю, но foodbox типа удобно ща
RESPONDER: да ладн, но в зал ходить все же полезнее
```

---

### FitClub + fitness (Natural Fit)

**Brand:** Сеть фитнес-клубов с бассейном и сауной | **Promo:** FIT2024
**Time:** 17606ms | **Brand mentioned:** ✗ | **Promo mentioned:** ✓

**Context (input):**
```
sender: слушай надо бы в зал начать ходить
responder: да я тоже думаю об этом
sender: может вместе запишемся
```

**Generated (output):**
```
SENDER: погуглил.fit2024 клубы тут есть ща
RESPONDER: ну и как туда ок?
SENDER: вот интересно, бассейн там есть афиша посмотрите типа
RESPONDER: ладн будет заниматься в таком спорт займемся
```

---

### FitClub + transport (Forced)

**Brand:** Сеть фитнес-клубов с бассейном и сауной | **Promo:** FIT2024
**Time:** 32399ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: че делаешь на выходных
responder: хз пока не решил
sender: может куда съездим
responder: у тебя машина есть
sender: неа в сервисе блин
```

**Generated (output):**
```
SENDER: ну что делать без машины щас заехать куда-то не получится
RESPONDER: да ладн, но можно просто отдохнуть дома и никуда не выезжать
SENDER: а как ты думаешь, без машины жизнь хуже или лучше?
RESPONDER: я думаю, иногда без машины спокойнее. можно просто повеселиться дома с друзьями типа в FITClub бассейн послабше
SENDER: даа, но как без неё прокатитьась на велопатере или поехать в гости?
RESPONDER: можешь и так, а то я вчера друзей вызвались отвезти на мото и был норм чел
```

---

## dolphin3:latest

### CityRide + transport (Natural Fit)

**Brand:** Сервис аренды электросамокатов и велосипедов | **Promo:** WEEKEND
**Time:** 16551ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: че делаешь на выходных
responder: хз пока не решил
sender: может куда съездим
responder: у тебя машина есть
sender: неа в сервисе блин
```

**Generated (output):**
```
SENDER: ну я вот думал, может взять электросамокат из CityRide, походить на что-то новенькое
RESPONDER: а че там с ценой?
```

---

### CityRide + food (Forced)

**Brand:** Сервис аренды электросамокатов и велосипедов | **Promo:** WEEKEND
**Time:** 29539ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: жрать охота
responder: да и мне, лень готовить
sender: может закажем чо нить
```

**Generated (output):**
```
SENDER: мне бы чпокать срочно
RESPONDER: я что, заказываю? ну
SENDER: ну да, закажем че
RESPONDER: думаю хамон и сыр да ладн
SENDER: я вот смотрел на cityride байл эти самокаты хитные какие-то
RESPONDER: а у меня есть промокод? ну так, для еды пфф
SENDER: ну и ладн все чпокаем сами да
RESPONDER: хм, звучит норм, давай тогда
```

---

### FoodBox + food (Natural Fit)

**Brand:** Доставка еды из ресторанов за 30 минут | **Promo:** HUNGRY
**Time:** 17684ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: жрать охота
responder: да и мне, лень готовить
sender: может закажем чо нить
```

**Generated (output):**
```
SENDER: ну что там, давай закажем пиццу
RESPONDER: хорошо, ты выбираешь или мне?
SENDER: я уже что-то нашел, хз я недавно пробовал foodbox норм было быстро привезли
RESPONDER: да ладн, если уж очень хочется быстрый вариант
```

---

### FoodBox + fitness (Forced)

**Brand:** Доставка еды из ресторанов за 30 минут | **Promo:** HUNGRY
**Time:** 26107ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: слушай надо бы в зал начать ходить
responder: да я тоже думаю об этом
sender: может вместе запишемся
```

**Generated (output):**
```
SENDER: "text": "ну я уже скинул лишний вес короче"
RESPONDER: },
SENDER: "text": "пару чашек кофе тебе помогло?"
RESPONDER: "text": "да но и здоровье тоже важно"
SENDER: },
RESPONDER: "text": "да ладн, надо крутиться как фитнес-тренер в рекламе"
SENDER: "text": "а я вот думаю заниматься спортом с foodbox"
RESPONDER: },
SENDER: "text": "хм, как так?"
```

---

### FitClub + fitness (Natural Fit)

**Brand:** Сеть фитнес-клубов с бассейном и сауной | **Promo:** FIT2024
**Time:** 24152ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: слушай надо бы в зал начать ходить
responder: да я тоже думаю об этом
sender: может вместе запишемся
```

**Generated (output):**
```
SENDER: ну и где ты смотрел я тут уже подписался на FitClub месяц назад
RESPONDER: а мне еще предстоит это сделать, блин, ты как там тренируешься?
SENDER: короче просто пошли туда после работы, сауна хороша и бассейн большой
RESPONDER: да ладн подысься на работу вместе ты бы там тоже повеселишься да?
```

---

### FitClub + transport (Forced)

**Brand:** Сеть фитнес-клубов с бассейном и сауной | **Promo:** FIT2024
**Time:** 10118ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: че делаешь на выходных
responder: хз пока не решил
sender: может куда съездим
responder: у тебя машина есть
sender: неа в сервисе блин
```

**Generated (output):**
```
SENDER: ну ты че думаешь про фитнес-тренды на выходные?
RESPONDER: хм, интересно... а как насчет FitClub? у меня там еще код есть.
```

---

## nous-hermes2:10.7b

### CityRide + transport (Natural Fit)

**Brand:** Сервис аренды электросамокатов и велосипедов | **Promo:** WEEKEND
**Time:** 9001ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: че делаешь на выходных
responder: хз пока не решил
sender: может куда съездим
responder: у тебя машина есть
sender: неа в сервисе блин
```

**Generated (output):**
```
SENDER: а толку машина без выходных
RESPONDER: правда да ладн, идея
SENDER: вот а подумай что если покататься на электросамокате?
RESPONDER: окей типа как там с арендой
SENDER: а у меня кста код есть на cityride
RESPONDER: ну давай в какую сторону поедем?
SENDER: например в парк, а там смотреть крутые виды
```

---

### CityRide + food (Forced)

**Brand:** Сервис аренды электросамокатов и велосипедов | **Promo:** WEEKEND
**Time:** 2176ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: жрать охота
responder: да и мне, лень готовить
sender: может закажем чо нить
```

**Generated (output):**
```
SENDER: есть ли в CityRide какая-то доставка еды?
RESPONDER: недавно услышал, что они начали экспериментировать с этим
```

---

### FoodBox + food (Natural Fit)

**Brand:** Доставка еды из ресторанов за 30 минут | **Promo:** HUNGRY
**Time:** 3740ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: жрать охота
responder: да и мне, лень готовить
sender: может закажем чо нить
```

**Generated (output):**
```
SENDER: а у меня кста код есть на скидку на foodbox
RESPONDER: окей давай используй
SENDER: ну и что тебе сегодня захочется
RESPONDER: хм я точно не решал
```

---

### FoodBox + fitness (Forced)

**Brand:** Доставка еды из ресторанов за 30 минут | **Promo:** HUNGRY
**Time:** 4454ms | **Brand mentioned:** ✗ | **Promo mentioned:** ✗

**Context (input):**
```
sender: слушай надо бы в зал начать ходить
responder: да я тоже думаю об этом
sender: может вместе запишемся
```

**Generated (output):**
```
SENDER: надо же найти что-то подходящее для нас
RESPONDER: да, ведь у меня есть определенные предпочтения в спорте
SENDER: например, я думаю, что зал подходит для нас всем
RESPONDER: у меня есть идея: попробуем сначала что-то проще, типа йоги или аэробики
```

---

### FitClub + fitness (Natural Fit)

**Brand:** Сеть фитнес-клубов с бассейном и сауной | **Promo:** FIT2024
**Time:** 5181ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: слушай надо бы в зал начать ходить
responder: да я тоже думаю об этом
sender: может вместе запишемся
```

**Generated (output):**
```
SENDER: я записался в FitClub, они хорошие клубы, бассейн и сауна есть
RESPONDER: а кста типа сколько у них стоить месяц?
SENDER: у меня кста код есть на скидку, может это тебе тоже подойдет
RESPONDER: а сколько у тебя итог со скидкой?
```

---

### FitClub + transport (Forced)

**Brand:** Сеть фитнес-клубов с бассейном и сауной | **Promo:** FIT2024
**Time:** 3312ms | **Brand mentioned:** ✓ | **Promo mentioned:** ✗

**Context (input):**
```
sender: че делаешь на выходных
responder: хз пока не решил
sender: может куда съездим
responder: у тебя машина есть
sender: неа в сервисе блин
```

**Generated (output):**
```
SENDER: а может поехали бы на занятия FitClub?
RESPONDER: окей, тогда сходим туда
SENDER: ну и после можно покататься на велотрейнере
RESPONDER: ах да, у меня кста код на FitClub, скидка будет
```

---

## Recommendations

| Use Case | Model | Why |
|----------|-------|-----|
| Natural chat | hermes3:8b | Best slang usage |
| Speed | nous-hermes2:10.7b | 3-4x faster |
| Balanced | dolphin3 | Good middle ground |