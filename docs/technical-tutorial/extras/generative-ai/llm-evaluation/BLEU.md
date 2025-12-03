---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3
    name: python3
---

# Evaluating LLM Outputs with BLEU

*NLP evaluation metric used in Machine Translation tasks*

*Suitable for measuring corpus level similarity*

*$n$-gram comparison between words in candidate sentence and reference sentences*

*Range: 0 (no match) to 1 (exact match)*


### 1. Libraries
*Install and import necessary libraries*


```python
import nltk
import nltk.translate.bleu_score as bleu

import math
import numpy
import os

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
```

### 2. Dataset
*Array of words: candidate and reference sentences split into words*

```python
hyp = str("she read the book because she was interested in world history").split()
ref_a = str("she read the book because she was interested in world history").split()
ref_b = str("she was interested in world history because she read the book").split()
```

### 3. *Sentence* score calculation
*Compares 1 hypothesis (candidate or source sentence) with 1+ reference sentences, returning the highest score when compared to multiple reference sentences.*

```python
score_ref_a = bleu.sentence_bleu([ref_a], hyp)
print("Hyp and ref_a are the same: {}".format(score_ref_a))
score_ref_b = bleu.sentence_bleu([ref_b], hyp)
print("Hyp and ref_b are different: {}".format(score_ref_b))
score_ref_ab = bleu.sentence_bleu([ref_a, ref_b], hyp)
print("Hyp vs multiple refs: {}".format(score_ref_ab))
```

### 4. *Corpus* score calculation
*Compares 1 candidate document with multiple sentence and 1+ reference documents also with multiple sentences.*

* Different than averaging BLEU scores of each sentence, it calculates the score by *"summing the numerators and denominators for each hypothesis-reference(s) pairs before the division"*

```python
score_ref_a = bleu.corpus_bleu([[ref_a]], [hyp])
print("1 document with 1 reference sentence: {}".format(score_ref_a))
score_ref_a = bleu.corpus_bleu([[ref_a, ref_b]], [hyp])
print("1 document with 2 reference sentences: {}".format(score_ref_a))
score_ref_a = bleu.corpus_bleu([[ref_a], [ref_b]], [hyp, hyp])
print("2 documents with 1 reference sentence each: {}".format(score_ref_a))
```

### 5. BLEU-$n$
*In BLEU-$n$, $n$-gram scores can be obtained in both **sentence** and **corpus** calculations and they're indicated by the **weights** parameter.*

* *weights*: length 4, where each index contains a weight corresponding to its respective $n$-gram.
* $n$-gram with $n \in \{1, 2, 3, 4\}$
* $\textit{weights}=(W_{N=1}, W_{N=2}, W_{N=3}, W_{N=4})$



```python
score_1gram = bleu.sentence_bleu([ref_b], hyp, weights=(1, 0, 0, 0))
score_2gram = bleu.sentence_bleu([ref_b], hyp, weights=(0, 1, 0, 0))
score_3gram = bleu.sentence_bleu([ref_b], hyp, weights=(0, 0, 1, 0))
score_4gram = bleu.sentence_bleu([ref_b], hyp, weights=(0, 0, 0, 1))
print("N-grams: 1-{}, 2-{}, 3-{}, 4-{}".format(score_1gram, score_2gram, score_3gram, score_4gram))
```

* Cumulative N-grams: *by default, the score is calculatedby considering all $N$-grams equally in a geometric mean*

```python
score_ngram1 = bleu.sentence_bleu([ref_b], hyp)
score_ngram = bleu.sentence_bleu([ref_b], hyp, weights=(0.25, 0.25, 0.25, 0.25))
score_ngram_geo = (11 / 11 * 9 / 10 * 6 / 9 * 4 / 8) ** 0.25
print("N-grams: {} = {} = ".format(score_ngram1, score_ngram, score_ngram_geo))
```

### Further testing

```python
hyp = str("she read the book because she was interested in world history").split()
ref_a = str("she was interested in world history because she read the book").split()
hyp_b = str("the book she read was about modern civilizations.").split()
ref_b = str("the book she read was about modern civilizations.").split()

score_a = bleu.sentence_bleu([ref_a], hyp)
score_b = bleu.sentence_bleu([ref_b], hyp_b)
score_ab = bleu.sentence_bleu([ref_a], hyp_b)
score_ba = bleu.sentence_bleu([ref_b], hyp)
score_ref_a = bleu.corpus_bleu([[ref_a], [ref_b]], [hyp, hyp_b])
average = (score_a + score_b) / 2
corpus = math.pow((11 + 8) / 19 * (9 + 7) / (17) * (6 + 6) / (9 + 6) * (4 + 5) / (8 + 5), 1 / 4)
print(
    "Sent: {}, {}, {}, {} - Corpus {}, {}, {}".format(
        score_a, score_b, score_ab, score_ba, score_ref_a, average, corpus
    )
)
```


---

**Previous**: [Bertscore](BERTScore.md) | **Next**: [Mobile Banking > Mobile-Banking](../mobile-banking/mobile-banking.md)
