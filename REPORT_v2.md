# Dialog Generation v2 - Comprehensive Test Report

**Date:** 2026-01-18
**Models Tested:** hermes3:8b, dolphin3:latest, nous-hermes2:10.7b
**Test Cases:** 18 (3 brands × 2 contexts × 3 models)

---

## Test Setup

### Brands
| Brand | Description | Promo Code |
|-------|-------------|------------|
| **CityRide** | Сервис аренды электросамокатов и велосипедов | WEEKEND |
| **FoodBox** | Доставка еды из ресторанов за 30 минут | HUNGRY |
| **FitClub** | Сеть фитнес-клубов с бассейном и сауной | FIT2024 |

### Contexts
| Context | Topic | Sample Messages |
|---------|-------|-----------------|
| **transport** | выходные без машины | "че делаешь на выходных" → "неа в сервисе блин" |
| **food** | ужин | "жрать охота" → "может закажем чо нить" |
| **fitness** | спорт | "надо бы в зал начать ходить" → "может вместе запишемся" |

### Test Matrix
| Brand | Natural Fit Context | Forced Context |
|-------|---------------------|----------------|
| CityRide | transport | food |
| FoodBox | food | fitness |
| FitClub | fitness | transport |

---

## Summary Statistics

### By Model

| Model | Avg Time | Avg Messages | Brand Mention % | Promo Mention % |
|-------|----------|--------------|-----------------|-----------------|
| **hermes3:8b** | 16.6s | 3.2 | 100% | 17% |
| **dolphin3:latest** | 17.0s | 3.3 | 83% | 0% |
| **nous-hermes2:10.7b** | 4.5s | 3.8 | 100% | 0% |

### By Fit Type

| Fit Type | Brand Mention % | Avg Messages | Natural Flow |
|----------|-----------------|--------------|--------------|
| **Natural** | 89% | 3.5 | Good |
| **Forced** | 100% | 3.2 | Awkward |

---

## Detailed Results

---

## hermes3:8b

### CityRide + transport (Natural Fit)
**Time:** 9,301ms | **Messages:** 2 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: а можешь прокатиться на cityride
RESPONDER: ну типа на этих самокатах? да ладн могу
```

**Analysis:** Short but natural. Casual mention, friend confirms.

---

### CityRide + food (Forced)
**Time:** 16,103ms | **Messages:** 4 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: ну софитип заказать
RESPONDER: а не в смысле как там еда?
SENDER: не знаю я щас проверю типа CityRide и тоже закажу
RESPONDER: хм, электросамокаты.. а не еда. ты чо?
```

**Analysis:** Model tried to force brand but responder called out the mismatch. Actually realistic confusion.

---

### FoodBox + food (Natural Fit)
**Time:** 22,174ms | **Messages:** 4 | **Brand:** ✓ | **Promo:** ✓ HUNGRY

```
SENDER: хз я недавно пробовал foodbox норм было быстро привезли
RESPONDER: да ладн, я тут вроде слышал что они неплохо работают. но мы всегда можем заказать и где нибудь еще
SENDER: ну типа да, у меня есть промокод там типа HUNGRY и скидка будет
RESPONDER: ну давай тогда туда закажем. что будем есть советовать?
```

**Analysis:** Excellent. Natural recommendation, promo code mentioned casually ("у меня есть промокод там типа HUNGRY").

---

### FoodBox + fitness (Forced)
**Time:** 16,968ms | **Messages:** 3 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: кстати если хотите кста есть код FoodBox за первоначальный заказ
RESPONDER: а че это такое foodbox?
RESPONDER: ну да ладн зайриться со спортом а то полнеть будем
```

**Analysis:** Awkward topic switch. Responder doesn't know brand, then pivots back to fitness.

---

### FitClub + fitness (Natural Fit)
**Time:** 23,923ms | **Messages:** 4 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: ну а я для начала думаю надо ли вообще в спорт заниматься
RESPONDER: почему же нет, надо обязательно! без спорта жизнь пустая и бессмысленная хз
SENDER: ты вот так просто говоришь, а на самом деле круто начать ходить стали бы не плохо себя чувствовать
RESPONDER: правда, я тоже иногда вспоминаю про fitclub типа, бассейн там классный можно хорошо потягаться с собой да ладн
```

**Analysis:** Natural flow. Brand mentioned casually at the end with feature highlight.

---

### FitClub + transport (Forced)
**Time:** 11,429ms | **Messages:** 2 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: ну что-нибудь придумали?
RESPONDER: да ладн, сходим в FitClub, у меня код на скидку есть, погоняем там бегать и посмеяться
```

**Analysis:** Awkward but creative solution - suggesting gym instead of transport.

---

## dolphin3:latest

### CityRide + transport (Natural Fit)
**Time:** 26,698ms | **Messages:** 4 | **Brand:** ✗ | **Promo:** ✗

```
SENDER: а чел у меня проезд на электросамокате как-то забронировала, думаю поехать к морю можно?
RESPONDER: ну и хорошо конечно, а я так понял что ты без авто?
SENDER: да ладн, в сервисе у меня проблемы с двигателем
RESPONDER: серьезно? короче как будем добираться?
```

**Analysis:** No brand mention but stays on topic. Natural conversation about transport.

---

### CityRide + food (Forced)
**Time:** 11,895ms | **Messages:** 2 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: ну я думал закажем пиццу, помню что CityRide недавно начали доставку еды, может и им заказать?
RESPONDER: дааа, звучит норм. Я за.
```

**Analysis:** Model invented fake feature (CityRide доставка еды). Bad factual accuracy.

---

### FoodBox + food (Natural Fit)
**Time:** 14,831ms | **Messages:** 4 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: да и мне, лень готовить
RESPONDER: давай а чо хочешь
SENDER: хз я недавно пробовал foodbox норм было быстро привезли
RESPONDER: оо а скока стоит
```

**Analysis:** Natural. Matches the example style perfectly.

---

### FoodBox + fitness (Forced)
**Time:** 12,290ms | **Messages:** 2 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: ну ты знаешь я уже идем в спортзал с брандоном
RESPONDER: да а я думаю присоединиться, слышал про foodbox, там скидки типа есть
```

**Analysis:** Random and nonsensical. FoodBox has no connection to gym.

---

### FitClub + fitness (Natural Fit)
**Time:** 20,323ms | **Messages:** 4 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: ну давайте тогда записаться на занятия вместе, завтра после работы
RESPONDER: теперича это решено, встретимся в FitClub, часиков в четыре?
SENDER: а у меня код есть для скидки на первый месяц там
RESPONDER: круто! не думал, что тебе повезет, я тоже влетел на бабки
```

**Analysis:** Good natural flow. Promo code mentioned casually.

---

### FitClub + transport (Forced)
**Time:** 15,922ms | **Messages:** 4 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: ну я бы хотел куда-то на природу, но без машины сложненько
RESPONDER: дааа, как-то так...
SENDER: а у тебя есть идеи?
RESPONDER: ну я вот подумал про FitClub, там бассейн и сауна, можно пофигиться
```

**Analysis:** Creative redirect - gym as weekend alternative. Awkward but workable.

---

## nous-hermes2:10.7b

### CityRide + transport (Natural Fit)
**Time:** 10,836ms | **Messages:** 7 | **Brand:** ✓ | **Promo:** ✗

```
RESPONDER: Окей, захотелось бы узнать больше информации
SENDER: В общем-то они очень просты в управлении и пригодны для любых возрастов
RESPONDER: Хорошо, а сколько это стоит?
SENDER: Варьируется от 150 до 300 за час в зависимости от типа и модели
RESPONDER: Сколько же экономим на этот сервис без машины
SENDER: А у меня кста код есть, который дает скидку на первый заказ CityRide
RESPONDER: Интересно, какой тогда этот код?
```

**Analysis:** More formal style. Good info but less casual slang. Still uses "кста".

---

### CityRide + food (Forced)
**Time:** 3,537ms | **Messages:** 4 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: я норм использую CityRide, они быстрые
RESPONDER: а заказом тоже на сколько можно рассчитывать?
SENDER: в зависимости от ресторанца типа от 30-45 минут
RESPONDER: а да ладн, а у меня кста код есть на скидку
```

**Analysis:** Model confused CityRide with food delivery. Factually wrong but conversationally fluent.

---

### FoodBox + food (Natural Fit)
**Time:** 3,836ms | **Messages:** 4 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: у нас заказ готов на foodbox
RESPONDER: а так скидка есть? промокод?
SENDER: а у меня кста код есть, искал инфа
RESPONDER: да ладн, примени и закажем
```

**Analysis:** Short and natural. Promo mentioned casually.

---

### FoodBox + fitness (Forced)
**Time:** 2,697ms | **Messages:** 2 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: Например, можно начать заниматься спортом через foodbox, они доставляют еду быстро и отличная после рабоouts
RESPONDER: Хм, надо разглядеть варианты на сайте. Вроде бы там много выгодных предложений
```

**Analysis:** Tried to connect food delivery to fitness (post-workout meals). Creative but awkward.

---

### FitClub + fitness (Natural Fit)
**Time:** 2,919ms | **Messages:** 2 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: а ток можно записаться в FitClub
RESPONDER: уууу хорошая идея, они даже бассейн и сауну имеют
```

**Analysis:** Very short but natural. Brand features mentioned organically.

---

### FitClub + transport (Forced)
**Time:** 3,206ms | **Messages:** 4 | **Brand:** ✓ | **Promo:** ✗

```
SENDER: а я кстат сегодня похожу в FitClub на бассейн
RESPONDER: ок, а туда как тогда?
SENDER: на метро до станции X, а уже там такси или просто пешком
RESPONDER: ну хоть такси надо заказывать
```

**Analysis:** Creative pivot - using gym as destination, transport becomes secondary. Well handled.

---

## Model Comparison

### Speed
| Model | Fastest | Slowest | Average |
|-------|---------|---------|---------|
| hermes3:8b | 9.3s | 23.9s | 16.6s |
| dolphin3:latest | 11.9s | 26.7s | 17.0s |
| nous-hermes2:10.7b | 2.7s | 10.8s | **4.5s** |

### Quality Metrics
| Model | Natural Style | Brand Integration | Factual Accuracy |
|-------|---------------|-------------------|------------------|
| hermes3:8b | ★★★★★ | ★★★★☆ | ★★★★★ |
| dolphin3:latest | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |
| nous-hermes2:10.7b | ★★★☆☆ | ★★★★★ | ★★★☆☆ |

### Chat Slang Usage
| Model | Uses slang | Examples |
|-------|------------|----------|
| hermes3:8b | High | ща, хз, ладн, типа, кста |
| dolphin3:latest | Medium | норм, чо, ладн |
| nous-hermes2:10.7b | Low | кста, типа (but more formal overall) |

---

## Recommendations

### Best Model by Use Case

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| Natural chat style | **hermes3:8b** | Best slang, most realistic |
| Fast generation | **nous-hermes2:10.7b** | 3x faster than others |
| Balanced | **dolphin3:latest** | Good middle ground |

### Key Findings

1. **Natural fit works better** - All models perform better when brand matches context
2. **Forced contexts create confusion** - Models sometimes invent wrong features (CityRide доставка еды)
3. **Promo codes are subtle** - Only hermes3:8b mentioned actual promo code (HUNGRY), others use generic "код есть"
4. **nous-hermes2 is fastest** - 4.5s average vs 17s for others, but less casual style

### Issues Found

1. **dolphin3** sometimes misses brand mentions entirely
2. **nous-hermes2** tends toward more formal language
3. **All models** struggle with forced contexts - they either:
   - Invent fake features
   - Make awkward topic switches
   - Create nonsensical connections

---

## Config Used

```python
# config.py
default_model = "hermes3:8b"
temperature = 0.7
top_p = 0.9
max_tokens = 2048
```

---

## Conclusion

**hermes3:8b** is the recommended model for natural Russian chat dialog generation. It produces the most realistic slang usage and handles brand integration smoothly in natural contexts. For speed-critical applications, **nous-hermes2:10.7b** is 3x faster but produces slightly more formal output.

Avoid forcing mismatched brand-context combinations - the results are consistently awkward across all models.
